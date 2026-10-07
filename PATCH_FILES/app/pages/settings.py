from __future__ import annotations

from pathlib import Path
from zoneinfo import available_timezones

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
    QInputDialog, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QSpinBox,
    QStackedWidget
)

from .base import Page
from ..design_system import SIZING
from ..services.migration import LegacyMigrationService
from ..services.privacy import make_pin_hash, validate_new_pin
from ..styles import THEMES
from ..services.network_guard import canonical_trusted_networks, primary_local_ipv4, suggested_local_network
from ..services.recovery import RecoveryService
from ..widgets import ScrollPage, SectionCard


class SettingsPage(Page):
    """Settings redesigned around a vertical category rail and reusable cards.

    The previous horizontal QTabWidget compressed nine tabs into a small width and
    exposed native white backgrounds.  This layout is stable from 1024px upward,
    scrolls each category independently and caps form widths to avoid oversized
    fields on 1920px displays.
    """

    theme_changed = Signal(str)
    language_changed = Signal(str)
    settings_changed = Signal()

    SECTION_KEYS = [
        "settings.general", "settings.appearance", "settings.language_region",
        "settings.notifications", "settings.wellness", "settings.privacy",
        "settings.data_backup", "settings.files", "settings.about",
    ]

    def __init__(self, db, i18n):
        super().__init__()
        self.db = db
        self.i18n = i18n
        self.field_labels: dict[str, QLabel] = {}
        self.cards: dict[str, SectionCard] = {}
        self.recovery_service = RecoveryService(db)
        self.recovery_service.ensure_installation_id()

        self.body = QFrame(self)
        self.body.setObjectName("SettingsBody")
        body_layout = QHBoxLayout(self.body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(16)

        self.section_nav = QListWidget(self.body)
        self.section_nav.setObjectName("SettingsNav")
        self.section_nav.setFixedWidth(SIZING["settings_nav_width"])
        self.section_nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.section_nav.setVerticalScrollMode(QListWidget.ScrollPerPixel)

        self.stack = QStackedWidget(self.body)
        self.stack.setObjectName("SettingsStack")
        body_layout.addWidget(self.section_nav, 0)
        body_layout.addWidget(self.stack, 1)
        self.layout_root.addWidget(self.body, 1)

        self.action_bar = QFrame(self)
        self.action_bar.setObjectName("ActionBar")
        actions = QHBoxLayout(self.action_bar)
        actions.setContentsMargins(12, 8, 12, 8)
        actions.setSpacing(10)
        self.save_hint = QLabel()
        self.save_hint.setObjectName("Muted")
        self.reset_btn = QPushButton()
        self.reset_btn.setProperty("variant", "ghost")
        self.save_btn = QPushButton()
        self.save_btn.setObjectName("Primary")
        self.save_btn.setProperty("variant", "primary")
        actions.addWidget(self.save_hint)
        actions.addStretch(1)
        actions.addWidget(self.reset_btn)
        actions.addWidget(self.save_btn)
        self.layout_root.addWidget(self.action_bar)

        self._build()
        self.section_nav.currentRowChanged.connect(self._select_section)
        self.save_btn.clicked.connect(self.save)
        self.reset_btn.clicked.connect(self.reset_defaults)
        self.section_nav.setCurrentRow(0)
        self.retranslate()
        self.load()

    def _new_section(self) -> ScrollPage:
        page = ScrollPage(max_content_width=920)
        self.stack.addWidget(page)
        self.section_nav.addItem("")
        return page

    def _card(self, page: ScrollPage, key: str) -> SectionCard:
        card = SectionCard()
        card.setMaximumWidth(880)
        self.cards[key] = card
        page.add_widget(card)
        return card

    def _form(self, card: SectionCard) -> QFormLayout:
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.DontWrapRows)
        card.add_layout(form)
        return form

    def _cap(self, widget, width: int = 520):
        widget.setMinimumWidth(240)
        widget.setMaximumWidth(width)
        return widget

    def _add_row(self, form: QFormLayout, key: str, widget):
        label = QLabel()
        label.setObjectName("FormLabel")
        label.setMinimumWidth(170)
        self.field_labels[key] = label
        form.addRow(label, widget)

    def _build(self):
        # General -------------------------------------------------------------
        page = self._new_section()
        profile = self._card(page, "profile")
        form = self._form(profile)
        self.name = self._cap(QLineEdit())
        self.phrase = self._cap(QLineEdit())
        self._add_row(form, "settings.display_name", self.name)
        self._add_row(form, "settings.personal_phrase", self.phrase)

        behavior = self._card(page, "behavior")
        form = self._form(behavior)
        self.tray = QCheckBox()
        self._add_row(form, "settings.tray", self.tray)
        page.add_stretch()

        # Appearance ----------------------------------------------------------
        page = self._new_section()
        theme_card = self._card(page, "theme")
        form = self._form(theme_card)
        self.theme = self._cap(QComboBox())
        self.theme.addItems(THEMES.keys())
        self._add_row(form, "settings.visual_theme", self.theme)

        typography = self._card(page, "typography")
        form = self._form(typography)
        self.font = self._cap(QSpinBox())
        self.font.setRange(8, 18)
        self.font.setSuffix(" pt")
        self._add_row(form, "settings.text_size", self.font)
        page.add_stretch()

        # Language & region ---------------------------------------------------
        page = self._new_section()
        region = self._card(page, "region")
        form = self._form(region)
        self.language = self._cap(QComboBox())
        self.language.addItem("Español", "es")
        self.language.addItem("English", "en")
        self.currency = self._cap(QComboBox())
        self.currency.setEditable(True)
        self.currency.addItems(["AUD", "ARS", "USD", "EUR", "BRL", "GBP", "JPY", "CAD", "NZD"])
        self.timezone = self._cap(QComboBox(), 620)
        self.timezone.setEditable(True)
        self.timezone.addItems(sorted(available_timezones()))
        self.date_format = self._cap(QComboBox())
        self.date_format.addItems(["dd/MM/yyyy", "MM/dd/yyyy", "yyyy-MM-dd"])
        self.time_format = self._cap(QComboBox())
        self.time_format.addItems(["24", "12"])
        self._add_row(form, "settings.language", self.language)
        self._add_row(form, "settings.currency", self.currency)
        self._add_row(form, "settings.timezone", self.timezone)
        self._add_row(form, "settings.date_format", self.date_format)
        self._add_row(form, "settings.time_format", self.time_format)
        page.add_stretch()

        # Notifications -------------------------------------------------------
        page = self._new_section()
        notifications = self._card(page, "notifications")
        form = self._form(notifications)
        self.notify_events = QCheckBox()
        self.notify_tasks = QCheckBox()
        self.notify_birthdays = QCheckBox()
        self.notify_payments = QCheckBox()
        self.notify_health = QCheckBox()
        self._add_row(form, "settings.events", self.notify_events)
        self._add_row(form, "settings.tasks", self.notify_tasks)
        self._add_row(form, "settings.birthdays", self.notify_birthdays)
        self._add_row(form, "settings.payments", self.notify_payments)
        self._add_row(form, "settings.health", self.notify_health)
        page.add_stretch()

        # Wellness ------------------------------------------------------------
        page = self._new_section()
        modules = self._card(page, "modules")
        form = self._form(modules)
        self.module_cycle = QCheckBox()
        self.module_sleep = QCheckBox()
        self.module_mood = QCheckBox()
        self.module_beauty = QCheckBox()
        self.module_style = QCheckBox()
        self.module_multimedia = QCheckBox()
        self._add_row(form, "settings.cycle", self.module_cycle)
        self._add_row(form, "settings.sleep", self.module_sleep)
        self._add_row(form, "settings.mood", self.module_mood)
        self._add_row(form, "settings.beauty", self.module_beauty)
        self._add_row(form, "settings.style", self.module_style)
        self._add_row(form, "settings.multimedia", self.module_multimedia)

        goals = self._card(page, "personal_goals")
        form = self._form(goals)
        self.water_goal = self._cap(QSpinBox())
        self.water_goal.setRange(0, 10000)
        self.water_goal.setSingleStep(50)
        self.water_goal.setSuffix(" ml")
        self._add_row(form, "settings.water_goal", self.water_goal)
        page.add_stretch()

        # Privacy -------------------------------------------------------------
        page = self._new_section()
        lock = self._card(page, "local_lock")
        form = self._form(lock)
        self.pin = self._cap(QLineEdit())
        self.pin.setEchoMode(QLineEdit.Password)
        self.autolock = self._cap(QComboBox())
        self.autolock.addItem("", "0")
        for m in (1, 5, 15, 30):
            self.autolock.addItem("", str(m))
        self.lock_on_startup = QCheckBox()
        self.notification_privacy = self._cap(QComboBox())
        self.notification_privacy.addItem("", "show_content")
        self.notification_privacy.addItem("", "hide_sensitive")
        self._add_row(form, "privacy.pin", self.pin)
        self._add_row(form, "privacy.autolock", self.autolock)
        self._add_row(form, "security.lock_on_startup", self.lock_on_startup)
        self._add_row(form, "security.notification_privacy", self.notification_privacy)

        master = self._card(page, "master_recovery")
        form = self._form(master)
        self.installation_id = self._cap(QLineEdit(), 620)
        self.installation_id.setReadOnly(True)
        self.master_status = QLabel()
        self.master_status.setObjectName("Muted")
        self.master_status.setWordWrap(True)
        self.generate_master_btn = QPushButton()
        self.generate_master_btn.setMaximumWidth(320)
        self.create_recovery_btn = QPushButton()
        self.create_recovery_btn.setMaximumWidth(320)
        self.restore_recovery_btn = QPushButton()
        self.restore_recovery_btn.setMaximumWidth(320)
        self.generate_master_btn.clicked.connect(self.generate_master_key)
        self.create_recovery_btn.clicked.connect(self.create_recovery_kit)
        self.restore_recovery_btn.clicked.connect(self.restore_recovery_kit)
        self._add_row(form, "security.installation_id", self.installation_id)
        form.addRow(QLabel(""), self.master_status)
        form.addRow(QLabel(""), self.generate_master_btn)
        form.addRow(QLabel(""), self.create_recovery_btn)
        form.addRow(QLabel(""), self.restore_recovery_btn)

        network = self._card(page, "trusted_network")
        form = self._form(network)
        self.local_ip = self._cap(QLineEdit(), 620)
        self.local_ip.setReadOnly(True)
        self.trusted_networks = self._cap(QLineEdit(), 620)
        self.network_lock = QCheckBox()
        self.use_current_network_btn = QPushButton()
        self.use_current_network_btn.setMaximumWidth(320)
        self.use_current_network_btn.clicked.connect(self.use_current_network)
        self._add_row(form, "security.local_ip", self.local_ip)
        self._add_row(form, "security.trusted_networks", self.trusted_networks)
        self._add_row(form, "security.network_lock", self.network_lock)
        form.addRow(QLabel(""), self.use_current_network_btn)

        protection = self._card(page, "data_protection")
        self.privacy_info = QLabel()
        self.privacy_info.setObjectName("Muted")
        self.privacy_info.setWordWrap(True)
        protection.add_widget(self.privacy_info)
        page.add_stretch()

        # Data & backups ------------------------------------------------------
        page = self._new_section()
        backup = self._card(page, "backup_policy")
        form = self._form(backup)
        self.retention = self._cap(QSpinBox())
        self.retention.setRange(1, 365)
        self.retention.setSuffix(" days")
        self.import_legacy = QPushButton()
        self.import_legacy.setMaximumWidth(280)
        self.import_legacy.clicked.connect(self.import_old)
        self._add_row(form, "settings.backup_retention", self.retention)
        form.addRow(QLabel(""), self.import_legacy)
        page.add_stretch()

        # Files ---------------------------------------------------------------
        page = self._new_section()
        storage = self._card(page, "storage")
        form = self._form(storage)
        self.file_storage = self._cap(QComboBox())
        self.file_storage.addItem("", "reference")
        self.file_storage.addItem("", "local_copy")
        self._add_row(form, "settings.default_storage", self.file_storage)
        page.add_stretch()

        # About ---------------------------------------------------------------
        page = self._new_section()
        identity = self._card(page, "identity")
        self.about = QLabel()
        self.about.setWordWrap(True)
        self.about.setTextInteractionFlags(Qt.TextSelectableByMouse)
        identity.add_widget(self.about)
        page.add_stretch()

    def _select_section(self, row: int):
        if 0 <= row < self.stack.count():
            self.stack.setCurrentIndex(row)

    def retranslate(self):
        self.title_label.setText(self.i18n.t("page.settings"))
        self.subtitle_label.setText(self.i18n.t("settings.subtitle"))

        for index, key in enumerate(self.SECTION_KEYS):
            item = self.section_nav.item(index)
            if item:
                item.setText(self.i18n.t(key))

        card_headers = {
            "profile": ("settings.profile", "settings.profile_help"),
            "behavior": ("settings.behavior", "settings.behavior_help"),
            "theme": ("settings.visual_theme", "settings.theme_help"),
            "typography": ("settings.typography", "settings.typography_help"),
            "region": ("settings.region", "settings.region_help"),
            "notifications": ("settings.notification_types", "settings.notification_types_help"),
            "modules": ("settings.modules", "settings.modules_help"),
            "personal_goals": ("settings.personal_goals", "settings.personal_goals_help"),
            "local_lock": ("settings.local_lock", "settings.local_lock_help"),
            "master_recovery": ("security.master_recovery", "security.master_recovery_help"),
            "trusted_network": ("security.trusted_network", "security.trusted_network_help"),
            "data_protection": ("settings.data_protection", "settings.data_protection_help"),
            "backup_policy": ("settings.backup_policy", "settings.backup_policy_help"),
            "storage": ("settings.storage", "settings.storage_help"),
            "identity": ("settings.identity", "settings.identity_help"),
        }
        for key, (title_key, help_key) in card_headers.items():
            self.cards[key].set_header(self.i18n.t(title_key), self.i18n.t(help_key))

        for key, label in self.field_labels.items():
            label.setText(self.i18n.t(key))

        self.name.setPlaceholderText(self.i18n.t("settings.name"))
        self.phrase.setPlaceholderText(self.i18n.t("settings.phrase"))
        self.pin.setPlaceholderText(self.i18n.t("privacy.pin"))
        self.privacy_info.setText(
            self.i18n.t("settings.data_protection_help") + "\n" + self.i18n.t("privacy.disclaimer")
            + "\n" + self.i18n.t("security.no_universal_backdoor")
        )
        self.notification_privacy.setItemText(0, self.i18n.t("security.show_content"))
        self.notification_privacy.setItemText(1, self.i18n.t("security.hide_sensitive"))
        self.generate_master_btn.setText(self.i18n.t("security.generate_master"))
        self.create_recovery_btn.setText(self.i18n.t("security.create_recovery_kit"))
        self.restore_recovery_btn.setText(self.i18n.t("security.restore_recovery_kit"))
        self.use_current_network_btn.setText(self.i18n.t("security.use_current_network"))
        self.import_legacy.setText(self.i18n.t("settings.import_v1"))
        self.reset_btn.setText(self.i18n.t("settings.reset"))
        self.save_btn.setText(self.i18n.t("settings.save_changes"))
        self.save_hint.setText(self.i18n.t("settings.unsaved_hint"))
        self.about.setText(self.i18n.t("settings.about_text"))

        self.autolock.setItemText(0, self.i18n.t("settings.never"))
        for i, minutes in enumerate((1, 5, 15, 30), start=1):
            self.autolock.setItemText(i, self.i18n.t("settings.minutes", value=minutes))
        self.file_storage.setItemText(0, self.i18n.t("settings.reference"))
        self.file_storage.setItemText(1, self.i18n.t("settings.local_copy"))
        self.retention.setSuffix(" días" if self.i18n.language == "es" else " days")

    def load(self):
        self.name.setText(self.db.setting("user_name", "Tu nombre"))
        self.phrase.setText(self.db.setting("welcome_phrase", ""))
        self.tray.setChecked(self.db.setting("minimize_to_tray", "1") == "1")
        self.theme.setCurrentText(self.db.setting("theme", "Pink Crystal"))
        self.font.setValue(int(self.db.setting("font_size", "10") or 10))
        idx = self.language.findData(self.db.setting("language", "es"))
        self.language.setCurrentIndex(max(0, idx))
        self.currency.setCurrentText(self.db.setting("currency", ""))
        self.timezone.setCurrentText(self.db.setting("timezone", ""))
        self.date_format.setCurrentText(self.db.setting("date_format", "dd/MM/yyyy"))
        self.time_format.setCurrentText(self.db.setting("time_format", "24"))
        self.water_goal.setValue(int(self.db.setting("water_goal", "2000") or 2000))
        self.retention.setValue(int(self.db.setting("backup_retention", "30") or 30))

        for key, widget in [
            ("module_cycle", self.module_cycle), ("module_sleep", self.module_sleep),
            ("module_mood", self.module_mood), ("module_beauty", self.module_beauty),
            ("module_style", self.module_style), ("module_multimedia", self.module_multimedia),
            ("notify_events", self.notify_events), ("notify_tasks", self.notify_tasks),
            ("notify_birthdays", self.notify_birthdays), ("notify_payments", self.notify_payments),
            ("notify_health", self.notify_health),
        ]:
            widget.setChecked(self.db.setting(key, "1") == "1")

        idx = self.autolock.findData(self.db.setting("auto_lock_minutes", "0"))
        self.autolock.setCurrentIndex(max(0, idx))
        self.lock_on_startup.setChecked(self.db.setting("lock_on_startup", "0") == "1")
        idx = self.notification_privacy.findData(
            self.db.setting("notification_privacy", "show_content")
        )
        if idx < 0:
            idx = 0
        self.notification_privacy.setCurrentIndex(idx)
        self.installation_id.setText(self.recovery_service.ensure_installation_id())
        self.local_ip.setText(primary_local_ipv4() or self.i18n.t("security.ip_unavailable"))
        self.trusted_networks.setText(self.db.setting("trusted_networks", ""))
        self.network_lock.setChecked(self.db.setting("network_lock_enabled", "0") == "1")
        self._refresh_master_status()
        idx = self.file_storage.findData(self.db.setting("file_storage_default", "reference"))
        self.file_storage.setCurrentIndex(max(0, idx))

    def save(self):
        old_lang = self.db.setting("language", "es")
        if self.pin.text():
            valid, _ = validate_new_pin(self.pin.text())
            if not valid:
                QMessageBox.warning(self, self.i18n.t("error.title"), self.i18n.t("security.pin_minimum"))
                return
        try:
            trusted = canonical_trusted_networks(self.trusted_networks.text())
        except ValueError:
            QMessageBox.warning(
                self, self.i18n.t("error.title"), self.i18n.t("security.invalid_network")
            )
            return
        if self.network_lock.isChecked() and not self.recovery_service.has_master_key():
            QMessageBox.warning(
                self, self.i18n.t("error.title"), self.i18n.t("security.master_required_for_network")
            )
            return
        if self.network_lock.isChecked() and not trusted:
            QMessageBox.warning(
                self, self.i18n.t("error.title"), self.i18n.t("security.network_required")
            )
            return
        values = {
            "user_name": self.name.text().strip() or ("Tu nombre" if self.language.currentData() == "es" else "Your name"),
            "welcome_phrase": self.phrase.text().strip(),
            "minimize_to_tray": "1" if self.tray.isChecked() else "0",
            "theme": self.theme.currentText(),
            "font_size": str(self.font.value()),
            "language": self.language.currentData(),
            "currency": self.currency.currentText().strip().upper(),
            "timezone": self.timezone.currentText().strip(),
            "date_format": self.date_format.currentText(),
            "time_format": self.time_format.currentText(),
            "water_goal": str(self.water_goal.value()),
            "backup_retention": str(self.retention.value()),
            "auto_lock_minutes": self.autolock.currentData() or "0",
            "lock_on_startup": "1" if self.lock_on_startup.isChecked() else "0",
            "notification_privacy": self.notification_privacy.currentData() or "show_content",
            "trusted_networks": trusted,
            "network_lock_enabled": "1" if self.network_lock.isChecked() else "0",
            "last_known_local_ip": primary_local_ipv4(),
            "file_storage_default": self.file_storage.currentData() or "reference",
        }
        for key, widget in [
            ("module_cycle", self.module_cycle), ("module_sleep", self.module_sleep),
            ("module_mood", self.module_mood), ("module_beauty", self.module_beauty),
            ("module_style", self.module_style), ("module_multimedia", self.module_multimedia),
            ("notify_events", self.notify_events), ("notify_tasks", self.notify_tasks),
            ("notify_birthdays", self.notify_birthdays), ("notify_payments", self.notify_payments),
            ("notify_health", self.notify_health),
        ]:
            values[key] = "1" if widget.isChecked() else "0"

        if self.pin.text():
            hashed, salt = make_pin_hash(self.pin.text())
            values["pin_hash"] = hashed
            values["pin_salt"] = salt
            self.pin.clear()

        self.db.set_settings(values)
        self.db.audit("UPDATE_SETTINGS", "settings")
        self.i18n.set_language(values["language"])
        self.theme_changed.emit(values["theme"])
        if old_lang != values["language"]:
            self.language_changed.emit(values["language"])
        else:
            self.retranslate()
        self.settings_changed.emit()
        QMessageBox.information(self, self.i18n.t("success.title"), self.i18n.t("settings.saved"))

    def _refresh_master_status(self):
        if self.recovery_service.has_master_key():
            created = self.db.setting("master_key_created_at", "")
            self.master_status.setText(self.i18n.t("security.master_configured", value=created or "—"))
        else:
            self.master_status.setText(self.i18n.t("security.master_not_configured"))

    def generate_master_key(self):
        if self.recovery_service.has_master_key():
            answer = QMessageBox.question(
                self, self.i18n.t("security.master_title"), self.i18n.t("security.regenerate_warning")
            )
            if answer != QMessageBox.Yes:
                return
        key = self.recovery_service.create_master_key()
        clipboard = QApplication.clipboard()
        clipboard.setText(key)
        QTimer.singleShot(60_000, lambda: clipboard.clear() if clipboard.text() == key else None)
        QMessageBox.information(
            self,
            self.i18n.t("security.master_title"),
            self.i18n.t("security.master_generated", value=key),
        )
        self._refresh_master_status()

    def _ask_master_key(self) -> str:
        key, ok = QInputDialog.getText(
            self,
            self.i18n.t("security.master_title"),
            self.i18n.t("security.master_prompt"),
            QLineEdit.Password,
        )
        return key if ok else ""

    def create_recovery_kit(self):
        if not self.recovery_service.has_master_key():
            QMessageBox.warning(
                self, self.i18n.t("error.title"), self.i18n.t("security.master_first")
            )
            return
        key = self._ask_master_key()
        if not key:
            return
        target, _ = QFileDialog.getSaveFileName(
            self, self.i18n.t("security.create_recovery_kit"), "AuraAgenda_Recovery.aurarecovery",
            "AuraAgenda Recovery (*.aurarecovery)"
        )
        if not target:
            return
        try:
            path = self.recovery_service.create_recovery_kit(Path(target), key)
        except Exception as exc:
            QMessageBox.critical(self, self.i18n.t("error.title"), str(exc))
            return
        QMessageBox.information(
            self, self.i18n.t("success.title"), self.i18n.t("security.recovery_created", value=str(path))
        )

    def restore_recovery_kit(self):
        source, _ = QFileDialog.getOpenFileName(
            self, self.i18n.t("security.restore_recovery_kit"), "",
            "AuraAgenda Recovery (*.aurarecovery)"
        )
        if not source:
            return
        key = self._ask_master_key()
        if not key:
            return
        answer = QMessageBox.question(
            self, self.i18n.t("common.confirm"), self.i18n.t("security.restore_warning")
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self.recovery_service.restore_recovery_kit(Path(source), key)
            self.load()
        except Exception as exc:
            QMessageBox.critical(self, self.i18n.t("error.title"), str(exc))
            return
        QMessageBox.information(
            self, self.i18n.t("success.title"), self.i18n.t("security.restore_done")
        )

    def use_current_network(self):
        suggested = suggested_local_network()
        if not suggested:
            QMessageBox.warning(
                self, self.i18n.t("error.title"), self.i18n.t("security.ip_unavailable")
            )
            return
        self.trusted_networks.setText(suggested)

    def reset_defaults(self):
        if QMessageBox.question(
            self, self.i18n.t("common.confirm"), self.i18n.t("settings.reset") + "?"
        ) != QMessageBox.Yes:
            return
        from ..database import DEFAULTS
        self.db.set_settings(DEFAULTS)
        self.i18n.set_language("es")
        self.load()
        self.language_changed.emit("es")
        self.theme_changed.emit("Pink Crystal")
        self.settings_changed.emit()

    def import_old(self):
        svc = LegacyMigrationService()
        if not svc.exists():
            QMessageBox.information(
                self, self.i18n.t("success.title"),
                "No se encontraron datos V1." if self.i18n.language == "es" else "No V1 data found.",
            )
            return
        if QMessageBox.question(
            self, self.i18n.t("common.confirm"), self.i18n.t("migration.detected")
        ) != QMessageBox.Yes:
            return
        try:
            svc.migrate(self.db)
            QMessageBox.information(self, self.i18n.t("success.title"), self.i18n.t("migration.done"))
            self.settings_changed.emit()
        except Exception as exc:
            QMessageBox.critical(self, self.i18n.t("error.title"), str(exc))
