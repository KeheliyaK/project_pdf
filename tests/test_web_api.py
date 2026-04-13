from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfWriter

import api.app.main as web_main
from api.app.storage import DocumentStore


def _sample_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    payload = BytesIO()
    writer.write(payload)
    return payload.getvalue()


def test_web_api_upload_metadata_and_download(tmp_path: Path) -> None:
    original_store = web_main.store
    web_main.store = DocumentStore(tmp_path / "documents")
    client = TestClient(web_main.app)

    try:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        upload = client.post(
            "/upload",
            files={"file": ("sample.pdf", _sample_pdf_bytes(), "application/pdf")},
        )
        assert upload.status_code == 200
        upload_body = upload.json()
        assert upload_body["filename"] == "sample.pdf"
        assert upload_body["page_count"] == 1

        doc_id = upload_body["doc_id"]

        metadata = client.get(f"/document/{doc_id}")
        assert metadata.status_code == 200
        metadata_body = metadata.json()
        assert metadata_body["doc_id"] == doc_id
        assert metadata_body["page_count"] == 1
        assert metadata_body["download_url"].endswith(f"/download/{doc_id}")

        download = client.get(f"/download/{doc_id}")
        assert download.status_code == 200
        assert download.headers["content-type"].startswith("application/pdf")
        assert download.content.startswith(b"%PDF")
    finally:
        web_main.store = original_store
