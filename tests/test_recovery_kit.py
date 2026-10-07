import tempfile
import unittest
from pathlib import Path

from app.services import backup as backup_mod
from app.services.recovery import RecoveryError, RecoveryService
from tests.common import temp_db


class RecoveryKitTests(unittest.TestCase):
    def test_encrypted_recovery_kit_round_trip(self):
        td, db = temp_db()
        self.addCleanup(td.cleanup)
        with tempfile.TemporaryDirectory() as root_text:
            root = Path(root_text)
            old = (backup_mod.DATA_ROOT, backup_mod.BACKUP_DIR, backup_mod.DB_PATH)
            backup_mod.DATA_ROOT = root
            backup_mod.BACKUP_DIR = root / 'Backups'
            backup_mod.DB_PATH = db.path
            try:
                (root / 'Database').mkdir(parents=True, exist_ok=True)
                service = RecoveryService(db)
                key = service.create_master_key()
                kit = service.create_recovery_kit(root / 'owner.aurarecovery', key)
                self.assertTrue(kit.exists())
                payload = root / 'payload.zip'
                header = service.decrypt_to_backup(kit, key, payload)
                self.assertEqual(header['application'], 'AuraAgenda')
                self.assertTrue(backup_mod.BackupService(db).validate(payload))
                with self.assertRaises(RecoveryError):
                    service.decrypt_to_backup(kit, 'WRONG-' * 12, root / 'bad.zip')
            finally:
                backup_mod.DATA_ROOT, backup_mod.BACKUP_DIR, backup_mod.DB_PATH = old


if __name__ == '__main__':
    unittest.main()
