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
        self.active_index = (self.active_index + 1) % len(self.results)
        self._emit_active()

    def previous_result(self) -> None:
        if not self.results:
            return
        self.active_index = (self.active_index - 1) % len(self.results)
        self._emit_active()

    def activate_index(self, index: int) -> None:
        if 0 <= index < len(self.results):
            self.active_index = index
            self._emit_active()

    def sync_to_page(self, page_index: int) -> None:
        for idx, result in enumerate(self.results):
            if result.page_index == page_index:
                self.active_index = idx
                self._emit_active()
                break

    def clear(self) -> None:
        self.query = ""
        self.results = []
        self.active_index = -1
        self.results_updated.emit([])

    def _emit_active(self) -> None:
        if 0 <= self.active_index < len(self.results):
            result = self.results[self.active_index]
            self.active_result_changed.emit(result, self.active_index + 1, len(self.results))
