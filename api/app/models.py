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
    updated_at: str
    version: int
    download_url: str


class PageSelectionRequest(BaseModel):
    doc_id: str
    page_indices: list[int]


class RotateRequest(PageSelectionRequest):
    degrees: int = 90


class SplitRequest(BaseModel):
    doc_id: str
    start_page: int
    end_page: int


class ReorderRequest(BaseModel):
    doc_id: str
    page_order: list[int]


class SearchRequest(BaseModel):
    doc_id: str
    query: str


class SearchResultItem(BaseModel):
    result_index: int
    page_number: int
    snippet: str


class SearchResponse(BaseModel):
    query: str
    total_matches: int
    results: list[SearchResultItem]


class AnnotationRect(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class AnnotationRequest(BaseModel):
    doc_id: str
    page_number: int
    annotation_type: str
    text: str
    rects: list[AnnotationRect]
