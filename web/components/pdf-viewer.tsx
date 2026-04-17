"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import type { AnnotationRect } from "../lib/types";
import type { PdfDocumentProxyLike } from "../lib/pdfjs";

type ViewerPhase =
  | "idle"
  | "page-loading"
  | "page-loaded"
  | "rendering"
  | "ready"
  | "error";

type AnnotationMode = "highlight" | "underline" | null;

type PdfViewerSelection = {
  pageNumber: number;
  text: string;
  rects: AnnotationRect[];
};

type PdfViewerProps = {
  pdfDocument: PdfDocumentProxyLike | null;
  currentPage: number;
  zoom: number;
  annotationMode?: AnnotationMode;
  selectionResetToken?: number;
  onSelectionChange?: (selection: PdfViewerSelection | null) => void;
  onTextSelectionAvailabilityChange?: (available: boolean) => void;
};

type ViewerState = {
  phase: ViewerPhase;
  message: string;
};

type TextLayerItem = {
  key: string;
  text: string;
  left: number;
  top: number;
  fontSize: number;
  width: number;
  height: number;
};

type ViewportLike = {
  width: number;
  height: number;
  transform: [number, number, number, number, number, number];
  scale: number;
};

type TextContentItemLike = {
  str?: string;
  transform?: [number, number, number, number, number, number];
  width?: number;
  height?: number;
};

type TextContentLike = {
  items?: TextContentItemLike[];
};

function logViewer(message: string, details?: Record<string, unknown>) {
  if (details) {
    console.log(`[pdf-viewer] ${message}`, details);
    return;
  }
  console.log(`[pdf-viewer] ${message}`);
}

function multiplyTransform(
  first: [number, number, number, number, number, number],
  second: [number, number, number, number, number, number]
): [number, number, number, number, number, number] {
  return [
    first[0] * second[0] + first[2] * second[1],
    first[1] * second[0] + first[3] * second[1],
    first[0] * second[2] + first[2] * second[3],
    first[1] * second[2] + first[3] * second[3],
    first[0] * second[4] + first[2] * second[5] + first[4],
    first[1] * second[4] + first[3] * second[5] + first[5],
  ];
}

function normalizeRect(value: number, dimension: number): number {
  if (dimension <= 0) {
    return 0;
  }
  return Math.max(0, Math.min(1, value / dimension));
}

