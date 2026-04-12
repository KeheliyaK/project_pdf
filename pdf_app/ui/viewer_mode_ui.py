from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from pdf_app.pdf_render.render_service import PageMetrics, PdfRenderService


class ClickablePageLabel(QLabel):
    clicked = Signal(int)

    def __init__(self, page_index: int) -> None:
        super().__init__()
        self.page_index = page_index
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setStyleSheet(
            "background: white; border: 1px solid #c9d1d9; padding: 0px; border-radius: 6px;"
        )

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.clicked.emit(self.page_index)
        super().mousePressEvent(event)


class ViewerWorkspace(QWidget):
    page_clicked = Signal(int)
    page_focus_changed = Signal(int)

    def __init__(self, render_service: PdfRenderService) -> None:
        super().__init__()
        self.render_service = render_service
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

    def load_document(self, pdf_path: Path, page_count: int, zoom_percent: int) -> None:
        self.clear()
        self.pdf_path = pdf_path
        self.zoom_percent = zoom_percent
        self.page_metrics = self.render_service.page_metrics(pdf_path)[:page_count]

        for page_index in range(page_count):
            label = ClickablePageLabel(page_index)
            label.setText(f"Loading page {page_index + 1}…")
            label.clicked.connect(self.page_clicked.emit)
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
