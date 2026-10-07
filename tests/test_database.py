import unittest
from tests.common import temp_db
class DatabaseTests(unittest.TestCase):
 def test_new_database_has_core_tables(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); names={r[0] for r in db.all("SELECT name FROM sqlite_master WHERE type='table'")}; self.assertTrue({'settings','schema_version','agenda','tasks','finance','cycle_records','wardrobe','backups'} <= names); self.assertEqual(db.setting('language'),'es'); self.assertEqual(db.setting('user_name'),'Tu nombre')
if __name__=='__main__': unittest.main()
