import type { DocumentMetadata, UploadResponse } from "./types";

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
