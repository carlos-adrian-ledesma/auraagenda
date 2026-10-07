import unittest
from pathlib import Path
class MixedTextTests(unittest.TestCase):
 def test_known_mixed_legacy_phrases_absent(self):
  root=Path(__file__).parents[1]/'app'; text='\n'.join(p.read_text(encoding='utf-8') for p in root.rglob('*.py')); self.assertNotIn('Settings guardada',text); self.assertNotIn('File no encontrado',text); self.assertNotIn('Time de inicio',text); self.assertNotIn('Completed / Completada',text); self.assertNotIn('Notifications / Notificaciones',text)
if __name__=='__main__':unittest.main()
