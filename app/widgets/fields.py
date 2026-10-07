from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class FieldSpec:
    name: str
    label_es: str
    label_en: str
    kind: str = "text"
    choices: Sequence[str] = ()
    required: bool = False
    default: str = ""
