from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Mapping

from .paths import DB_PATH, ensure_structure
from .timeutil import now_in_timezone, system_timezone_name

SCHEMA_VERSION = 4

BASE_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS migration_log(id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, status TEXT NOT NULL, detail TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, entity TEXT, entity_id INTEGER, detail TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS backups(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, kind TEXT DEFAULT 'Manual', size_bytes INTEGER DEFAULT 0, created_at TEXT NOT NULL, status TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS agenda(
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, event_date TEXT NOT NULL, start_time TEXT, end_time TEXT,
 all_day INTEGER DEFAULT 0, category TEXT DEFAULT 'Personal', color TEXT, priority TEXT DEFAULT 'Normal', location TEXT,
 description TEXT, reminder_minutes INTEGER DEFAULT 0, repeat_rule TEXT DEFAULT 'once', repeat_detail TEXT,
 status TEXT DEFAULT 'pending', created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS idx_agenda_date ON agenda(event_date, deleted);
CREATE TABLE IF NOT EXISTS event_categories(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, color TEXT, active INTEGER DEFAULT 1);

CREATE TABLE IF NOT EXISTS alarms(
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, alarm_date TEXT NOT NULL, alarm_time TEXT NOT NULL,
 repeat_rule TEXT DEFAULT 'once', message TEXT, enabled TEXT DEFAULT 'Yes', completed TEXT DEFAULT 'No', snooze_until TEXT,
 related_type TEXT, related_id INTEGER, last_triggered TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS tasks(
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT, category TEXT, tags TEXT, priority TEXT DEFAULT 'Normal',
 status TEXT DEFAULT 'pending', start_date TEXT, due_date TEXT, reminder_at TEXT, recurrence TEXT, estimated_minutes INTEGER DEFAULT 0,
 progress INTEGER DEFAULT 0, parent_id INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS habits(
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, frequency TEXT DEFAULT 'daily', days TEXT, target REAL DEFAULT 1,
 unit TEXT, color TEXT, icon TEXT, active INTEGER DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS habit_logs(id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER NOT NULL, log_date TEXT NOT NULL, value REAL DEFAULT 1, note TEXT, created_at TEXT NOT NULL, UNIQUE(habit_id,log_date), FOREIGN KEY(habit_id) REFERENCES habits(id));

CREATE TABLE IF NOT EXISTS lists(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, list_type TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS list_items(id INTEGER PRIMARY KEY AUTOINCREMENT, list_id INTEGER NOT NULL, text TEXT NOT NULL, checked INTEGER DEFAULT 0, quantity TEXT, note TEXT, priority TEXT DEFAULT 'Normal', position INTEGER DEFAULT 0, deleted INTEGER DEFAULT 0, FOREIGN KEY(list_id) REFERENCES lists(id));

CREATE TABLE IF NOT EXISTS diary(
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT, category TEXT DEFAULT 'Día de hoy', mood TEXT, tags TEXT,
 favorite TEXT DEFAULT 'No', privacy TEXT DEFAULT 'Normal', template TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS diary_attachments(id INTEGER PRIMARY KEY AUTOINCREMENT, diary_id INTEGER NOT NULL, original_name TEXT NOT NULL, media_kind TEXT NOT NULL, path TEXT NOT NULL, created_at TEXT NOT NULL, deleted INTEGER DEFAULT 0, FOREIGN KEY(diary_id) REFERENCES diary(id));
CREATE TABLE IF NOT EXISTS writing(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT, status TEXT DEFAULT 'Draft', created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, relationship TEXT, birthday TEXT, phone TEXT, email TEXT, address TEXT, gift_ideas TEXT, last_interaction TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT, start_date TEXT, target_date TEXT, progress INTEGER DEFAULT 0, subtasks TEXT, notes TEXT, status TEXT DEFAULT 'active', created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS cycle_records(id INTEGER PRIMARY KEY AUTOINCREMENT, start_date TEXT NOT NULL, end_date TEXT, duration_days INTEGER, intensity TEXT, symptoms TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS wellness_logs(id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT NOT NULL, pain INTEGER, energy INTEGER, mood INTEGER, sleep INTEGER, stress INTEGER, appetite INTEGER, skin TEXT, migraine INTEGER, bloating INTEGER, custom_symptoms TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS health_items(id INTEGER PRIMARY KEY AUTOINCREMENT, item_type TEXT NOT NULL, title TEXT NOT NULL, event_date TEXT, reminder_at TEXT, provider TEXT, medication TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS water(id INTEGER PRIMARY KEY AUTOINCREMENT, amount_ml INTEGER NOT NULL, recorded_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sleep_logs(id INTEGER PRIMARY KEY AUTOINCREMENT, sleep_date TEXT NOT NULL, bedtime TEXT, wake_time TEXT, hours REAL, quality INTEGER, interruptions INTEGER DEFAULT 0, comment TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS mood_logs(id INTEGER PRIMARY KEY AUTOINCREMENT, emotion TEXT NOT NULL, intensity INTEGER DEFAULT 3, recorded_at TEXT NOT NULL, note TEXT, tags TEXT, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS selfcare(id INTEGER PRIMARY KEY AUTOINCREMENT, activity TEXT NOT NULL, category TEXT, frequency TEXT, scheduled_date TEXT, completed INTEGER DEFAULT 0, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS beauty_products(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, brand TEXT, category TEXT, price REAL, currency TEXT, purchase_date TEXT, open_date TEXT, expiry_date TEXT, rating INTEGER, notes TEXT, photo TEXT, repurchase TEXT DEFAULT 'No', status TEXT DEFAULT 'active', created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS wardrobe(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT, color TEXT, season TEXT, occasion TEXT, brand TEXT, photo TEXT, notes TEXT, favorite INTEGER DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS outfits(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, item_ids TEXT, occasion TEXT, wear_date TEXT, photo TEXT, favorite INTEGER DEFAULT 0, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS finance(
 id INTEGER PRIMARY KEY AUTOINCREMENT, txn_date TEXT NOT NULL, txn_type TEXT NOT NULL, category TEXT, concept TEXT NOT NULL,
 amount REAL NOT NULL, currency TEXT, status TEXT DEFAULT 'paid', payment_method TEXT, recurring TEXT DEFAULT 'No', due_date TEXT,
 note TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS budgets(id INTEGER PRIMARY KEY AUTOINCREMENT, month TEXT NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL, currency TEXT, notes TEXT, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS subscriptions(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, amount REAL NOT NULL, currency TEXT, frequency TEXT DEFAULT 'monthly', next_payment TEXT, payment_method TEXT, active INTEGER DEFAULT 1, notes TEXT, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS savings_goals(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, target_amount REAL, current_amount REAL DEFAULT 0, currency TEXT, target_date TEXT, notes TEXT, deleted INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS trips(id INTEGER PRIMARY KEY AUTOINCREMENT, destination TEXT NOT NULL, start_date TEXT, end_date TEXT, accommodation TEXT, transport TEXT, reservations TEXT, budget REAL, currency TEXT, checklist TEXT, documents TEXT, places TEXT, outfits TEXT, reminders TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS library(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, file_type TEXT, path TEXT NOT NULL, storage_mode TEXT DEFAULT 'reference', category TEXT, tags TEXT, favorite INTEGER DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS multimedia(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, media_type TEXT NOT NULL, artist TEXT, song TEXT, path TEXT, storage_mode TEXT DEFAULT 'reference', status TEXT DEFAULT 'idea', tags TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deleted INTEGER DEFAULT 0);
"""

DEFAULTS = {
    "user_name": "Tu nombre", "language": "es", "theme": "Pink Crystal", "accent": "#FF4FCB",
    "currency": "", "water_goal": "2000", "timezone": "", "minimize_to_tray": "1",
    "welcome_phrase": "Organiza tu día a tu manera", "date_format": "dd/MM/yyyy", "time_format": "24",
    "font_size": "10", "pin_hash": "", "pin_salt": "", "auto_lock_minutes": "0",
    "lock_on_startup": "0", "notification_privacy": "show_content",
    "installation_id": "", "master_key_hash": "", "master_key_salt": "", "master_key_created_at": "",
    "network_lock_enabled": "0", "trusted_networks": "", "last_known_local_ip": "",
    "onboarding_complete": "0", "module_cycle": "1", "module_sleep": "1", "module_mood": "1",
    "module_beauty": "1", "module_style": "1", "module_multimedia": "1", "backup_retention": "30",
    "legacy_migration_checked": "0", "notify_events":"1", "notify_tasks":"1", "notify_birthdays":"1", "notify_payments":"1", "notify_health":"1", "file_storage_default":"reference",
}

REQUIRED_COLUMNS = {
    "agenda": {"all_day":"INTEGER DEFAULT 0", "color":"TEXT", "location":"TEXT", "reminder_minutes":"INTEGER DEFAULT 0", "repeat_rule":"TEXT DEFAULT 'once'", "repeat_detail":"TEXT", "last_reminded":"TEXT"},
    "alarms": {"snooze_until":"TEXT", "related_type":"TEXT", "related_id":"INTEGER"},
    "tasks": {"tags":"TEXT", "start_date":"TEXT", "reminder_at":"TEXT", "recurrence":"TEXT", "estimated_minutes":"INTEGER DEFAULT 0", "parent_id":"INTEGER"},
    "diary": {"tags":"TEXT", "privacy":"TEXT DEFAULT 'Normal'", "template":"TEXT"},
    "finance": {"payment_method":"TEXT", "recurring":"TEXT DEFAULT 'No'", "due_date":"TEXT"},
    "library": {"category":"TEXT", "favorite":"INTEGER DEFAULT 0"},
}

SOFT_DELETE_TABLES = {
    "agenda", "alarms", "tasks", "habits", "lists", "list_items", "diary",
    "diary_attachments", "writing", "people", "goals", "cycle_records",
    "wellness_logs", "health_items", "sleep_logs", "mood_logs", "selfcare",
    "beauty_products", "wardrobe", "outfits", "finance", "budgets",
    "subscriptions", "savings_goals", "trips", "library", "multimedia",
}


class Database:
    def __init__(self, path: Path = DB_PATH):
        ensure_structure()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path, timeout=15)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=15000")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    @staticmethod
    def _columns(con: sqlite3.Connection, table: str) -> set[str]:
        return {str(r[1]) for r in con.execute(f"PRAGMA table_info({table})")}

    def initialize(self) -> None:
        with self.connect() as con:
            con.executescript(BASE_SCHEMA)
            for table, columns in REQUIRED_COLUMNS.items():
                existing = self._columns(con, table)
                for name, decl in columns.items():
                    if name not in existing:
                        con.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")
            # Legacy table renamed logically into the generic multimedia module.
            tables = {str(r[0]) for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "media_sm" in tables and con.execute("SELECT COUNT(*) FROM multimedia").fetchone()[0] == 0:
                cols = self._columns(con, "media_sm")
                storage_expr = "storage_mode" if "storage_mode" in cols else "'reference'"
                con.execute(f"INSERT INTO multimedia(title,media_type,artist,song,path,storage_mode,status,tags,created_at,updated_at,deleted) SELECT title,media_type,artist,song,path,{storage_expr},status,tags,created_at,updated_at,deleted FROM media_sm")
            con.executemany("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", DEFAULTS.items())
            if not self.setting_in_connection(con, "timezone"):
                con.execute("UPDATE settings SET value=? WHERE key='timezone'", (system_timezone_name(),))
            current = con.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
            if not current or int(current) < SCHEMA_VERSION:
                con.execute("INSERT INTO schema_version(version,applied_at) VALUES(?,?)", (SCHEMA_VERSION, self.now(con)))
            for cat in ("Personal","Trabajo","Salud","Belleza","Familia","Social","Estudios","Viajes","Compras","Trámites","Otros"):
                con.execute("INSERT OR IGNORE INTO event_categories(name) VALUES(?)", (cat,))

    def now(self, con: sqlite3.Connection | None = None) -> str:
        tz = self.setting_in_connection(con, "timezone") if con is not None else self.setting("timezone", "")
        return now_in_timezone(tz).isoformat(timespec="seconds")

    @staticmethod
    def setting_in_connection(con: sqlite3.Connection | None, key: str, default: str = "") -> str:
        if con is None:
            return default
        row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row else default

    def all(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        with self.connect() as con:
            return list(con.execute(sql, tuple(params)).fetchall())

    def one(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        with self.connect() as con:
            return con.execute(sql, tuple(params)).fetchone()

    def execute(self, sql: str, params: Iterable[Any] = ()) -> int:
        with self.connect() as con:
            cur = con.execute(sql, tuple(params))
            return int(cur.lastrowid or 0)

    def setting(self, key: str, default: str = "") -> str:
        row = self.one("SELECT value FROM settings WHERE key=?", (key,))
        return str(row["value"]) if row else default

    def set_setting(self, key: str, value: Any) -> None:
        self.set_settings({key: value})

    def set_settings(self, values: Mapping[str, Any]) -> None:
        with self.connect() as con:
            con.executemany("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", [(str(k), str(v)) for k,v in values.items()])

    def audit(self, action: str, entity: str = "", entity_id: int | None = None, detail: str = "") -> None:
        self.execute("INSERT INTO audit(action,entity,entity_id,detail,created_at) VALUES(?,?,?,?,?)", (action, entity, entity_id, detail, self.now()))

    def _validate_soft_delete_table(self, table: str) -> str:
        if table not in SOFT_DELETE_TABLES:
            raise ValueError("Unsupported table")
        columns = {str(row[1]) for row in self.all(f"PRAGMA table_info({table})")}
        if "id" not in columns or "deleted" not in columns:
            raise ValueError("Unsupported table")
        return table

    def soft_delete(self, table: str, record_id: int) -> None:
        safe_table = self._validate_soft_delete_table(table)
        self.execute(f"UPDATE {safe_table} SET deleted=1 WHERE id=?", (record_id,))
        self.audit("TRASH", safe_table, record_id)

    def restore(self, table: str, record_id: int) -> None:
        safe_table = self._validate_soft_delete_table(table)
        self.execute(f"UPDATE {safe_table} SET deleted=0 WHERE id=?", (record_id,))
        self.audit("RESTORE", safe_table, record_id)

    def integrity_check(self) -> bool:
        row = self.one("PRAGMA integrity_check")
        return bool(row and str(row[0]).lower() == "ok")
