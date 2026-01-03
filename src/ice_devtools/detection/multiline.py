"""
Multiline Buffer - Gestione multiline log (BASE DETECTION)

Responsabilità:
- Bufferizzare linee
- Riconoscere start / continuation
- Restituire testo completo
"""

from __future__ import annotations

import re
from typing import Optional, List
from datetime import datetime


class MultilineBuffer:
    """
    Gestore multiline log.

    NON fa detection semantica.
    NON crea LogEvent.
    """

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._buffer: List[str] = []
        self._started_at: Optional[datetime] = None

        self._start_patterns = [
            re.compile(r'^Traceback \(most recent call last\):'),
            re.compile(r'^Exception in thread ".+"'),
        ]

        self._continue_patterns = [
            re.compile(r'^\s+'),
            re.compile(r'^\s+at '),
            re.compile(r'^\s+File "'),
        ]

    # ------------------------------------------------------------------ #
    # PUBLIC API
    # ------------------------------------------------------------------ #

    def should_start(self, line: str) -> bool:
        if not self.enabled:
            return False
        return any(p.match(line) for p in self._start_patterns)

    def should_continue(self, line: str) -> bool:
        return any(p.match(line) for p in self._continue_patterns)

    def push(self, line: str) -> None:
        if not self._buffer:
            self._started_at = datetime.now()
        self._buffer.append(line)

    def has_pending(self) -> bool:
        return bool(self._buffer)

    def flush(self) -> Optional[str]:
        if not self._buffer:
            return None

        text = "\n".join(self._buffer)
        self._buffer.clear()
        self._started_at = None
        return text

    # ------------------------------------------------------------------ #
    # HIGH-LEVEL HELPER
    # ------------------------------------------------------------------ #

    def handle_line(self, line: str) -> Optional[str]:
        """
        Gestisce una linea:
        - ritorna None se buffering continua
        - ritorna multiline text se termina
        """
        if not self.enabled:
            return None

        if self.should_start(line):
            self.push(line)
            return None

        if self.has_pending():
            if self.should_continue(line):
                self.push(line)
                return None
            else:
                return self.flush()

        return None
