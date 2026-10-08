import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class VisualDesignSystemTests(unittest.TestCase):
    def test_all_themes_have_semantic_tokens(self):
        from app.styles import THEMES, validate_themes
        self.assertTrue(validate_themes())
        self.assertGreaterEqual(len(THEMES), 8)

    def test_dark_surfaces_are_explicitly_styled(self):
        text = (ROOT / 'app' / 'styles.py').read_text(encoding='utf-8')
        for selector in ('QTabWidget::pane', 'QScrollArea', 'QComboBox QAbstractItemView', 'QCalendarWidget', 'QDialog'):
            self.assertIn(selector, text)
        self.assertIn('background:{c[\'surface\']}', text)

    def test_settings_uses_vertical_navigation_not_compressed_tabs(self):
        text = (ROOT / 'app' / 'pages' / 'settings.py').read_text(encoding='utf-8')
        self.assertIn('QListWidget', text)
        self.assertIn('QStackedWidget', text)
        self.assertIn('SettingsNav', text)
        self.assertNotIn('self.tabs', text)

    def test_settings_fields_are_width_capped(self):
        text = (ROOT / 'app' / 'pages' / 'settings.py').read_text(encoding='utf-8')
        self.assertIn('setMaximumWidth', text)
        self.assertIn('max_content_width=920', text)

    def test_sidebar_groups_can_collapse(self):
        text = (ROOT / 'app' / 'main_window.py').read_text(encoding='utf-8')
        self.assertIn('NavGroupButton', text)
        self.assertIn('def _toggle_group', text)
        self.assertIn('setChecked(True)', text)

    def test_crud_dialogs_scroll_instead_of_clipping(self):
        text = (ROOT / 'app' / 'pages' / 'generic.py').read_text(encoding='utf-8')
        self.assertIn('QScrollArea', text)
        self.assertIn('setWidgetResizable(True)', text)
        self.assertIn('setMinimumSize(560, 420)', text)

    def test_design_tokens_define_responsive_dimensions(self):
        from app.design_system import SIZING, SPACING, RADIUS
        self.assertEqual(SIZING['sidebar_width'], 236)
        self.assertGreaterEqual(SIZING['form_max_width'], 700)
        self.assertEqual(SPACING['lg'], 16)
        self.assertEqual(RADIUS['xl'], 16)

    def test_v204_identity_is_consistent(self):
        text = (ROOT / 'app' / 'paths.py').read_text(encoding='utf-8')
        self.assertIn('VERSION = "2.0.4"', text)
        for path in [ROOT / 'VERSION.txt', ROOT / 'installer' / 'AuraAgenda.iss']:
            data = path.read_text(encoding='utf-8')
            self.assertIn('2.0.4', data)
            self.assertNotIn('2.0.2', data)


if __name__ == '__main__':
    unittest.main()
