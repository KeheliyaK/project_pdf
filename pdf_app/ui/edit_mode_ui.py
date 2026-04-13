from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QDropEvent, QFont, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from pdf_app.pdf_render.render_service import PdfRenderService

EDITOR_ICON_SIZE = QSize(120, 170)
EDITOR_ITEM_SIZE = QSize(140, 208)
EDITOR_GRID_SIZE = QSize(148, 216)


class EditorPageItemDelegate(QStyledItemDelegate):
    checkbox_clicked = Signal(int, object)

    @staticmethod
    def _is_checked(index) -> bool:
        state = index.data(Qt.ItemDataRole.CheckStateRole)
        if isinstance(state, Qt.CheckState):
            return state == Qt.CheckState.Checked
        if isinstance(state, int):
            return state == Qt.CheckState.Checked.value
        return False

    def paint(self, painter: QPainter, option, index) -> None:  # type: ignore[override]
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        card_rect = option.rect.adjusted(4, 4, -4, -4)
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        background = QColor("#eff6ff") if is_selected else QColor("#ffffff")
        border = QColor("#2563eb") if is_selected else QColor("#d0d7de")

        painter.setPen(QPen(border, 2 if is_selected else 1))
        painter.setBrush(background)
        painter.drawRoundedRect(card_rect, 8, 8)

        top_padding = 8
        side_padding = 8
        footer_height = 26
        thumb_area = QRect(
            card_rect.left() + side_padding,
            card_rect.top() + top_padding,
            card_rect.width() - side_padding * 2,
            card_rect.height() - top_padding - footer_height - 6,
        )

        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(icon, QIcon):
            pixmap = icon.pixmap(EDITOR_ICON_SIZE)
            display_width = min(EDITOR_ICON_SIZE.width(), thumb_area.width())
            display_height = min(EDITOR_ICON_SIZE.height(), thumb_area.height())
            pixmap_rect = QRect(
                thumb_area.left() + (thumb_area.width() - display_width) // 2,
                thumb_area.top(),
                display_width,
                display_height,
            )
            painter.drawPixmap(pixmap_rect, pixmap)

        footer_rect = QRect(
            card_rect.left() + side_padding,
            card_rect.bottom() - footer_height + 1,
            card_rect.width() - side_padding * 2,
            footer_height - 2,
        )

        checkbox_rect = QRect(
            footer_rect.center().x() - 8,
            footer_rect.center().y() - 8,
            16,
            16,
        )
        is_checked = self._is_checked(index)
        checkbox_border = QColor("#64748b")
        checkbox_fill = QColor("#ffffff")
        if is_checked:
            checkbox_border = QColor("#0f766e")
            checkbox_fill = QColor("#0f766e")
        painter.setPen(QPen(checkbox_border, 1.2))
        painter.setBrush(checkbox_fill)
        painter.drawRoundedRect(checkbox_rect, 3, 3)
        if is_checked:
            check_pen = QPen(QColor("#ffffff"), 2.4)
            check_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            check_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(check_pen)
            painter.drawLine(
                checkbox_rect.left() + 3,
                checkbox_rect.center().y(),
                checkbox_rect.left() + 6,
                checkbox_rect.bottom() - 4,
            )
            painter.drawLine(
                checkbox_rect.left() + 6,
                checkbox_rect.bottom() - 4,
                checkbox_rect.right() - 3,
                checkbox_rect.top() + 4,
            )

        page_number = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        number_rect = QRect(
            footer_rect.right() - 28,
            footer_rect.top(),
            28,
            footer_rect.height(),
        )
        font = QFont(option.font)
        font.setPointSize(max(font.pointSize() - 1, 9))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#334155"))
        painter.drawText(number_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, page_number)

        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:  # type: ignore[override]
        if event.type() in {QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonDblClick}:
            point = event.position().toPoint() if hasattr(event, "position") else event.pos()
            checkbox_rect = self._checkbox_rect(option.rect)
            if checkbox_rect.contains(point):
                return True
        if event.type() == QEvent.Type.MouseButtonRelease:
            point = event.position().toPoint() if hasattr(event, "position") else event.pos()
            checkbox_rect = self._checkbox_rect(option.rect)
            if checkbox_rect.contains(point):
                self.checkbox_clicked.emit(index.row(), event.modifiers())
                return True
        return super().editorEvent(event, model, option, index)

    def _checkbox_rect(self, rect: QRect) -> QRect:
        card_rect = rect.adjusted(4, 4, -4, -4)
        footer_height = 26
        footer_rect = QRect(card_rect.left() + 8, card_rect.bottom() - footer_height + 1, card_rect.width() - 16, footer_height - 2)
        return QRect(footer_rect.center().x() - 8, footer_rect.center().y() - 8, 16, 16)


class EditorMiniToolbar(QWidget):
    undo_requested = Signal()
    redo_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 6)
        layout.setSpacing(8)

        self.title_label = QLabel("Page Organization")
        self.hint_label = QLabel("Drag pages to reorder")
        self.selection_label = QLabel("0 pages selected")
        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")

        layout.addWidget(self.title_label)
        layout.addStretch(1)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.selection_label)
        layout.addWidget(self.undo_button)
        layout.addWidget(self.redo_button)

        self.undo_button.clicked.connect(self.undo_requested.emit)
        self.redo_button.clicked.connect(self.redo_requested.emit)

    def update_selection_count(self, count: int) -> None:
        self.selection_label.setText(f"{count} pages selected")

    def update_history_state(self, can_undo: bool, can_redo: bool) -> None:
        self.undo_button.setEnabled(can_undo)
        self.redo_button.setEnabled(can_redo)


