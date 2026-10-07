import unittest
from pathlib import Path
class LayoutTests(unittest.TestCase):
 def test_default_1366_and_flexible_larger_layout(self):
  text=(Path(__file__).parents[1]/'app'/'main_window.py').read_text(encoding='utf-8'); self.assertIn('resize(1366,768)',text); self.assertIn("QScrollArea()",text); self.assertNotIn('setMaximumSize(1366',text)
if __name__=='__main__':unittest.main()
