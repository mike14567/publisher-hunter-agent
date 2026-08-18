"""Tracks which domains have already been reported, so daily emails only show new leads."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path


class SeenStore:
    def __init__(self, path: Path):
        self.path = path
        self._data: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {}

    def is_new(self, domain: str) -> bool:
        return domain not in self._data

    def mark_seen(self, domain: str) -> None:
        self._data[domain] = date.today().isoformat()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True))
