import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from app.services import backup as mod
from tests.common import temp_db


class BackupHardeningTests(unittest.TestCase):
    def _service(self):
        td, db = temp_db()
        self.addCleanup(td.cleanup)
        return db, mod.BackupService(db)

    def test_path_traversal_and_absolute_paths_are_rejected(self):
        db, service = self._service()
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            for bad in ('../escape', '../../escape', '/absolute/file', 'C:/escape'):
                with self.assertRaises(ValueError):
                    service.safe_target(base, bad)

    def test_wrong_application_is_rejected(self):
        db, service = self._service()
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'bad.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('Database/auraagenda.db', b'not sqlite')
                z.writestr('backup_manifest.json', json.dumps({
                    'application': 'OtherApp', 'database': 'Database/auraagenda.db'
                }))
            self.assertFalse(service.validate(path))

    def test_restore_table_allowlist(self):
        td, db = temp_db()
        self.addCleanup(td.cleanup)
        with self.assertRaises(ValueError):
            db.restore('settings', 1)
        with self.assertRaises(ValueError):
            db.soft_delete('sqlite_master', 1)

    def test_hash_mismatch_is_rejected(self):
        td, db = temp_db()
        self.addCleanup(td.cleanup)
        with tempfile.TemporaryDirectory() as root_text:
            root = Path(root_text)
            path = root / 'hash_bad.zip'
            db_bytes = db.path.read_bytes()
            manifest = {
                'application': 'AuraAgenda',
                'version': '2.0.3',
                'database': 'Database/auraagenda.db',
                'file_count': 1,
                'total_uncompressed_size': len(db_bytes),
                'hash_algorithm': 'SHA-256',
                'hashes': {'Database/auraagenda.db': '0' * 64},
            }
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
                z.writestr('Database/auraagenda.db', db_bytes)
                z.writestr('backup_manifest.json', json.dumps(manifest))
            self.assertFalse(mod.BackupService(db).validate(path))

    def test_suspicious_compression_ratio_is_rejected(self):
        td, db = temp_db()
        self.addCleanup(td.cleanup)
        with tempfile.TemporaryDirectory() as root_text:
            root = Path(root_text)
            path = root / 'ratio_bad.zip'
            db_bytes = db.path.read_bytes()
            bomb = b'0' * (2 * 1024 * 1024)
            manifest = {
                'application': 'AuraAgenda',
                'version': '2.0.3',
                'database': 'Database/auraagenda.db',
                'file_count': 2,
                'total_uncompressed_size': len(db_bytes) + len(bomb),
                'hashes': {},
            }
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
                z.writestr('Database/auraagenda.db', db_bytes)
                z.writestr('Attachments/bomb.txt', bomb)
                z.writestr('backup_manifest.json', json.dumps(manifest))
            self.assertFalse(mod.BackupService(db).validate(path))


if __name__ == '__main__':
    unittest.main()
