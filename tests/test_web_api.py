from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from datetime import UTC, datetime, timedelta

import fitz
from fastapi.testclient import TestClient
from pypdf import PdfReader, PdfWriter

import api.app.main as web_main
from api.app.storage import DocumentStore


def _sample_pdf_bytes(page_count: int = 3) -> bytes:
    writer = PdfWriter()
    for index in range(page_count):
        writer.add_blank_page(width=200 + (index * 10), height=200 + (index * 5))
    payload = BytesIO()
    writer.write(payload)
    return payload.getvalue()


def _upload_sample_pdf(client: TestClient) -> str:
    upload = client.post(
        "/upload",
        files={"file": ("sample.pdf", _sample_pdf_bytes(), "application/pdf")},
    )
    assert upload.status_code == 200
    return upload.json()["doc_id"]


def _text_pdf_bytes(pages: list[str]) -> bytes:
    document = fitz.open()
    for text in pages:
        page = document.new_page(width=595, height=842)
        page.insert_text((72, 96), text)
    return document.tobytes()


def test_web_api_upload_metadata_and_download(tmp_path: Path) -> None:
    original_store = web_main.store
    web_main.store = DocumentStore(tmp_path / "documents")
    client = TestClient(web_main.app)

    try:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        doc_id = _upload_sample_pdf(client)

        metadata = client.get(f"/document/{doc_id}")
        assert metadata.status_code == 200
        metadata_body = metadata.json()
        assert metadata_body["doc_id"] == doc_id
        assert metadata_body["page_count"] == 3
        assert metadata_body["version"] == 1
        assert metadata_body["download_url"].endswith(f"/download/{doc_id}")

        download = client.get(f"/download/{doc_id}")
        assert download.status_code == 200
        assert download.headers["content-type"].startswith("application/pdf")
        assert download.content.startswith(b"%PDF")
    finally:
        web_main.store = original_store


def test_web_api_rotate_delete_reorder_extract_and_split(tmp_path: Path) -> None:
    original_store = web_main.store
    web_main.store = DocumentStore(tmp_path / "documents")
    client = TestClient(web_main.app)

    try:
        doc_id = _upload_sample_pdf(client)

        rotate = client.post("/rotate", json={"doc_id": doc_id, "page_indices": [0, 1], "degrees": 90})
        assert rotate.status_code == 200
        rotate_body = rotate.json()
        assert rotate_body["version"] == 2
        assert rotate_body["page_count"] == 3

        extract = client.post("/extract", json={"doc_id": doc_id, "page_indices": [0, 2]})
        assert extract.status_code == 200
        extract_reader = PdfReader(BytesIO(extract.content))
        assert len(extract_reader.pages) == 2

        split = client.post("/split", json={"doc_id": doc_id, "start_page": 0, "end_page": 1})
        assert split.status_code == 200
        split_reader = PdfReader(BytesIO(split.content))
        assert len(split_reader.pages) == 2

        reorder = client.post("/reorder", json={"doc_id": doc_id, "page_order": [2, 1, 0]})
        assert reorder.status_code == 200
        reorder_body = reorder.json()
        assert reorder_body["version"] == 3
        assert reorder_body["page_count"] == 3

        delete = client.post("/delete", json={"doc_id": doc_id, "page_indices": [1]})
        assert delete.status_code == 200
        delete_body = delete.json()
        assert delete_body["version"] == 4
        assert delete_body["page_count"] == 2

        final_download = client.get(f"/download/{doc_id}")
        final_reader = PdfReader(BytesIO(final_download.content))
        assert len(final_reader.pages) == 2
    finally:
        web_main.store = original_store


