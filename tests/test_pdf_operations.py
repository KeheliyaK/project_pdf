from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from pdf_app.annotations.models import AnnotationRect, AnnotationStyle, AnnotationType
from pdf_app.pdf_ops.pdf_operation_service import PdfOperationService
from pdf_app.services.annotation_service import AnnotationService
from pdf_app.services.document_manager import DocumentManager
from pdf_app.services.operation_history import OperationHistoryService
from pdf_app.services.pdf_access_service import (
    PdfAccessService,
    PdfInvalidPasswordError,
    PdfPasswordRequiredError,
)
from pdf_app.services.recent_files_service import RecentFilesService
from pdf_app.services.search_service import SearchService
from pdf_app.services.unified_history_service import UnifiedHistoryService
from pdf_app.ui.edit_mode_ui import EditorWorkspace


class _StubRenderService:
    def render_editor_thumbnail(self, pdf_path: Path, page_index: int, width: int = 120) -> QPixmap:
        pixmap = QPixmap(width, int(width * 1.4))
        pixmap.fill()
        return pixmap


@pytest.fixture(scope="module", autouse=True)
def _qt_app():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    return app


def _make_pdf(path: Path, pages: int) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with path.open("wb") as handle:
        writer.write(handle)


def _make_encrypted_pdf(path: Path, pages: int, password: str) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    writer.encrypt(password)
    with path.open("wb") as handle:
        writer.write(handle)


