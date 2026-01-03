# ice_devtools/formatting/color.py

from typing import Any

try:
    from rich.console import Console
    _console = Console()
    _enabled = True
except Exception:
    _console = None
    _enabled = False


def info(msg: Any) -> None:
    if _enabled:
        _console.print(f"[cyan]{msg}[/cyan]")
    else:
        print(msg)


def warn(msg: Any) -> None:
    if _enabled:
        _console.print(f"[yellow]{msg}[/yellow]")
    else:
        print(msg)


def error(msg: Any) -> None:
    if _enabled:
        _console.print(f"[red]{msg}[/red]")
    else:
        print(msg)
