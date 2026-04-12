from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from pypdf import PdfReader
from PySide6.QtCore import QObject, Signal

from pdf_app.services.pdf_access_service import PdfAccessService
from pdf_app.services.recent_files_service import RecentFilesService
from pdf_app.state.document_state import DocumentState


class DocumentManager(QObject):
    document_changed = Signal()
    dirty_changed = Signal(bool)

    def __init__(
        self,
        pdf_access_service: PdfAccessService | None = None,
        recent_files_service: RecentFilesService | None = None,
    ) -> None:
        super().__init__()
        self.state = DocumentState()
        self._temp_dir = Path(tempfile.mkdtemp(prefix="pdf-app-mvp-"))
        self._pdf_access_service = pdf_access_service or PdfAccessService()
        self._recent_files_service = recent_files_service or RecentFilesService()
        self.state.recent_files = self._recent_files_service.load()

    def open_document(self, path: str | Path, password: str | None = None) -> DocumentState:
        source = Path(path)
        working_path = self._temp_dir / source.name
        prepared = self._pdf_access_service.prepare_pdf(source, destination_path=working_path, password=password)
        self.state.original_path = source
        self.state.working_path = working_path
        self.state.page_count = prepared.page_count
        self.state.current_page = 0
        self.state.zoom_percent = 100
        self._add_recent(source)
        self.set_dirty(False)
        self.document_changed.emit()
        return self.state

    def refresh_page_count(self) -> int:
        if not self.state.working_path:
            self.state.page_count = 0
            self.state.current_page = 0
            return 0
        self.state.page_count = len(PdfReader(str(self.state.working_path)).pages)
        self.state.current_page = min(self.state.current_page, max(self.state.page_count - 1, 0))
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
        self.state.recent_files = self._recent_files_service.add(path)

    def remove_recent(self, path: str | Path) -> list[Path]:
        self.state.recent_files = self._recent_files_service.remove(Path(path))
        self.document_changed.emit()
        return self.state.recent_files

    def recent_file_status(self, path: str | Path) -> str:
        return self._recent_files_service.status_for(Path(path))
