from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
import logging

from ice_devtools.core.types import LogEvent
from ice_devtools.core.exceptions import DetectionError

logger = logging.getLogger(__name__)


class BaseDetector(ABC):
    """
    Base astratta per detector euristici.

    Responsabilità:
    - analizzare UNA linea
    - estrarre campi base
    - assegnare confidence
    """

    name: str = "BaseDetector"
    version: str = "1.0.0"

    def __init__(self) -> None:
        self._stats = {
            "processed": 0,
            "matched": 0,
            "failed": 0,
        }

    @abstractmethod
    def detect(self, line: str) -> Optional[LogEvent]:
        """Analizza una linea e restituisce LogEvent o None."""
        raise NotImplementedError

    def flush(self) -> Optional[LogEvent]:
        """Hook per multiline detector."""
        return None

    def get_stats(self) -> dict:
        return dict(self._stats)

    def reset_stats(self) -> None:
        for k in self._stats:
            self._stats[k] = 0
