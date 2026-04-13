"use client";

import * as pdfjsLib from "pdfjs-dist";

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

export type PdfDocumentProxyLike = {
  numPages: number;
  destroy: () => Promise<void>;
  getPage: (pageNumber: number) => Promise<unknown>;
};

export function getPdfDocument(url: string) {
  return pdfjsLib.getDocument(url);
}
