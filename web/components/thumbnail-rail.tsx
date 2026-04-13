"use client";

import { useEffect, useRef, useState } from "react";

import type { PdfDocumentProxyLike } from "../lib/pdfjs";

type ThumbnailRailProps = {
  pdfDocument: PdfDocumentProxyLike | null;
  pageCount: number;
  currentPage: number;
  onSelectPage: (pageNumber: number) => void;
};

type ThumbnailItemProps = {
  pdfDocument: PdfDocumentProxyLike;
  pageNumber: number;
  isActive: boolean;
  onSelectPage: (pageNumber: number) => void;
};

function ThumbnailItem({ pdfDocument, pageNumber, isActive, onSelectPage }: ThumbnailItemProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    let active = true;
    let renderTask: { cancel: () => void; promise: Promise<void> } | null = null;

    async function renderThumbnail() {
      const canvas = canvasRef.current;
      if (!canvas) {
        return;
      }

      try {
        const page = await pdfDocument.getPage(pageNumber);
        if (!active) {
          return;
        }

        const baseViewport = (page as { getViewport: (args: { scale: number }) => { width: number; height: number } }).getViewport({
          scale: 1,
        });
        const thumbnailWidth = 140;
        const scale = thumbnailWidth / Math.max(baseViewport.width, 1);
        const viewport = (page as { getViewport: (args: { scale: number }) => { width: number; height: number } }).getViewport({
          scale,
        });

        const context = canvas.getContext("2d", { alpha: false });
        if (!context) {
          throw new Error("Thumbnail canvas context unavailable.");
        }

        const pixelRatio = window.devicePixelRatio || 1;
        canvas.width = Math.max(1, Math.floor(viewport.width * pixelRatio));
        canvas.height = Math.max(1, Math.floor(viewport.height * pixelRatio));
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;

        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
        context.fillStyle = "#ffffff";
        context.fillRect(0, 0, viewport.width, viewport.height);

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
        if (active) {
          setError("");
        }
      } catch (renderError) {
        if (active) {
          setError(renderError instanceof Error ? renderError.message : "Thumbnail render failed.");
        }
      }
    }

    void renderThumbnail();

    return () => {
      active = false;
      renderTask?.cancel();
    };
  }, [pdfDocument, pageNumber]);

  return (
    <button
      type="button"
      className={`thumbnail-button ${isActive ? "thumbnail-button--active" : ""}`}
      onClick={() => onSelectPage(pageNumber)}
      aria-pressed={isActive}
    >
      <div className="thumbnail-button__canvas">
        <canvas ref={canvasRef} className="thumbnail-canvas" />
      </div>
      <div className="thumbnail-button__footer">
        <span>Page {pageNumber}</span>
        {error ? <span className="thumbnail-button__error">!</span> : null}
      </div>
    </button>
  );
}

export function ThumbnailRail({ pdfDocument, pageCount, currentPage, onSelectPage }: ThumbnailRailProps) {
  if (!pdfDocument || pageCount <= 0) {
    return (
      <div className="thumb-placeholder">
        <div className="thumb-card">Upload a PDF to generate page thumbnails.</div>
      </div>
    );
  }

  return (
    <div className="thumbnail-list">
      {Array.from({ length: pageCount }, (_, index) => {
        const pageNumber = index + 1;
        return (
          <ThumbnailItem
            key={pageNumber}
            pdfDocument={pdfDocument}
            pageNumber={pageNumber}
            isActive={currentPage === pageNumber}
            onSelectPage={onSelectPage}
          />
        );
      })}
    </div>
  );
}
