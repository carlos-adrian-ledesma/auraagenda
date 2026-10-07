from __future__ import annotations

from zoneinfo import available_timezones

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QWizard,
    QWizardPage,
)

from .styles import THEMES


class OnboardingWizard(QWizard):
    """First-run setup wizard.

    Labels are kept as explicit QLabel instances instead of relying on
    QFormLayout field-label lookup. Some PySide6/Qt combinations can return
    None for rows created from empty string labels, which previously caused
    AuraAgenda to crash on first launch while translating the wizard.
    """

    def __init__(self, db, i18n, parent=None):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self._labels: dict[str, QLabel] = {}
        self.setMinimumSize(680, 520)
        self.resize(760, 580)

        self.p1 = QWizardPage()
        self.f1 = QFormLayout(self.p1); self._tune_form(self.f1)
        self.language = QComboBox()
        self.language.addItem("Español", "es")
        self.language.addItem("English", "en")
        self.name = QLineEdit()
        self.country = QLineEdit()
        self._add_row(self.f1, "language", self.language)
        self._add_row(self.f1, "name", self.name)
        self._add_row(self.f1, "country", self.country)
        self.addPage(self.p1)

        self.p2 = QWizardPage()
        self.f2 = QFormLayout(self.p2); self._tune_form(self.f2)
        self.timezone = QComboBox()
        self.timezone.setEditable(True)
        self.timezone.addItems(sorted(available_timezones()))
        self.timezone.setCurrentText(db.setting("timezone", ""))
        self.currency = QComboBox()
        self.currency.setEditable(True)
        self.currency.addItems(["AUD", "ARS", "USD", "EUR", "BRL", "GBP", "JPY", "CAD", "NZD"])
        self.currency.setCurrentIndex(-1)
        self.date_format = QComboBox()
        self.date_format.addItems(["dd/MM/yyyy", "MM/dd/yyyy", "yyyy-MM-dd"])
        self._add_row(self.f2, "timezone", self.timezone)
        self._add_row(self.f2, "currency", self.currency)
        self._add_row(self.f2, "date_format", self.date_format)
        self.addPage(self.p2)

        self.p3 = QWizardPage()
        self.f3 = QFormLayout(self.p3); self._tune_form(self.f3)
        self.water = QSpinBox()
        self.water.setRange(0, 10000)
        self.water.setValue(2000)
        self.cycle = QCheckBox()
        self.sleep = QCheckBox()
        self.mood = QCheckBox()
        self.beauty = QCheckBox()
        self.style = QCheckBox()
        self.multimedia = QCheckBox()
        for widget in (self.cycle, self.sleep, self.mood, self.beauty, self.style, self.multimedia):
            widget.setChecked(True)
        self._add_row(self.f3, "water", self.water)
        self._add_row(self.f3, "cycle", self.cycle)
        self._add_row(self.f3, "sleep", self.sleep)
        self._add_row(self.f3, "mood", self.mood)
        self._add_row(self.f3, "beauty", self.beauty)
        self._add_row(self.f3, "style", self.style)
        self._add_row(self.f3, "multimedia", self.multimedia)
        self.addPage(self.p3)

        self.p4 = QWizardPage()
        self.f4 = QFormLayout(self.p4); self._tune_form(self.f4)
        self.theme = QComboBox()
        self.theme.addItems(THEMES.keys())
        self.pin = QLineEdit()
        self.pin.setEchoMode(QLineEdit.Password)
        self._add_row(self.f4, "theme", self.theme)
        self._add_row(self.f4, "pin", self.pin)
        self.addPage(self.p4)

        self.language.currentIndexChanged.connect(self.retranslate)
        self.retranslate()


    def _tune_form(self, form: QFormLayout) -> None:
        form.setContentsMargins(24, 20, 24, 20)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(13)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

    def _add_row(self, form: QFormLayout, key: str, widget) -> None:
        label = QLabel()
        label.setBuddy(widget)
        label.setMinimumWidth(170)
        if hasattr(widget, "setMaximumWidth"):
            widget.setMaximumWidth(480)
        self._labels[key] = label
        form.addRow(label, widget)

    def retranslate(self):
        lang = self.language.currentData() or "es"
        es = lang == "es"
        self.setWindowTitle("Configuración de AuraAgenda" if es else "AuraAgenda Setup")
        self.p1.setTitle("Bienvenida" if es else "Welcome")
        self.p2.setTitle("Región" if es else "Region")
        self.p3.setTitle("Módulos" if es else "Modules")
        self.p4.setTitle("Apariencia y privacidad" if es else "Appearance and privacy")

        texts = {
            "language": "Idioma" if es else "Language",
            "name": "Nombre" if es else "Name",
            "country": "País" if es else "Country",
            "timezone": "Zona horaria" if es else "Timezone",
            "currency": "Moneda" if es else "Currency",
            "date_format": "Formato de fecha" if es else "Date format",
            "water": "Objetivo de agua (ml)" if es else "Water goal (ml)",
            "cycle": "Ciclo" if es else "Cycle",
            "sleep": "Sueño" if es else "Sleep",
            "mood": "Estado de ánimo" if es else "Mood",
            "beauty": "Belleza" if es else "Beauty",
            "style": "Estilo" if es else "Style",
            "multimedia": "Multimedia",
            "theme": "Tema" if es else "Theme",
            "pin": "PIN local opcional" if es else "Optional local PIN",
        }
        for key, text in texts.items():
            label = self._labels.get(key)
            if label is not None:
                label.setText(text)

    def accept(self):
        vals = {
            "language": self.language.currentData(),
            "user_name": self.name.text().strip() or ("Tu nombre" if self.language.currentData() == "es" else "Your name"),
            "country": self.country.text().strip(),
            "timezone": self.timezone.currentText().strip(),
            "currency": self.currency.currentText().strip().upper(),
            "date_format": self.date_format.currentText(),
            "water_goal": str(self.water.value()),
            "theme": self.theme.currentText(),
            "module_cycle": "1" if self.cycle.isChecked() else "0",
            "module_sleep": "1" if self.sleep.isChecked() else "0",
            "module_mood": "1" if self.mood.isChecked() else "0",
            "module_beauty": "1" if self.beauty.isChecked() else "0",
            "module_style": "1" if self.style.isChecked() else "0",
            "module_multimedia": "1" if self.multimedia.isChecked() else "0",
            "onboarding_complete": "1",
        }
        if self.pin.text():
            from .services.privacy import make_pin_hash, validate_new_pin

            valid, _ = validate_new_pin(self.pin.text())
            if not valid:
                QMessageBox.warning(
                    self,
                    "AuraAgenda",
                    "El PIN debe tener al menos 6 caracteres."
                    if self.language.currentData() == "es"
                    else "The PIN must contain at least 6 characters.",
                )
                return
            h, s = make_pin_hash(self.pin.text())
            vals["pin_hash"] = h
            vals["pin_salt"] = s
        self.db.set_settings(vals)
        self.i18n.set_language(vals["language"])
        super().accept()
