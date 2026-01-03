from __future__ import annotations

"""
Log Processor (BASE)

Pipeline:
Reader → LogEvent → Normalizer → output

⚠️ NO detection
⚠️ NO ML
⚠️ NO orchestrator
"""

from pathlib import Path
from typing import Iterator, Union
import logging
from datetime import datetime

from ice_devtools.parsing.reader import LogReader
from ice_devtools.parsing.normalizer import LogNormalizer
from ice_devtools.core.types import LogEvent
from ice_devtools.core.exceptions import ParseError

logger = logging.getLogger(__name__)


class LogProcessor:
    """Processor base per parsing offline."""

    def __init__(self, normalizer: LogNormalizer | None = None):
        self.normalizer = normalizer or LogNormalizer()
        self.stats = {
            "events": 0,
            "normalized": 0,
            "failed": 0,
            "started_at": None,
        }

    # ------------------------------------------------------------------

    def process_file(self, path: Union[str, Path]) -> Iterator[LogEvent]:
        reader = LogReader(path)
        self.stats["started_at"] = datetime.utcnow()

        for record in reader.read():
            try:
                event = LogEvent(
                    raw_message=str(record),
                    structured_data=record if isinstance(record, dict) else {},
                )

                event = self.normalizer.normalize(event)

                self.stats["events"] += 1
                self.stats["normalized"] += 1

                yield event

            except Exception as exc:
                self.stats["events"] += 1
                self.stats["failed"] += 1
                logger.debug("Failed event", exc_info=exc)

    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        return {
            "processor": dict(self.stats),
            "normalizer": self.normalizer.get_stats(),
        }

    def reset_stats(self) -> None:
        for k in self.stats:
            self.stats[k] = 0
        self.normalizer.reset_stats()
