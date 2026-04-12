from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QRubberBand, QScrollArea, QVBoxLayout, QWidget

from pdf_app.annotations.models import Annotation
from pdf_app.pdf_render.render_service import PageMetrics, PdfRenderService


class ClickablePageLabel(QLabel):
    clicked = Signal(int)
    position_clicked = Signal(int, float, float)
    selection_drag_completed = Signal(int, float, float, float, float)

    def __init__(self, page_index: int) -> None:
        super().__init__()
        self.page_index = page_index
        self.drag_selection_enabled = False
        self._drag_origin: QPoint | None = None
        self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setStyleSheet(
            "background: white; border: 1px solid #c9d1d9; padding: 0px; border-radius: 6px;"
        )

    def set_drag_selection_enabled(self, enabled: bool) -> None:
        self.drag_selection_enabled = enabled
        if not enabled:
            self._drag_origin = None
            self._rubber_band.hide()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        if self.drag_selection_enabled and event.button() == Qt.MouseButton.LeftButton:
            point = event.position().toPoint()
            self._drag_origin = point
            self._rubber_band.setGeometry(QRect(point, QSize()))
            self._rubber_band.show()
            event.accept()
            return
        point = event.position() if hasattr(event, "position") else event.pos()
        self.position_clicked.emit(self.page_index, float(point.x()), float(point.y()))
        self.clicked.emit(self.page_index)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if self.drag_selection_enabled and self._drag_origin is not None:
            current = event.position().toPoint()
            self._rubber_band.setGeometry(QRect(self._drag_origin, current).normalized())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if self.drag_selection_enabled and self._drag_origin is not None and event.button() == Qt.MouseButton.LeftButton:
            end_point = event.position().toPoint()
            start_point = self._drag_origin
            self._drag_origin = None
            self._rubber_band.hide()
            if (end_point - start_point).manhattanLength() >= 6:
                self.selection_drag_completed.emit(
                    self.page_index,
                    float(start_point.x()),
                    float(start_point.y()),
                    float(end_point.x()),
                    float(end_point.y()),
                )
            event.accept()
            return
        self._drag_origin = None
        self._rubber_band.hide()
        super().mouseReleaseEvent(event)


