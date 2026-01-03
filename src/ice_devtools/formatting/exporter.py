# ice_devtools/formatting/exporter.py

import csv
import json
import html
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class TableExporter:
    """
    Esporta dati tabellari (list[dict]) in formati standard.
    """

    SUPPORTED_FORMATS = {"csv", "json", "html", "md", "txt"}

    def __init__(self, rows: List[Dict[str, Any]]):
        self.rows = rows

    def export(self, path: str | Path, fmt: str = "json") -> None:
        fmt = fmt.lower()
        if fmt not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Formato non supportato: {fmt}")

        path = Path(path)

        if fmt == "json":
            self._json(path)
        elif fmt == "csv":
            self._csv(path)
        elif fmt == "html":
            self._html(path)
        elif fmt == "md":
            self._markdown(path)
        elif fmt == "txt":
            self._txt(path)

    def _json(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.rows, f, indent=2, ensure_ascii=False)

    def _csv(self, path: Path) -> None:
        if not self.rows:
            return
        keys = self.rows[0].keys()
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.rows)

    def _html(self, path: Path) -> None:
        if not self.rows:
            return
        keys = self.rows[0].keys()

        rows_html = "\n".join(
            "<tr>" + "".join(f"<td>{html.escape(str(row.get(k,'')))}</td>" for k in keys) + "</tr>"
            for row in self.rows
        )

        html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Export {datetime.now().isoformat()}</title>
<style>
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid #444; padding: 6px; }}
</style>
</head>
<body>
<table>
<thead>
<tr>{"".join(f"<th>{html.escape(str(k))}</th>" for k in keys)}</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</body>
</html>
"""
        path.write_text(html_doc, encoding="utf-8")

    def _markdown(self, path: Path) -> None:
        if not self.rows:
            return
        keys = list(self.rows[0].keys())
        lines = [
            "| " + " | ".join(keys) + " |",
            "| " + " | ".join(["---"] * len(keys)) + " |",
        ]
        for row in self.rows:
            lines.append("| " + " | ".join(str(row.get(k, "")) for k in keys) + " |")
        path.write_text("\n".join(lines), encoding="utf-8")

    def _txt(self, path: Path) -> None:
        if not self.rows:
            return
        keys = list(self.rows[0].keys())
        lines = ["\t".join(keys)]
        for row in self.rows:
            lines.append("\t".join(str(row.get(k, "")) for k in keys))
        path.write_text("\n".join(lines), encoding="utf-8")
