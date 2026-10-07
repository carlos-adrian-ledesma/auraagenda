from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
errors: list[str] = []

translations = ROOT / "app" / "i18n" / "translations.py"
if not translations.is_file():
    raise SystemExit("Ejecuta este verificador desde la raiz de AuraAgenda o pasa la ruta como argumento.")

tree = ast.parse(translations.read_text(encoding="utf-8"))
for node in ast.walk(tree):
    if not isinstance(node, ast.Dict):
        continue
    seen: dict[str, int] = {}
    for key in node.keys:
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            if key.value in seen:
                errors.append(
                    f"Clave duplicada {key.value!r} en linea {key.lineno} "
                    f"(primera en {seen[key.value]})"
                )
            else:
                seen[key.value] = key.lineno

pages_init = (ROOT / "app" / "pages" / "__init__.py").read_text(encoding="utf-8")
if "__all__" not in pages_init:
    errors.append("app/pages/__init__.py no declara __all__ para sus re-exports.")

main_window = (ROOT / "app" / "main_window.py").read_text(encoding="utf-8")
if "close=box.addButton" in main_window:
    errors.append("Sigue presente la asignacion no usada close=box.addButton.")

known_removed = {
    "app/pages/calendar.py": ["from PySide6.QtCore import QDate"],
    "app/pages/settings.py": ["RecoveryService, RecoveryError", "QStackedWidget, QVBoxLayout, QWidget"],
    "app/pages/statistics.py": ["QGridLayout,QLabel,QProgressBar"],
    "app/services/migration.py": ["LEGACY_ROOT, DATA_ROOT"],
    "app/services/recovery.py": ["import shutil"],
    "tests/test_backup_hardening.py": ["import hashlib"],
    "tests/test_navigation.py": ["from ast import literal_eval"],
}
for rel, snippets in known_removed.items():
    data = (ROOT / rel).read_text(encoding="utf-8")
    for snippet in snippets:
        if snippet in data:
            errors.append(f"Todavia aparece en {rel}: {snippet}")

sec = (ROOT / "tests" / "test_security_recovery.py").read_text(encoding="utf-8")
for snippet in ("import tempfile", "from pathlib import Path", "canonical_trusted_networks, network_status"):
    if snippet in sec:
        errors.append(f"Import no usado aun presente en tests/test_security_recovery.py: {snippet}")

if errors:
    print("VERIFICACION: ERROR")
    for item in errors:
        print("-", item)
    raise SystemExit(1)

print("VERIFICACION: OK")
print("Las correcciones objetivo del fallo Ruff estan presentes.")
