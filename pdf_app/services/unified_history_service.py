from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnifiedHistoryEntry:
    domain: str
    description: str


class UnifiedHistoryService:
    def __init__(self) -> None:
        self._undo_stack: list[UnifiedHistoryEntry] = []
        self._redo_stack: list[UnifiedHistoryEntry] = []

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

    def record_action(self, domain: str, description: str) -> None:
        self._undo_stack.append(UnifiedHistoryEntry(domain=domain, description=description))
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def next_undo(self) -> UnifiedHistoryEntry | None:
        if not self._undo_stack:
            return None
        return self._undo_stack[-1]

    def next_redo(self) -> UnifiedHistoryEntry | None:
        if not self._redo_stack:
            return None
        return self._redo_stack[-1]

    def consume_undo(self) -> UnifiedHistoryEntry | None:
        if not self._undo_stack:
            return None
        return self._undo_stack.pop()

    def push_redo(self, entry: UnifiedHistoryEntry) -> None:
        self._redo_stack.append(entry)

    def consume_redo(self) -> UnifiedHistoryEntry | None:
        if not self._redo_stack:
            return None
        return self._redo_stack.pop()

    def push_undo(self, entry: UnifiedHistoryEntry) -> None:
        self._undo_stack.append(entry)
