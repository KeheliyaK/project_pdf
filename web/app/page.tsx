"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";

import { PdfViewer } from "../components/pdf-viewer";
import { ThumbnailRail } from "../components/thumbnail-rail";
import { apiBaseUrl, downloadUrl, fetchDocument, uploadPdf } from "../lib/api";
import { getPdfDocument, type PdfDocumentProxyLike } from "../lib/pdfjs";
import type { DocumentMetadata } from "../lib/types";

const ZOOM_STEP = 0.2;
const MIN_ZOOM = 0.6;
const MAX_ZOOM = 2.6;

export default function HomePage() {
  const [docId, setDocId] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<DocumentMetadata | null>(null);
  const [pdfDocument, setPdfDocument] = useState<PdfDocumentProxyLike | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageInput, setPageInput] = useState<string>("1");
  const [zoom, setZoom] = useState<number>(1);
  const [busy, setBusy] = useState<boolean>(false);
  const [viewerLoading, setViewerLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>("Upload a PDF to begin.");
  const [errorMessage, setErrorMessage] = useState<string>("");

  const pdfUrl = useMemo(() => (docId ? downloadUrl(docId) : null), [docId]);
  const pageCount = metadata?.page_count ?? pdfDocument?.numPages ?? 0;
  const zoomPercent = Math.round(zoom * 100);

  useEffect(() => {
    async function loadMetadata() {
      if (!docId) {
        setMetadata(null);
        return;
      }

      try {
        const nextMetadata = await fetchDocument(docId);
        setMetadata(nextMetadata);
        setStatusMessage(`Loaded ${nextMetadata.filename}.`);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Could not load the document metadata.");
      }
    }

    void loadMetadata();
  }, [docId]);

  useEffect(() => {
    let active = true;

    async function loadPdfDocument() {
      if (!pdfUrl) {
        if (pdfDocument) {
          await pdfDocument.destroy();
        }
        if (active) {
          setPdfDocument(null);
          setViewerLoading(false);
        }
        return;
      }

      setViewerLoading(true);
      setErrorMessage("");
      setStatusMessage("Loading PDF into the web viewer…");
      console.log("[pdf-viewer] document load started", { pdfUrl });

      try {
        const loadingTask = getPdfDocument(pdfUrl);
        const nextPdfDocument = (await loadingTask.promise) as PdfDocumentProxyLike;
        if (!active) {
          await nextPdfDocument.destroy();
          return;
        }

        if (pdfDocument) {
          await pdfDocument.destroy();
        }

        console.log("[pdf-viewer] document loaded", { numPages: nextPdfDocument.numPages });
        setPdfDocument(nextPdfDocument);
        setCurrentPage(1);
        setPageInput("1");
        setStatusMessage(`Loaded PDF with ${nextPdfDocument.numPages} page(s).`);
      } catch (error) {
        if (!active) {
          return;
        }
        const message = error instanceof Error ? error.message : "Could not load the uploaded PDF.";
        console.error("[pdf-viewer] document load failed", { error: message });
        setPdfDocument(null);
        setErrorMessage(message);
        setStatusMessage("Viewer load failed.");
      } finally {
        if (active) {
          setViewerLoading(false);
        }
      }
    }

    void loadPdfDocument();

    return () => {
      active = false;
    };
  }, [pdfUrl]);

  useEffect(() => {
    setPageInput(String(currentPage));
  }, [currentPage]);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    setBusy(true);
    setErrorMessage("");
    setStatusMessage(`Uploading ${file.name}…`);

    try {
      const response = await uploadPdf(file);
      setDocId(response.doc_id);
      setZoom(1);
      setCurrentPage(1);
      setPageInput("1");
      setStatusMessage(`Uploaded ${response.filename}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Upload failed.");
      setStatusMessage("Upload failed.");
      setDocId(null);
      setMetadata(null);
      setPdfDocument(null);
    } finally {
      setBusy(false);
    }
  }

  function selectPage(pageNumber: number) {
    if (pageCount <= 0) {
      return;
    }
    const nextPage = Math.max(1, Math.min(pageNumber, pageCount));
    setCurrentPage(nextPage);
    setStatusMessage(`Viewing page ${nextPage} of ${pageCount}.`);
  }

  function handlePageInputCommit() {
    const parsed = Number(pageInput);
    if (!Number.isFinite(parsed)) {
      setPageInput(String(currentPage));
      return;
    }
    selectPage(parsed);
  }

  return (
    <main className="shell">
      <header className="toolbar">
        <div className="toolbar__group">
          <div className="brand">PDF App Web</div>
          <label className="upload-button" aria-label="Upload PDF">
            {busy ? "Uploading…" : "Open PDF"}
            <input type="file" accept="application/pdf,.pdf" onChange={handleUpload} disabled={busy} />
          </label>
          <button type="button" onClick={() => selectPage(currentPage - 1)} disabled={!docId || currentPage <= 1}>
            Previous
          </button>
          <button type="button" onClick={() => selectPage(currentPage + 1)} disabled={!docId || currentPage >= pageCount}>
            Next
          </button>
          <div className="page-jump">
            <input
              type="number"
              min={1}
              max={Math.max(pageCount, 1)}
              value={pageInput}
              onChange={(event) => setPageInput(event.target.value)}
              onBlur={handlePageInputCommit}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handlePageInputCommit();
                }
              }}
              disabled={!docId}
              aria-label="Current page"
            />
            <span>/ {pageCount || 0}</span>
          </div>
          <button type="button" onClick={() => setZoom((value) => Math.max(MIN_ZOOM, value - ZOOM_STEP))} disabled={!docId}>
            Zoom Out
          </button>
          <button type="button" onClick={() => setZoom((value) => Math.min(MAX_ZOOM, value + ZOOM_STEP))} disabled={!docId}>
            Zoom In
          </button>
          <button type="button" onClick={() => setZoom(1)} disabled={!docId}>
            Reset Zoom
          </button>
          <span className="badge">{zoomPercent}%</span>
        </div>

        <div className="toolbar__group">
          <button type="button" onClick={() => window.open(downloadUrl(docId ?? ""), "_blank")} disabled={!docId}>
            Download
          </button>
        </div>
      </header>

      <section className="layout">
        <aside className="panel panel--rail">
          <h2>Pages</h2>
          <p>{docId ? `Click a thumbnail to jump directly to a page.` : "Upload a PDF to generate thumbnails."}</p>
          <ThumbnailRail pdfDocument={pdfDocument} pageCount={pageCount} currentPage={currentPage} onSelectPage={selectPage} />
        </aside>

        <section className="viewer-card">
          <div className="viewer-meta">
            <div>
              <div className="viewer-meta__title">{metadata?.filename || "No document loaded"}</div>
              <div className="viewer-meta__sub">
                {metadata
                  ? `Page ${currentPage} of ${pageCount} • ${metadata.size_bytes.toLocaleString()} bytes`
                  : `API: ${apiBaseUrl()}`}
              </div>
            </div>
            {metadata ? <span className="badge">doc_id: {metadata.doc_id.slice(0, 8)}</span> : null}
          </div>

          <div className="viewer-stage">
            {viewerLoading && !pdfDocument ? <div className="status-note">Loading document and page thumbnails…</div> : null}
            <PdfViewer pdfDocument={pdfDocument} currentPage={currentPage} zoom={zoom} />
            <div className="status-note">{errorMessage || statusMessage}</div>
          </div>
        </section>

        <aside className="panel">
          <h2>Viewer Context</h2>
          <p>W3 keeps the right panel light while the viewer is completed.</p>
          <ul className="side-list">
            <li>Current page: {pageCount ? `${currentPage} / ${pageCount}` : "No document loaded"}</li>
            <li>Zoom: {zoomPercent}%</li>
            <li>Search, annotations, and editing tools remain deferred.</li>
          </ul>
        </aside>
      </section>
    </main>
  );
}
