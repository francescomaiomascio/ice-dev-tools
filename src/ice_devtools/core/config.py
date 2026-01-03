from __future__ import annotations

"""
Global configuration for ICE DevTools.

Scope:
- Parsing
- Detection
- Tooling behavior
- Local workspace & cache

⚠️ IMPORTANT:
- NO ML / AI / embeddings configuration here.
- ML-related config belongs to ICE-AI or Runtime.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import yaml


# ======================================================================
# DETECTION
# ======================================================================

@dataclass
class DetectionConfig:
    """
    Detection configuration (patterns, heuristics, rules).
    """
    enabled: bool = True
    min_confidence: float = 0.3
    max_patterns: int = 1000
    enable_multiline: bool = True
    multiline_timeout: float = 2.0


# ======================================================================
# PARSING
# ======================================================================

@dataclass
class ParsingConfig:
    """
    Parsing configuration.
    """
    encoding: str = "utf-8"
    buffer_size: int = 8192
    max_line_length: int = 10_000
    timeout: float = 30.0
    chunk_size: int = 1_000


# ======================================================================
# GLOBAL CONFIG
# ======================================================================

@dataclass
class DevToolsConfig:
    """
    Global DevTools configuration.
    """

    # Core subsystems
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    parsing: ParsingConfig = field(default_factory=ParsingConfig)

    # Workspace
    workspace_dir: Path = field(
        default_factory=lambda: Path.home() / ".ice_devtools"
    )
    cache_dir: Path = field(init=False)
    plugins_dir: Path = field(init=False)

    # Performance / behavior
    max_concurrent_tasks: int = 5
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600

    def __post_init__(self) -> None:
        """
        Initialize derived paths and ensure directories exist.
        """
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.cache_dir = self.workspace_dir / "cache"
        self.plugins_dir = self.workspace_dir / "plugins"

        self.cache_dir.mkdir(exist_ok=True)
        self.plugins_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # LOADERS
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(cls, path: Path) -> DevToolsConfig:
        if not path.exists():
            return cls()

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DevToolsConfig:
        cfg = cls()

        if "detection" in data:
            cfg.detection = DetectionConfig(**data["detection"])

        if "parsing" in data:
            cfg.parsing = ParsingConfig(**data["parsing"])

        if "workspace_dir" in data:
            cfg.workspace_dir = Path(data["workspace_dir"])

        cfg.max_concurrent_tasks = data.get(
            "max_concurrent_tasks",
            cfg.max_concurrent_tasks,
        )
        cfg.enable_cache = data.get("enable_cache", cfg.enable_cache)
        cfg.cache_ttl_seconds = data.get(
            "cache_ttl_seconds",
            cfg.cache_ttl_seconds,
        )

        cfg.__post_init__()
        return cfg

    # ------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection": vars(self.detection),
            "parsing": vars(self.parsing),
            "workspace_dir": str(self.workspace_dir),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "enable_cache": self.enable_cache,
            "cache_ttl_seconds": self.cache_ttl_seconds,
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(self.to_dict(), f, indent=2)


# ----------------------------------------------------------------------
# DEFAULT INSTANCE
# ----------------------------------------------------------------------

default_config = DevToolsConfig()
