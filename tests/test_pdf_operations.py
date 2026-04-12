from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from pdf_app.pdf_ops.pdf_operation_service import PdfOperationService


def _make_pdf(path: Path, pages: int) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
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
