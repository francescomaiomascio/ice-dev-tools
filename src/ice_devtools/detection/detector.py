from __future__ import annotations

import json
from typing import Optional
import logging

from ice_devtools.core.types import LogEvent, LogLevel
from ice_devtools.detection.base import BaseDetector
from ice_devtools.detection.patterns import PATTERNS

logger = logging.getLogger(__name__)


class UniversalDetector(BaseDetector):
    """
    Detector euristico BASE.
    Nessuna persistenza, nessuna ML.
    """

    name = "UniversalDetector"
    version = "1.0.0"

    def detect(self, line: str) -> Optional[LogEvent]:
        self._stats["processed"] += 1

        # JSON fast-path
        event = self._detect_json(line)
        if event:
            self._stats["matched"] += 1
            return event

        extracted = {}

        for p in PATTERNS.values():
            m = p.regex.search(line)
            if m:
                extracted[p.name] = m.group(0)

        if extracted:
            self._stats["matched"] += 1
            return LogEvent(
                raw_message=line,
                parsed_message=line[:300],
                extracted_fields=extracted,
                confidence=0.6,
                event_type="heuristic",
            )

        self._stats["failed"] += 1
        return None

    def _detect_json(self, line: str) -> Optional[LogEvent]:
        try:
            data = json.loads(line)
        except Exception:
            return None

        event = LogEvent(
            raw_message=line,
            parsed_message=str(data.get("message", ""))[:300],
            structured_data=data,
            event_type="json",
            confidence=0.9,
        )

        level = data.get("level")
        if isinstance(level, str):
            try:
                event.level = LogLevel(level.upper())
            except ValueError:
                pass

        return event
