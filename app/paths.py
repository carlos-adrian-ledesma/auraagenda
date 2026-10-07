from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "AuraAgenda"
DISPLAY_NAME = "AuraAgenda"
SUBTITLE = "Personal Life Planner"
VERSION = "2.0.3"
PUBLISHER = "QuintaDimension Tecnologia"


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / relative


def documents_dir() -> Path:
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return Path(user_profile) / "Documents"
    return Path.home() / "Documents"

DATA_ROOT = documents_dir() / APP_NAME
DB_DIR = DATA_ROOT / "Database"
DB_PATH = DB_DIR / "auraagenda.db"
LOG_DIR = DATA_ROOT / "Logs"
LOG_PATH = LOG_DIR / "auraagenda.log"
BACKUP_DIR = DATA_ROOT / "Backups"
EXPORT_DIR = DATA_ROOT / "Exports"
ATTACHMENTS_DIR = DATA_ROOT / "Attachments"
TRASH_DIR = DATA_ROOT / "Trash"
LEGACY_ROOT = documents_dir() / "DanicaDavis"
LEGACY_DB = LEGACY_ROOT / "BaseDatos" / "danica_davis.db"

FOLDERS = [
    DB_DIR, LOG_DIR, BACKUP_DIR, EXPORT_DIR, ATTACHMENTS_DIR, TRASH_DIR,
    DATA_ROOT / "Diary" / "Attachments",
    DATA_ROOT / "Library" / "Photos", DATA_ROOT / "Library" / "Videos",
    DATA_ROOT / "Library" / "Audio", DATA_ROOT / "Library" / "Documents",
    DATA_ROOT / "Multimedia" / "Covers", DATA_ROOT / "Multimedia" / "Songs",
    DATA_ROOT / "Multimedia" / "Videos", DATA_ROOT / "Multimedia" / "Audio",
    DATA_ROOT / "Multimedia" / "Artwork", DATA_ROOT / "Multimedia" / "Lyrics",
    DATA_ROOT / "Multimedia" / "Projects",
    DATA_ROOT / "Style" / "Wardrobe", DATA_ROOT / "Beauty" / "Products",
    DATA_ROOT / "Travel", DATA_ROOT / "Finance" / "Receipts",
    EXPORT_DIR / "PDF", EXPORT_DIR / "DOCX", EXPORT_DIR / "CSV", EXPORT_DIR / "XLSX",
]


def ensure_structure() -> None:
    for folder in FOLDERS:
        folder.mkdir(parents=True, exist_ok=True)
