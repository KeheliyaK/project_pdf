"use client";

import { useEffect, useRef, useState } from "react";

import type { PdfDocumentProxyLike } from "../lib/pdfjs";

type ViewerPhase =
  | "idle"
  | "page-loading"
  | "page-loaded"
  | "rendering"
  | "ready"
  | "error";

type PdfViewerProps = {
  pdfDocument: PdfDocumentProxyLike | null;
  currentPage: number;
  zoom: number;
};

type ViewerState = {
  phase: ViewerPhase;
  message: string;
};

function logViewer(message: string, details?: Record<string, unknown>) {
  if (details) {
    console.log(`[pdf-viewer] ${message}`, details);
    return;
  }
  console.log(`[pdf-viewer] ${message}`);
}

export function PdfViewer({ pdfDocument, currentPage, zoom }: PdfViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const renderAttemptRef = useRef(0);
  const [viewerState, setViewerState] = useState<ViewerState>({
    phase: "idle",
    message: "Upload a PDF to start viewing pages.",
  });

  useEffect(() => {
    let active = true;
    let renderTask: { cancel: () => void; promise: Promise<void> } | null = null;

    async function renderActivePage() {
      const attempt = renderAttemptRef.current + 1;
      renderAttemptRef.current = attempt;

      if (!pdfDocument) {
        setViewerState({
          phase: "idle",
          message: "Upload a PDF to start viewing pages.",
        });
        logViewer("render skipped: no document");
        return;
      }

      const canvas = canvasRef.current;
      if (!canvas) {
        setViewerState({
          phase: "error",
          message: "Viewer phase failed: canvas element was not available before rendering started.",
        });
        logViewer("render failed: canvas missing before page load");
        return;
      }

      logViewer("zoom/page-triggered rerender", { attempt, zoom, currentPage });
      setViewerState({
        phase: "page-loading",
        message: `Loading page ${currentPage}…`,
      });

      try {
        const page = await pdfDocument.getPage(currentPage);
        if (!active) {
          return;
        }

        setViewerState({
          phase: "page-loaded",
          message: `Page ${currentPage} loaded. Preparing canvas…`,
        });
        logViewer("page loaded", { attempt, currentPage });

        const viewport = (page as { getViewport: (args: { scale: number }) => { width: number; height: number } }).getViewport({
          scale: zoom,
        });

        const context = canvas.getContext("2d", { alpha: false });
        if (!context) {
          throw new Error("canvas context acquisition failed");
        }
        logViewer("canvas context acquired", {
          attempt,
          currentPage,
          viewportWidth: viewport.width,
          viewportHeight: viewport.height,
        });

        const pixelRatio = window.devicePixelRatio || 1;
        const intrinsicWidth = Math.max(1, Math.floor(viewport.width * pixelRatio));
        const intrinsicHeight = Math.max(1, Math.floor(viewport.height * pixelRatio));

        canvas.width = intrinsicWidth;
        canvas.height = intrinsicHeight;
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;

        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
        context.fillStyle = "#ffffff";
        context.fillRect(0, 0, viewport.width, viewport.height);

        setViewerState({
          phase: "rendering",
          message: `Rendering page ${currentPage}…`,
        });
        logViewer("render started", {
          attempt,
          currentPage,
          viewportWidth: viewport.width,
          viewportHeight: viewport.height,
          canvasWidth: canvas.width,
          canvasHeight: canvas.height,
          cssWidth: canvas.style.width,
          cssHeight: canvas.style.height,
          pixelRatio,
        });

        renderTask = (page as {
          render: (args: {
            canvasContext: CanvasRenderingContext2D;
            viewport: { width: number; height: number };
          }) => { cancel: () => void; promise: Promise<void> };
        }).render({
          canvasContext: context,
          viewport,
        });

        await renderTask.promise;
        if (!active) {
          return;
        }

        setViewerState({
          phase: "ready",
          message: `Page ${currentPage} rendered.`,
        });
        logViewer("render completed", {
          attempt,
          currentPage,
          canvasWidth: canvas.width,
          canvasHeight: canvas.height,
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : "unknown render failure";
        setViewerState({
          phase: "error",
          message: `Viewer phase failed on page ${currentPage}: ${message}`,
        });
        logViewer("render failed", { attempt, currentPage, error: message });
      }
    }

    void renderActivePage();

    return () => {
      active = false;
      renderTask?.cancel();
    };
  }, [pdfDocument, currentPage, zoom]);

  const showOverlay = viewerState.phase !== "ready" && viewerState.phase !== "idle";

  return (
    <div className="viewer-surface">
      {!pdfDocument ? (
        <div className="viewer-empty">{viewerState.message}</div>
      ) : (
        <>
          <div className="canvas-frame">
            <canvas ref={canvasRef} className="viewer-canvas" />
          </div>
          {showOverlay ? (
            <div className={`viewer-overlay ${viewerState.phase === "error" ? "viewer-overlay--error" : ""}`}>
              <div className="viewer-overlay__card">
                <strong>{viewerState.phase === "error" ? "Render error" : "Rendering PDF"}</strong>
                <div>{viewerState.message}</div>
              </div>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
