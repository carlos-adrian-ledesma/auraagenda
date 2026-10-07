from __future__ import annotations

from PySide6.QtCore import QDate, QTime, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMessageBox, QPushButton, QScrollArea, QSpinBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QTimeEdit, QVBoxLayout, QWidget
)

from .base import Page
from ..database import Database
from ..widgets import FieldSpec


class GenericCrudPage(Page):
    changed = Signal()

    def __init__(
        self, db: Database, i18n, page_key: str, subtitle_es: str, subtitle_en: str,
        table: str, columns: list[str], fields: list[FieldSpec], order_by: str = "id DESC"
    ):
        super().__init__()
        self.db, self.i18n, self.page_key, self.table = db, i18n, page_key, table
        self.subtitle_es, self.subtitle_en = subtitle_es, subtitle_en
        self.columns, self.fields, self.order_by = columns, fields, order_by

        toolbar = QFrame()
        toolbar.setObjectName("ActionBar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(8)
        self.search = QLineEdit()
        self.search.setMaximumWidth(520)
        self.search.textChanged.connect(self.refresh)
        self.add_btn = QPushButton()
        self.add_btn.setObjectName("Primary")
        self.add_btn.setProperty("variant", "primary")
        self.edit_btn = QPushButton()
        self.del_btn = QPushButton()
        self.del_btn.setObjectName("Danger")
        self.del_btn.setProperty("variant", "danger")
        toolbar_layout.addWidget(self.search, 1)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.del_btn)
        self.layout_root.addWidget(toolbar)

        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setShowGrid(False)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.verticalHeader().setDefaultSectionSize(38)
        self.table_widget.horizontalHeader().setMinimumSectionSize(90)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.layout_root.addWidget(self.table_widget, 1)

        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.del_btn.clicked.connect(self.delete_record)
        self.table_widget.itemDoubleClicked.connect(lambda _item: self.edit_record())
        self.retranslate()
        self.refresh()

    def lang(self):
        return self.i18n.language

    def field_label(self, name: str) -> str:
        spec = next((s for s in self.fields if s.name == name), None)
        if spec:
            return spec.label_es if self.lang() == "es" else spec.label_en
        return name.replace("_", " ").title()

    def retranslate(self):
        self.title_label.setText(self.i18n.t(self.page_key))
        self.subtitle_label.setText(self.subtitle_es if self.lang() == "es" else self.subtitle_en)
        self.search.setPlaceholderText(self.i18n.t("common.search") + "…")
        self.add_btn.setText("＋ " + self.i18n.t("common.add"))
        self.edit_btn.setText(self.i18n.t("common.edit"))
        self.del_btn.setText(self.i18n.t("common.delete"))
        self.refresh()

    def refresh(self):
        if not hasattr(self, "table_widget"):
            return
        term = self.search.text().strip() if hasattr(self, "search") else ""
        sql = f"SELECT * FROM {self.table} WHERE deleted=0"
        params = []
        if term:
            text_cols = [
                c for c in self.columns
                if c not in {"id", "progress", "amount", "price", "intensity", "quality"}
            ]
            if text_cols:
                sql += " AND (" + " OR ".join(f"CAST({c} AS TEXT) LIKE ?" for c in text_cols) + ")"
                params = [f"%{term}%"] * len(text_cols)
        sql += f" ORDER BY {self.order_by}"
        try:
            rows = self.db.all(sql, params)
        except Exception:
            rows = []

        self.table_widget.setUpdatesEnabled(False)
        self.table_widget.setColumnCount(len(self.columns) + 1)
        self.table_widget.setHorizontalHeaderLabels(["ID"] + [self.field_label(c) for c in self.columns])
        self.table_widget.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table_widget.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            for c, name in enumerate(self.columns, 1):
                value = row[name] if name in row.keys() and row[name] is not None else ""
                if name in {
                    "priority", "status", "repeat_rule", "enabled", "completed", "frequency",
                    "active", "txn_type", "storage_mode", "category", "list_type", "occasion",
                    "intensity", "repurchase",
                }:
                    value = self.i18n.choice(str(value))
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                self.table_widget.setItem(r, c, item)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.setColumnWidth(0, min(self.table_widget.columnWidth(0), 72))
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setUpdatesEnabled(True)

    def selected_id(self):
        row = self.table_widget.currentRow()
        if row < 0:
            return None
        item = self.table_widget.item(row, 0)
        return int(item.text()) if item else None

    def _editor(self, spec: FieldSpec, value=None):
        value_text = "" if value is None else str(value)
        if spec.kind == "multiline":
            widget = QTextEdit()
            widget.setPlainText(value_text or spec.default)
            widget.setMinimumHeight(100)
            return widget
        if spec.kind == "combo":
            widget = QComboBox()
            for choice in spec.choices:
                widget.addItem(self.i18n.choice(str(choice)), str(choice))
            target = value_text or spec.default
            idx = widget.findData(target)
            if idx < 0:
                idx = widget.findText(target)
            if idx >= 0:
                widget.setCurrentIndex(idx)
            return widget
        if spec.kind == "date":
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            parsed = QDate.fromString(value_text, "yyyy-MM-dd")
            widget.setDate(parsed if parsed.isValid() else QDate.currentDate())
            widget.setDisplayFormat("yyyy-MM-dd")
            return widget
        if spec.kind == "time":
            widget = QTimeEdit()
            parsed = QTime.fromString(value_text, "HH:mm")
            widget.setTime(parsed if parsed.isValid() else QTime.currentTime())
            widget.setDisplayFormat("HH:mm")
            return widget
        if spec.kind == "int":
            widget = QSpinBox()
            widget.setRange(0, 1000000)
            widget.setValue(int(float(value_text or spec.default or 0)))
            return widget
        if spec.kind == "double":
            widget = QDoubleSpinBox()
            widget.setRange(0, 999999999)
            widget.setDecimals(2)
            widget.setValue(float(value_text or spec.default or 0))
            return widget
        if spec.kind == "bool":
            widget = QCheckBox()
            widget.setChecked((value_text or spec.default) in {"1", "true", "True", "Yes", "Sí"})
            return widget
        return QLineEdit(value_text or spec.default)

    def _value(self, widget):
        if isinstance(widget, QTextEdit):
            return widget.toPlainText().strip()
        if isinstance(widget, QComboBox):
            return widget.currentData() if widget.currentData() is not None else widget.currentText()
        if isinstance(widget, QDateEdit):
            return widget.date().toString("yyyy-MM-dd")
        if isinstance(widget, QTimeEdit):
            return widget.time().toString("HH:mm")
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        if isinstance(widget, QCheckBox):
            return 1 if widget.isChecked() else 0
        return widget.text().strip()

    def _dialog(self, record=None):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.i18n.t("common.edit") if record else self.i18n.t("common.add"))
        dlg.setMinimumSize(560, 420)
        dlg.resize(680, 620)
        root = QVBoxLayout(dlg)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        scroll = QScrollArea(dlg)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        host = QWidget()
        host.setObjectName("ScrollViewport")
        form = QFormLayout(host)
        form.setContentsMargins(6, 4, 12, 10)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(11)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        editors = {}
        for spec in self.fields:
            value = record[spec.name] if record is not None and spec.name in record.keys() else None
            editor = self._editor(spec, value)
            if not isinstance(editor, QCheckBox):
                editor.setMinimumWidth(280)
                editor.setMaximumWidth(480)
            editors[spec.name] = editor
            label = QLabel((spec.label_es if self.lang() == "es" else spec.label_en) + (" *" if spec.required else ""))
            label.setMinimumWidth(150)
            form.addRow(label, editor)
        scroll.setWidget(host)
        root.addWidget(scroll, 1)

        box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        box.accepted.connect(dlg.accept)
        box.rejected.connect(dlg.reject)
        root.addWidget(box)

        if dlg.exec() != QDialog.Accepted:
            return None
        values = {key: self._value(widget) for key, widget in editors.items()}
        for spec in self.fields:
            if spec.required and str(values.get(spec.name, "")) == "":
                QMessageBox.warning(
                    self, self.i18n.t("error.title"),
                    f"{spec.label_es if self.lang() == 'es' else spec.label_en}: "
                    f"{'requerido' if self.lang() == 'es' else 'required'}",
                )
                return None
        return values

    def add_record(self):
        values = self._dialog()
        if not values:
            return
        cols = set(r[1] for r in self.db.all(f"PRAGMA table_info({self.table})"))
        now = self.db.now()
        if "created_at" in cols:
            values["created_at"] = now
        if "updated_at" in cols:
            values["updated_at"] = now
        names = list(values)
        rid = self.db.execute(
            f"INSERT INTO {self.table}({','.join(names)}) VALUES({','.join('?' for _ in names)})",
            [values[n] for n in names],
        )
        self.db.audit("CREATE", self.table, rid)
        self.refresh()
        self.changed.emit()

    def edit_record(self):
        rid = self.selected_id()
        if rid is None:
            return
        record = self.db.one(f"SELECT * FROM {self.table} WHERE id=?", (rid,))
        values = self._dialog(record)
        if not values:
            return
        cols = set(r[1] for r in self.db.all(f"PRAGMA table_info({self.table})"))
        if "updated_at" in cols:
            values["updated_at"] = self.db.now()
        names = list(values)
        self.db.execute(
            f"UPDATE {self.table} SET " + ",".join(f"{n}=?" for n in names) + " WHERE id=?",
            [values[n] for n in names] + [rid],
        )
        self.db.audit("UPDATE", self.table, rid)
        self.refresh()
        self.changed.emit()

    def delete_record(self):
        rid = self.selected_id()
        if rid is None:
            return
        if QMessageBox.question(
            self, self.i18n.t("common.confirm"), self.i18n.t("confirm.delete")
        ) != QMessageBox.Yes:
            return
        self.db.soft_delete(self.table, rid)
        self.refresh()
        self.changed.emit()
