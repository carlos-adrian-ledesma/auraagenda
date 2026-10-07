from __future__ import annotations
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from ..database import Database
from ..paths import BACKUP_DIR, DB_PATH, LEGACY_DB, LEGACY_ROOT

class LegacyMigrationService:
    def exists(self) -> bool:
        return LEGACY_ROOT.exists() and LEGACY_DB.is_file()

    def migrate(self, db: Database) -> Path | None:
        if not self.exists():
            return None
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        legacy_backup = BACKUP_DIR / f"PreMigration_Legacy_{stamp}.db"
        shutil.copy2(LEGACY_DB, legacy_backup)
        if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
            current_backup = BACKUP_DIR / f"PreMigration_AuraAgenda_{stamp}.db"
            shutil.copy2(DB_PATH, current_backup)
        # Import table-by-table so a pre-existing AuraAgenda DB is never overwritten.
        src = sqlite3.connect(LEGACY_DB)
        src.row_factory = sqlite3.Row
        try:
            with db.connect() as dst:
                src_tables = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                common = ["agenda","alarms","water","diary","diary_attachments","writing","tasks","finance","library"]
                for table in common:
                    if table not in src_tables:
                        continue
                    src_cols = [r[1] for r in src.execute(f"PRAGMA table_info({table})")]
                    dst_cols = {r[1] for r in dst.execute(f"PRAGMA table_info({table})")}
                    cols = [c for c in src_cols if c in dst_cols and c != "id"]
                    if not cols:
                        continue
                    rows = src.execute(f"SELECT {','.join(cols)} FROM {table}").fetchall()
                    placeholders = ",".join("?" for _ in cols)
                    for row in rows:
                        dst.execute(f"INSERT INTO {table}({','.join(cols)}) VALUES({placeholders})", tuple(row[c] for c in cols))
                if "media_sm" in src_tables:
                    rows = src.execute("SELECT title,media_type,artist,song,path,status,tags,created_at,updated_at,deleted FROM media_sm").fetchall()
                    for r in rows:
                        dst.execute("INSERT INTO multimedia(title,media_type,artist,song,path,status,tags,created_at,updated_at,deleted) VALUES(?,?,?,?,?,?,?,?,?,?)", tuple(r))
                # Preserve user settings selectively; do not copy legacy identity into the new name.
                if "settings" in src_tables:
                    allowed = {"theme","water_goal","minimize_to_tray","diary_font_size"}
                    for r in src.execute("SELECT key,value FROM settings"):
                        if r["key"] in allowed:
                            dst.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (r["key"], r["value"]))
                    old_tz = src.execute("SELECT value FROM settings WHERE key='timezone'").fetchone()
                    if old_tz and old_tz[0]:
                        dst.execute("UPDATE settings SET value=? WHERE key='timezone'", (old_tz[0],))
                dst.execute("UPDATE settings SET value='1' WHERE key='legacy_migration_checked'")
                dst.execute("INSERT INTO migration_log(source,status,detail,created_at) VALUES(?,?,?,?)", (str(LEGACY_DB),"success","Legacy data imported; original folder retained",db.now(dst)))
        except Exception as exc:
            db.execute("INSERT INTO migration_log(source,status,detail,created_at) VALUES(?,?,?,?)", (str(LEGACY_DB),"failed",str(exc),db.now()))
            raise
        finally:
            src.close()
        return legacy_backup
