import sqlite3,tempfile,unittest
from pathlib import Path
from tests.common import temp_db
from app.services import migration as mod
class LegacyMigrationTests(unittest.TestCase):
 def test_old_database_import_is_non_destructive(self):
  td,db=temp_db(); self.addCleanup(td.cleanup)
  with tempfile.TemporaryDirectory() as root:
   root=Path(root); legacy_root=root/'legacy'; legacy_db=legacy_root/'BaseDatos'/'old.db'; legacy_db.parent.mkdir(parents=True); c=sqlite3.connect(legacy_db); c.executescript("CREATE TABLE tasks(id INTEGER PRIMARY KEY,title TEXT,description TEXT,category TEXT,priority TEXT,status TEXT,due_date TEXT,progress INTEGER,created_at TEXT,updated_at TEXT,deleted INTEGER); CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT); INSERT INTO tasks VALUES(1,'Legacy task','','','Normal','Pending','',0,'2026-01-01','2026-01-01',0); INSERT INTO settings VALUES('theme','Pink Crystal');"); c.commit(); c.close(); old=(mod.LEGACY_ROOT,mod.LEGACY_DB,mod.DB_PATH,mod.BACKUP_DIR); mod.LEGACY_ROOT=legacy_root; mod.LEGACY_DB=legacy_db; mod.DB_PATH=db.path; mod.BACKUP_DIR=root/'backups'
   try: svc=mod.LegacyMigrationService(); self.assertTrue(svc.exists()); backup=svc.migrate(db); self.assertTrue(legacy_db.exists()); self.assertTrue(backup.exists()); self.assertEqual(db.one("SELECT title FROM tasks WHERE title='Legacy task'")[0],'Legacy task')
   finally: mod.LEGACY_ROOT,mod.LEGACY_DB,mod.DB_PATH,mod.BACKUP_DIR=old
if __name__=='__main__': unittest.main()
