import unittest
from pathlib import Path


class OnboardingStartupRegressionTests(unittest.TestCase):
    def test_onboarding_does_not_use_fragile_label_for_field(self):
        source = (Path(__file__).parents[1] / "app" / "onboarding.py").read_text(encoding="utf-8")
        self.assertNotIn("labelForField(", source)
        self.assertIn('self._labels: dict[str, QLabel]', source)
        self.assertIn('form.addRow(label, widget)', source)


if __name__ == "__main__":
    unittest.main()
