"use client";

import { DragEvent, MouseEvent, useEffect, useRef, useState } from "react";

import type { PdfDocumentProxyLike } from "../lib/pdfjs";

type ThumbnailRailProps = {
  pdfDocument: PdfDocumentProxyLike | null;
  pageOrder: number[];
  selectedPages: number[];
  currentPage: number;
  onSelectPage: (pageNumber: number) => void;
  onToggleSelection: (pageNumber: number) => void;
  onReorder: (sourcePage: number, targetPage: number) => void;
};

type ThumbnailItemProps = {
  pdfDocument: PdfDocumentProxyLike;
  pageNumber: number;
  isActive: boolean;
  isSelected: boolean;
  onSelectPage: (pageNumber: number) => void;
  onToggleSelection: (pageNumber: number) => void;
  onReorder: (sourcePage: number, targetPage: number) => void;
};

function ThumbnailItem({
  pdfDocument,
  pageNumber,
  isActive,
  isSelected,
  onSelectPage,
  onToggleSelection,
  onReorder,
}: ThumbnailItemProps) {
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

  function handleSelectClick(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation();
    onToggleSelection(pageNumber);
  }

  function handleDragStart(event: DragEvent<HTMLDivElement>) {
    event.dataTransfer.setData("text/plain", String(pageNumber));
    event.dataTransfer.effectAllowed = "move";
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const sourcePage = Number(event.dataTransfer.getData("text/plain"));
    if (Number.isFinite(sourcePage) && sourcePage !== pageNumber) {
      onReorder(sourcePage, pageNumber);
    }
  }

  return (
    <div
      className={`thumbnail-button ${isActive ? "thumbnail-button--active" : ""} ${isSelected ? "thumbnail-button--selected" : ""}`}
      draggable
      onDragStart={handleDragStart}
      onDragOver={(event) => event.preventDefault()}
      onDrop={handleDrop}
      onClick={() => onSelectPage(pageNumber)}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelectPage(pageNumber);
        }
      }}
    >
      <div className="thumbnail-button__canvas">
        <canvas ref={canvasRef} className="thumbnail-canvas" />
      </div>
      <div className="thumbnail-button__footer">
        <span>Page {pageNumber}</span>
        <div className="thumbnail-button__actions">
          {error ? <span className="thumbnail-button__error">!</span> : null}
          <button
            type="button"
            className={`thumbnail-select ${isSelected ? "thumbnail-select--active" : ""}`}
            onClick={handleSelectClick}
            aria-label={`${isSelected ? "Deselect" : "Select"} page ${pageNumber}`}
          >
            {isSelected ? "Selected" : "Select"}
          </button>
        </div>
      </div>
    </div>
  );
}

export function ThumbnailRail({
  pdfDocument,
  pageOrder,
  selectedPages,
  currentPage,
  onSelectPage,
  onToggleSelection,
  onReorder,
}: ThumbnailRailProps) {
  if (!pdfDocument || pageOrder.length === 0) {
    return (
      <div className="thumb-placeholder">
        <div className="thumb-card">Upload a PDF to generate page thumbnails.</div>
      </div>
    );
  }

  return (
    <div className="thumbnail-list">
      {pageOrder.map((pageNumber) => (
        <ThumbnailItem
          key={pageNumber}
          pdfDocument={pdfDocument}
          pageNumber={pageNumber}
          isActive={currentPage === pageNumber}
          isSelected={selectedPages.includes(pageNumber)}
          onSelectPage={onSelectPage}
          onToggleSelection={onToggleSelection}
          onReorder={onReorder}
        />
      ))}
    </div>
  );
}
