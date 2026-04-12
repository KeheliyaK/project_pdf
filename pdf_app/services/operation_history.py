from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HistoryEntry:
    snapshot_path: Path
    description: str


class OperationHistoryService:
    def __init__(self) -> None:
        self._undo_stack: list[HistoryEntry] = []
        self._redo_stack: list[HistoryEntry] = []
        self._temp_dir = Path(tempfile.mkdtemp(prefix="pdf-app-history-"))

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def push_undo_snapshot(self, source_path: Path, description: str) -> None:
        snapshot_path = self._copy_snapshot(source_path)
        self._undo_stack.append(HistoryEntry(snapshot_path=snapshot_path, description=description))
        self._redo_stack.clear()

    def undo(self, working_path: Path) -> str | None:
        if not self._undo_stack:
            return None
        current_snapshot = self._copy_snapshot(working_path)
        previous = self._undo_stack.pop()
        shutil.copy2(previous.snapshot_path, working_path)
        self._redo_stack.append(HistoryEntry(snapshot_path=current_snapshot, description=previous.description))
        return previous.description

    def redo(self, working_path: Path) -> str | None:
        if not self._redo_stack:
            return None
        current_snapshot = self._copy_snapshot(working_path)
        upcoming = self._redo_stack.pop()
        shutil.copy2(upcoming.snapshot_path, working_path)
        self._undo_stack.append(HistoryEntry(snapshot_path=current_snapshot, description=upcoming.description))
        return upcoming.description

    def _copy_snapshot(self, source_path: Path) -> Path:
        fd, temp_name = tempfile.mkstemp(suffix=".pdf", dir=self._temp_dir)
        os.close(fd)
        Path(temp_name).unlink(missing_ok=True)
        snapshot_path = Path(temp_name)
        shutil.copy2(source_path, snapshot_path)
        return snapshot_path
