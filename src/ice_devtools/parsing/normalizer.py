from __future__ import annotations

"""
Log Normalizer

Responsabilità:
- pulizia messaggi
- normalizzazione campi già estratti
- coercion di tipi primitivi

⚠️ NON:
- detection
- parsing regex
- ML
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any

from ice_devtools.core.types import LogEvent, LogLevel
from ice_devtools.core.exceptions import ParseError

logger = logging.getLogger(__name__)


class LogNormalizer:
    """Normalizer puro, senza detection."""

    _LEVEL_MAP = {
        "debug": LogLevel.DEBUG,
        "info": LogLevel.INFO,
        "warn": LogLevel.WARNING,
        "warning": LogLevel.WARNING,
        "error": LogLevel.ERROR,
        "fatal": LogLevel.CRITICAL,
        "critical": LogLevel.CRITICAL,
    }

    _CLEANUP_PATTERNS = [
        (re.compile(r"\x1b\[[0-9;]*m"), ""),     # ANSI
        (re.compile(r"[\x00-\x1f\x7f-\x9f]"), ""),  # control chars
        (re.compile(r"\s+"), " "),
    ]

    def __init__(self) -> None:
        self.stats = {
            "normalized": 0,
            "levels": 0,
            "timestamps": 0,
            "messages": 0,
        }

    # ------------------------------------------------------------------

    def normalize(self, event: LogEvent) -> LogEvent:
        try:
            self._normalize_level(event)
            self._normalize_timestamp(event)
            self._clean_message(event)
            self._coerce_fields(event)

            self.stats["normalized"] += 1
            return event

        except Exception as exc:
            raise ParseError(f"Normalization failed: {exc}") from exc

    # ------------------------------------------------------------------

    def _normalize_level(self, event: LogEvent) -> None:
        if event.level:
            return

        raw = (
            event.extracted_fields.get("level")
            or event.extracted_fields.get("severity")
        )

        if isinstance(raw, str):
            level = self._LEVEL_MAP.get(raw.lower())
            if level:
                event.level = level
                self.stats["levels"] += 1

    # ------------------------------------------------------------------

    def _normalize_timestamp(self, event: LogEvent) -> None:
        if event.timestamp:
            return

        raw = event.extracted_fields.get("timestamp")
        if not raw:
            return

        if isinstance(raw, datetime):
            event.timestamp = raw
            self.stats["timestamps"] += 1
            return

        if isinstance(raw, (int, float)):
            event.timestamp = datetime.fromtimestamp(raw)
            self.stats["timestamps"] += 1
            return

        if isinstance(raw, str):
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ):
                try:
                    event.timestamp = datetime.strptime(raw, fmt)
                    self.stats["timestamps"] += 1
                    return
                except ValueError:
                    continue

    # ------------------------------------------------------------------

    def _clean_message(self, event: LogEvent) -> None:
        if not event.raw_message:
            return

        msg = event.raw_message
        for pattern, repl in self._CLEANUP_PATTERNS:
            msg = pattern.sub(repl, msg)

        msg = msg.strip()

        if msg != event.raw_message:
            event.parsed_message = msg
            self.stats["messages"] += 1
        elif not event.parsed_message:
            event.parsed_message = event.raw_message

    # ------------------------------------------------------------------

    def _coerce_fields(self, event: LogEvent) -> None:
        for k, v in list(event.extracted_fields.items()):
            if isinstance(v, str) and v.isdigit():
                event.extracted_fields[k] = int(v)

    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, int]:
        return dict(self.stats)

    def reset_stats(self) -> None:
        for k in self.stats:
            self.stats[k] = 0