class ViewerWorkspace(QWidget):
    page_clicked = Signal(int)
    page_focus_changed = Signal(int)
    page_position_clicked = Signal(int, float, float)
    page_region_selected = Signal(int, float, float, float, float)

    def __init__(self, render_service: PdfRenderService) -> None:
        super().__init__()
        self.render_service = render_service
        self.annotation_provider = lambda _page_index: []
        self.selected_annotation_provider = lambda _page_index: set()
        self.scroll_area = QScrollArea()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.container = QWidget()
        self.container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.pages_layout = QVBoxLayout(self.container)
        self.pages_layout.setContentsMargins(24, 24, 24, 24)
        self.pages_layout.setSpacing(24)
        self.scroll_area.setWidget(self.container)
        self.scroll_area.viewport().setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self.refresh_visible_pages)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self._schedule_refresh)
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self._schedule_refresh)

        self.page_widgets: list[ClickablePageLabel] = []
        self.page_metrics: list[PageMetrics] = []
        self.pdf_path: Path | None = None
        self.zoom_percent = 100
        self._active_page = 0
        self._drag_selection_enabled = False

    def load_document(self, pdf_path: Path, page_count: int, zoom_percent: int) -> None:
        self.clear()
        self.pdf_path = pdf_path
        self.zoom_percent = zoom_percent
        self.page_metrics = self.render_service.page_metrics(pdf_path)[:page_count]

        for page_index in range(page_count):
            label = ClickablePageLabel(page_index)
            label.setText(f"Loading page {page_index + 1}…")
            label.clicked.connect(self.page_clicked.emit)
            label.position_clicked.connect(self._emit_document_position_click)
            label.selection_drag_completed.connect(self._emit_document_region_selection)
            label.set_drag_selection_enabled(self._drag_selection_enabled)
            self.pages_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.page_widgets.append(label)

        self.pages_layout.addStretch(1)
        self._apply_placeholder_sizes()
        self._schedule_refresh()

    def clear(self) -> None:
        self.pdf_path = None
        self.page_metrics = []
        while self.pages_layout.count():
            item = self.pages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.page_widgets.clear()

    def scroll_to_page(self, page_index: int) -> None:
        if 0 <= page_index < len(self.page_widgets):
            self.scroll_area.ensureWidgetVisible(self.page_widgets[page_index], 0, 24)
            self._active_page = page_index
            self._schedule_refresh()

    def focus_document_view(self) -> None:
        self.scroll_area.viewport().setFocus(Qt.FocusReason.ShortcutFocusReason)

    def set_annotation_provider(self, provider) -> None:
        self.annotation_provider = provider
        self._schedule_refresh()

    def set_selected_annotation_provider(self, provider) -> None:
        self.selected_annotation_provider = provider
        self._schedule_refresh()

    def set_drag_selection_enabled(self, enabled: bool) -> None:
        self._drag_selection_enabled = enabled
        for widget in self.page_widgets:
            widget.set_drag_selection_enabled(enabled)

    def set_annotation_cursor_enabled(self, enabled: bool) -> None:
        cursor = Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor
        self.setCursor(cursor)
        self.scroll_area.viewport().setCursor(cursor)
        for widget in self.page_widgets:
            widget.setCursor(cursor)

    def refresh_visible_pages(self) -> None:
        if not self.pdf_path or not self.page_widgets:
            return

        viewport_rect = QRect(QPoint(0, 0), self.scroll_area.viewport().size())
        content_width = max(360, self.scroll_area.viewport().width() - 48)
        best_index = self._active_page
        best_distance = None

        for index, widget in enumerate(self.page_widgets):
            widget_rect = self._widget_rect_in_viewport(widget)
            self._apply_placeholder_size(index, content_width)
            if widget_rect.bottom() >= -viewport_rect.height() and widget_rect.top() <= viewport_rect.height() * 2:
                pixmap = self.render_service.render_view_page(
                    self.pdf_path,
                    index,
                    self.zoom_percent,
                    content_width,
                    device_pixel_ratio=self.devicePixelRatioF(),
                )
                annotations: list[Annotation] = self.annotation_provider(index) if self.annotation_provider else []
                if index < len(self.page_metrics):
                    pixmap = self.render_service.draw_annotation_overlays(
                        pixmap,
                        self.page_metrics[index],
                        annotations,
                        self.selected_annotation_provider(index) if self.selected_annotation_provider else set(),
                    )
                widget.setPixmap(pixmap)
                widget.resize(
                    int(pixmap.width() / pixmap.devicePixelRatio()),
                    int(pixmap.height() / pixmap.devicePixelRatio()),
                )
                widget.setText("")

            distance = abs(widget_rect.center().y() - viewport_rect.center().y())
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_index = index

        if best_index != self._active_page:
            self._active_page = best_index
            self.page_focus_changed.emit(best_index)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._schedule_refresh()

    def _apply_placeholder_sizes(self) -> None:
        content_width = max(360, self.scroll_area.viewport().width() - 48)
        for index in range(len(self.page_widgets)):
            self._apply_placeholder_size(index, content_width)

    def _apply_placeholder_size(self, index: int, content_width: int) -> None:
        if not (0 <= index < len(self.page_widgets)) or not (0 <= index < len(self.page_metrics)):
            return
        metrics = self.page_metrics[index]
        fit_scale = content_width / max(metrics.width, 1.0)
        display_scale = fit_scale * (self.zoom_percent / 100.0)
        width = max(240, int(metrics.width * display_scale))
        height = max(320, int(metrics.height * display_scale))
        self.page_widgets[index].setMinimumSize(width, height)
        self.page_widgets[index].setMaximumWidth(width)

    def _widget_rect_in_viewport(self, widget: QWidget) -> QRect:
        top_left = widget.mapTo(self.scroll_area.viewport(), QPoint(0, 0))
        return QRect(top_left, widget.size())

    def _schedule_refresh(self) -> None:
        self._refresh_timer.start(0)

    def _emit_document_position_click(self, page_index: int, local_x: float, local_y: float) -> None:
        if not (0 <= page_index < len(self.page_widgets)) or not (0 <= page_index < len(self.page_metrics)):
            return
        widget = self.page_widgets[page_index]
        metrics = self.page_metrics[page_index]
        width = max(float(widget.width()), 1.0)
        height = max(float(widget.height()), 1.0)
        document_x = max(0.0, min(metrics.width, (local_x / width) * metrics.width))
        document_y = max(0.0, min(metrics.height, (local_y / height) * metrics.height))
        self.page_position_clicked.emit(page_index, document_x, document_y)

    def _emit_document_region_selection(
        self,
        page_index: int,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
    ) -> None:
        if not (0 <= page_index < len(self.page_widgets)) or not (0 <= page_index < len(self.page_metrics)):
            return
        widget = self.page_widgets[page_index]
        metrics = self.page_metrics[page_index]
        width = max(float(widget.width()), 1.0)
        height = max(float(widget.height()), 1.0)
        document_start_x = max(0.0, min(metrics.width, (start_x / width) * metrics.width))
        document_start_y = max(0.0, min(metrics.height, (start_y / height) * metrics.height))
        document_end_x = max(0.0, min(metrics.width, (end_x / width) * metrics.width))
        document_end_y = max(0.0, min(metrics.height, (end_y / height) * metrics.height))
        self.page_region_selected.emit(
            page_index,
            document_start_x,
            document_start_y,
            document_end_x,
            document_end_y,
        )
