"""
Date Parser - Parsing avanzato timestamp per log (BASE DETECTION)

Responsabilità:
- Estrarre timestamp da testo
- Identificare formato
- Restituire confidence
- NESSUN side-effect su LogEvent
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any
import logging

try:
    from dateutil.parser import parse as date_parse
except ImportError:  # pragma: no cover
    date_parse = None

logger = logging.getLogger(__name__)


class DateParser:
    """
    Parser avanzato per timestamp nei log.

    Supporta:
    - ISO 8601
    - Syslog
    - Apache / Nginx
    - Unix timestamps (sec/ms)
    - Fallback fuzzy (dateutil)
    """

    def __init__(self) -> None:
        self._patterns = self._compile_patterns()
        self._cache: Dict[str, Tuple[Optional[datetime], str, float]] = {}

    # ------------------------------------------------------------------ #
    # PATTERN SETUP
    # ------------------------------------------------------------------ #

    def _compile_patterns(self) -> list[tuple[re.Pattern, str, float]]:
        return [
            # ISO 8601
            (
                re.compile(
                    r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
                    r'(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)'
                ),
                "iso8601",
                0.95,
            ),
            # Syslog: "Mon DD HH:MM:SS"
            (
                re.compile(r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'),
                "syslog",
                0.85,
            ),
            # Apache / Nginx
            (
                re.compile(
                    r'(\d{2}/[A-Z][a-z]{2}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+-]\d{4})'
                ),
                "apache",
                0.85,
            ),
            # Simple datetime
            (
                re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'),
                "simple",
                0.75,
            ),
            # Unix timestamp (seconds)
            (
                re.compile(r'\b(\d{10})\b'),
                "unix_seconds",
                0.7,
            ),
            # Unix timestamp (milliseconds)
            (
                re.compile(r'\b(\d{13})\b'),
                "unix_millis",
                0.7,
            ),
        ]

    # ------------------------------------------------------------------ #
    # PUBLIC API
    # ------------------------------------------------------------------ #

    def parse(
        self,
        text: str,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[datetime], str, float]:
        """
        Estrae timestamp da testo.

        Returns:
            (datetime | None, format_name, confidence)
        """
        cache_key = f"{text}|{context}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        for pattern, fmt, confidence in self._patterns:
            match = pattern.search(text)
            if not match:
                continue

            raw = match.group(1)
            try:
                dt = self._parse_specific(raw, fmt)
                if dt:
                    result = (dt, fmt, confidence)
                    self._cache[cache_key] = result
                    return result
            except Exception:
                continue

        # Fallback fuzzy parsing
        if date_parse:
            try:
                dt = date_parse(text, fuzzy=True)
                result = (dt, "fuzzy", 0.4)
                self._cache[cache_key] = result
                return result
            except Exception:
                pass

        result = (None, "unknown", 0.0)
        self._cache[cache_key] = result
        return result

    # ------------------------------------------------------------------ #
    # INTERNALS
    # ------------------------------------------------------------------ #

    def _parse_specific(self, value: str, fmt: str) -> Optional[datetime]:
        if fmt == "iso8601":
            normalized = value.replace(" ", "T")
            if normalized.endswith("Z"):
                normalized = normalized.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)

        if fmt == "syslog":
            year = datetime.now().year
            return datetime.strptime(f"{year} {value}", "%Y %b %d %H:%M:%S")

        if fmt == "apache":
            return datetime.strptime(value, "%d/%b/%Y:%H:%M:%S %z")

        if fmt == "simple":
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

        if fmt == "unix_seconds":
            return datetime.fromtimestamp(int(value), tz=timezone.utc)

        if fmt == "unix_millis":
            return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)

        return None

    def clear_cache(self) -> None:
        self._cache.clear()


# Singleton opzionale
global_date_parser = DateParser()
