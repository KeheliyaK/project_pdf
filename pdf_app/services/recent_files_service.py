from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths


class RecentFilesService:
    def __init__(self, storage_path: Path | None = None, max_items: int = 8) -> None:
        self._storage_path = storage_path or self._default_storage_path()
        self._max_items = max_items

    def load(self) -> list[Path]:
        if not self._storage_path.exists():
            return []
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(payload, list):
            return []

        recent_paths: list[Path] = []
        for raw_path in payload:
            if not isinstance(raw_path, str):
                continue
            path = self._normalize(Path(raw_path))
            if path not in recent_paths:
                recent_paths.append(path)
        return recent_paths[: self._max_items]

    def add(self, path: Path) -> list[Path]:
        normalized = self._normalize(path)
        recent_paths = [item for item in self.load() if item != normalized]
        recent_paths.insert(0, normalized)
        recent_paths = recent_paths[: self._max_items]
        self._write(recent_paths)
        return recent_paths

    def remove(self, path: Path) -> list[Path]:
        normalized = self._normalize(path)
        recent_paths = [item for item in self.load() if item != normalized]
        self._write(recent_paths)
        return recent_paths

    def status_for(self, path: Path) -> str:
        try:
            if not path.exists():
                return "missing"
            if not path.is_file():
                return "unavailable"
            if not path.suffix.lower() == ".pdf":
                return "unavailable"
            with path.open("rb"):
                pass
        except OSError:
            return "unavailable"
        return "available"

    @staticmethod
    def _normalize(path: Path) -> Path:
        return path.expanduser().resolve(strict=False)

    def _write(self, paths: list[Path]) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [str(path) for path in paths]
        self._storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _default_storage_path() -> Path:
        config_root = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
        base_dir = Path(config_root) if config_root else Path.home() / ".pdf-app-mvp"
        return base_dir / "recent_files.json"
