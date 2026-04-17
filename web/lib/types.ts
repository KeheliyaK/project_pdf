export type UploadResponse = {
  doc_id: string;
  filename: string;
  size_bytes: number;
  page_count: number;
};

export type DocumentMetadata = {
  doc_id: string;
  filename: string;
  size_bytes: number;
  page_count: number;
  uploaded_at: string;
  updated_at: string;
  version: number;
  download_url: string;
};

export type SearchResultItem = {
  result_index: number;
  page_number: number;
  snippet: string;
};

export type SearchResponse = {
  query: string;
  total_matches: number;
  results: SearchResultItem[];
};

export type AnnotationRect = {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
};
