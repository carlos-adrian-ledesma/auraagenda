import tempfile,unittest
from pathlib import Path
from tests.common import temp_db
from app.services import backup as mod
class BackupTests(unittest.TestCase):
 def test_create_validate_and_safe_path(self):
  td,db=temp_db(); self.addCleanup(td.cleanup)
  with tempfile.TemporaryDirectory() as root:
   root=Path(root); old=(mod.BACKUP_DIR,mod.DATA_ROOT,mod.DB_PATH); mod.DATA_ROOT=root; mod.BACKUP_DIR=root/'Backups'; mod.DB_PATH=db.path
   try:
    (root/'Database').mkdir(); (root/'Database'/'auraagenda.db').write_bytes(db.path.read_bytes()); svc=mod.BackupService(db); p=svc.create(); self.assertTrue(svc.validate(p)); self.assertRaises(ValueError,svc.safe_target,root/'tmp','../../escape')
   finally: mod.BACKUP_DIR,mod.DATA_ROOT,mod.DB_PATH=old
if __name__=='__main__': unittest.main()
