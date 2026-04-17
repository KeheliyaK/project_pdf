"use client";

import { ChangeEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";

import {
  ChevronLeftIcon,
  ChevronRightIcon,
  ClearIcon,
  DownloadIcon,
  ExtractIcon,
  HighlightIcon,
  IconButton,
  IconButtonLabel,
  OpenIcon,
  RotateCcwIcon,
  RotateCwIcon,
  SearchIcon,
  SplitIcon,
  TrashIcon,
  UnderlineIcon,
  ZoomInIcon,
  ZoomOutIcon,
  ZoomResetIcon,
} from "../components/icon-button";
import { PdfViewer } from "../components/pdf-viewer";
import { ThumbnailRail } from "../components/thumbnail-rail";
import {
  apiBaseUrl,
  annotateDocument,
  deletePages,
  downloadDocument,
  downloadUrl,
  extractPages,
  fetchDocument,
  reorderPages,
  rotatePages,
  searchDocument,
  splitDocument,
  triggerBrowserDownload,
  uploadPdf,
} from "../lib/api";
import { getPdfDocument, type PdfDocumentProxyLike } from "../lib/pdfjs";
import type { AnnotationRect, DocumentMetadata, SearchResultItem } from "../lib/types";

const ZOOM_STEP = 0.2;
const MIN_ZOOM = 0.6;
const MAX_ZOOM = 2.6;
const MAX_UPLOAD_BYTES = 20 * 1024 * 1024;
type AnnotationMode = "highlight" | "underline" | null;
type AnnotationSelection = {
  pageNumber: number;
  text: string;
  rects: AnnotationRect[];
};

export default function HomePage() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const annotationRequestKeyRef = useRef<string>("");
  const [docId, setDocId] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<DocumentMetadata | null>(null);
  const [pdfDocument, setPdfDocument] = useState<PdfDocumentProxyLike | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageInput, setPageInput] = useState<string>("1");
  const [pageOrder, setPageOrder] = useState<number[]>([]);
  const [selectedPages, setSelectedPages] = useState<number[]>([]);
  const [zoom, setZoom] = useState<number>(1);
  const [activeTask, setActiveTask] = useState<string | null>(null);
  const [viewerLoading, setViewerLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>("Upload a PDF to begin.");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeSearchQuery, setActiveSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
  const [activeSearchIndex, setActiveSearchIndex] = useState<number>(-1);
  const [searchBusy, setSearchBusy] = useState<boolean>(false);
  const [searchError, setSearchError] = useState<string>("");
  const [annotationMode, setAnnotationMode] = useState<AnnotationMode>(null);
  const [annotationSelection, setAnnotationSelection] = useState<AnnotationSelection | null>(null);
  const [selectionResetToken, setSelectionResetToken] = useState<number>(0);
  const [textSelectionAvailable, setTextSelectionAvailable] = useState<boolean>(false);

  const documentDownloadUrl = useMemo(() => {
    if (!docId) {
      return null;
    }
    return downloadUrl(docId);
  }, [docId]);

  const documentViewerUrl = useMemo(() => {
    if (!docId) {
      return null;
    }
    const version = metadata?.version ? `?v=${metadata.version}` : "";
    return `${documentDownloadUrl}${version}`;
  }, [docId, documentDownloadUrl, metadata?.version]);

  const pageCount = metadata?.page_count ?? pdfDocument?.numPages ?? 0;
  const zoomPercent = Math.round(zoom * 100);
  const selectedPageIndices = selectedPages.map((pageNumber) => pageNumber - 1);
  const activeSearchResult =
    activeSearchIndex >= 0 && activeSearchIndex < searchResults.length ? searchResults[activeSearchIndex] : null;
  const busy = activeTask !== null;
  const controlsDisabled = !docId || busy || viewerLoading;
  const selectedCount = selectedPages.length;

  useEffect(() => {
    async function loadMetadata() {
      if (!docId) {
        setMetadata(null);
        return;
      }

      try {
        const nextMetadata = await fetchDocument(docId);
        setMetadata(nextMetadata);
        setPageOrder(Array.from({ length: nextMetadata.page_count }, (_, index) => index + 1));
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
      if (!documentViewerUrl) {
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
      console.log("[pdf-viewer] document load started", { documentViewerUrl });

      try {
        const loadingTask = getPdfDocument(documentViewerUrl);
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
        setCurrentPage((previous) => Math.max(1, Math.min(previous, nextPdfDocument.numPages)));
        setPageInput((previous) => {
          const numeric = Number(previous);
          return String(Number.isFinite(numeric) ? Math.max(1, Math.min(numeric, nextPdfDocument.numPages)) : 1);
        });
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
  }, [documentViewerUrl]);

  useEffect(() => {
    setPageInput(String(currentPage));
  }, [currentPage]);

  useEffect(() => {
    if (searchResults.length === 0) {
      return;
    }
    if (activeSearchResult?.page_number === currentPage) {
      return;
    }
    const pageResultIndex = searchResults.findIndex((result) => result.page_number === currentPage);
    if (pageResultIndex !== -1) {
      setActiveSearchIndex(pageResultIndex);
    }
  }, [activeSearchResult?.page_number, currentPage, searchResults]);

  useEffect(() => {
    setSearchQuery("");
    setActiveSearchQuery("");
    setSearchResults([]);
    setActiveSearchIndex(-1);
    setSearchBusy(false);
    setSearchError("");
    setAnnotationMode(null);
    setAnnotationSelection(null);
    setSelectionResetToken((value) => value + 1);
    setTextSelectionAvailable(false);
    annotationRequestKeyRef.current = "";
  }, [docId]);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    if (file.size > MAX_UPLOAD_BYTES) {
      const message = `This PDF is larger than the ${Math.round(MAX_UPLOAD_BYTES / (1024 * 1024))} MB web upload limit.`;
      setErrorMessage(message);
      setStatusMessage("Upload blocked.");
      return;
    }

    setActiveTask("uploading");
    setErrorMessage("");
    setStatusMessage(`Uploading ${file.name}…`);

    try {
      const response = await uploadPdf(file);
      setDocId(response.doc_id);
      setZoom(1);
      setCurrentPage(1);
      setPageInput("1");
      setSelectedPages([]);
      setPageOrder(Array.from({ length: response.page_count }, (_, index) => index + 1));
      setStatusMessage(`Uploaded ${response.filename}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Upload failed.");
      setStatusMessage("Upload failed.");
    } finally {
      setActiveTask(null);
    }
  }

  function handleUploadTriggerKeyDown(event: KeyboardEvent<HTMLLabelElement>) {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }
    event.preventDefault();
    if (!busy) {
      fileInputRef.current?.click();
    }
  }

  function clearSearchState(resetQuery = false) {
    if (resetQuery) {
      setSearchQuery("");
    }
    setActiveSearchQuery("");
    setSearchResults([]);
    setActiveSearchIndex(-1);
    setSearchBusy(false);
    setSearchError("");
  }

  function clearAnnotationSelection() {
    setAnnotationSelection(null);
    setSelectionResetToken((value) => value + 1);
    annotationRequestKeyRef.current = "";
  }

  function handleAnnotationModeToggle(nextMode: Exclude<AnnotationMode, null>) {
    const resolved = annotationMode === nextMode ? null : nextMode;
    setAnnotationMode(resolved);
    if (resolved === null) {
      clearAnnotationSelection();
      setStatusMessage(docId ? `Viewing page ${currentPage} of ${pageCount}.` : "Upload a PDF to begin.");
      return;
    }
    setErrorMessage("");
    setStatusMessage(`${resolved === "highlight" ? "Highlight" : "Underline"} mode active.`);
  }

  function exitAnnotationMode() {
    setAnnotationMode(null);
    clearAnnotationSelection();
    setStatusMessage(docId ? `Viewing page ${currentPage} of ${pageCount}.` : "Upload a PDF to begin.");
  }

  function selectPage(pageNumber: number) {
    if (pageCount <= 0) {
      return;
    }
    const nextPage = Math.max(1, Math.min(pageNumber, pageCount));
    setCurrentPage(nextPage);
    clearAnnotationSelection();
    setStatusMessage(`Viewing page ${nextPage} of ${pageCount}.`);
  }

  function activateSearchResult(index: number, results = searchResults) {
    if (results.length === 0) {
      setActiveSearchIndex(-1);
      return;
    }
    const normalizedIndex = ((index % results.length) + results.length) % results.length;
    const nextResult = results[normalizedIndex];
    setActiveSearchIndex(normalizedIndex);
    setCurrentPage(nextResult.page_number);
    setPageInput(String(nextResult.page_number));
    setStatusMessage(`Viewing match ${normalizedIndex + 1} of ${results.length} on page ${nextResult.page_number}.`);
  }

  async function runSearch(
    queryText: string,
    options?: {
      activate?: "first" | "preserve-page" | "none";
      preferredPage?: number;
      preserveStatus?: boolean;
    }
  ) {
    if (!docId) {
      return;
    }

    const trimmedQuery = queryText.trim();
    if (!trimmedQuery) {
      clearSearchState(false);
      if (!options?.preserveStatus) {
        setStatusMessage("Search cleared.");
      }
      return;
    }

    setSearchBusy(true);
    setSearchError("");
    setActiveSearchQuery(trimmedQuery);

    try {
      const response = await searchDocument(docId, trimmedQuery);
      setSearchResults(response.results);

      if (response.results.length === 0) {
        setActiveSearchIndex(-1);
        if (!options?.preserveStatus) {
          setStatusMessage(`No matches found for "${response.query}".`);
        }
        return;
      }

      const preferredPage = options?.preferredPage ?? currentPage;
      const preferredIndex =
        options?.activate === "preserve-page"
          ? response.results.findIndex((result) => result.page_number === preferredPage)
          : 0;

      if (options?.activate === "none") {
        setActiveSearchIndex(-1);
      } else {
        activateSearchResult(preferredIndex === -1 ? 0 : preferredIndex, response.results);
      }

      if (!options?.preserveStatus && options?.activate === "none") {
        setStatusMessage(
          response.total_matches === 1 ? `Found 1 match for "${response.query}".` : `Found ${response.total_matches} matches for "${response.query}".`
        );
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Search failed.";
      setSearchError(message);
      setSearchResults([]);
      setActiveSearchIndex(-1);
      if (!options?.preserveStatus) {
        setStatusMessage("Search failed.");
      }
    } finally {
      setSearchBusy(false);
    }
  }

  async function handleSearchSubmit() {
    if (!searchQuery.trim()) {
      setSearchError("Enter a word or phrase to search.");
      setStatusMessage("Search needs a query.");
      return;
    }
    await runSearch(searchQuery, { activate: "first" });
  }

  function handleSearchNavigation(direction: 1 | -1) {
    if (searchResults.length === 0) {
      return;
    }
    const originIndex = activeSearchIndex >= 0 ? activeSearchIndex : direction === 1 ? -1 : 0;
    activateSearchResult(originIndex + direction);
  }

  function handleClearSearch() {
    clearSearchState(true);
    setStatusMessage(docId ? `Viewing page ${currentPage} of ${pageCount}.` : "Upload a PDF to begin.");
  }

  function handleViewerSelectionChange(selection: AnnotationSelection | null) {
    setAnnotationSelection(selection);
    if (!annotationMode) {
      return;
    }
    if (!selection) {
      if (!busy) {
        setStatusMessage(`${annotationMode === "highlight" ? "Highlight" : "Underline"} mode active.`);
      }
      return;
    }
    setErrorMessage("");
    void handleDirectAnnotation(selection, annotationMode);
  }

  function toggleSelection(pageNumber: number) {
    setSelectedPages((previous) =>
      previous.includes(pageNumber) ? previous.filter((page) => page !== pageNumber) : [...previous, pageNumber].sort((a, b) => a - b)
    );
  }

  function handlePageInputCommit() {
    const parsed = Number(pageInput);
    if (!Number.isFinite(parsed)) {
      setPageInput(String(currentPage));
      return;
    }
    selectPage(parsed);
  }

  async function applyDocumentMutation(
    action: () => Promise<DocumentMetadata>,
    successMessage: string,
    nextPageResolver?: (nextMetadata: DocumentMetadata) => number,
    taskLabel = "updating document"
  ): Promise<boolean> {
    if (!docId) {
      return false;
    }

    setActiveTask(taskLabel);
    setErrorMessage("");

    try {
      const nextMetadata = await action();
      setMetadata(nextMetadata);
      setSelectedPages([]);
      setPageOrder(Array.from({ length: nextMetadata.page_count }, (_, index) => index + 1));
      const resolvedPage = nextPageResolver ? nextPageResolver(nextMetadata) : Math.max(1, Math.min(currentPage, nextMetadata.page_count));
      const nextPage = Math.max(1, Math.min(resolvedPage, nextMetadata.page_count));
      setCurrentPage(nextPage);
      setPageInput(String(nextPage));
      if (activeSearchQuery.trim()) {
        await runSearch(activeSearchQuery, {
          activate: "preserve-page",
          preferredPage: nextPage,
          preserveStatus: true,
        });
      }
      setStatusMessage(successMessage);
      return true;
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Document operation failed.");
      setStatusMessage("Operation failed.");
      return false;
    } finally {
      setActiveTask(null);
    }
  }

  async function handleRotate(degrees = 90, directionLabel = "clockwise") {
    if (!docId || selectedPages.length === 0) {
      return;
    }
    await applyDocumentMutation(
      () => rotatePages(docId, selectedPageIndices, degrees),
      `Rotated ${selectedPages.length} page(s) ${directionLabel}.`,
      undefined,
      directionLabel === "counterclockwise" ? "rotating pages counterclockwise" : "rotating pages clockwise"
    );
  }

  async function handleDelete() {
    if (!docId || selectedPages.length === 0) {
      return;
    }
    if (!window.confirm(`Delete ${selectedPages.length} selected page(s)?`)) {
      return;
    }

    const selectedSet = new Set(selectedPages);
    const fallbackPage = currentPage;
    await applyDocumentMutation(
      () => deletePages(docId, selectedPageIndices),
      `Deleted ${selectedPages.length} page(s).`,
      (nextMetadata) => {
        if (nextMetadata.page_count <= 0) {
          return 1;
        }
        const removedBefore = selectedPages.filter((page) => page < fallbackPage).length;
        const shiftedPage = fallbackPage - removedBefore;
        if (!selectedSet.has(fallbackPage)) {
          return Math.max(1, Math.min(shiftedPage, nextMetadata.page_count));
        }
        return Math.max(1, Math.min(shiftedPage, nextMetadata.page_count));
      },
      "deleting pages"
    );
  }

  async function handleExtract() {
    if (!docId || selectedPages.length === 0) {
      return;
    }

    setActiveTask("extracting pages");
    setErrorMessage("");
    try {
      const result = await extractPages(docId, selectedPageIndices);
      triggerBrowserDownload(result.blob, result.filename);
      setSelectedPages([]);
      setStatusMessage(`Extracted ${selectedPages.length} page(s).`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Extract failed.");
      setStatusMessage("Extract failed.");
    } finally {
      setActiveTask(null);
    }
  }

  async function handleSplit() {
    if (!docId || pageCount <= 0) {
      return;
    }

    const input = window.prompt(`Enter a page range like 1-${pageCount}`, `1-${pageCount}`);
    if (input === null) {
      return;
    }
    if (!input.includes("-")) {
      setErrorMessage("Enter a range like 1-3.");
      setStatusMessage("Split needs a valid range.");
      return;
    }

    const [startRaw, endRaw] = input.split("-", 2);
    const startPage = Number(startRaw.trim());
    const endPage = Number(endRaw.trim());
    if (!Number.isFinite(startPage) || !Number.isFinite(endPage) || startPage < 1 || endPage < startPage || endPage > pageCount) {
      setErrorMessage("Please enter a valid page range.");
      setStatusMessage("Split failed.");
      return;
    }

    setActiveTask("splitting document");
    setErrorMessage("");
    try {
      const result = await splitDocument(docId, startPage - 1, endPage - 1);
      triggerBrowserDownload(result.blob, result.filename);
      setSelectedPages([]);
      setStatusMessage(`Split pages ${startPage}-${endPage}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Split failed.");
      setStatusMessage("Split failed.");
    } finally {
      setActiveTask(null);
    }
  }

  async function handleReorder(sourcePage: number, targetPage: number) {
    if (!docId || sourcePage === targetPage) {
      return;
    }

    const sourceIndex = pageOrder.indexOf(sourcePage);
    const targetIndex = pageOrder.indexOf(targetPage);
    if (sourceIndex === -1 || targetIndex === -1) {
      return;
    }

    const nextOrder = [...pageOrder];
    const [moved] = nextOrder.splice(sourceIndex, 1);
    nextOrder.splice(targetIndex, 0, moved);
    const previousOrder = pageOrder;
    setPageOrder(nextOrder);

    const succeeded = await applyDocumentMutation(
      () => reorderPages(docId, nextOrder.map((pageNumber) => pageNumber - 1)),
      "Reordered pages.",
      undefined,
      "reordering pages"
    );
    if (!succeeded) {
      setPageOrder(previousOrder);
    }
  }

  async function handleDownload() {
    if (!docId) {
      return;
    }

    setActiveTask("downloading");
    setErrorMessage("");
    setStatusMessage("Preparing your PDF download…");

    try {
      const result = await downloadDocument(docId);
      triggerBrowserDownload(result.blob, result.filename);
      setStatusMessage(`Downloaded ${result.filename}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Download failed.");
      setStatusMessage("Download failed.");
    } finally {
      setActiveTask(null);
    }
  }

  async function handleDirectAnnotation(selection: AnnotationSelection, mode: Exclude<AnnotationMode, null>) {
    if (!docId) {
      return;
    }
    if (!textSelectionAvailable) {
      setErrorMessage("Text selection is not available on this page. Scanned or image-only PDFs are not supported for annotations yet.");
      setStatusMessage("Annotation unavailable.");
      return;
    }
    if (!selection.text.trim() || selection.rects.length === 0) {
      return;
    }

    const selectionKey = `${mode}:${selection.pageNumber}:${selection.text.trim()}:${selection.rects
      .map((rect) => `${rect.x0.toFixed(4)}:${rect.y0.toFixed(4)}:${rect.x1.toFixed(4)}:${rect.y1.toFixed(4)}`)
      .join("|")}`;
    if (annotationRequestKeyRef.current === selectionKey || busy) {
      return;
    }
    annotationRequestKeyRef.current = selectionKey;

    const succeeded = await applyDocumentMutation(
      () =>
        annotateDocument(
          docId,
          selection.pageNumber,
          mode,
          selection.text,
          selection.rects
        ),
      `${mode === "highlight" ? "Highlight" : "Underline"} added on page ${selection.pageNumber}.`,
      () => selection.pageNumber,
      `applying ${mode}`
    );

    if (succeeded) {
      clearAnnotationSelection();
      return;
    }
    annotationRequestKeyRef.current = "";
  }

  return (
    <main className="shell">
      <header className="toolbar">
        <div className="toolbar__group">
          <div className="brand">PDF App Web</div>
          <label
            className="upload-button"
            aria-label="Open PDF"
            title="Open PDF"
            role="button"
            tabIndex={busy ? -1 : 0}
            onKeyDown={handleUploadTriggerKeyDown}
          >
            <IconButtonLabel
              ariaLabel={activeTask === "uploading" ? "Uploading PDF" : "Open PDF"}
              title={activeTask === "uploading" ? "Uploading PDF" : "Open PDF"}
              label={activeTask === "uploading" ? "Uploading…" : "Open"}
              icon={<OpenIcon />}
              disabled={busy}
            />
            <input ref={fileInputRef} type="file" accept="application/pdf,.pdf" onChange={handleUpload} disabled={busy} />
          </label>
        </div>

        <div className="toolbar__group toolbar__group--controls">
          <div className="control-group" aria-label="Page navigation">
            <IconButton
              ariaLabel="Previous page"
              title="Previous page"
              icon={<ChevronLeftIcon />}
              onClick={() => selectPage(currentPage - 1)}
              disabled={controlsDisabled || currentPage <= 1}
            />
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
                disabled={controlsDisabled}
                aria-label="Current page"
              />
              <span>/ {pageCount || 0}</span>
            </div>
            <IconButton
              ariaLabel="Next page"
              title="Next page"
              icon={<ChevronRightIcon />}
              onClick={() => selectPage(currentPage + 1)}
              disabled={controlsDisabled || currentPage >= pageCount}
            />
          </div>

          <div className="control-group" aria-label="Zoom controls">
            <IconButton
              ariaLabel="Zoom out"
              title="Zoom out"
              icon={<ZoomOutIcon />}
              onClick={() => setZoom((value) => Math.max(MIN_ZOOM, value - ZOOM_STEP))}
              disabled={controlsDisabled}
            />
            <span className="badge badge--metric" title="Current zoom level">
              {zoomPercent}%
            </span>
            <IconButton
              ariaLabel="Zoom in"
              title="Zoom in"
              icon={<ZoomInIcon />}
              onClick={() => setZoom((value) => Math.min(MAX_ZOOM, value + ZOOM_STEP))}
              disabled={controlsDisabled}
            />
            <IconButton
              ariaLabel="Reset zoom"
              title="Reset zoom"
              icon={<ZoomResetIcon />}
              onClick={() => setZoom(1)}
              disabled={controlsDisabled}
            />
          </div>

          <div className="control-group" aria-label="Annotation controls">
            <IconButton
              ariaLabel="Toggle highlight mode"
              title="Toggle highlight mode"
              icon={<HighlightIcon />}
              onClick={() => handleAnnotationModeToggle("highlight")}
              disabled={controlsDisabled}
              active={annotationMode === "highlight"}
            />
            <IconButton
              ariaLabel="Toggle underline mode"
              title="Toggle underline mode"
              icon={<UnderlineIcon />}
              onClick={() => handleAnnotationModeToggle("underline")}
              disabled={controlsDisabled}
              active={annotationMode === "underline"}
            />
            <IconButton
              ariaLabel="Exit annotation mode"
              title="Exit annotation mode"
              icon={<ClearIcon />}
              onClick={exitAnnotationMode}
              disabled={controlsDisabled || annotationMode === null}
            />
          </div>

          <form
            className="searchbar"
            onSubmit={(event) => {
              event.preventDefault();
              void handleSearchSubmit();
            }}
          >
            <input
              type="search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search document text"
              disabled={controlsDisabled}
              aria-label="Search document text"
            />
            <div className="control-group" aria-label="Search controls">
              <IconButton
                type="submit"
                ariaLabel={searchBusy ? "Searching document text" : "Search document text"}
                title={searchBusy ? "Searching document text" : "Search document text"}
                icon={<SearchIcon />}
                disabled={controlsDisabled || searchBusy}
                active={searchBusy}
              />
              <IconButton
                ariaLabel="Previous search result"
                title="Previous search result"
                icon={<ChevronLeftIcon />}
                onClick={() => handleSearchNavigation(-1)}
                disabled={searchResults.length === 0 || busy || searchBusy}
              />
              <IconButton
                ariaLabel="Next search result"
                title="Next search result"
                icon={<ChevronRightIcon />}
                onClick={() => handleSearchNavigation(1)}
                disabled={searchResults.length === 0 || busy || searchBusy}
              />
              <IconButton
                ariaLabel="Clear search"
                title="Clear search"
                icon={<ClearIcon />}
                onClick={handleClearSearch}
                disabled={(!searchQuery && searchResults.length === 0) || busy || searchBusy}
              />
            </div>
          </form>
          <span className="search-summary">
            {searchBusy
              ? "Searching…"
              : searchResults.length === 0
                ? activeSearchQuery
                  ? "0 matches"
                  : "Search ready"
                : activeSearchResult
                  ? `${activeSearchIndex + 1} of ${searchResults.length} matches`
                  : `${searchResults.length} matches`}
          </span>
          <IconButton
            ariaLabel={activeTask === "downloading" ? "Downloading PDF" : "Download PDF"}
            title={activeTask === "downloading" ? "Downloading PDF" : "Download PDF"}
            icon={<DownloadIcon />}
            label={activeTask === "downloading" ? "Downloading…" : "Download"}
            onClick={() => void handleDownload()}
            disabled={controlsDisabled}
          />
        </div>
      </header>

      <section className="layout">
        <aside className="panel panel--rail">
          <h2>Pages</h2>
          <p>{docId ? "Click to view. Use Select to build a multi-page operation set. Drag to reorder." : "Upload a PDF to generate thumbnails."}</p>
          <ThumbnailRail
            pdfDocument={pdfDocument}
            pageOrder={pageOrder}
            selectedPages={selectedPages}
            currentPage={currentPage}
            onSelectPage={selectPage}
            onToggleSelection={toggleSelection}
            onReorder={handleReorder}
          />
        </aside>

        <section className="viewer-card">
          <div className="viewer-meta">
            <div>
              <div className="viewer-meta__title">{metadata?.filename || "No document loaded"}</div>
              <div className="viewer-meta__sub">
                {metadata
                  ? `Page ${currentPage} of ${pageCount} • ${metadata.size_bytes.toLocaleString()} bytes • v${metadata.version}`
                  : `API: ${apiBaseUrl()}`}
              </div>
            </div>
            {metadata ? <span className="badge">doc_id: {metadata.doc_id.slice(0, 8)}</span> : null}
          </div>

          <div className="viewer-stage">
            {viewerLoading && !pdfDocument ? <div className="status-note">Loading document and page thumbnails…</div> : null}
            <PdfViewer
              pdfDocument={pdfDocument}
              currentPage={currentPage}
              zoom={zoom}
              annotationMode={annotationMode}
              selectionResetToken={selectionResetToken}
              onSelectionChange={handleViewerSelectionChange}
              onTextSelectionAvailabilityChange={setTextSelectionAvailable}
            />
            <div className={`status-note ${errorMessage ? "status-note--error" : "status-note--info"}`}>
              {busy ? `Working: ${activeTask}…` : errorMessage || statusMessage}
            </div>
          </div>
        </section>

        <aside className="panel panel--side">
          <section className="side-section">
            <div className="action-list">
              <IconButton
                ariaLabel="Highlight mode"
                title="Highlight mode"
                icon={<HighlightIcon />}
                label="Highlight"
                variant="panel"
                onClick={() => handleAnnotationModeToggle("highlight")}
                disabled={controlsDisabled}
                active={annotationMode === "highlight"}
              />
              <IconButton
                ariaLabel="Underline mode"
                title="Underline mode"
                icon={<UnderlineIcon />}
                label="Underline"
                variant="panel"
                onClick={() => handleAnnotationModeToggle("underline")}
                disabled={controlsDisabled}
                active={annotationMode === "underline"}
              />
              <IconButton
                ariaLabel="Exit annotation mode"
                title="Exit annotation mode"
                icon={<ClearIcon />}
                label="Clear"
                variant="panel"
                onClick={exitAnnotationMode}
                disabled={controlsDisabled || annotationMode === null}
              />
            </div>
            {annotationMode ? (
              <div className="annotation-status">
                {busy && activeTask?.startsWith("applying ")
                  ? "Applying annotation…"
                  : !textSelectionAvailable
                    ? "Text selection unavailable on this page."
                    : annotationSelection?.text?.trim()
                      ? `${annotationMode === "highlight" ? "Highlighting" : "Underlining"} selected text…`
                      : `${annotationMode === "highlight" ? "Highlight" : "Underline"} mode`}
              </div>
            ) : null}
          </section>

          <section className="side-section">
            <h2>Search Results</h2>
            <p>
              {!docId
                ? "Upload a PDF to search its text."
                : activeSearchQuery
                  ? searchResults.length
                    ? `${searchResults.length} match${searchResults.length === 1 ? "" : "es"} for "${activeSearchQuery}".`
                    : searchBusy
                      ? "Searching document text…"
                      : "No matches for the current query."
                  : "Enter a term in the toolbar to search this PDF."}
            </p>
            <div className="search-results">
              {searchError ? <div className="search-results__empty search-results__empty--error">{searchError}</div> : null}
              {!searchError && !docId ? <div className="search-results__empty">No document loaded.</div> : null}
              {!searchError && docId && searchBusy ? <div className="search-results__empty">Searching…</div> : null}
              {!searchError && docId && !searchBusy && activeSearchQuery && searchResults.length === 0 ? (
                <div className="search-results__empty">No matches found.</div>
              ) : null}
              {!searchError && docId && !searchBusy && !activeSearchQuery ? (
                <div className="search-results__empty">Search results will appear here.</div>
              ) : null}
              {!searchError &&
                !searchBusy &&
                searchResults.map((result, index) => (
                  <button
                    key={`${result.page_number}-${index}`}
                    type="button"
                    className={`search-result ${index === activeSearchIndex ? "search-result--active" : ""}`}
                    onClick={() => activateSearchResult(index)}
                  >
                    <span className="search-result__meta">Page {result.page_number}</span>
                    <span className="search-result__snippet">{result.snippet}</span>
                  </button>
                ))}
            </div>
          </section>

          <section className="side-section">
            <h2>Page Actions</h2>
            <p>{selectedCount ? `${selectedCount} page(s) selected.` : "Select one or more pages from the thumbnail rail."}</p>
            <div className="action-list">
              <IconButton
                ariaLabel="Rotate selected pages counterclockwise"
                title="Rotate selected pages counterclockwise"
                icon={<RotateCcwIcon />}
                label="Rotate CCW"
                variant="panel"
                onClick={() => void handleRotate(270, "counterclockwise")}
                disabled={controlsDisabled || selectedCount === 0}
              />
              <IconButton
                ariaLabel="Rotate selected pages clockwise"
                title="Rotate selected pages clockwise"
                icon={<RotateCwIcon />}
                label="Rotate CW"
                variant="panel"
                onClick={() => void handleRotate(90, "clockwise")}
                disabled={controlsDisabled || selectedCount === 0}
              />
              <IconButton
                ariaLabel="Delete selected pages"
                title="Delete selected pages"
                icon={<TrashIcon />}
                label="Delete"
                variant="panel"
                onClick={handleDelete}
                disabled={controlsDisabled || selectedCount === 0}
              />
              <IconButton
                ariaLabel="Extract selected pages"
                title="Extract selected pages"
                icon={<ExtractIcon />}
                label="Extract"
                variant="panel"
                onClick={handleExtract}
                disabled={controlsDisabled || selectedCount === 0}
              />
              <IconButton
                ariaLabel="Split document by range"
                title="Split document by range"
                icon={<SplitIcon />}
                label="Split"
                variant="panel"
                onClick={handleSplit}
                disabled={controlsDisabled}
              />
            </div>
            <ul className="side-list">
              <li>Current page: {pageCount ? `${currentPage} / ${pageCount}` : "No document loaded"}</li>
              <li>Selected pages: {selectedPages.length ? selectedPages.join(", ") : "None"}</li>
              <li>Reorder by dragging thumbnails in the left rail.</li>
            </ul>
          </section>
        </aside>
      </section>
    </main>
  );
}