class PageGridWidget(QListWidget):
    order_changed = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setWrapping(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setMovement(QListView.Movement.Snap)
        self.setGridSize(EDITOR_GRID_SIZE)
        self.setSpacing(8)
        self.setWordWrap(True)
        self.setIconSize(EDITOR_ICON_SIZE)
        self.setStyleSheet(
            "QListWidget::item { border: 1px solid #d0d7de; border-radius: 8px; padding: 6px; margin: 2px; background: white; }"
            "QListWidget::item:selected { border: 2px solid #2563eb; background: #eff6ff; color: #0f172a; }"
            "QListWidget::indicator { width: 16px; height: 16px; border: 1px solid #64748b; background: #111827; }"
            "QListWidget::indicator:checked { background: #0f766e; border: 1px solid #0f766e; }"
        )

    def dropEvent(self, event: QDropEvent) -> None:
        selected_rows = sorted(self.row(item) for item in self.selectedItems())
        if not selected_rows:
            event.ignore()
            return

        target_row = self._drop_row(event)
        if target_row == -1:
            target_row = self.count()

        moving_items = [self.takeItem(row) for row in reversed(selected_rows)]
        moving_items.reverse()

        removed_before_target = sum(1 for row in selected_rows if row < target_row)
        target_row -= removed_before_target
        target_row = max(0, min(target_row, self.count()))

        for offset, item in enumerate(moving_items):
            self.insertItem(target_row + offset, item)
            item.setSelected(True)

        event.acceptProposedAction()
        self.order_changed.emit([self.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.count())])

    def _drop_row(self, event: QDropEvent) -> int:
        point = event.position().toPoint()
        item = self.itemAt(point)
        if item is None:
            return self.count()
        row = self.row(item)
        item_rect = self.visualItemRect(item)
        if point.x() > item_rect.center().x():
            row += 1
        return row


class EditorWorkspace(QWidget):
    order_changed = Signal(list)
    selection_changed_pages = Signal(list)
    undo_requested = Signal()
    redo_requested = Signal()

    def __init__(self, render_service: PdfRenderService) -> None:
        super().__init__()
        self.render_service = render_service
        self._selected_pages: set[int] = set()
        self._syncing_selection = False
        self._selection_anchor_row: int | None = None
        self.mini_toolbar = EditorMiniToolbar()
        self.grid = PageGridWidget()
        self.page_delegate = EditorPageItemDelegate(self.grid)
        self.grid.setItemDelegate(self.page_delegate)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.mini_toolbar)
        layout.addWidget(self.grid, 1)

        self.grid.order_changed.connect(self.order_changed.emit)
        self.grid.itemSelectionChanged.connect(self._selection_changed_from_highlight)
        self.page_delegate.checkbox_clicked.connect(self._selection_changed_from_checkbox_click)
        self.mini_toolbar.undo_requested.connect(self.undo_requested.emit)
        self.mini_toolbar.redo_requested.connect(self.redo_requested.emit)

    def load_document(self, pdf_path: Path, page_count: int) -> None:
        self.grid.clear()
        self._selected_pages.clear()
        self._selection_anchor_row = None
        self.grid.setIconSize(EDITOR_ICON_SIZE)
        for page_index in range(page_count):
            item = QListWidgetItem(str(page_index + 1))
            item.setData(Qt.ItemDataRole.UserRole, page_index)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsDragEnabled
                | Qt.ItemFlag.ItemIsDropEnabled
            )
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setIcon(QIcon(self.render_service.render_editor_thumbnail(pdf_path, page_index, width=120)))
            item.setSizeHint(EDITOR_ITEM_SIZE)
            self.grid.addItem(item)
        self._apply_shared_selection()

    def selected_pages(self) -> list[int]:
        return sorted(self._selected_pages)

    def select_all_pages(self) -> None:
        self._selected_pages = {
            self.grid.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.grid.count())
        }
        if self.grid.count():
            self._selection_anchor_row = 0
        self._apply_shared_selection()

    def set_history_state(self, can_undo: bool, can_redo: bool) -> None:
        self.mini_toolbar.update_history_state(can_undo, can_redo)

    def _selection_changed_from_checkbox_click(self, row: int, modifiers) -> None:
        if row < 0 or row >= self.grid.count():
            return

        extend_range = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        page_index = self.grid.item(row).data(Qt.ItemDataRole.UserRole)
        selected_pages = set(self._selected_pages)

        if extend_range and self._selection_anchor_row is not None:
            start, end = sorted((self._selection_anchor_row, row))
            range_pages = {
                self.grid.item(range_row).data(Qt.ItemDataRole.UserRole)
                for range_row in range(start, end + 1)
            }
            selected_pages |= range_pages
            self._selection_anchor_row = row
        else:
            if page_index in selected_pages:
                selected_pages.remove(page_index)
            else:
                selected_pages.add(page_index)
            self._selection_anchor_row = row

        self._selected_pages = selected_pages
        self._apply_shared_selection()

    def _selection_changed_from_highlight(self) -> None:
        if self._syncing_selection:
            return
        self._selected_pages = {
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.grid.selectedItems()
        }
        if not (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier):
            current_row = self.grid.currentRow()
            if current_row >= 0:
                self._selection_anchor_row = current_row
        self._apply_shared_selection()

    def _apply_shared_selection(self) -> None:
        self._syncing_selection = True
        for row in range(self.grid.count()):
            item = self.grid.item(row)
            is_selected = item.data(Qt.ItemDataRole.UserRole) in self._selected_pages
            item.setCheckState(Qt.CheckState.Checked if is_selected else Qt.CheckState.Unchecked)
            item.setSelected(is_selected)
        self._syncing_selection = False
        selected_pages = sorted(self._selected_pages)
        self.mini_toolbar.update_selection_count(len(selected_pages))
        self.selection_changed_pages.emit(selected_pages)
        self.grid.viewport().update()
