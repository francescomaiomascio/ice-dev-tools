from __future__ import annotations

"""
Custom exceptions for ICE DevTools.

Scope:
- Parsing
- Detection
- Validation
- Tooling & developer utilities

⚠️ IMPORTANT:
- This module is ML-agnostic.
- Errors related to ML / AI / inference belong to ICE-AI.
"""


# ======================================================================
# BASE
# ======================================================================

class DevToolsError(Exception):
    """
    Base exception for all ICE DevTools errors.
    """
    pass


# ======================================================================
# PARSING
# ======================================================================

class ParsingError(DevToolsError):
    """
    Raised when a parsing operation fails.
    """

    def __init__(
        self,
        message: str,
        *,
        line: str | None = None,
        line_number: int | None = None,
        source: str | None = None,
    ) -> None:
        self.line = line
        self.line_number = line_number
        self.source = source
        super().__init__(message)


# ======================================================================
# DETECTION / PATTERN MATCHING
# ======================================================================

class DetectionError(DevToolsError):
    """
    Raised when detection or pattern matching fails.
    """
    pass


# ======================================================================
# VALIDATION
# ======================================================================

class ValidationError(DevToolsError):
    """
    Raised when validation of data or configuration fails.
    """
    pass


# ======================================================================
# CONFIGURATION
# ======================================================================

class ConfigurationError(DevToolsError):
    """
    Raised when configuration is missing, invalid, or inconsistent.
    """
    pass


# ======================================================================
# PLUGINS / EXTENSIONS
# ======================================================================

class PluginError(DevToolsError):
    """
    Raised when a plugin fails to load, initialize, or execute.
    """
    pass


# ======================================================================
# STORAGE / IO
# ======================================================================

class StorageError(DevToolsError):
    """
    Raised on storage or persistence errors (filesystem, cache, export).
    """
    pass


class ResourceError(DevToolsError):
    """
    Raised when required resources are unavailable.

    Examples:
    - missing files
    - permission errors
    - memory constraints
    """
    pass


# ======================================================================
# EXECUTION
# ======================================================================

class TimeoutError(DevToolsError):
    """
    Raised when an operation exceeds its allowed execution time.
    """
    pass
