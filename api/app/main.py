from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.app.config import ALLOWED_ORIGINS
from api.app.models import DocumentMetadata, HealthResponse, UploadResponse
from api.app.storage import DocumentStore, StorageError

app = FastAPI(title="PDF App Web API", version="0.1.0")
store = DocumentStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    content_type = (file.content_type or "").lower()
    if content_type not in {"application/pdf", "application/x-pdf", ""}:
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    try:
        metadata = store.save_upload(file)
    except StorageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await file.close()

    return UploadResponse(
        doc_id=metadata["doc_id"],
        filename=metadata["filename"],
        size_bytes=metadata["size_bytes"],
        page_count=metadata["page_count"],
    )


@app.get("/document/{doc_id}", response_model=DocumentMetadata)
def document_metadata(doc_id: str, request: Request) -> DocumentMetadata:
    metadata = store.load_metadata(doc_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    return DocumentMetadata(
        doc_id=metadata["doc_id"],
        filename=metadata["filename"],
        size_bytes=metadata["size_bytes"],
        page_count=metadata["page_count"],
        uploaded_at=metadata["uploaded_at"],
        download_url=str(request.url_for("download_document", doc_id=doc_id)),
    )


@app.get("/download/{doc_id}", name="download_document")
def download_document(doc_id: str) -> FileResponse:
    metadata = store.load_metadata(doc_id)
    file_path = store.file_path_for(doc_id)
    if metadata is None or file_path is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=metadata["filename"],
    )
