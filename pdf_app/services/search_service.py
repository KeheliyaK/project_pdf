from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from pdf_app.search.engine import SearchEngine
from pdf_app.search.models import SearchResult


class SearchService(QObject):
    results_updated = Signal(list)
    active_result_changed = Signal(object, int, int)

    def __init__(self) -> None:
        super().__init__()
        self.engine = SearchEngine()
        self.results: list[SearchResult] = []
        self.query = ""
        self.active_index = -1

    def search(self, pdf_path: Path | None, query: str) -> list[SearchResult]:
        self.query = query.strip()
        self.results = self.engine.search(pdf_path, self.query) if pdf_path and self.query else []
        self.active_index = 0 if self.results else -1
        self.results_updated.emit(self.results)
        if self.results:
            self._emit_active()
        return self.results

    def next_result(self) -> None:
        if not self.results:
            return
        if self.active_index < 0:
            self.active_index = 0
        else:
            self.active_index = (self.active_index + 1) % len(self.results)
        self._emit_active()

    def previous_result(self) -> None:
        if not self.results:
            return
        if self.active_index < 0:
            self.active_index = len(self.results) - 1
        else:
            self.active_index = (self.active_index - 1) % len(self.results)
        self._emit_active()

    def activate_index(self, index: int) -> None:
        if 0 <= index < len(self.results):
            self.active_index = index
            self._emit_active()

    def sync_to_page(self, page_index: int) -> bool:
        if not self.results:
            return False

        if 0 <= self.active_index < len(self.results):
            active_result = self.results[self.active_index]
            if active_result.page_index == page_index:
                return False

        matching_indexes = [
            idx for idx, result in enumerate(self.results) if result.page_index == page_index
        ]
        if not matching_indexes:
            return False

        start_index = max(self.active_index, 0)
        synced_index = next((idx for idx in matching_indexes if idx >= start_index), matching_indexes[0])
        if synced_index == self.active_index:
            return False

        self.active_index = synced_index
        return True

    def clear(self) -> None:
        self.query = ""
        self.results = []
        self.active_index = -1
        self.results_updated.emit([])

    def active_result_state(self) -> tuple[SearchResult, int, int] | None:
        if 0 <= self.active_index < len(self.results):
            return self.results[self.active_index], self.active_index + 1, len(self.results)
        return None

    def _emit_active(self) -> None:
        active_state = self.active_result_state()
        if active_state is not None:
            result, index, total = active_state
            self.active_result_changed.emit(result, index, total)
