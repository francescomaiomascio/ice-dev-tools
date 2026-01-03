from __future__ import annotations

"""
Log Reader

Responsabilità:
- leggere file di input (testo / CSV / JSON / JSONL)
- rilevare formato ed encoding
- produrre stream di righe o record strutturati

⚠️ NON:
- creare LogEvent
- fare parsing semantico
- fare detection
- fare ML
"""

import csv
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Iterator, Dict, Any, Union

from ice_devtools.core.exceptions import ParseError

logger = logging.getLogger(__name__)


# =====================================================================
# FORMAT ENUM
# =====================================================================

class LogFormat(str, Enum):
    TEXT = "text"
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    UNKNOWN = "unknown"


# =====================================================================
# READER
# =====================================================================

class LogReader:
    """
    Reader universale per file di log.
    """

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise ParseError(f"File not found: {self.path}")

        self.format = self._detect_format()
        self.encoding = self._detect_encoding()

        self.stats: Dict[str, int] = {
            "records_read": 0,
            "records_skipped": 0,
            "decode_errors": 0,
        }

        logger.debug(
            "LogReader initialized",
            extra={"path": str(self.path), "format": self.format},
        )

    # -----------------------------------------------------------------
    # FORMAT / ENCODING
    # -----------------------------------------------------------------

    def _detect_format(self) -> LogFormat:
        ext = self.path.suffix.lower()
        return {
            ".log": LogFormat.TEXT,
            ".txt": LogFormat.TEXT,
            ".csv": LogFormat.CSV,
            ".json": LogFormat.JSON,
            ".jsonl": LogFormat.JSONL,
        }.get(ext, LogFormat.UNKNOWN)

    def _detect_encoding(self) -> str:
        candidates = ("utf-8", "latin-1", "cp1252", "iso-8859-1")

        for enc in candidates:
            try:
                with self.path.open("r", encoding=enc) as f:
                    f.read(1024)
                return enc
            except UnicodeDecodeError:
                continue

        logger.warning(
            "Encoding detection failed, using utf-8 with replacement",
            extra={"path": str(self.path)},
        )
        return "utf-8"

    # -----------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------

    def read(self) -> Iterator[Union[str, Dict[str, Any]]]:
        """
        Entry point unico.
        Ritorna:
        - str per TEXT
        - dict per CSV / JSON / JSONL
        """
        if self.format == LogFormat.TEXT:
            yield from self._read_text()
        elif self.format == LogFormat.CSV:
            yield from self._read_csv()
        elif self.format == LogFormat.JSON:
            yield from self._read_json()
        elif self.format == LogFormat.JSONL:
            yield from self._read_jsonl()
        else:
            raise ParseError(f"Unsupported file format: {self.path.suffix}")

    # -----------------------------------------------------------------
    # TEXT
    # -----------------------------------------------------------------

    def _read_text(self) -> Iterator[str]:
        try:
            with self.path.open(
                "r", encoding=self.encoding, errors="replace"
            ) as f:
                for line_no, line in enumerate(f, 1):
                    text = line.rstrip()
                    if not text:
                        self.stats["records_skipped"] += 1
                        continue

                    self.stats["records_read"] += 1
                    yield text

        except Exception as exc:
            raise ParseError(
                f"Failed to read text file: {self.path}"
            ) from exc

    # -----------------------------------------------------------------
    # CSV
    # -----------------------------------------------------------------

    def _read_csv(self) -> Iterator[Dict[str, Any]]:
        try:
            with self.path.open(
                "r", encoding=self.encoding, newline="", errors="replace"
            ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.stats["records_read"] += 1
                    yield dict(row)

        except Exception as exc:
            raise ParseError(
                f"Failed to read CSV file: {self.path}"
            ) from exc

    # -----------------------------------------------------------------
    # JSON
    # -----------------------------------------------------------------

    def _read_json(self) -> Iterator[Dict[str, Any]]:
        try:
            with self.path.open(
                "r", encoding=self.encoding, errors="replace"
            ) as f:
                data = json.load(f)

            if isinstance(data, list):
                for item in data:
                    self.stats["records_read"] += 1
                    yield item
            else:
                self.stats["records_read"] += 1
                yield data

        except json.JSONDecodeError:
            logger.info(
                "JSON decode failed, falling back to JSONL",
                extra={"path": str(self.path)},
            )
            yield from self._read_jsonl()

        except Exception as exc:
            raise ParseError(
                f"Failed to read JSON file: {self.path}"
            ) from exc

    # -----------------------------------------------------------------
    # JSONL
    # -----------------------------------------------------------------

    def _read_jsonl(self) -> Iterator[Dict[str, Any]]:
        try:
            with self.path.open(
                "r", encoding=self.encoding, errors="replace"
            ) as f:
                for line_no, line in enumerate(f, 1):
                    raw = line.strip()
                    if not raw:
                        self.stats["records_skipped"] += 1
                        continue

                    try:
                        data = json.loads(raw)
                        self.stats["records_read"] += 1
                        yield data
                    except json.JSONDecodeError:
                        self.stats["decode_errors"] += 1
                        self.stats["records_skipped"] += 1
                        logger.debug(
                            "JSONL parse error",
                            extra={"line": line_no, "path": str(self.path)},
                        )

        except Exception as exc:
            raise ParseError(
                f"Failed to read JSONL file: {self.path}"
            ) from exc

    # -----------------------------------------------------------------
    # STATS
    # -----------------------------------------------------------------

    def get_stats(self) -> Dict[str, int]:
        return dict(self.stats)

    def reset_stats(self) -> None:
        for k in self.stats:
            self.stats[k] = 0
