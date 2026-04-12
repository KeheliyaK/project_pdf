from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


class PdfOperationService:
    def reorder_pages(self, input_path: Path, order: list[int], output_path: Path) -> None:
        reader = PdfReader(str(input_path))
        self._validate_reorder(len(reader.pages), order)
        writer = PdfWriter()
        for page_index in order:
            writer.add_page(reader.pages[page_index])
        self._write(writer, output_path)

    def delete_pages(self, input_path: Path, page_indices: list[int], output_path: Path) -> None:
        reader = PdfReader(str(input_path))
        to_remove = set(self._validate_page_indices(len(reader.pages), page_indices, operation="delete"))
        writer = PdfWriter()
        for idx, page in enumerate(reader.pages):
            if idx not in to_remove:
                writer.add_page(page)
        self._write(writer, output_path)

    def rotate_pages(self, input_path: Path, page_indices: list[int], output_path: Path, degrees: int) -> None:
        reader = PdfReader(str(input_path))
        target = set(self._validate_page_indices(len(reader.pages), page_indices, operation="rotate"))
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
        selected = self._validate_page_indices(len(reader.pages), page_indices, operation="extract")
        writer = PdfWriter()
        for page_index in selected:
            writer.add_page(reader.pages[page_index])
        self._write(writer, output_path)

    def split_range(self, input_path: Path, start_page: int, end_page: int, output_path: Path) -> None:
        reader = PdfReader(str(input_path))
        self._validate_split_range(len(reader.pages), start_page, end_page)
        writer = PdfWriter()
        for page_index in range(start_page, end_page + 1):
            writer.add_page(reader.pages[page_index])
        self._write(writer, output_path)

    def merge_pdfs(self, input_paths: list[Path], output_path: Path) -> None:
        writer = PdfWriter()
        for input_path in input_paths:
            reader = PdfReader(str(input_path))
            if reader.is_encrypted:
                raise ValueError(f"{input_path.name} must be unlocked before it can be merged.")
            for page in reader.pages:
                writer.add_page(page)
        self._write(writer, output_path)

    @staticmethod
    def _validate_page_indices(page_count: int, page_indices: list[int], operation: str) -> list[int]:
        if not page_indices:
            raise ValueError(f"No pages were selected for {operation}.")
        if len(set(page_indices)) != len(page_indices):
            raise ValueError(f"Duplicate pages were supplied for {operation}.")
        invalid = [page_index for page_index in page_indices if not 0 <= page_index < page_count]
        if invalid:
            raise ValueError(f"Page indices out of range for {operation}: {invalid}")
        return page_indices

    @staticmethod
    def _validate_reorder(page_count: int, order: list[int]) -> None:
        if len(order) != page_count or set(order) != set(range(page_count)):
            raise ValueError("Reorder must include each page exactly once.")

    @staticmethod
    def _validate_split_range(page_count: int, start_page: int, end_page: int) -> None:
        if not (0 <= start_page <= end_page < page_count):
            raise ValueError("Split range is out of bounds.")

    @staticmethod
    def _write(writer: PdfWriter, output_path: Path) -> None:
        with output_path.open("wb") as handle:
            writer.write(handle)
