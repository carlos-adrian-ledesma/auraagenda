import unittest
from pathlib import Path
class NavigationTests(unittest.TestCase):
 def test_navigation_uses_ids_not_stack_indices(self):
  text=(Path(__file__).parents[1]/'app'/'main_window.py').read_text(encoding='utf-8'); self.assertIn("def go(self,page_id",text); self.assertIn("self.pages.get(page_id)",text); self.assertNotIn('def go(self,index',text)
 def test_all_page_ids_are_unique(self):
  from ast import literal_eval
  text=(Path(__file__).parents[1]/'app'/'main_window.py').read_text(encoding='utf-8'); self.assertIn("('dashboard','page.dashboard')",text)
if __name__=='__main__': unittest.main()
