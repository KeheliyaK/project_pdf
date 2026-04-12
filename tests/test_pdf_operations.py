from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from pdf_app.pdf_ops.pdf_operation_service import PdfOperationService
from pdf_app.services.document_manager import DocumentManager
from pdf_app.services.operation_history import OperationHistoryService
from pdf_app.services.pdf_access_service import (
    PdfAccessService,
    PdfInvalidPasswordError,
    PdfPasswordRequiredError,
)
from pdf_app.services.recent_files_service import RecentFilesService
from pdf_app.services.search_service import SearchService


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
