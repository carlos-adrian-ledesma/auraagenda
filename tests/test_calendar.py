import unittest
from tests.common import temp_db
class CalendarTests(unittest.TestCase):
 def test_event_fields(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); cols={r[1] for r in db.all('PRAGMA table_info(agenda)')}; self.assertTrue({'all_day','location','reminder_minutes','repeat_rule','repeat_detail','color'} <= cols)
if __name__=='__main__': unittest.main()
