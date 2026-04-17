import type { AnnotationRect, DocumentMetadata, SearchResponse, UploadResponse } from "./types";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL;
}

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  if (response.ok) {
    return (await response.json()) as T;
  }

  let detail = "Request failed.";
  try {
    const payload = (await response.json()) as { detail?: string };
    if (payload.detail) {
      detail = payload.detail;
    }
  } catch {
    // Fall back to the generic message.
  }
  throw new Error(detail);
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${apiBaseUrl()}/upload`, {
    method: "POST",
    body: formData,
  });
  return parseJsonOrThrow<UploadResponse>(response);
}

export async function fetchDocument(docId: string): Promise<DocumentMetadata> {
  const response = await fetch(`${apiBaseUrl()}/document/${docId}`, {
    cache: "no-store",
  });
  return parseJsonOrThrow<DocumentMetadata>(response);
}

export function downloadUrl(docId: string): string {
  return `${apiBaseUrl()}/download/${docId}`;
}

export async function downloadDocument(docId: string): Promise<{ blob: Blob; filename: string }> {
  const response = await fetch(downloadUrl(docId));

  if (!response.ok) {
    let detail = "Download failed.";
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      // Keep the generic message.
    }
    throw new Error(detail);
  }

  const disposition = response.headers.get("content-disposition") || "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/i);
  return {
    blob: await response.blob(),
    filename: filenameMatch?.[1] || "document.pdf",
  };
}

type PageSelectionPayload = {
  doc_id: string;
  page_indices: number[];
};

async function postJson<T>(path: string, payload: object): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return parseJsonOrThrow<T>(response);
}

export async function rotatePages(docId: string, pageIndices: number[], degrees = 90): Promise<DocumentMetadata> {
  return postJson<DocumentMetadata>("/rotate", {
    doc_id: docId,
    page_indices: pageIndices,
    degrees,
  });
}

export async function searchDocument(docId: string, query: string): Promise<SearchResponse> {
  return postJson<SearchResponse>("/search", {
    doc_id: docId,
    query,
  });
}

export async function annotateDocument(
  docId: string,
  pageNumber: number,
  annotationType: "highlight" | "underline",
  text: string,
  rects: AnnotationRect[]
): Promise<DocumentMetadata> {
  return postJson<DocumentMetadata>("/annotate", {
    doc_id: docId,
    page_number: pageNumber,
    annotation_type: annotationType,
    text,
    rects,
  });
}

export async function deletePages(docId: string, pageIndices: number[]): Promise<DocumentMetadata> {
  return postJson<DocumentMetadata>("/delete", {
    doc_id: docId,
    page_indices: pageIndices,
  } satisfies PageSelectionPayload);
}

export async function reorderPages(docId: string, pageOrder: number[]): Promise<DocumentMetadata> {
  return postJson<DocumentMetadata>("/reorder", {
    doc_id: docId,
    page_order: pageOrder,
  });
}

async function postFile(path: string, payload: object): Promise<{ blob: Blob; filename: string }> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = "Request failed.";
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      // Ignore parse failures and keep generic error text.
    }
    throw new Error(detail);
  }

  const disposition = response.headers.get("content-disposition") || "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/i);
  return {
    blob: await response.blob(),
    filename: filenameMatch?.[1] || "output.pdf",
  };
}

export async function extractPages(docId: string, pageIndices: number[]) {
  return postFile("/extract", {
    doc_id: docId,
    page_indices: pageIndices,
  } satisfies PageSelectionPayload);
}

export async function splitDocument(docId: string, startPage: number, endPage: number) {
  return postFile("/split", {
    doc_id: docId,
    start_page: startPage,
    end_page: endPage,
  });
}

export function triggerBrowserDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
