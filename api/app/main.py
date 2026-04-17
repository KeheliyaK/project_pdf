from __future__ import annotations

import logging

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.app.config import ALLOWED_ORIGINS
from api.app.models import (
    DocumentMetadata,
    HealthResponse,
    PageSelectionRequest,
    ReorderRequest,
    RotateRequest,
    AnnotationRequest,
    SearchRequest,
    SearchResponse,
    SplitRequest,
    UploadResponse,
)
from api.app.storage import DocumentStore, StorageError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

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
        logger.info("upload requested filename=%s content_type=%s", file.filename, content_type)
        metadata = store.save_upload(file)
    except StorageError as exc:
        logger.warning("upload failed filename=%s error=%s", file.filename, exc)
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
        updated_at=metadata["updated_at"],
        version=metadata["version"],
        download_url=str(request.url_for("download_document", doc_id=doc_id)),
    )


@app.get("/download/{doc_id}", name="download_document")
def download_document(doc_id: str) -> FileResponse:
    metadata = store.load_metadata(doc_id)
    file_path = store.file_path_for(doc_id)
    if metadata is None or file_path is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    logger.info("download requested doc_id=%s filename=%s", doc_id, metadata["filename"])
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=metadata["filename"],
    )


@app.post("/rotate", response_model=DocumentMetadata)
def rotate_pages(payload: RotateRequest, request: Request) -> DocumentMetadata:
    try:
        logger.info("rotate requested doc_id=%s pages=%s degrees=%s", payload.doc_id, payload.page_indices, payload.degrees)
        metadata = store.rotate_pages(payload.doc_id, payload.page_indices, payload.degrees)
    except StorageError as exc:
        logger.warning("rotate failed doc_id=%s error=%s", payload.doc_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _metadata_response(metadata, request)


@app.post("/delete", response_model=DocumentMetadata)
def delete_pages(payload: PageSelectionRequest, request: Request) -> DocumentMetadata:
    try:
        logger.info("delete requested doc_id=%s pages=%s", payload.doc_id, payload.page_indices)
        metadata = store.delete_pages(payload.doc_id, payload.page_indices)
    except StorageError as exc:
        logger.warning("delete failed doc_id=%s error=%s", payload.doc_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _metadata_response(metadata, request)


@app.post("/reorder", response_model=DocumentMetadata)
def reorder_pages(payload: ReorderRequest, request: Request) -> DocumentMetadata:
    try:
        logger.info("reorder requested doc_id=%s order_length=%s", payload.doc_id, len(payload.page_order))
        metadata = store.reorder_pages(payload.doc_id, payload.page_order)
    except StorageError as exc:
        logger.warning("reorder failed doc_id=%s error=%s", payload.doc_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _metadata_response(metadata, request)


@app.post("/extract")
def extract_pages(payload: PageSelectionRequest) -> FileResponse:
    try:
        logger.info("extract requested doc_id=%s pages=%s", payload.doc_id, payload.page_indices)
        file_path, filename = store.extract_pages(payload.doc_id, payload.page_indices)
    except StorageError as exc:
        logger.warning("extract failed doc_id=%s error=%s", payload.doc_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileResponse(path=file_path, media_type="application/pdf", filename=filename)


@app.post("/split")
def split_document(payload: SplitRequest) -> FileResponse:
    try:
        logger.info("split requested doc_id=%s start=%s end=%s", payload.doc_id, payload.start_page, payload.end_page)
        file_path, filename = store.split_range(payload.doc_id, payload.start_page, payload.end_page)
    except StorageError as exc:
        logger.warning("split failed doc_id=%s error=%s", payload.doc_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileResponse(path=file_path, media_type="application/pdf", filename=filename)


@app.post("/search", response_model=SearchResponse)
def search_document(payload: SearchRequest) -> SearchResponse:
    try:
        logger.info("search requested doc_id=%s query=%r", payload.doc_id, payload.query.strip())
        response = store.search(payload.doc_id, payload.query)
    except StorageError as exc:
        logger.warning("search failed doc_id=%s error=%s", payload.doc_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SearchResponse(**response)


@app.post("/annotate", response_model=DocumentMetadata)
def annotate_document(payload: AnnotationRequest, request: Request) -> DocumentMetadata:
    try:
        logger.info(
            "annotation requested doc_id=%s page=%s type=%s rect_count=%s",
            payload.doc_id,
            payload.page_number,
            payload.annotation_type,
            len(payload.rects),
        )
        metadata = store.annotate(
            payload.doc_id,
            payload.page_number,
            payload.annotation_type,
            payload.text,
            [rect.model_dump() for rect in payload.rects],
        )
    except StorageError as exc:
        logger.warning("annotation failed doc_id=%s error=%s", payload.doc_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _metadata_response(metadata, request)


def _metadata_response(metadata: dict, request: Request) -> DocumentMetadata:
    return DocumentMetadata(
        doc_id=metadata["doc_id"],
        filename=metadata["filename"],
        size_bytes=metadata["size_bytes"],
        page_count=metadata["page_count"],
        uploaded_at=metadata["uploaded_at"],
        updated_at=metadata["updated_at"],
        version=metadata["version"],
        download_url=str(request.url_for("download_document", doc_id=metadata["doc_id"])),
    )