def test_web_api_search_returns_page_numbered_results(tmp_path: Path) -> None:
    original_store = web_main.store
    web_main.store = DocumentStore(tmp_path / "documents")
    client = TestClient(web_main.app)

    try:
        upload = client.post(
            "/upload",
            files={
                "file": (
                    "searchable.pdf",
                    _text_pdf_bytes(
                        [
                            "lipid bilayer behavior is discussed here.",
                            "No keyword on this page.",
                            "Another lipid paragraph about membrane structure.",
                        ]
                    ),
                    "application/pdf",
                )
            },
        )
        assert upload.status_code == 200
        doc_id = upload.json()["doc_id"]

        response = client.post("/search", json={"doc_id": doc_id, "query": "lipid"})
        assert response.status_code == 200
        body = response.json()
        assert body["query"] == "lipid"
        assert body["total_matches"] == 2
        assert [result["page_number"] for result in body["results"]] == [1, 3]
        assert all("lipid" in result["snippet"].lower() for result in body["results"])

        blank_response = client.post("/search", json={"doc_id": doc_id, "query": "   "})
        assert blank_response.status_code == 200
        assert blank_response.json()["total_matches"] == 0
    finally:
        web_main.store = original_store


def test_web_api_annotation_writeback_updates_pdf(tmp_path: Path) -> None:
    original_store = web_main.store
    web_main.store = DocumentStore(tmp_path / "documents")
    client = TestClient(web_main.app)

    try:
        upload = client.post(
            "/upload",
            files={
                "file": (
                    "annotated.pdf",
                    _text_pdf_bytes(["Highlight this sentence for annotation testing."]),
                    "application/pdf",
                )
            },
        )
        assert upload.status_code == 200
        doc_id = upload.json()["doc_id"]

        response = client.post(
            "/annotate",
            json={
                "doc_id": doc_id,
                "page_number": 1,
                "annotation_type": "highlight",
                "text": "Highlight this sentence",
                "rects": [
                    {
                        "x0": 0.1,
                        "y0": 0.08,
                        "x1": 0.5,
                        "y1": 0.12,
                    }
                ],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == 2

        stored_pdf = client.get(f"/download/{doc_id}")
        assert stored_pdf.status_code == 200

        document = fitz.open(stream=stored_pdf.content, filetype="pdf")
        page = document.load_page(0)
        annotations = list(page.annots() or [])
        assert len(annotations) == 1
        assert annotations[0].type[1].lower() == "highlight"
        document.close()
    finally:
        web_main.store = original_store


def test_web_api_rejects_invalid_requests(tmp_path: Path) -> None:
    original_store = web_main.store
    web_main.store = DocumentStore(tmp_path / "documents")
    client = TestClient(web_main.app)

    try:
        invalid_upload = client.post(
            "/upload",
            files={"file": ("notes.txt", b"not a pdf", "text/plain")},
        )
        assert invalid_upload.status_code == 400
        assert "Only PDF uploads" in invalid_upload.json()["detail"]

        doc_id = _upload_sample_pdf(client)

        bad_rotate = client.post("/rotate", json={"doc_id": doc_id, "page_indices": [0], "degrees": 45})
        assert bad_rotate.status_code == 400
        assert "90-degree increments" in bad_rotate.json()["detail"]

        bad_split = client.post("/split", json={"doc_id": doc_id, "start_page": 5, "end_page": 6})
        assert bad_split.status_code == 400
        assert "out of bounds" in bad_split.json()["detail"]

        long_query = "a" * 201
        bad_search = client.post("/search", json={"doc_id": doc_id, "query": long_query})
        assert bad_search.status_code == 400
        assert "under 200 characters" in bad_search.json()["detail"]
    finally:
        web_main.store = original_store


def test_document_store_cleans_expired_temp_documents(tmp_path: Path) -> None:
    storage_root = tmp_path / "documents"
    expired_dir = storage_root / "expired-doc"
    expired_dir.mkdir(parents=True)
    (expired_dir / "document.pdf").write_bytes(_sample_pdf_bytes(page_count=1))
    (expired_dir / "metadata.json").write_text(
        json.dumps(
            {
                "doc_id": "expired-doc",
                "filename": "expired.pdf",
                "size_bytes": 123,
                "page_count": 1,
                "uploaded_at": (datetime.now(UTC) - timedelta(hours=48)).isoformat(),
                "updated_at": (datetime.now(UTC) - timedelta(hours=48)).isoformat(),
                "version": 1,
                "stored_filename": "document.pdf",
            }
        ),
        encoding="utf-8",
    )

    store = DocumentStore(storage_root)
    assert store.load_metadata("expired-doc") is None
    assert not expired_dir.exists()
