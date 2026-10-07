import unittest
from tests.common import temp_db
class SettingsTests(unittest.TestCase):
 def test_settings_transaction(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); db.set_settings({'language':'en','currency':'USD','theme':'Rose Night'}); self.assertEqual(db.setting('language'),'en'); self.assertEqual(db.setting('currency'),'USD')
if __name__=='__main__': unittest.main()
