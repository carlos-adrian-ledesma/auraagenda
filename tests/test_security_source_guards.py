import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class SecuritySourceGuardTests(unittest.TestCase):
    def test_tray_routes_through_security_gate(self):
        text = (ROOT / 'app' / 'main_window.py').read_text(encoding='utf-8')
        self.assertIn('controller.request_show()', text)
        self.assertIn('def _show_unlocked', text)
        self.assertIn('controller.locked', text)

    def test_cancel_does_not_clear_locked_state(self):
        text = (ROOT / 'app' / 'services' / 'autolock.py').read_text(encoding='utf-8')
        self.assertIn('self.locked = True', text)
        self.assertIn('return False', text)
        self.assertNotIn('if not ok: self.reset(); return', text)

    def test_network_lock_requires_master_recovery(self):
        text = (ROOT / 'app' / 'pages' / 'settings.py').read_text(encoding='utf-8')
        self.assertIn('master_required_for_network', text)
        self.assertIn('canonical_trusted_networks', text)

    def test_no_universal_master_secret_is_embedded(self):
        text = '\n'.join(
            path.read_text(encoding='utf-8', errors='ignore')
            for path in (ROOT / 'app').rglob('*.py')
        )
        forbidden = [r'MASTER_PASSWORD\s*=', r'BACKDOOR\s*=', r'UNIVERSAL_KEY\s*=']
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, text, flags=re.IGNORECASE))


if __name__ == '__main__':
    unittest.main()