export function PdfViewer({
  pdfDocument,
  currentPage,
  zoom,
  annotationMode = null,
  selectionResetToken = 0,
  onSelectionChange,
  onTextSelectionAvailabilityChange,
}: PdfViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const textLayerRef = useRef<HTMLDivElement | null>(null);
  const renderAttemptRef = useRef(0);
  const [viewerState, setViewerState] = useState<ViewerState>({
    phase: "idle",
    message: "Upload a PDF to start viewing pages.",
  });
  const [textItems, setTextItems] = useState<TextLayerItem[]>([]);
  const [viewportSize, setViewportSize] = useState<{ width: number; height: number }>({
    width: 0,
    height: 0,
  });

  const showOverlay = viewerState.phase !== "ready" && viewerState.phase !== "idle";
  const textSelectionEnabled = annotationMode !== null && textItems.length > 0;

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
        setTextItems([]);
        setViewportSize({ width: 0, height: 0 });
        onTextSelectionAvailabilityChange?.(false);
        onSelectionChange?.(null);
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
        const page = (await pdfDocument.getPage(currentPage)) as {
          getViewport: (args: { scale: number }) => ViewportLike;
          getTextContent: () => Promise<TextContentLike>;
          render: (args: {
            canvasContext: CanvasRenderingContext2D;
            viewport: ViewportLike;
          }) => { cancel: () => void; promise: Promise<void> };
        };
        if (!active) {
          return;
        }

        setViewerState({
          phase: "page-loaded",
          message: `Page ${currentPage} loaded. Preparing canvas…`,
        });
        logViewer("page loaded", { attempt, currentPage });

        const viewport = page.getViewport({ scale: zoom });
        setViewportSize({ width: viewport.width, height: viewport.height });

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

        const textContent = await page.getTextContent();
        if (!active) {
          return;
        }
        const nextTextItems = (textContent.items || [])
          .map((item, index) => {
            if (!item.str || !item.transform) {
              return null;
            }
            const transformed = multiplyTransform(viewport.transform, item.transform);
            const fontHeight = Math.max(1, Math.hypot(transformed[2], transformed[3]));
            const width = Math.max((item.width || 0) * viewport.scale, 1);
            return {
              key: `${currentPage}-${index}`,
              text: item.str,
              left: transformed[4],
              top: transformed[5] - fontHeight,
              fontSize: fontHeight,
              width,
              height: fontHeight * 1.2,
            } satisfies TextLayerItem;
          })
          .filter((item): item is TextLayerItem => item !== null && item.text.trim().length > 0);
        setTextItems(nextTextItems);
        onTextSelectionAvailabilityChange?.(nextTextItems.length > 0);

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
          textItems: nextTextItems.length,
        });

        renderTask = page.render({
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
        setTextItems([]);
        onTextSelectionAvailabilityChange?.(false);
        onSelectionChange?.(null);
        logViewer("render failed", { attempt, currentPage, error: message });
      }
    }

    void renderActivePage();

    return () => {
      active = false;
      renderTask?.cancel();
    };
  }, [currentPage, onSelectionChange, onTextSelectionAvailabilityChange, pdfDocument, zoom]);

  useEffect(() => {
    if (!selectionResetToken) {
      return;
    }
    window.getSelection()?.removeAllRanges();
    onSelectionChange?.(null);
  }, [onSelectionChange, selectionResetToken]);

  useEffect(() => {
    if (annotationMode !== null) {
      return;
    }
    window.getSelection()?.removeAllRanges();
    onSelectionChange?.(null);
  }, [annotationMode, onSelectionChange]);

  useEffect(() => {
    if (!textSelectionEnabled) {
      return;
    }

    let animationFrameId = 0;
    const handlePointerSelectionEnd = () => {
      animationFrameId = window.requestAnimationFrame(() => {
        captureSelection();
      });
    };

    document.addEventListener("mouseup", handlePointerSelectionEnd);
    document.addEventListener("touchend", handlePointerSelectionEnd);

    return () => {
      if (animationFrameId) {
        window.cancelAnimationFrame(animationFrameId);
      }
      document.removeEventListener("mouseup", handlePointerSelectionEnd);
      document.removeEventListener("touchend", handlePointerSelectionEnd);
    };
  }, [textSelectionEnabled]);

  function captureSelection() {
    if (!textSelectionEnabled) {
      onSelectionChange?.(null);
      return;
    }

    const selection = window.getSelection();
    const textLayer = textLayerRef.current;
    if (!selection || !textLayer || selection.rangeCount === 0 || selection.isCollapsed) {
      onSelectionChange?.(null);
      return;
    }

    const range = selection.getRangeAt(0);
    const commonAncestor = range.commonAncestorContainer;
    const selectionRoot = commonAncestor.nodeType === Node.TEXT_NODE ? commonAncestor.parentNode : commonAncestor;
    if (!selectionRoot || !textLayer.contains(selectionRoot)) {
      onSelectionChange?.(null);
      return;
    }

    const layerBounds = textLayer.getBoundingClientRect();
    const rects = Array.from(range.getClientRects())
      .filter((rect) => rect.width > 0 && rect.height > 0)
      .map((rect) => ({
        x0: normalizeRect(rect.left - layerBounds.left, layerBounds.width),
        y0: normalizeRect(rect.top - layerBounds.top, layerBounds.height),
        x1: normalizeRect(rect.right - layerBounds.left, layerBounds.width),
        y1: normalizeRect(rect.bottom - layerBounds.top, layerBounds.height),
      }))
      .filter((rect) => rect.x1 > rect.x0 && rect.y1 > rect.y0);

    if (rects.length === 0) {
      onSelectionChange?.(null);
      return;
    }

    onSelectionChange?.({
      pageNumber: currentPage,
      text: selection.toString(),
      rects,
    });
  }

  const textLayerClassName = useMemo(
    () => `text-layer ${textSelectionEnabled ? "text-layer--selectable" : "text-layer--disabled"}`,
    [textSelectionEnabled]
  );

  return (
    <div className="viewer-surface">
      {!pdfDocument ? (
        <div className="viewer-empty">{viewerState.message}</div>
      ) : (
        <>
          <div className="canvas-frame">
            <div
              className={`page-layer ${annotationMode ? `page-layer--${annotationMode}` : ""}`}
              style={{
                width: viewportSize.width ? `${Math.floor(viewportSize.width)}px` : undefined,
                height: viewportSize.height ? `${Math.floor(viewportSize.height)}px` : undefined,
              }}
            >
              <canvas ref={canvasRef} className="viewer-canvas" />
              <div
                ref={textLayerRef}
                className={textLayerClassName}
                onMouseUp={captureSelection}
                onKeyUp={captureSelection}
                onTouchEnd={captureSelection}
              >
                {textItems.map((item) => (
                  <span
                    key={item.key}
                    className="text-layer__item"
                    style={{
                      left: `${item.left}px`,
                      top: `${item.top}px`,
                      width: `${item.width}px`,
                      height: `${item.height}px`,
                      fontSize: `${item.fontSize}px`,
                    }}
                  >
                    {item.text}
                  </span>
                ))}
              </div>
            </div>
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
