from __future__ import annotations

import json
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

from pypdf import PdfReader

from api.app.config import MAX_UPLOAD_BYTES, STORAGE_DIR


class StorageError(Exception):
    """Raised for recoverable storage or validation failures."""


class DocumentStore:
    def __init__(self, storage_dir: Path = STORAGE_DIR) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, upload_file) -> dict:
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
                page_count = len(reader.pages)
            except Exception as exc:  # pragma: no cover - defensive validation path
                raise StorageError(f"Uploaded file is not a valid readable PDF: {exc}") from exc

            if page_count <= 0:
                raise StorageError("Uploaded PDF does not contain any readable pages.")

            metadata = {
                "doc_id": doc_id,
                "filename": filename,
                "size_bytes": total_bytes,
                "page_count": page_count,
                "uploaded_at": datetime.now(UTC).isoformat(),
                "stored_filename": file_path.name,
            }
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
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
