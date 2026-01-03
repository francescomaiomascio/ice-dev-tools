from __future__ import annotations

"""
Core type definitions for ICE DevTools.

Scope:
- Parsing
- Detection
- Offline analysis
- Tooling support

⚠️ IMPORTANT:
- This module MUST remain ML-agnostic.
- No embeddings, clustering, scoring, or inference logic here.
- Anything ML-related belongs to ICE-AI or ML-specific modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


# ======================================================================
# LOG LEVEL
# ======================================================================

class LogLevel(str, Enum):
    """
    Standard log severity levels.

    Kept minimal and interoperable with common logging systems.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ======================================================================
# LOG SOURCE
# ======================================================================

@dataclass
class LogSource:
    """
    Definition of a log source.

    This represents WHERE logs come from, not their meaning.
    """
    id: int
    name: str
    path: str
    source_type: str  # file, stream, syslog, socket, etc.

    encoding: str = "utf-8"
    enabled: bool = True

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        """Update modification timestamp."""
        self.updated_at = datetime.utcnow()


# ======================================================================
# LOG EVENT
# ======================================================================

@dataclass
class LogEvent:
    """
    Parsed log event.

    Contains ONLY:
    - raw data
    - parsed fields
    - contextual metadata

    ❌ Does NOT contain:
    - embeddings
    - scores
    - ML-derived attributes
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    event_id: Optional[int] = None
    source_id: Optional[int] = None

    # ------------------------------------------------------------------
    # Time
    # ------------------------------------------------------------------
    timestamp: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------
    raw_message: Optional[str] = None
    parsed_message: Optional[str] = None
    level: Optional[LogLevel] = None

    # ------------------------------------------------------------------
    # Parsing metadata
    # ------------------------------------------------------------------
    event_type: Optional[str] = None
    confidence: float = 1.0
    parser_version: str = "1.0.0"

    # ------------------------------------------------------------------
    # Source context
    # ------------------------------------------------------------------
    file_name: Optional[str] = None
    line_number: Optional[int] = None
    logger_name: Optional[str] = None

    # ------------------------------------------------------------------
    # Execution context
    # ------------------------------------------------------------------
    process_id: Optional[int] = None
    thread_name: Optional[str] = None

    # ------------------------------------------------------------------
    # Extracted data
    # ------------------------------------------------------------------
    extracted_fields: Dict[str, Any] = field(default_factory=dict)
    structured_data: Dict[str, Any] = field(default_factory=dict)

    # ==================================================================
    # Lifecycle
    # ==================================================================

    def __post_init__(self) -> None:
        # Normalize log level if provided as string
        if isinstance(self.level, str):
            try:
                self.level = LogLevel(self.level.upper())
            except ValueError:
                self.level = None

    # ==================================================================
    # Helpers
    # ==================================================================

    @property
    def is_structured(self) -> bool:
        """True if structured data is present."""
        return bool(self.structured_data)

    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize event to plain dict.

        Safe for JSON / IPC / persistence.
        """
        return {
            "event_id": self.event_id,
            "source_id": self.source_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat(),
            "raw_message": self.raw_message,
            "parsed_message": self.parsed_message,
            "level": self.level.value if self.level else None,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "parser_version": self.parser_version,
            "file_name": self.file_name,
            "line_number": self.line_number,
            "logger_name": self.logger_name,
            "process_id": self.process_id,
            "thread_name": self.thread_name,
            "extracted_fields": self.extracted_fields,
            "structured_data": self.structured_data,
        }

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LogEvent:
        """
        Deserialize event from dict.
        """
        def _parse_dt(value: Any) -> Optional[datetime]:
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            return value

        level = data.get("level")
        if isinstance(level, str):
            try:
                level = LogLevel(level.upper())
            except ValueError:
                level = None

        return cls(
            event_id=data.get("event_id"),
            source_id=data.get("source_id"),
            timestamp=_parse_dt(data.get("timestamp")),
            created_at=_parse_dt(data.get("created_at")) or datetime.utcnow(),
            raw_message=data.get("raw_message"),
            parsed_message=data.get("parsed_message"),
            level=level,
            event_type=data.get("event_type"),
            confidence=data.get("confidence", 1.0),
            parser_version=data.get("parser_version", "1.0.0"),
            file_name=data.get("file_name"),
            line_number=data.get("line_number"),
            logger_name=data.get("logger_name"),
            process_id=data.get("process_id"),
            thread_name=data.get("thread_name"),
            extracted_fields=data.get("extracted_fields", {}),
            structured_data=data.get("structured_data", {}),
        )
