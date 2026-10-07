import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class RepositoryHygieneTests(unittest.TestCase):
    def test_no_runtime_databases_or_logs_are_committed(self):
        bad = []
        for path in ROOT.rglob('*'):
            if not path.is_file():
                continue
            if any(part in {'.venv', '__pycache__'} for part in path.parts):
                continue
            if path.suffix.lower() in {'.db', '.sqlite', '.sqlite3', '.log', '.pem', '.pfx', '.p12'}:
                bad.append(str(path.relative_to(ROOT)))
        self.assertEqual(bad, [])

    def test_no_common_secret_patterns(self):
        pattern = re.compile(r'(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|' + 'BEGIN ' + 'PRIVATE KEY' + r'|AIza[A-Za-z0-9_-]{20,})')
        matches = []
        for path in ROOT.rglob('*'):
            if not path.is_file() or path.suffix.lower() not in {'.py', '.md', '.txt', '.yml', '.yaml', '.bat', '.ps1', '.iss'}:
                continue
            if path.name == 'test_repository_hygiene.py':
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            if pattern.search(text):
                matches.append(str(path.relative_to(ROOT)))
        self.assertEqual(matches, [])


if __name__ == '__main__':
    unittest.main()
