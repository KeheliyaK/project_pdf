from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


class PdfOperationService:
    def reorder_pages(self, input_path: Path, order: list[int], output_path: Path) -> None:
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for page_index in order:
            writer.add_page(reader.pages[page_index])
        self._write(writer, output_path)

    def delete_pages(self, input_path: Path, page_indices: list[int], output_path: Path) -> None:
        to_remove = set(page_indices)
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for idx, page in enumerate(reader.pages):
            if idx not in to_remove:
                writer.add_page(page)
        self._write(writer, output_path)

    def rotate_pages(self, input_path: Path, page_indices: list[int], output_path: Path, degrees: int) -> None:
        target = set(page_indices)
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for idx, page in enumerate(reader.pages):
            if idx in target:
                page.rotate(degrees)
            writer.add_page(page)
        self._write(writer, output_path)

    def rotate_all_pages(self, input_path: Path, output_path: Path, degrees: int) -> None:
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for page in reader.pages:
            page.rotate(degrees)
            writer.add_page(page)
        self._write(writer, output_path)

    def extract_pages(self, input_path: Path, page_indices: list[int], output_path: Path) -> None:
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for page_index in sorted(page_indices):
            writer.add_page(reader.pages[page_index])
        self._write(writer, output_path)

    def split_range(self, input_path: Path, start_page: int, end_page: int, output_path: Path) -> None:
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        for page_index in range(start_page, end_page + 1):
            writer.add_page(reader.pages[page_index])
        self._write(writer, output_path)

    def merge_pdfs(self, input_paths: list[Path], output_path: Path) -> None:
        writer = PdfWriter()
        for input_path in input_paths:
            reader = PdfReader(str(input_path))
            for page in reader.pages:
                writer.add_page(page)
        self._write(writer, output_path)

    @staticmethod
    def _write(writer: PdfWriter, output_path: Path) -> None:
        with output_path.open("wb") as handle:
            writer.write(handle)
