import unittest
from app.i18n import I18n
class I18nTests(unittest.TestCase):
 def test_language_key_sets_match(self): self.assertEqual(I18n.validate(),(set(),set()))
 def test_no_missing_key_echo(self):
  i=I18n('es'); self.assertNotEqual(i.t('page.dashboard'),'page.dashboard'); i.set_language('en'); self.assertEqual(i.t('common.save'),'Save')
if __name__=='__main__': unittest.main()
