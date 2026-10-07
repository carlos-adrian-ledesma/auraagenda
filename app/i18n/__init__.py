from __future__ import annotations

from .translations import TRANSLATIONS, CHOICE_LABELS

class I18n:
    def __init__(self, language: str = "es"):
        self.language = language if language in TRANSLATIONS else "es"

    def set_language(self, language: str) -> None:
        self.language = language if language in TRANSLATIONS else "es"

    def t(self, key: str, **kwargs) -> str:
        table = TRANSLATIONS[self.language]
        fallback = TRANSLATIONS["es"]
        value = table.get(key, fallback.get(key, key))
        try:
            return value.format(**kwargs)
        except Exception:
            return value

    def choice(self, value: str) -> str:
        return CHOICE_LABELS.get(self.language, {}).get(str(value), str(value))

    @staticmethod
    def validate() -> tuple[set[str], set[str]]:
        es, en = set(TRANSLATIONS["es"]), set(TRANSLATIONS["en"])
        return es - en, en - es
