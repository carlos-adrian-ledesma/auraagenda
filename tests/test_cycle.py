import unittest
from tests.common import temp_db
class CycleTests(unittest.TestCase):
 def test_cycle_table(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); cols={r[1] for r in db.all('PRAGMA table_info(cycle_records)')}; self.assertTrue({'start_date','end_date','duration_days','symptoms','intensity'} <= cols)
if __name__=='__main__': unittest.main()
