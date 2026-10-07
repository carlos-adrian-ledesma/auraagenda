from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QFileDialog, QInputDialog, QLineEdit, QMessageBox

from app.database import Database
from app.i18n import I18n
from app.services.recovery import RecoveryService


def main() -> int:
    app = QApplication(sys.argv)
    db = Database()
    i18n = I18n(db.setting("language", "es"))
    service = RecoveryService(db)

    source, _ = QFileDialog.getOpenFileName(
        None,
        "Restaurar AuraAgenda" if i18n.language == "es" else "Restore AuraAgenda",
        "",
        "AuraAgenda Recovery (*.aurarecovery)",
    )
    if not source:
        return 0

    key, ok = QInputDialog.getText(
        None,
        i18n.t("security.master_title"),
        i18n.t("security.master_prompt"),
        QLineEdit.Password,
    )
    if not ok or not key:
        return 0

    try:
        service.restore_recovery_kit(Path(source), key)
    except Exception as exc:
        QMessageBox.critical(None, i18n.t("error.title"), str(exc))
        return 1

    QMessageBox.information(None, i18n.t("success.title"), i18n.t("security.restore_done"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
