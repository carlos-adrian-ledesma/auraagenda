import unittest
from tests.common import temp_db
class TaskTests(unittest.TestCase):
 def test_task_advanced_fields(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); cols={r[1] for r in db.all('PRAGMA table_info(tasks)')}; self.assertTrue({'tags','recurrence','estimated_minutes','parent_id','reminder_at'} <= cols)
if __name__=='__main__': unittest.main()
