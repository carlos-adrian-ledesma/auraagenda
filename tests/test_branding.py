import unittest
from pathlib import Path
class BrandingTests(unittest.TestCase):
 def test_legacy_identity_only_in_migration_compatibility(self):
  root=Path(__file__).parents[1]; allowed={'paths.py','MIGRATION_FROM_DANICA_V1.md','test_old_danica_migration.py','test_branding.py'}; hits=[]
  for p in root.rglob('*'):
   if not p.is_file() or '__pycache__' in p.parts or p.suffix.lower() in {'.png','.ico','.pyc'}: continue
   try:text=p.read_text(encoding='utf-8',errors='ignore')
   except Exception:continue
   if any(x in text for x in ('Danica Davis','DanicaDavis','danica_davis')) and p.name not in allowed: hits.append(str(p.relative_to(root)))
  self.assertEqual(hits,[])
 def test_no_old_product_phrase(self):
  root=Path(__file__).parents[1]; phrase='Magical Pink'+' Universe'; hits=[]
  for base in (root/'app',root/'docs'):
   for p in base.rglob('*'):
    if p.is_file() and p.suffix in {'.py','.md','.txt'} and phrase in p.read_text(encoding='utf-8',errors='ignore'): hits.append(str(p.relative_to(root)))
  self.assertEqual(hits,[])
if __name__=='__main__':unittest.main()