def test_delete_pages(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    output = tmp_path / "output.pdf"
    _make_pdf(source, 4)

    PdfOperationService().delete_pages(source, [1, 3], output)

    assert len(PdfReader(str(output)).pages) == 2


def test_extract_pages(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    output = tmp_path / "extract.pdf"
    _make_pdf(source, 5)

    PdfOperationService().extract_pages(source, [0, 2, 4], output)

    assert len(PdfReader(str(output)).pages) == 3


def test_merge_pdfs(tmp_path: Path) -> None:
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    output = tmp_path / "merged.pdf"
    _make_pdf(first, 2)
    _make_pdf(second, 3)

    PdfOperationService().merge_pdfs([first, second], output)

    assert len(PdfReader(str(output)).pages) == 5


def test_reorder_pages(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    output = tmp_path / "reordered.pdf"
    _make_pdf(source, 4)

    PdfOperationService().reorder_pages(source, [2, 0, 3, 1], output)

    assert len(PdfReader(str(output)).pages) == 4


def test_reorder_pages_rejects_invalid_order(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    output = tmp_path / "reordered.pdf"
    _make_pdf(source, 4)

    with pytest.raises(ValueError):
        PdfOperationService().reorder_pages(source, [2, 0, 2, 1], output)


def test_refresh_page_count_clamps_current_page_after_delete(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    updated = tmp_path / "updated.pdf"
    storage_path = tmp_path / "recent_files.json"
    _make_pdf(source, 4)

    manager = DocumentManager(recent_files_service=RecentFilesService(storage_path=storage_path))
    manager.open_document(source)
    manager.set_current_page(3)

    PdfOperationService().delete_pages(manager.working_path(), [3], updated)
    updated.replace(manager.working_path())

    assert manager.refresh_page_count() == 3
    assert manager.state.current_page == 2


def test_discard_last_undo_snapshot_removes_failed_history_entry(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    _make_pdf(source, 2)

    history = OperationHistoryService()
    history.push_undo_snapshot(source, "Delete selected pages")
    history.discard_last_undo_snapshot()

    assert history.can_undo() is False


def test_prepare_pdf_requires_password(tmp_path: Path) -> None:
    source = tmp_path / "protected.pdf"
    _make_encrypted_pdf(source, 2, "secret")

    with pytest.raises(PdfPasswordRequiredError):
        PdfAccessService().prepare_pdf(source)


def test_prepare_pdf_rejects_incorrect_password(tmp_path: Path) -> None:
    source = tmp_path / "protected.pdf"
    _make_encrypted_pdf(source, 2, "secret")

    with pytest.raises(PdfInvalidPasswordError):
        PdfAccessService().prepare_pdf(source, password="wrong")


def test_prepare_pdf_unlocks_password_protected_pdf(tmp_path: Path) -> None:
    source = tmp_path / "protected.pdf"
    _make_encrypted_pdf(source, 2, "secret")

    prepared = PdfAccessService().prepare_pdf(source, password="secret")
    unlocked_reader = PdfReader(str(prepared.prepared_path))

    assert prepared.page_count == 2
    assert prepared.was_password_protected is True
    assert unlocked_reader.is_encrypted is False
    assert len(unlocked_reader.pages) == 2


def test_recent_files_service_persists_and_deduplicates(tmp_path: Path) -> None:
    storage_path = tmp_path / "recent_files.json"
    service = RecentFilesService(storage_path=storage_path, max_items=3)
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    third = tmp_path / "third.pdf"
    fourth = tmp_path / "fourth.pdf"

    service.add(first)
    service.add(second)
    service.add(first)
    service.add(third)
    paths = service.add(fourth)

    assert paths == [fourth.resolve(), third.resolve(), first.resolve()]
    assert service.load() == [fourth.resolve(), third.resolve(), first.resolve()]


def test_recent_files_service_remove_and_status(tmp_path: Path) -> None:
    storage_path = tmp_path / "recent_files.json"
    service = RecentFilesService(storage_path=storage_path)
    existing = tmp_path / "existing.pdf"
    missing = tmp_path / "missing.pdf"
    _make_pdf(existing, 1)
    service.add(existing)
    service.add(missing)

    assert service.status_for(existing) == "available"
    assert service.status_for(missing) == "missing"

    remaining = service.remove(missing)
    assert remaining == [existing.resolve()]


def test_search_service_ignores_blank_query() -> None:
    service = SearchService()

    assert service.search(None, "   ") == []
    assert service.query == ""
    assert service.active_index == -1


def test_annotation_service_add_update_delete_and_query() -> None:
    service = AnnotationService()
    service.open_document(Path("/tmp/test-working.pdf"))

    annotation = service.add_annotation(
        AnnotationType.HIGHLIGHT,
        page_index=1,
        rect=AnnotationRect(x=10, y=12, width=100, height=18),
    )
    updated = service.update_annotation(
        annotation.id,
        annotation_type=AnnotationType.TEXT_BOX,
        text_content="Hello",
        style=AnnotationStyle(color="#f97316", opacity=1.0, stroke_width=1.0),
    )

    page_annotations = service.annotations_for_page(1)

    assert len(page_annotations) == 1
    assert page_annotations[0].id == annotation.id
    assert updated.annotation_type == AnnotationType.TEXT_BOX
    assert updated.text_content == "Hello"

    service.delete_annotation(annotation.id)

    assert service.annotations_for_page(1) == []
    assert service.all_annotations() == []


def test_annotation_service_resets_on_different_document() -> None:
    service = AnnotationService()
    service.open_document(Path("/tmp/first-working.pdf"))
    service.add_annotation(
        AnnotationType.UNDERLINE,
        page_index=0,
        rect=AnnotationRect(x=5, y=25, width=80, height=4),
    )

    service.open_document(Path("/tmp/second-working.pdf"))

    assert service.all_annotations() == []


def test_annotation_service_can_force_reset_same_document_key() -> None:
    service = AnnotationService()
    working_path = Path("/tmp/shared-working.pdf")
    service.open_document(working_path)
    service.add_annotation(
        AnnotationType.HIGHLIGHT,
        page_index=0,
        rect=AnnotationRect(x=0, y=0, width=10, height=10),
    )

    service.open_document(working_path, force_reset=True)

    assert service.all_annotations() == []


def test_annotation_service_undo_and_redo_creation() -> None:
    service = AnnotationService()
    service.open_document(Path("/tmp/annotated-working.pdf"))

    created = service.add_annotation(
        AnnotationType.HIGHLIGHT,
        page_index=0,
        rect=AnnotationRect(x=10, y=10, width=40, height=12),
    )

    assert service.can_undo() is True
    assert service.can_redo() is False
    assert service.all_annotations()[0].id == created.id

    service.undo()

    assert service.all_annotations() == []
    assert service.can_redo() is True

    service.redo()

    assert len(service.all_annotations()) == 1
    assert service.all_annotations()[0].id == created.id


def test_annotation_service_clear_document_annotations_is_undoable() -> None:
    service = AnnotationService()
    service.open_document(Path("/tmp/annotated-working.pdf"))
    created = service.add_annotation(
        AnnotationType.UNDERLINE,
        page_index=1,
        rect=AnnotationRect(x=8, y=20, width=80, height=3),
    )

    cleared = service.clear_document_annotations()

    assert cleared is True
    assert service.all_annotations() == []

    service.undo()

    restored = service.all_annotations()
    assert len(restored) == 1
    assert restored[0].id == created.id


def test_annotation_service_clear_annotations_by_type_targets_visible_tools_only() -> None:
    service = AnnotationService()
    service.open_document(Path("/tmp/annotated-working.pdf"))
    highlight = service.add_annotation(
        AnnotationType.HIGHLIGHT,
        page_index=0,
        rect=AnnotationRect(x=10, y=10, width=40, height=12),
    )
    text_box = service.add_annotation(
        AnnotationType.TEXT_BOX,
        page_index=0,
        rect=AnnotationRect(x=30, y=30, width=80, height=40),
        text_content="Internal note",
    )

    cleared_count = service.clear_annotations_by_type({AnnotationType.HIGHLIGHT, AnnotationType.UNDERLINE})

    assert cleared_count == 1
    remaining = service.all_annotations()
    assert len(remaining) == 1
    assert remaining[0].id == text_box.id
    assert remaining[0].id != highlight.id


def test_annotation_service_delete_annotations_returns_deleted_count() -> None:
    service = AnnotationService()
    service.open_document(Path("/tmp/annotated-working.pdf"))
    first = service.add_annotation(
        AnnotationType.HIGHLIGHT,
        page_index=0,
        rect=AnnotationRect(x=10, y=10, width=40, height=12),
    )
    second = service.add_annotation(
        AnnotationType.UNDERLINE,
        page_index=1,
        rect=AnnotationRect(x=8, y=20, width=80, height=3),
    )

    deleted_count = service.delete_annotations([first.id, second.id, "missing"])

    assert deleted_count == 2
    assert service.all_annotations() == []


def test_unified_history_service_tracks_cross_domain_action_order() -> None:
    service = UnifiedHistoryService()

    service.record_action("structural", "Delete selected pages")
    service.record_action("annotation", "Add highlight")

    next_undo = service.consume_undo()

    assert next_undo is not None
    assert next_undo.domain == "annotation"
    assert next_undo.description == "Add highlight"

    service.push_redo(next_undo)
    next_redo = service.consume_redo()

    assert next_redo is not None
    assert next_redo.domain == "annotation"


def test_unified_history_service_clears_redo_on_new_action() -> None:
    service = UnifiedHistoryService()

    service.record_action("annotation", "Add underline")
    undone = service.consume_undo()
    assert undone is not None
    service.push_redo(undone)

    service.record_action("structural", "Rotate 90 degrees")

    assert service.can_redo() is False


def test_editor_checkbox_select_updates_shared_selection_state(tmp_path: Path) -> None:
    workspace = EditorWorkspace(_StubRenderService())
    workspace.load_document(tmp_path / "source.pdf", 5)

    first = workspace.grid.item(0)
    first.setCheckState(Qt.CheckState.Checked)

    assert workspace.selected_pages() == [0]
    assert first.checkState() == Qt.CheckState.Checked
    assert first.isSelected() is True
    assert workspace.mini_toolbar.selection_label.text() == "1 pages selected"


def test_editor_checkbox_multi_select_preserves_prior_selection(tmp_path: Path) -> None:
    workspace = EditorWorkspace(_StubRenderService())
    workspace.load_document(tmp_path / "source.pdf", 5)

    first = workspace.grid.item(0)
    third = workspace.grid.item(2)
    first.setCheckState(Qt.CheckState.Checked)
    third.setCheckState(Qt.CheckState.Checked)

    assert workspace.selected_pages() == [0, 2]
    assert first.checkState() == Qt.CheckState.Checked
    assert third.checkState() == Qt.CheckState.Checked
    assert first.isSelected() is True
    assert third.isSelected() is True
    assert workspace.mini_toolbar.selection_label.text() == "2 pages selected"


def test_editor_checkbox_deselect_removes_only_target_page(tmp_path: Path) -> None:
    workspace = EditorWorkspace(_StubRenderService())
    workspace.load_document(tmp_path / "source.pdf", 5)

    first = workspace.grid.item(0)
    third = workspace.grid.item(2)
    first.setCheckState(Qt.CheckState.Checked)
    third.setCheckState(Qt.CheckState.Checked)
    first.setCheckState(Qt.CheckState.Unchecked)

    assert workspace.selected_pages() == [2]
    assert first.checkState() == Qt.CheckState.Unchecked
    assert first.isSelected() is False
    assert third.checkState() == Qt.CheckState.Checked
    assert third.isSelected() is True
    assert workspace.mini_toolbar.selection_label.text() == "1 pages selected"


def test_editor_mixed_checkbox_and_highlight_selection_stays_synchronized(tmp_path: Path) -> None:
    workspace = EditorWorkspace(_StubRenderService())
    workspace.load_document(tmp_path / "source.pdf", 5)

    first = workspace.grid.item(0)
    third = workspace.grid.item(2)
    fourth = workspace.grid.item(3)
    first.setCheckState(Qt.CheckState.Checked)
    third.setCheckState(Qt.CheckState.Checked)
    fourth.setSelected(True)

    assert workspace.selected_pages() == [0, 2, 3]
    assert first.checkState() == Qt.CheckState.Checked
    assert third.checkState() == Qt.CheckState.Checked
    assert fourth.checkState() == Qt.CheckState.Checked
    assert workspace.mini_toolbar.selection_label.text() == "3 pages selected"


def test_editor_selected_page_operations_target_checkbox_selected_pages(tmp_path: Path) -> None:
    workspace = EditorWorkspace(_StubRenderService())
    workspace.load_document(tmp_path / "source.pdf", 5)

    workspace.grid.item(0).setCheckState(Qt.CheckState.Checked)
    workspace.grid.item(2).setCheckState(Qt.CheckState.Checked)

    assert workspace.selected_pages() == [0, 2]
