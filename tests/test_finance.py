import unittest
from tests.common import temp_db
class FinanceTests(unittest.TestCase):
 def test_finance_support_tables(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); names={r[0] for r in db.all("SELECT name FROM sqlite_master WHERE type='table'")}; self.assertTrue({'budgets','subscriptions','savings_goals'} <= names); self.assertEqual(db.setting('currency'),'')
if __name__=='__main__': unittest.main()
