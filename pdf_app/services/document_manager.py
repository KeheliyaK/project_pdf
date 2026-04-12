from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import fitz
from PySide6.QtCore import QObject, Signal

from pdf_app.state.document_state import DocumentState


class DocumentManager(QObject):
    document_changed = Signal()
    dirty_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.state = DocumentState()
        self._temp_dir = Path(tempfile.mkdtemp(prefix="pdf-app-mvp-"))

    def open_document(self, path: str | Path) -> DocumentState:
        source = Path(path)
        working_path = self._temp_dir / source.name
        shutil.copy2(source, working_path)
        document = fitz.open(working_path)
        page_count = document.page_count
        document.close()
        self.state.original_path = source
        self.state.working_path = working_path
        self.state.page_count = page_count
        self.state.current_page = 0
        self.state.zoom_percent = 100
        self._add_recent(source)
        self.set_dirty(False)
        self.document_changed.emit()
        return self.state

    def refresh_page_count(self) -> int:
        if not self.state.working_path:
            self.state.page_count = 0
            return 0
        document = fitz.open(self.state.working_path)
        self.state.page_count = document.page_count
        document.close()
        self.document_changed.emit()
        return self.state.page_count

    def set_current_page(self, page_index: int) -> None:
        self.state.current_page = max(0, page_index)
        self.document_changed.emit()

    def set_zoom_percent(self, zoom_percent: int) -> None:
        self.state.zoom_percent = zoom_percent
        self.document_changed.emit()

    def set_dirty(self, is_dirty: bool) -> None:
        self.state.is_dirty = is_dirty
        self.dirty_changed.emit(is_dirty)

    def save_as(self, output_path: str | Path) -> None:
        if not self.state.working_path:
            raise ValueError("No working document to save.")
        shutil.copy2(self.state.working_path, output_path)
        self.set_dirty(False)

    def working_path(self) -> Path:
        if not self.state.working_path:
            raise ValueError("No document is open.")
        return self.state.working_path

    def _add_recent(self, path: Path) -> None:
        recents = [item for item in self.state.recent_files if item != path]
        recents.insert(0, path)
        self.state.recent_files = recents[:8]
