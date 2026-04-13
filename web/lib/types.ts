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
  download_url: string;
};
