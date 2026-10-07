import unittest
from app.i18n import I18n
class SwitchTests(unittest.TestCase):
 def test_es_en_es(self):
  i=I18n('es'); a=i.t('settings.saved'); i.set_language('en'); b=i.t('settings.saved'); i.set_language('es'); self.assertNotEqual(a,b); self.assertEqual(a,i.t('settings.saved'))
if __name__=='__main__': unittest.main()
