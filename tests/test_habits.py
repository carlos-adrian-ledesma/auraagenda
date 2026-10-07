import unittest
from tests.common import temp_db
class HabitTests(unittest.TestCase):
 def test_habits_and_logs(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); names={r[0] for r in db.all("SELECT name FROM sqlite_master WHERE type='table'")}; self.assertTrue({'habits','habit_logs'} <= names)
if __name__=='__main__': unittest.main()
