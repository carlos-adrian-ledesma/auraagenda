import unittest
from tests.common import temp_db
class DashboardDataTests(unittest.TestCase):
 def test_empty_database_returns_zero_metrics(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); self.assertEqual(db.one('SELECT COUNT(*) FROM tasks WHERE deleted=0')[0],0); self.assertEqual(db.one('SELECT COALESCE(SUM(amount_ml),0) FROM water')[0],0); self.assertEqual(db.one('SELECT COUNT(*) FROM agenda WHERE deleted=0')[0],0)
if __name__=='__main__': unittest.main()
