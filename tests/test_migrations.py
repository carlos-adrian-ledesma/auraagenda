import sqlite3,tempfile,unittest
from pathlib import Path
from app.database import Database,SCHEMA_VERSION
class MigrationTests(unittest.TestCase):
 def test_compatible_columns_are_added(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db.sqlite'; con=sqlite3.connect(p); con.executescript("CREATE TABLE agenda(id INTEGER PRIMARY KEY,title TEXT,event_date TEXT,created_at TEXT,updated_at TEXT,deleted INTEGER DEFAULT 0); CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);"); con.close(); db=Database(p); cols={r[1] for r in db.all('PRAGMA table_info(agenda)')}; self.assertIn('repeat_rule',cols); self.assertGreaterEqual(db.one('SELECT MAX(version) FROM schema_version')[0],SCHEMA_VERSION)
if __name__=='__main__': unittest.main()
