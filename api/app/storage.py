from __future__ import annotations

import json
import logging
import shutil
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile

import fitz
from pypdf import PdfReader

from api.app.config import DOCUMENT_TTL_HOURS, MAX_UPLOAD_BYTES, STORAGE_DIR
from pdf_app.pdf_ops.pdf_operation_service import PdfOperationService
from pdf_app.search.engine import SearchEngine

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Raised for recoverable storage or validation failures."""


class DocumentStore:
    def __init__(self, storage_dir: Path = STORAGE_DIR) -> None:
        self.storage_dir = storage_dir
        self.operation_service = PdfOperationService()
        self.search_engine = SearchEngine()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup_expired_documents()

    def save_upload(self, upload_file) -> dict:
        self.cleanup_expired_documents()
        filename = (upload_file.filename or "document.pdf").strip() or "document.pdf"
        if not filename.lower().endswith(".pdf"):
            raise StorageError("Only PDF uploads are supported.")

        doc_id = uuid.uuid4().hex
        document_dir = self.storage_dir / doc_id
        document_dir.mkdir(parents=True, exist_ok=False)
        file_path = document_dir / "document.pdf"
        metadata_path = document_dir / "metadata.json"

        try:
            total_bytes = 0
            with file_path.open("wb") as output:
                while True:
                    chunk = upload_file.file.read(1024 * 1024)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > MAX_UPLOAD_BYTES:
                        raise StorageError(f"PDF exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
                    output.write(chunk)

            try:
                reader = PdfReader(str(file_path))
                if reader.is_encrypted:
                    raise StorageError("Encrypted PDFs are not supported in the web app yet.")
                page_count = len(reader.pages)
            except Exception as exc:  # pragma: no cover - defensive validation path
                if isinstance(exc, StorageError):
                    raise
                raise StorageError(f"Uploaded file is not a valid readable PDF: {exc}") from exc

            if page_count <= 0:
                raise StorageError("Uploaded PDF does not contain any readable pages.")

            metadata = {
                "doc_id": doc_id,
                "filename": filename,
                "size_bytes": total_bytes,
                "page_count": page_count,
                "uploaded_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
                "version": 1,
                "stored_filename": file_path.name,
            }
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            logger.info("stored uploaded document doc_id=%s filename=%s page_count=%s", doc_id, filename, page_count)
            return metadata
        except Exception:
            shutil.rmtree(document_dir, ignore_errors=True)
            raise

    def load_metadata(self, doc_id: str) -> dict | None:
        metadata_path = self.storage_dir / doc_id / "metadata.json"
        if not metadata_path.exists():
            return None
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def file_path_for(self, doc_id: str) -> Path | None:
        metadata = self.load_metadata(doc_id)
        if metadata is None:
            return None
        file_path = self.storage_dir / doc_id / metadata.get("stored_filename", "document.pdf")
        return file_path if file_path.exists() else None

    def rotate_pages(self, doc_id: str, page_indices: list[int], degrees: int) -> dict:
        self._validate_rotation(degrees)
        return self._apply_mutation(
            doc_id,
            lambda input_path, output_path: self.operation_service.rotate_pages(
                input_path,
                page_indices,
                output_path,
                degrees,
            ),
        )

    def delete_pages(self, doc_id: str, page_indices: list[int]) -> dict:
        return self._apply_mutation(
            doc_id,
            lambda input_path, output_path: self.operation_service.delete_pages(
                input_path,
                page_indices,
                output_path,
            ),
        )

    def reorder_pages(self, doc_id: str, page_order: list[int]) -> dict:
        return self._apply_mutation(
            doc_id,
            lambda input_path, output_path: self.operation_service.reorder_pages(
                input_path,
                page_order,
                output_path,
            ),
        )

    def extract_pages(self, doc_id: str, page_indices: list[int]) -> tuple[Path, str]:
        metadata = self._require_metadata(doc_id)
        input_path = self._require_file_path(doc_id)
        temp_file = NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_file.close()
        output_path = Path(temp_file.name)
        try:
            self.operation_service.extract_pages(input_path, page_indices, output_path)
        except Exception as exc:
            output_path.unlink(missing_ok=True)
            logger.warning("extract operation failed doc_id=%s error=%s", doc_id, exc)
            raise StorageError(str(exc)) from exc
        stem = Path(metadata["filename"]).stem or "document"
        return output_path, f"{stem}_extract.pdf"

    def split_range(self, doc_id: str, start_page: int, end_page: int) -> tuple[Path, str]:
        metadata = self._require_metadata(doc_id)
        input_path = self._require_file_path(doc_id)
        temp_file = NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_file.close()
        output_path = Path(temp_file.name)
        try:
            self.operation_service.split_range(input_path, start_page, end_page, output_path)
        except Exception as exc:
            output_path.unlink(missing_ok=True)
            logger.warning("split operation failed doc_id=%s error=%s", doc_id, exc)
            raise StorageError(str(exc)) from exc
        stem = Path(metadata["filename"]).stem or "document"
        return output_path, f"{stem}_split_{start_page + 1}-{end_page + 1}.pdf"

    def search(self, doc_id: str, query: str) -> dict:
        self._require_metadata(doc_id)
        input_path = self._require_file_path(doc_id)
        cleaned = query.strip()
        if not cleaned:
            return {
                "query": "",
                "total_matches": 0,
                "results": [],
            }
        if len(cleaned) > 200:
            raise StorageError("Search query is too long. Please keep it under 200 characters.")

        try:
            matches = self.search_engine.search(input_path, cleaned)
        except Exception as exc:
            raise StorageError(str(exc)) from exc

        results = [
            {
                "result_index": index,
                "page_number": match.page_index + 1,
                "snippet": match.snippet,
            }
            for index, match in enumerate(matches)
        ]
        return {
            "query": cleaned,
            "total_matches": len(results),
            "results": results,
        }

    def annotate(self, doc_id: str, page_number: int, annotation_type: str, text: str, rects: list[dict]) -> dict:
        normalized_type = annotation_type.strip().lower()
        if normalized_type not in {"highlight", "underline"}:
            raise StorageError("Unsupported annotation type.")
        if not text.strip():
            raise StorageError("Annotation text selection is empty.")
        if not rects:
            raise StorageError("No annotation rectangles were provided.")

        def apply_annotation(input_path: Path, output_path: Path) -> None:
            document = fitz.open(input_path)
            try:
                if not 1 <= page_number <= document.page_count:
                    raise StorageError("Annotation page is out of bounds.")
                page = document.load_page(page_number - 1)
                page_rect = page.rect
                annotations_created = 0

                for rect_payload in rects:
                    normalized = self._validate_annotation_rect(rect_payload)
                    rect = fitz.Rect(
                        normalized["x0"] * page_rect.width,
                        normalized["y0"] * page_rect.height,
                        normalized["x1"] * page_rect.width,
                        normalized["y1"] * page_rect.height,
                    )
                    if rect.is_empty or rect.width <= 0 or rect.height <= 0:
                        continue
                    if normalized_type == "highlight":
                        annotation = page.add_highlight_annot(rect)
                    else:
                        annotation = page.add_underline_annot(rect)
                    if annotation is not None:
                        annotation.set_info(content=text.strip())
                        annotation.update()
                        annotations_created += 1

                if annotations_created == 0:
                    raise StorageError("Could not derive any valid annotation area from the selected text.")

                output_path.unlink(missing_ok=True)
                document.save(output_path, garbage=3, deflate=True)
            finally:
                document.close()

        return self._apply_mutation(doc_id, apply_annotation)

    def cleanup_expired_documents(self) -> int:
        cutoff = datetime.now(UTC) - timedelta(hours=DOCUMENT_TTL_HOURS)
        removed = 0
        for child in self.storage_dir.iterdir():
            if not child.is_dir():
                continue
            metadata_path = child / "metadata.json"
            if not metadata_path.exists():
                shutil.rmtree(child, ignore_errors=True)
                removed += 1
                continue
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                timestamp_raw = metadata.get("updated_at") or metadata.get("uploaded_at")
                if not timestamp_raw:
                    raise ValueError("Missing timestamp")
                timestamp = datetime.fromisoformat(timestamp_raw)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=UTC)
                if timestamp < cutoff:
                    shutil.rmtree(child, ignore_errors=True)
                    removed += 1
            except Exception:
                logger.warning("removing unreadable temporary document directory path=%s", child)
                shutil.rmtree(child, ignore_errors=True)
                removed += 1
        if removed:
            logger.info("cleaned expired temporary documents count=%s ttl_hours=%s", removed, DOCUMENT_TTL_HOURS)
        return removed

    def _apply_mutation(self, doc_id: str, action) -> dict:
        metadata = self._require_metadata(doc_id)
        input_path = self._require_file_path(doc_id)
        temp_file = NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_file.close()
        output_path = Path(temp_file.name)

        try:
            action(input_path, output_path)
            output_path.replace(input_path)
            refreshed_reader = PdfReader(str(input_path))
            stat = input_path.stat()
            now = datetime.now(UTC).isoformat()
            metadata["size_bytes"] = stat.st_size
            metadata["page_count"] = len(refreshed_reader.pages)
            metadata["updated_at"] = now
            metadata["version"] = int(metadata.get("version", 1)) + 1
            self._write_metadata(doc_id, metadata)
            logger.info(
                "updated working document doc_id=%s version=%s page_count=%s",
                doc_id,
                metadata["version"],
                metadata["page_count"],
            )
            return metadata
        except Exception as exc:
            output_path.unlink(missing_ok=True)
            logger.exception("document mutation failed doc_id=%s", doc_id)
            raise StorageError(str(exc)) from exc

    def _require_metadata(self, doc_id: str) -> dict:
        metadata = self.load_metadata(doc_id)
        if metadata is None:
            raise StorageError("Document not found.")
        return metadata

    def _require_file_path(self, doc_id: str) -> Path:
        file_path = self.file_path_for(doc_id)
        if file_path is None:
            raise StorageError("Document file is missing.")
        return file_path

    def _write_metadata(self, doc_id: str, metadata: dict) -> None:
        metadata_path = self.storage_dir / doc_id / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    @staticmethod
    def _validate_rotation(degrees: int) -> None:
        if degrees == 0 or degrees % 90 != 0:
            raise StorageError("Rotation must be in 90-degree increments.")

    @staticmethod
    def _validate_annotation_rect(rect_payload: dict) -> dict:
        required_keys = {"x0", "y0", "x1", "y1"}
        if not required_keys.issubset(rect_payload):
            raise StorageError("Annotation rectangle payload is incomplete.")
        try:
            x0 = float(rect_payload["x0"])
            y0 = float(rect_payload["y0"])
            x1 = float(rect_payload["x1"])
            y1 = float(rect_payload["y1"])
        except (TypeError, ValueError) as exc:
            raise StorageError("Annotation rectangle payload is invalid.") from exc

        if min(x0, y0, x1, y1) < 0 or max(x0, y0, x1, y1) > 1:
            raise StorageError("Annotation selection is out of bounds.")
        if x1 <= x0 or y1 <= y0:
            raise StorageError("Annotation rectangle has invalid geometry.")

        return {"x0": x0, "y0": y0, "x1": x1, "y1": y1}
