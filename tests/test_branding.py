import unittest
from pathlib import Path


class BrandingTests(unittest.TestCase):
    def test_no_legacy_product_identity_remains(self):
        root = Path(__file__).parents[1]
        forbidden = "da" + "nica"
        hits = []

        ignored_parts = {
            ".git",
            ".venv",
            "__pycache__",
        }

        ignored_suffixes = {
            ".png",
            ".jpg",
            ".jpeg",
            ".ico",
            ".pyc",
            ".zip",
        }

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if any(part in ignored_parts for part in path.parts):
                continue

            if path.suffix.lower() in ignored_suffixes:
                continue

            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                continue

            if forbidden.casefold() in text.casefold():
                hits.append(str(path.relative_to(root)))

        self.assertEqual(
            hits,
            [],
            f"Legacy product identity found in: {hits}",
        )

    def test_no_old_product_phrase(self):
        root = Path(__file__).parents[1]
        phrase = "Magical Pink" + " Universe"
        hits = []

        for base in (root / "app", root / "docs"):
            for path in base.rglob("*"):
                if (
                    path.is_file()
                    and path.suffix.lower() in {".py", ".md", ".txt"}
                    and phrase in path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                ):
                    hits.append(str(path.relative_to(root)))

        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()