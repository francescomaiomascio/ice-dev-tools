from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Pattern, Dict


class PatternType(str, Enum):
    REGEX = "regex"


@dataclass(frozen=True)
class PatternDef:
    name: str
    regex: Pattern
    confidence: float = 0.6


PATTERNS: Dict[str, PatternDef] = {
    "iso_timestamp": PatternDef(
        name="iso_timestamp",
        regex=re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
        confidence=0.8,
    ),
    "log_level": PatternDef(
        name="log_level",
        regex=re.compile(r"\b(DEBUG|INFO|WARN|ERROR|CRITICAL)\b"),
        confidence=0.7,
    ),
    "ipv4": PatternDef(
        name="ipv4",
        regex=re.compile(r"\b\d{1,3}(\.\d{1,3}){3}\b"),
        confidence=0.6,
    ),
}
