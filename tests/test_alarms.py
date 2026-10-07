import unittest
from pathlib import Path
class AlarmTests(unittest.TestCase):
 def test_recurrence_is_implemented_not_only_listed(self):
  text=(Path(__file__).parents[1]/'app'/'main_window.py').read_text(encoding='utf-8'); self.assertIn("rule=='daily'",text); self.assertIn("rule=='weekly'",text); self.assertIn("rule=='monthly'",text); self.assertIn('UPDATE alarms SET last_triggered',text)
if __name__=='__main__': unittest.main()
