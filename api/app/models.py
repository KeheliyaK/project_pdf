from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    size_bytes: int
    page_count: int


class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    size_bytes: int
    page_count: int
    uploaded_at: str
    download_url: str
