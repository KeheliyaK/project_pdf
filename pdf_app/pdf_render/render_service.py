from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import fitz
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPixmap


@dataclass(frozen=True)
class PageMetrics:
    width: float
    height: float


class PdfRenderService:
    def __init__(self) -> None:
        self._thumbnail_cache: OrderedDict[tuple[str, str, int, int], QPixmap] = OrderedDict()
        self._viewer_cache: OrderedDict[tuple[str, int, int, int], QPixmap] = OrderedDict()
        self._page_metrics_cache: dict[str, list[PageMetrics]] = {}
        self._cache_limit = 48

    def page_metrics(self, pdf_path: Path) -> list[PageMetrics]:
        cache_key = str(pdf_path.resolve())
        if cache_key not in self._page_metrics_cache:
            document = fitz.open(pdf_path)
            self._page_metrics_cache[cache_key] = [
                PageMetrics(width=page.rect.width, height=page.rect.height) for page in document
            ]
            document.close()
        return self._page_metrics_cache[cache_key]

    def render_view_page(
        self,
        pdf_path: Path,
        page_index: int,
        zoom_percent: int,
        viewport_width: int,
        device_pixel_ratio: float = 1.0,
    ) -> QPixmap:
        resolved = str(pdf_path.resolve())
        width_bucket = max(320, int(viewport_width))
        cache_key = (resolved, page_index, zoom_percent, width_bucket)
        cached = self._viewer_cache.get(cache_key)
        if cached is not None:
            self._viewer_cache.move_to_end(cache_key)
            return cached

        document = fitz.open(pdf_path)
        page = document.load_page(page_index)
        page_rect = page.rect

        fit_scale = width_bucket / max(page_rect.width, 1.0)
        display_scale = fit_scale * (zoom_percent / 100.0)
        oversample = max(1.75, device_pixel_ratio)
        render_scale = display_scale * oversample

        matrix = fitz.Matrix(render_scale, render_scale)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888,
        ).copy()
        document.close()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(oversample)
        self._remember(self._viewer_cache, cache_key, pixmap)
        return pixmap

    def render_sidebar_thumbnail(self, pdf_path: Path, page_index: int, width: int = 156) -> QPixmap:
        return self._render_thumbnail(pdf_path, page_index, width, "sidebar", oversample=1.25)

    def render_editor_thumbnail(self, pdf_path: Path, page_index: int, width: int = 176) -> QPixmap:
        return self._render_thumbnail(pdf_path, page_index, width, "editor", oversample=1.5)

    def _render_thumbnail(
        self,
        pdf_path: Path,
        page_index: int,
        width: int,
        context: str,
        oversample: float,
    ) -> QPixmap:
        resolved = str(pdf_path.resolve())
        cache_key = (resolved, context, page_index, width)
        cached = self._thumbnail_cache.get(cache_key)
        if cached is not None:
            self._thumbnail_cache.move_to_end(cache_key)
            return cached

        document = fitz.open(pdf_path)
        page = document.load_page(page_index)
        base_scale = width / max(page.rect.width, 1.0)
        render_scale = base_scale * oversample
        pix = page.get_pixmap(matrix=fitz.Matrix(render_scale, render_scale), alpha=False)
        image = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888,
        ).copy()
        document.close()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(oversample)
        self._remember(self._thumbnail_cache, cache_key, pixmap)
        return pixmap

    def thumbnail_size(self, pdf_path: Path, page_index: int, width: int = 176, context: str = "editor") -> QSize:
        if context == "sidebar":
            pixmap = self.render_sidebar_thumbnail(pdf_path, page_index, width=width)
        else:
            pixmap = self.render_editor_thumbnail(pdf_path, page_index, width=width)
        return pixmap.size()

    def clear_document_cache(self, pdf_path: Path | None) -> None:
        if pdf_path is None:
            self._thumbnail_cache.clear()
            self._viewer_cache.clear()
            self._page_metrics_cache.clear()
            return

        resolved = str(pdf_path.resolve())
        self._thumbnail_cache = OrderedDict(
            (key, value) for key, value in self._thumbnail_cache.items() if key[0] != resolved
        )
        self._viewer_cache = OrderedDict(
            (key, value) for key, value in self._viewer_cache.items() if key[0] != resolved
        )
        self._page_metrics_cache.pop(resolved, None)

    def _remember(self, cache: OrderedDict, key: tuple, pixmap: QPixmap) -> None:
        cache[key] = pixmap
        cache.move_to_end(key)
        while len(cache) > self._cache_limit:
            cache.popitem(last=False)
