from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox

from .network_guard import network_status, primary_local_ipv4
from .privacy import AttemptLimiter, validate_new_pin, verify_pin
from .recovery import RecoveryService


class AutoLockController(QObject):
    """Central security gate for window visibility.

    All tray/open-window actions route through request_show(). A cancelled or
    failed unlock attempt leaves ``locked`` true, preventing the historical tray
    bypass where MainWindow.show_normal() could display protected content.
    """

    def __init__(self, app, window, db, i18n):
        super().__init__(app)
        self.app = app
        self.window = window
        self.db = db
        self.i18n = i18n
        self.locked = False
        self.lock_reason = ""
        self.limiter = AttemptLimiter()
        self.recovery = RecoveryService(db)
        self.recovery.ensure_installation_id()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.lock)
        app.installEventFilter(self)
        self.reset()

    def interval_ms(self) -> int:
        try:
            return int(self.db.setting("auto_lock_minutes", "0")) * 60_000
        except ValueError:
            return 0

    def reset(self) -> None:
        if self.locked:
            self.timer.stop()
            return
        ms = self.interval_ms()
        if ms > 0 and self.db.setting("pin_hash", ""):
            self.timer.start(ms)
        else:
            self.timer.stop()

    def eventFilter(self, obj, event):
        if not self.locked and event.type() in (
            QEvent.MouseButtonPress,
            QEvent.KeyPress,
            QEvent.Wheel,
            QEvent.TouchBegin,
        ):
            self.reset()
        return False

    def network_mismatch(self) -> bool:
        if self.db.setting("network_lock_enabled", "0") != "1":
            return False
        configured = self.db.setting("trusted_networks", "")
        if not configured:
            return False
        status = network_status(configured)
        self.db.set_setting("last_known_local_ip", primary_local_ipv4())
        return not status.trusted

    def initial_security_check(self) -> None:
        if self.network_mismatch():
            self.lock(reason="network")
            return
        if self.db.setting("lock_on_startup", "0") == "1" and self.db.setting("pin_hash", ""):
            self.lock(reason="startup")

    def on_settings_changed(self) -> None:
        self.reset()
        if self.network_mismatch():
            self.lock(reason="network")

    def lock(self, reason: str = "inactivity") -> None:
        has_pin = bool(self.db.setting("pin_hash", ""))
        if reason != "network" and not has_pin:
            return
        if reason == "network" and not self.recovery.has_master_key():
            # Settings prevent this combination, but fail safe rather than
            # creating an unrecoverable lockout if data was edited manually.
            self.db.set_setting("network_lock_enabled", "0")
            self.db.audit("DISABLE_UNSAFE_NETWORK_LOCK", "security")
            return
        self.locked = True
        self.lock_reason = reason
        self.timer.stop()
        self.window.hide()
        QTimer.singleShot(0, self.prompt_unlock)

    def request_show(self) -> bool:
        if self.locked:
            return self.prompt_unlock()
        if self.network_mismatch():
            self.lock(reason="network")
            return False
        self.window._show_unlocked()
        return True

    def _unlock(self) -> None:
        self.locked = False
        self.lock_reason = ""
        self.limiter.register_success()
        self.reset()
        self.window._show_unlocked()
        self.db.audit("UNLOCK", "security")

    def _prompt_master_key(self, purpose: str) -> bool:
        if not self.recovery.has_master_key():
            return False
        key, ok = QInputDialog.getText(
            None,
            self.i18n.t("security.master_title"),
            self.i18n.t("security.master_prompt"),
            QLineEdit.Password,
        )
        if not ok:
            return False
        if not self.recovery.verify_master_key(key):
            QMessageBox.warning(None, self.i18n.t("error.title"), self.i18n.t("security.master_invalid"))
            self.db.audit("MASTER_RECOVERY_FAILED", "security", None, purpose)
            return False
        self.db.audit("MASTER_RECOVERY_AUTH", "security", None, purpose)
        return True

    def _reset_pin_with_master(self) -> bool:
        if not self._prompt_master_key("pin_reset"):
            return False
        pin, ok = QInputDialog.getText(
            None,
            self.i18n.t("security.master_title"),
            self.i18n.t("security.new_pin"),
            QLineEdit.Password,
        )
        if not ok:
            return False
        valid, _ = validate_new_pin(pin)
        if not valid:
            QMessageBox.warning(None, self.i18n.t("error.title"), self.i18n.t("security.pin_minimum"))
            return False
        confirm, ok = QInputDialog.getText(
            None,
            self.i18n.t("security.master_title"),
            self.i18n.t("security.confirm_pin"),
            QLineEdit.Password,
        )
        if not ok or confirm != pin:
            QMessageBox.warning(None, self.i18n.t("error.title"), self.i18n.t("security.pin_mismatch"))
            return False
        # Prompt again for the master key is unnecessary because it was already
        # authenticated above; write the new PIN directly.
        from .privacy import make_pin_hash

        digest, salt = make_pin_hash(pin)
        self.db.set_settings({"pin_hash": digest, "pin_salt": salt})
        self.db.audit("RESET_PIN_WITH_MASTER_KEY", "security")
        return True

    def prompt_unlock(self) -> bool:
        if not self.locked:
            return True

        if self.lock_reason == "network":
            if self._prompt_master_key("network_override"):
                self._unlock()
                return True
            return False

        remaining = self.limiter.remaining_seconds()
        if remaining:
            QMessageBox.warning(
                None,
                self.i18n.t("error.title"),
                self.i18n.t("security.wait_seconds", value=remaining),
            )
            return False

        pin, ok = QInputDialog.getText(
            None,
            "AuraAgenda",
            self.i18n.t("privacy.pin"),
            QLineEdit.Password,
        )
        if not ok:
            if self.recovery.has_master_key():
                answer = QMessageBox.question(
                    None,
                    self.i18n.t("security.master_title"),
                    self.i18n.t("security.use_master_recovery"),
                )
                if answer == QMessageBox.Yes and self._reset_pin_with_master():
                    self._unlock()
                    return True
            # Critical: cancellation never clears locked state.
            return False

        if verify_pin(pin, self.db.setting("pin_hash", ""), self.db.setting("pin_salt", "")):
            self._unlock()
            return True

        delay = self.limiter.register_failure()
        message = self.i18n.t("security.pin_invalid")
        if delay:
            message += "\n" + self.i18n.t("security.wait_seconds", value=delay)
        QMessageBox.warning(None, self.i18n.t("error.title"), message)
        self.db.audit("PIN_UNLOCK_FAILED", "security")
        return False
