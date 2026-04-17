from __future__ import annotations

import os
import tempfile
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from pdf_app.annotations.models import AnnotationRect, AnnotationType
from pdf_app.pdf_ops.pdf_operation_service import PdfOperationService
from pdf_app.pdf_render.render_service import PdfRenderService
from pdf_app.services.annotation_service import AnnotationService
from pdf_app.services.pdf_access_service import (
    PdfAccessService,
    PdfInvalidPasswordError,
    PdfPasswordRequiredError,
)
from pdf_app.services.document_manager import DocumentManager
from pdf_app.services.export_service import ExportService
from pdf_app.services.operation_history import OperationHistoryService
from pdf_app.services.search_service import SearchService
from pdf_app.services.unified_history_service import UnifiedHistoryService
from pdf_app.state.mode_state import AppMode
from pdf_app.ui.dialogs.merge_dialog import MergeDialog
from pdf_app.ui.dialogs.shortcut_guide_dialog import ShortcutGuideDialog
from pdf_app.ui.app_tool_rail import AppToolRail, TOOL_HIGHLIGHT, TOOL_SEARCH, TOOL_UNDERLINE
from pdf_app.ui.edit_mode_ui import EditorWorkspace
from pdf_app.ui.home_screen import HomeScreen
from pdf_app.ui.right_tool_pane import RightToolPane
from pdf_app.ui.status_bar import AppStatusBar
from pdf_app.ui.toolbar import MainToolbar
from pdf_app.ui.viewer_mode_ui import ViewerWorkspace


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MyLeaflet - Mini Launch v0.2")
        self.resize(1480, 940)
        self.setAcceptDrops(True)

        self.document_manager = DocumentManager()
        self.render_service = PdfRenderService()
        self.operation_service = PdfOperationService()
        self.export_service = ExportService()
        self.search_service = SearchService()
        self.history_service = OperationHistoryService()
        self.unified_history_service = UnifiedHistoryService()
        self.annotation_service = AnnotationService()
        self.pdf_access_service = PdfAccessService()
        self.active_annotation_tool: AnnotationType | None = None
        self.selected_annotation_ids: set[str] = set()

        self.mode = AppMode.HOME
        self._banner_timer = QTimer(self)
        self._banner_timer.setSingleShot(True)
        self._banner_timer.timeout.connect(self._clear_banner)

        self.toolbar_widget = MainToolbar()
        self.status_widget = AppStatusBar()
        self.left_pane = QListWidget()
        self.center_stack = QStackedWidget()
        self.right_pane = RightToolPane()
        self.tool_rail = AppToolRail()
        self.home_screen = HomeScreen()
        self.viewer_workspace = ViewerWorkspace(self.render_service)
        self.viewer_workspace.set_annotation_provider(self._annotations_for_page)
        self.viewer_workspace.set_selected_annotation_provider(self._selected_annotations_for_page)
        self.editor_workspace = EditorWorkspace(self.render_service)
        self.banner_label = QLabel("")
        self.banner_label.setStyleSheet("background:#3a3f46; color:#f1f3f5; padding:8px;")
        self.banner_label.hide()

        self._build_ui()
        self._build_menus()
        self._build_shortcuts()
        self._connect_signals()
        self._set_document_controls_enabled(False)
        self._update_history_ui()
        self._update_annotation_ui()
        self.right_pane.show_placeholder()
        self.right_pane.hide_context_panel()
        self.tool_rail.set_mode("home")
        self._refresh_home_recents()

    def _build_ui(self) -> None:
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.toolbar_widget)
        shell_layout.addWidget(self.banner_label)

        self.left_pane.setViewMode(QListView.ViewMode.IconMode)
        self.left_pane.setResizeMode(QListView.ResizeMode.Adjust)
        self.left_pane.setMovement(QListView.Movement.Static)
        self.left_pane.setFlow(QListView.Flow.TopToBottom)
        self.left_pane.setWrapping(False)
        self.left_pane.setSpacing(16)
        self.left_pane.setIconSize(QSize(156, 208))
        self.left_pane.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.left_pane.setStyleSheet(
            "QListWidget::item { border: 1px solid #d0d7de; border-radius: 8px; padding: 8px; margin: 4px; }"
            "QListWidget::item:selected { border: 2px solid #3b82a0; background: #edf6fb; }"
        )

        content_widget = QWidget()
        content_widget.setObjectName("mainContentArea")
        content_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        splitter = QSplitter()
        splitter.setObjectName("mainContentSplitter")
        splitter.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.center_stack.setObjectName("mainCenterStack")
        self.center_stack.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        splitter.addWidget(self.left_pane)
        splitter.addWidget(self.center_stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([250, 920])

        content_layout.addWidget(splitter, 1)
        content_layout.addWidget(self.tool_rail, 0)

        self.center_stack.addWidget(self.home_screen)
        self.center_stack.addWidget(self.viewer_workspace)
        self.center_stack.addWidget(self.editor_workspace)

        content_widget.setStyleSheet(
            """
            QWidget#mainContentArea,
            QSplitter#mainContentSplitter,
            QStackedWidget#mainCenterStack {
                background-color: #3a3f46;
            }
            """
        )

        shell_layout.addWidget(content_widget, 1)
        shell_layout.addWidget(self.status_widget)
        self.setCentralWidget(shell)
        self.right_pane.setParent(shell)

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        help_menu = menu_bar.addMenu("Help")

        self.open_action = QAction("Open PDF", self)
        self.merge_action = QAction("Merge PDFs", self)
        self.save_as_action = QAction("Save As", self)
        self.exit_action = QAction("Exit", self)
        self.undo_action = QAction("Undo", self)
        self.redo_action = QAction("Redo", self)
        self.shortcuts_guide_action = QAction("Keyboard Shortcuts", self)

        file_menu.addAction(self.open_action)
        file_menu.addAction(self.merge_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        help_menu.addAction(self.shortcuts_guide_action)

    def _build_shortcuts(self) -> None:
        self.open_action.setShortcuts(QKeySequence.StandardKey.Open)
        self.save_as_action.setShortcuts(QKeySequence.StandardKey.SaveAs)
        self.undo_action.setShortcuts(QKeySequence.StandardKey.Undo)
        self.redo_action.setShortcuts(QKeySequence.StandardKey.Redo)
        self.exit_action.setShortcuts(QKeySequence.StandardKey.Quit)

        self.find_action = QAction("Find", self)
        self.find_action.setShortcuts(QKeySequence.StandardKey.Find)
        self.find_action.triggered.connect(self.focus_search)
        self.addAction(self.find_action)

        self.find_next_action = QAction("Find Next", self)
        self.find_next_action.setShortcuts(QKeySequence.StandardKey.FindNext)
        self.find_next_action.triggered.connect(self.search_next_result)
        self.addAction(self.find_next_action)

        self.find_previous_action = QAction("Find Previous", self)
        self.find_previous_action.setShortcuts(QKeySequence.StandardKey.FindPrevious)
        self.find_previous_action.triggered.connect(self.search_previous_result)
        self.addAction(self.find_previous_action)

        self.fullscreen_action = QAction("Toggle Full Screen", self)
        self.fullscreen_action.setShortcut(QKeySequence("F11"))
        self.fullscreen_action.triggered.connect(self._toggle_fullscreen)
        self.addAction(self.fullscreen_action)

        self.zoom_in_shortcut = QShortcut(QKeySequence(QKeySequence.StandardKey.ZoomIn), self)
        self.zoom_in_shortcut.activated.connect(lambda: self._adjust_zoom_shortcut(10))
        self.zoom_in_alternate_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.zoom_in_alternate_shortcut.activated.connect(lambda: self._adjust_zoom_shortcut(10))
        self.zoom_out_shortcut = QShortcut(QKeySequence(QKeySequence.StandardKey.ZoomOut), self)
        self.zoom_out_shortcut.activated.connect(lambda: self._adjust_zoom_shortcut(-10))
        self.zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        self.zoom_reset_shortcut.activated.connect(self.reset_zoom)

        self.next_page_shortcut = QShortcut(QKeySequence("PgDown"), self)
        self.next_page_shortcut.activated.connect(self.next_page)
        self.previous_page_shortcut = QShortcut(QKeySequence("PgUp"), self)
        self.previous_page_shortcut.activated.connect(self.previous_page)
        self.previous_page_arrow_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self.viewer_workspace)
        self.previous_page_arrow_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.previous_page_arrow_shortcut.activated.connect(self.previous_page_arrow)
        self.next_page_arrow_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self.viewer_workspace)
        self.next_page_arrow_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.next_page_arrow_shortcut.activated.connect(self.next_page_arrow)

        self.delete_pages_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.editor_workspace)
        self.delete_pages_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.delete_pages_shortcut.activated.connect(self.delete_selected_pages_shortcut)
        self.select_all_pages_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.SelectAll),
            self.editor_workspace,
        )
        self.select_all_pages_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.select_all_pages_shortcut.activated.connect(self.select_all_editor_pages)

        self.highlight_tool_shortcut = QShortcut(QKeySequence("H"), self.viewer_workspace)
        self.highlight_tool_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.highlight_tool_shortcut.activated.connect(
            lambda: self._activate_annotation_tool_shortcut(AnnotationType.HIGHLIGHT)
        )
        self.underline_tool_shortcut = QShortcut(QKeySequence("U"), self.viewer_workspace)
        self.underline_tool_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.underline_tool_shortcut.activated.connect(
            lambda: self._activate_annotation_tool_shortcut(AnnotationType.UNDERLINE)
        )
        self.clear_annotation_tool_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self.viewer_workspace)
        self.clear_annotation_tool_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.clear_annotation_tool_shortcut.activated.connect(self._clear_annotation_tool_shortcut)
        self.delete_annotation_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.viewer_workspace)
        self.delete_annotation_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.delete_annotation_shortcut.activated.connect(self.delete_selected_annotations)

    def _connect_signals(self) -> None:
        self.toolbar_widget.merge_requested.connect(self.open_merge_workflow)
        self.toolbar_widget.viewer_mode_requested.connect(lambda: self.switch_mode(AppMode.VIEWER))
        self.toolbar_widget.editor_mode_requested.connect(self._switch_to_editor)
        self.toolbar_widget.undo_requested.connect(self.undo_last_action)
        self.toolbar_widget.redo_requested.connect(self.redo_last_action)
        self.toolbar_widget.search_requested.connect(self.perform_search)

        self.open_action.triggered.connect(self.open_pdf_dialog)
        self.merge_action.triggered.connect(self.open_merge_workflow)
        self.save_as_action.triggered.connect(self.save_as_dialog)
        self.exit_action.triggered.connect(self.close)
        self.undo_action.triggered.connect(self.undo_last_action)
        self.redo_action.triggered.connect(self.redo_last_action)
        self.shortcuts_guide_action.triggered.connect(self.show_shortcut_guide)

        self.status_widget.page_jump_requested.connect(self.jump_to_page)

        self.home_screen.open_requested.connect(self.open_pdf_dialog)
        self.home_screen.merge_requested.connect(self.open_merge_workflow)
        self.home_screen.file_dropped.connect(self.open_pdf)
        self.home_screen.recent_open_requested.connect(self.open_pdf)

        self.left_pane.itemClicked.connect(self._thumbnail_clicked)
        self.viewer_workspace.page_clicked.connect(self._page_clicked)
        self.viewer_workspace.page_position_clicked.connect(self._place_annotation_from_click)
        self.viewer_workspace.page_region_selected.connect(self._place_annotation_from_drag)
        self.viewer_workspace.page_focus_changed.connect(self._viewer_page_focus_changed)
        self.editor_workspace.order_changed.connect(self._reorder_pages)
        self.editor_workspace.selection_changed_pages.connect(self._editor_selection_changed)
        self.editor_workspace.undo_requested.connect(self.undo_last_action)
        self.editor_workspace.redo_requested.connect(self.redo_last_action)

        self.right_pane.viewer_pane.search_requested.connect(self.perform_search)
        self.right_pane.viewer_pane.previous_requested.connect(self.search_service.previous_result)
        self.right_pane.viewer_pane.next_requested.connect(self.search_service.next_result)
        self.right_pane.viewer_pane.result_activated.connect(self.search_service.activate_index)
        self.right_pane.viewer_pane.annotation_tool_selected.connect(self.set_active_annotation_tool)
        self.right_pane.viewer_pane.annotation_tool_cleared.connect(self.clear_active_annotation_tool)
        self.right_pane.viewer_pane.annotation_reset_requested.connect(self.reset_document_annotations)
        self.right_pane.viewer_pane.annotation_delete_requested.connect(self.delete_selected_annotations)
        self.right_pane.viewer_pane.rotate_selected_requested.connect(self.rotate_current_or_selected_pages)
        self.right_pane.viewer_pane.rotate_all_requested.connect(self.rotate_all_pages)

        self.right_pane.editor_pane.delete_requested.connect(self.delete_selected_pages)
        self.right_pane.editor_pane.rotate_selected_requested.connect(self.rotate_selected_pages_editor)
        self.right_pane.editor_pane.rotate_all_requested.connect(self.rotate_all_pages)
        self.right_pane.editor_pane.extract_requested.connect(self.extract_selected_pages)
        self.right_pane.editor_pane.split_requested.connect(self.split_by_range)
        self.tool_rail.tool_selected.connect(self._on_rail_tool_selected)
        self.tool_rail.tool_deselected.connect(self._on_rail_tool_deselected)
        self.tool_rail.fullscreen_requested.connect(self._toggle_fullscreen)
        self.tool_rail.zoom_in_requested.connect(lambda: self.adjust_zoom(10))
        self.tool_rail.zoom_out_requested.connect(lambda: self.adjust_zoom(-10))
        self.tool_rail.rotate_page_cw_requested.connect(lambda: self.rotate_current_or_selected_pages(90))
        self.tool_rail.rotate_page_ccw_requested.connect(lambda: self.rotate_current_or_selected_pages(-90))
        self.tool_rail.rotate_doc_cw_requested.connect(lambda: self.rotate_all_pages(90))
        self.tool_rail.rotate_doc_ccw_requested.connect(lambda: self.rotate_all_pages(-90))
        self.tool_rail.cancel_tool_requested.connect(self.clear_active_annotation_tool)
        self.tool_rail.delete_annotation_requested.connect(self.delete_selected_annotations)
        self.tool_rail.reset_annotations_requested.connect(self.reset_document_annotations)
        self.tool_rail.extract_pages_requested.connect(self.extract_selected_pages)
        self.tool_rail.split_requested.connect(self.split_by_range)
        self.tool_rail.delete_pages_requested.connect(self.delete_selected_pages)
        self.right_pane.close_requested.connect(self._hide_search_context_panel)

        self.search_service.results_updated.connect(self.right_pane.viewer_pane.set_results)
        self.search_service.active_result_changed.connect(self._activate_search_result)
        self.annotation_service.annotations_changed.connect(self.viewer_workspace.refresh_visible_pages)
        self.annotation_service.annotations_changed.connect(self._update_annotation_ui)
        self.document_manager.document_changed.connect(self._refresh_title)
        self.document_manager.dirty_changed.connect(self._update_dirty_state)

    def open_pdf_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if path:
            self.open_pdf(path)

    def open_pdf(self, path: str) -> None:
        source_path = Path(path)
        if self.document_manager.state.has_document and not self._confirm_discard_changes():
            return
        recent_status = self.document_manager.recent_file_status(source_path)
        if recent_status != "available":
            self.document_manager.remove_recent(source_path)
            self._refresh_home_recents()
            if recent_status == "missing":
                QMessageBox.warning(self, "Recent file missing", f"{source_path.name} could not be found.")
            else:
                QMessageBox.warning(self, "Recent file unavailable", f"{source_path.name} is no longer accessible.")
            return
        try:
            if not self._open_document_with_password_prompt(source_path):
                return
            self.annotation_service.open_document(self.document_manager.state.working_path, force_reset=True)
            self.selected_annotation_ids.clear()
            self.clear_active_annotation_tool()
            self.history_service.clear()
            self.unified_history_service.clear()
            self.render_service.clear_document_cache(self.document_manager.state.working_path)
            self._reload_document_views()
            self.switch_mode(AppMode.VIEWER)
            self._refresh_home_recents()
            self.status_widget.update_state("Document opened")
            self._update_history_ui()
        except Exception as exc:
            QMessageBox.critical(self, "Open failed", f"Could not open the PDF.\n\n{exc}")

    def _reload_document_views(self) -> None:
        state = self.document_manager.state
        if not state.working_path:
            return
        self.render_service.clear_document_cache(state.working_path)
        self.viewer_workspace.load_document(state.working_path, state.page_count, state.zoom_percent)
        self._load_thumbnails()
        self.editor_workspace.load_document(state.working_path, state.page_count)
        self.status_widget.update_page_status(state.current_page, state.page_count)
        self.status_widget.update_zoom(state.zoom_percent)
        self.search_service.clear()
        self._set_document_controls_enabled(True)
        self.right_pane.viewer_pane.set_annotation_tool(self.active_annotation_tool)
        self._sync_annotation_tool_state()
        self._editor_selection_changed([])
        self._update_history_ui()
        self._update_annotation_ui()

    def _load_thumbnails(self) -> None:
        state = self.document_manager.state
        self.left_pane.clear()
        if not state.working_path:
            return
        for page_index in range(state.page_count):
            item = QListWidgetItem(str(page_index + 1))
            item.setData(Qt.ItemDataRole.UserRole, page_index)
            item.setIcon(QIcon(self.render_service.render_sidebar_thumbnail(state.working_path, page_index, width=156)))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(QSize(188, 272))
            self.left_pane.addItem(item)

    def perform_search(self, query: str) -> None:
        results = self.search_service.search(self.document_manager.state.working_path, query)
        normalized_query = query.strip()
        self.right_pane.viewer_pane.search_input.setText(query)
        self.toolbar_widget.search_input.setText(query)
        if not normalized_query:
            self._hide_search_context_panel()
            self.status_widget.update_state("Search cleared")
            return
        self.clear_active_annotation_tool()
        self._show_search_context_panel()
        if results:
            self.status_widget.update_state(f"{len(results)} result(s) for '{normalized_query}'")
        else:
            self.right_pane.viewer_pane.show_no_results(normalized_query)
            self.status_widget.update_state(f"No results for '{normalized_query}'")

    def _activate_search_result(self, result, index: int, total: int) -> None:
        self._show_search_context_panel()
        self.right_pane.viewer_pane.set_active_result(index, total)
        self.jump_to_page(result.page_index)
        self.status_widget.update_state(f"Search result {index} of {total}")

    def switch_mode(self, mode: AppMode) -> None:
        if mode in (AppMode.VIEWER, AppMode.EDITOR) and not self.document_manager.state.has_document:
            return
        self.mode = mode
        if mode == AppMode.HOME:
            self.center_stack.setCurrentWidget(self.home_screen)
            self.right_pane.show_placeholder()
            self.right_pane.hide_context_panel()
            self.toolbar_widget.set_mode("")
            self.tool_rail.set_mode("home")
        elif mode == AppMode.VIEWER:
            self.center_stack.setCurrentWidget(self.viewer_workspace)
            self.right_pane.show_viewer()
            self.right_pane.hide_context_panel()
            self.toolbar_widget.set_mode("viewer")
            self.tool_rail.set_mode("viewer")
        elif mode == AppMode.EDITOR:
            self.center_stack.setCurrentWidget(self.editor_workspace)
            self.right_pane.show_editor()
            self.right_pane.hide_context_panel()
            self.toolbar_widget.set_mode("editor")
            self.tool_rail.set_mode("editor")

    def _switch_to_editor(self) -> None:
        if not self.document_manager.state.has_document:
            return
        self.switch_mode(AppMode.EDITOR)

    def _on_rail_tool_selected(self, tool_name: str) -> None:
        if tool_name == TOOL_SEARCH:
            self.focus_search()
            return
        if tool_name == TOOL_HIGHLIGHT:
            self._hide_search_context_panel()
            self.set_active_annotation_tool(AnnotationType.HIGHLIGHT)
            return
        if tool_name == TOOL_UNDERLINE:
            self._hide_search_context_panel()
            self.set_active_annotation_tool(AnnotationType.UNDERLINE)

    def _on_rail_tool_deselected(self) -> None:
        self.clear_active_annotation_tool()
        self._hide_search_context_panel()

    def _thumbnail_clicked(self, item: QListWidgetItem) -> None:
        page_index = item.data(Qt.ItemDataRole.UserRole)
        self.jump_to_page(page_index)

    def _page_clicked(self, page_index: int) -> None:
        self.jump_to_page(page_index)

    def _place_annotation_from_click(self, page_index: int, document_x: float, document_y: float) -> None:
        if self.mode != AppMode.VIEWER:
            return
        self.jump_to_page(page_index)
        if self.active_annotation_tool is None:
            self._select_annotation_at(page_index, document_x, document_y)
            return
        if self.active_annotation_tool != AnnotationType.TEXT_BOX:
            return
        text_content, ok = QInputDialog.getText(self, "Add text box", "Text box content:")
        if not ok or not text_content.strip():
            return
        rect = self._annotation_rect_at(page_index, document_x, document_y, width=180.0, height=72.0)
        self.annotation_service.add_annotation(
            AnnotationType.TEXT_BOX,
            page_index=page_index,
            rect=rect,
            text_content=text_content.strip(),
        )
        self.selected_annotation_ids.clear()
        self.unified_history_service.record_action("annotation", "Add text box")
        self._update_history_ui()
        self._mark_annotations_unsaved("Text box added. Session annotations are not embedded by Save As yet.")

    def _place_annotation_from_drag(
        self,
        page_index: int,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
    ) -> None:
        if self.mode != AppMode.VIEWER or self.active_annotation_tool not in {
            AnnotationType.HIGHLIGHT,
            AnnotationType.UNDERLINE,
        }:
            return
        self.jump_to_page(page_index)
        rect = self._annotation_rect_from_drag(page_index, start_x, start_y, end_x, end_y)
        if rect is None:
            return
        self.annotation_service.add_annotation(
            self.active_annotation_tool,
            page_index=page_index,
            rect=rect,
        )
        self.selected_annotation_ids.clear()
        self.unified_history_service.record_action("annotation", f"Add {self.active_annotation_tool.value}")
        self._update_history_ui()
        message = "Highlight added. Session annotations are not embedded by Save As yet."
        if self.active_annotation_tool == AnnotationType.UNDERLINE:
            message = "Underline added. Session annotations are not embedded by Save As yet."
        self._mark_annotations_unsaved(message)

    def _viewer_page_focus_changed(self, page_index: int) -> None:
        state = self.document_manager.state
        if not state.has_document or page_index == state.current_page:
            return
        self.document_manager.set_current_page(page_index)
        self.status_widget.update_page_status(page_index, state.page_count)
        if 0 <= page_index < self.left_pane.count():
            self.left_pane.setCurrentRow(page_index)
        self._sync_search_to_page(page_index)

    def jump_to_page(self, page_index: int) -> None:
        state = self.document_manager.state
        if not state.has_document or not (0 <= page_index < state.page_count):
            return
        self.document_manager.set_current_page(page_index)
        self.viewer_workspace.scroll_to_page(page_index)
        self.status_widget.update_page_status(page_index, state.page_count)
        self._sync_search_to_page(page_index)
        if 0 <= page_index < self.left_pane.count():
            self.left_pane.setCurrentRow(page_index)

    def adjust_zoom(self, delta: int) -> None:
        state = self.document_manager.state
        if not state.has_document or self.mode == AppMode.HOME:
            return
        new_zoom = max(50, min(250, state.zoom_percent + delta))
        self.document_manager.set_zoom_percent(new_zoom)
        self._reload_document_views()
        self.jump_to_page(state.current_page)

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def rotate_current_or_selected_pages(self, degrees: int) -> None:
        selected = self._selected_viewer_pages()
        if not selected:
            selected = [self.document_manager.state.current_page]
        self._apply_operation(
            f"Rotate {degrees} degrees",
            lambda tmp: self.operation_service.rotate_pages(self.document_manager.working_path(), selected, tmp, degrees),
            track_history=True,
        )

    def rotate_selected_pages_editor(self, degrees: int) -> None:
        selected = self.editor_workspace.selected_pages()
        if not selected:
            return
        self._apply_operation(
            f"Rotate selected {degrees} degrees",
            lambda tmp: self.operation_service.rotate_pages(self.document_manager.working_path(), selected, tmp, degrees),
            track_history=True,
        )

    def rotate_all_pages(self, degrees: int) -> None:
        self._apply_operation(
            f"Rotate all {degrees} degrees",
            lambda tmp: self.operation_service.rotate_all_pages(self.document_manager.working_path(), tmp, degrees),
            track_history=True,
        )

    def delete_selected_pages(self) -> None:
        selected = self.editor_workspace.selected_pages()
        if not selected:
            return
        reply = QMessageBox.question(
            self,
            "Delete pages",
            f"Delete {len(selected)} selected pages from the working copy?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._apply_operation(
            "Delete selected pages",
            lambda tmp: self.operation_service.delete_pages(self.document_manager.working_path(), selected, tmp),
            track_history=True,
            banner_message=f"Deleted {len(selected)} page(s). Undo is available.",
        )

    def extract_selected_pages(self) -> None:
        selected = self.editor_workspace.selected_pages()
        if not selected:
            return
        suggested = self.export_service.suggest_output_path(self.document_manager.state.original_path, "extract")
        output_path, _ = QFileDialog.getSaveFileName(self, "Extract Selected Pages", suggested, "PDF Files (*.pdf)")
        if not output_path:
            return
        try:
            self.operation_service.extract_pages(self.document_manager.working_path(), selected, Path(output_path))
            self._show_success_with_open("Pages extracted successfully.", Path(output_path))
        except Exception as exc:
            QMessageBox.critical(self, "Extract failed", f"Could not extract pages.\n\n{exc}")

    def split_by_range(self) -> None:
        page_count = self.document_manager.state.page_count
        if page_count == 0:
            return
        range_text, ok = QInputDialog.getText(self, "Split by range", f"Enter a page range like 1-{page_count}:")
        if not ok or "-" not in range_text:
            return
        start_text, end_text = range_text.split("-", 1)
        if not (start_text.strip().isdigit() and end_text.strip().isdigit()):
            return
        start_page = int(start_text.strip()) - 1
        end_page = int(end_text.strip()) - 1
        if not (0 <= start_page <= end_page < page_count):
            QMessageBox.warning(self, "Invalid range", "Please enter a valid page range.")
            return
        suggested = self.export_service.suggest_output_path(self.document_manager.state.original_path, "split")
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Split PDF", suggested, "PDF Files (*.pdf)")
        if not output_path:
            return
        try:
            self.operation_service.split_range(self.document_manager.working_path(), start_page, end_page, Path(output_path))
            self._show_success_with_open("PDF range exported successfully.", Path(output_path))
        except Exception as exc:
            QMessageBox.critical(self, "Split failed", f"Could not split the PDF.\n\n{exc}")

    def open_merge_workflow(self) -> None:
        dialog = MergeDialog(self._prepare_merge_source, self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        input_paths = dialog.selected_paths()
        source_paths = dialog.selected_source_paths()
        if len(input_paths) < 2:
            QMessageBox.information(self, "Merge PDFs", "Add at least two PDFs to merge.")
            return
        suggested = self.export_service.suggest_output_path(source_paths[0], "merged")
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", suggested, "PDF Files (*.pdf)")
        if not output_path:
            return
        try:
            self.operation_service.merge_pdfs(input_paths, Path(output_path))
            self._show_success_with_open("Merged PDF created successfully.", Path(output_path))
        except Exception as exc:
            QMessageBox.critical(self, "Merge failed", f"Could not merge the PDFs.\n\n{exc}")

    def save_as_dialog(self) -> None:
        if not self.document_manager.state.has_document:
            return
        suggested = self.export_service.suggest_output_path(self.document_manager.state.original_path, "edited")
        output_path, _ = QFileDialog.getSaveFileName(self, "Save As", suggested, "PDF Files (*.pdf)")
        if not output_path:
            return
        try:
            self.document_manager.save_as(output_path)
            if self.annotation_service.has_annotations():
                self.document_manager.set_dirty(True)
                self.status_widget.update_state(f"Saved PDF to {Path(output_path).name}; session annotations are not embedded.")
                self._show_banner("Saved PDF working copy. Session annotations still need future export support.")
            else:
                self.status_widget.update_state(f"Saved to {Path(output_path).name}")
                self._show_banner("Saved working copy with Save As.")
        except Exception as exc:
            QMessageBox.critical(self, "Save failed", f"Could not write the PDF.\n\n{exc}")

    def undo_last_action(self) -> None:
        if not self.document_manager.state.has_document:
            return
        history_entry = self.unified_history_service.consume_undo()
        if history_entry is None:
            return
        description: str | None = None
        if history_entry.domain == "structural":
            description = self.history_service.undo(self.document_manager.working_path())
            if description is not None:
                self.document_manager.refresh_page_count()
                self.document_manager.set_dirty(True)
                self._reload_document_views()
        elif history_entry.domain == "annotation":
            description = self.annotation_service.undo()
            if description is not None:
                self.selected_annotation_ids.clear()
                self.document_manager.set_dirty(True)
        if description is None:
            self.unified_history_service.push_undo(history_entry)
            return
        self.unified_history_service.push_redo(history_entry)
        self._update_history_ui()
        self._show_banner(f"Undid: {description}")

    def redo_last_action(self) -> None:
        if not self.document_manager.state.has_document:
            return
        history_entry = self.unified_history_service.consume_redo()
        if history_entry is None:
            return
        description: str | None = None
        if history_entry.domain == "structural":
            description = self.history_service.redo(self.document_manager.working_path())
            if description is not None:
                self.document_manager.refresh_page_count()
                self.document_manager.set_dirty(True)
                self._reload_document_views()
        elif history_entry.domain == "annotation":
            description = self.annotation_service.redo()
            if description is not None:
                self.selected_annotation_ids.clear()
                self.document_manager.set_dirty(True)
        if description is None:
            self.unified_history_service.push_redo(history_entry)
            return
        self.unified_history_service.push_undo(history_entry)
        self._update_history_ui()
        self._show_banner(f"Redid: {description}")

    def _reorder_pages(self, order: list[int]) -> None:
        if self.mode != AppMode.EDITOR:
            return
        expected = list(range(self.document_manager.state.page_count))
        if order == expected:
            return
        self._apply_operation(
            "Reorder pages",
            lambda tmp: self.operation_service.reorder_pages(self.document_manager.working_path(), order, tmp),
            track_history=True,
        )

    def _editor_selection_changed(self, selected_pages: list[int]) -> None:
        self.editor_workspace.mini_toolbar.update_selection_count(len(selected_pages))

    def _apply_operation(
        self,
        description: str,
        action,
        track_history: bool = False,
        banner_message: str | None = None,
    ) -> None:
        temp_output: Path | None = None
        operation_committed = False
        try:
            if track_history:
                self.history_service.push_undo_snapshot(self.document_manager.working_path(), description)
            fd, temp_name = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
            temp_output = Path(temp_name)
            action(temp_output)
            temp_output.replace(self.document_manager.working_path())
            operation_committed = True
            self.document_manager.refresh_page_count()
            self.document_manager.set_dirty(True)
            self._reload_document_views()
            if track_history:
                self.unified_history_service.record_action("structural", description)
            if self.mode == AppMode.EDITOR:
                self.switch_mode(AppMode.EDITOR)
            self._update_history_ui()
            self._show_banner(banner_message or f"{description} complete.")
        except Exception as exc:
            if track_history and not operation_committed:
                self.history_service.discard_last_undo_snapshot()
                self._update_history_ui()
            if temp_output and temp_output.exists():
                temp_output.unlink(missing_ok=True)
            QMessageBox.critical(self, "Operation failed", f"Could not complete the PDF operation.\n\n{exc}")

    def _selected_viewer_pages(self) -> list[int]:
        return sorted(item.data(Qt.ItemDataRole.UserRole) for item in self.left_pane.selectedItems())

    def _show_success_with_open(self, message: str, output_path: Path) -> None:
        box = QMessageBox(self)
        box.setWindowTitle("Success")
        box.setText(message)
        open_button = box.addButton("Open Output", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if box.clickedButton() == open_button:
            self.export_service.open_output(output_path)

    def _show_banner(self, message: str) -> None:
        self.banner_label.setText(message)
        self.banner_label.show()
        self.status_widget.update_state(message)
        self._banner_timer.start(5000)

    def _clear_banner(self) -> None:
        self.banner_label.clear()
        self.banner_label.hide()

    def set_active_annotation_tool(self, annotation_type: AnnotationType) -> None:
        self.active_annotation_tool = annotation_type
        self.selected_annotation_ids.clear()
        if annotation_type == AnnotationType.HIGHLIGHT:
            self.tool_rail.set_active_tool(TOOL_HIGHLIGHT)
        elif annotation_type == AnnotationType.UNDERLINE:
            self.tool_rail.set_active_tool(TOOL_UNDERLINE)
        self.right_pane.viewer_pane.set_annotation_tool(annotation_type)
        self._sync_annotation_tool_state()
        self._update_annotation_ui()
        self.viewer_workspace.focus_document_view()

    def clear_active_annotation_tool(self) -> None:
        self.active_annotation_tool = None
        if self.tool_rail.active_tool() in {TOOL_HIGHLIGHT, TOOL_UNDERLINE}:
            self.tool_rail.set_active_tool(None)
        self.right_pane.viewer_pane.set_annotation_tool(None)
        self._sync_annotation_tool_state()
        self._update_annotation_ui()

    def _annotations_for_page(self, page_index: int):
        return self.annotation_service.annotations_for_page(page_index)

    def _selected_annotations_for_page(self, page_index: int) -> set[str]:
        return {
            annotation.id
            for annotation in self.annotation_service.annotations_for_page(page_index)
            if annotation.id in self.selected_annotation_ids
        }

    def _mark_annotations_unsaved(self, message: str) -> None:
        self.document_manager.set_dirty(True)
        self._show_banner(message)

    def _annotation_rect_at(
        self,
        page_index: int,
        document_x: float,
        document_y: float,
        width: float,
        height: float,
    ) -> AnnotationRect:
        metrics = self.viewer_workspace.page_metrics[page_index]
        x = min(max(0.0, document_x - (width / 2.0)), max(metrics.width - width, 0.0))
        y = min(max(0.0, document_y - (height / 2.0)), max(metrics.height - height, 0.0))
        clamped_width = min(width, metrics.width)
        clamped_height = min(height, metrics.height)
        return AnnotationRect(x=x, y=y, width=clamped_width, height=clamped_height)

    def _annotation_rect_from_drag(
        self,
        page_index: int,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
    ) -> AnnotationRect | None:
        metrics = self.viewer_workspace.page_metrics[page_index]
        x = max(0.0, min(start_x, end_x))
        y = max(0.0, min(start_y, end_y))
        max_x = min(metrics.width, max(start_x, end_x))
        max_y = min(metrics.height, max(start_y, end_y))
        width = max_x - x
        height = max_y - y
        if self.active_annotation_tool == AnnotationType.UNDERLINE:
            if width < 8.0:
                return None
            line_height = min(max(height, 2.0), 6.0)
            line_y = min(max(0.0, max_y - line_height), max(metrics.height - line_height, 0.0))
            return AnnotationRect(x=x, y=line_y, width=width, height=line_height)
        if width < 8.0 or height < 8.0:
            return None
        return AnnotationRect(x=x, y=y, width=width, height=height)

    def _sync_annotation_tool_state(self) -> None:
        drag_enabled = self.active_annotation_tool in {AnnotationType.HIGHLIGHT, AnnotationType.UNDERLINE}
        self.viewer_workspace.set_drag_selection_enabled(drag_enabled)
        self.viewer_workspace.set_annotation_cursor_enabled(drag_enabled)

    def _update_annotation_ui(self) -> None:
        valid_annotation_ids = {annotation.id for annotation in self.annotation_service.all_annotations()}
        self.selected_annotation_ids.intersection_update(valid_annotation_ids)
        visible_annotations = self._visible_launch_annotations()
        self.right_pane.viewer_pane.set_annotation_management_state(
            bool(visible_annotations),
            len(self.selected_annotation_ids),
        )
        self.viewer_workspace.refresh_visible_pages()

    def reset_document_annotations(self) -> None:
        if self.mode != AppMode.VIEWER or not self.document_manager.state.has_document:
            return
        if not self._visible_launch_annotations():
            return
        reply = QMessageBox.question(
            self,
            "Reset annotations",
            "Remove all session highlight and underline annotations from the current document?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        cleared_count = self.annotation_service.clear_annotations_by_type(
            {AnnotationType.HIGHLIGHT, AnnotationType.UNDERLINE},
            description="Reset highlight and underline annotations",
        )
        if cleared_count:
            self.selected_annotation_ids.clear()
            self.unified_history_service.record_action("annotation", "Reset highlight and underline annotations")
            self._update_history_ui()
            self._mark_annotations_unsaved(
                "Reset document highlight and underline annotations. Save As still does not embed annotations yet."
            )

    def delete_selected_annotations(self) -> None:
        if self.mode != AppMode.VIEWER or not self.document_manager.state.has_document or self._has_text_input_focus():
            return
        deletable_ids = self._deletable_selected_annotation_ids()
        if not deletable_ids:
            return
        deleted_count = self.annotation_service.delete_annotations(deletable_ids)
        if deleted_count:
            self.selected_annotation_ids.clear()
            description = "Delete annotation" if deleted_count == 1 else "Delete annotations"
            self.unified_history_service.record_action("annotation", description)
            self._update_history_ui()
            noun = "annotation" if deleted_count == 1 else "annotations"
            self._mark_annotations_unsaved(
                f"Deleted {deleted_count} selected {noun}. Save As still does not embed annotations yet."
            )

    def show_shortcut_guide(self) -> None:
        dialog = ShortcutGuideDialog(self)
        dialog.exec()

    def focus_search(self) -> None:
        if not self.document_manager.state.has_document:
            return
        self.switch_mode(AppMode.VIEWER)
        self._show_search_context_panel()
        self.toolbar_widget.search_input.setFocus()
        self.toolbar_widget.search_input.selectAll()

    def _refresh_home_recents(self) -> None:
        self.home_screen.set_recent_files(self.document_manager.state.recent_files)

    def search_next_result(self) -> None:
        if not self.document_manager.state.has_document or not self.search_service.results:
            return
        self.switch_mode(AppMode.VIEWER)
        self._show_search_context_panel()
        self.search_service.next_result()

    def search_previous_result(self) -> None:
        if not self.document_manager.state.has_document or not self.search_service.results:
            return
        self.switch_mode(AppMode.VIEWER)
        self._show_search_context_panel()
        self.search_service.previous_result()

    def next_page(self) -> None:
        if self.mode != AppMode.VIEWER or self._has_text_input_focus():
            return
        self.jump_to_page(self.document_manager.state.current_page + 1)

    def previous_page(self) -> None:
        if self.mode != AppMode.VIEWER or self._has_text_input_focus():
            return
        self.jump_to_page(self.document_manager.state.current_page - 1)

    def next_page_arrow(self) -> None:
        if not self._viewer_document_view_has_focus():
            return
        self.jump_to_page(self.document_manager.state.current_page + 1)

    def previous_page_arrow(self) -> None:
        if not self._viewer_document_view_has_focus():
            return
        self.jump_to_page(self.document_manager.state.current_page - 1)

    def reset_zoom(self) -> None:
        state = self.document_manager.state
        if not state.has_document or self.mode == AppMode.HOME or self._has_text_input_focus():
            return
        if state.zoom_percent == 100:
            return
        self.document_manager.set_zoom_percent(100)
        self._reload_document_views()
        self.jump_to_page(state.current_page)

    def delete_selected_pages_shortcut(self) -> None:
        if self.mode != AppMode.EDITOR or self._has_text_input_focus():
            return
        self.delete_selected_pages()

    def select_all_editor_pages(self) -> None:
        if self.mode != AppMode.EDITOR or self._has_text_input_focus():
            return
        self.editor_workspace.select_all_pages()

    def _adjust_zoom_shortcut(self, delta: int) -> None:
        if self._has_text_input_focus():
            return
        self.adjust_zoom(delta)

    def _activate_annotation_tool_shortcut(self, annotation_type: AnnotationType) -> None:
        if self.mode != AppMode.VIEWER or self._has_text_input_focus():
            return
        self.switch_mode(AppMode.VIEWER)
        self.set_active_annotation_tool(annotation_type)

    def _clear_annotation_tool_shortcut(self) -> None:
        if self.mode != AppMode.VIEWER or self._has_text_input_focus():
            return
        self.clear_active_annotation_tool()

    def _show_search_context_panel(self) -> None:
        if not self.document_manager.state.has_document:
            return
        self.right_pane.show_search_context()
        self._position_search_context_panel()
        self.tool_rail.set_active_tool(TOOL_SEARCH)

    def _hide_search_context_panel(self) -> None:
        self.right_pane.hide_context_panel()
        if self.tool_rail.active_tool() == TOOL_SEARCH:
            self.tool_rail.set_active_tool(None)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self.right_pane.isVisible():
            self._position_search_context_panel()

    def moveEvent(self, event) -> None:  # type: ignore[override]
        super().moveEvent(event)
        if self.right_pane.isVisible():
            self._position_search_context_panel()

    def _position_search_context_panel(self) -> None:
        anchor = self.toolbar_widget.search_input
        shell = self.centralWidget()
        if shell is None:
            return
        anchor_bottom_left = anchor.mapTo(shell, anchor.rect().bottomLeft())
        x = anchor_bottom_left.x()
        y = anchor_bottom_left.y() + 8
        max_x = max(shell.width() - self.right_pane.width() - 12, 12)
        x = min(max(12, x), max_x)
        self.right_pane.move(x, y)

    def _sync_search_to_page(self, page_index: int) -> None:
        if not self.search_service.sync_to_page(page_index):
            return
        active_state = self.search_service.active_result_state()
        if active_state is None:
            return
        _, index, total = active_state
        self.right_pane.viewer_pane.set_active_result(index, total)

    def _select_annotation_at(self, page_index: int, document_x: float, document_y: float) -> None:
        annotation = self._find_selectable_annotation_at(page_index, document_x, document_y)
        if annotation is None:
            if self.selected_annotation_ids:
                self.selected_annotation_ids.clear()
                self._update_annotation_ui()
            return
        modifiers = QApplication.keyboardModifiers()
        additive = bool(modifiers & Qt.KeyboardModifier.ControlModifier or modifiers & Qt.KeyboardModifier.MetaModifier)
        if additive:
            if annotation.id in self.selected_annotation_ids:
                self.selected_annotation_ids.remove(annotation.id)
            else:
                self.selected_annotation_ids.add(annotation.id)
        else:
            self.selected_annotation_ids = {annotation.id}
        self._update_annotation_ui()

    def _find_selectable_annotation_at(self, page_index: int, document_x: float, document_y: float):
        annotations = [
            annotation
            for annotation in self.annotation_service.annotations_for_page(page_index)
            if annotation.annotation_type in {AnnotationType.HIGHLIGHT, AnnotationType.UNDERLINE}
        ]
        for annotation in reversed(annotations):
            rect = annotation.rect
            if rect.x <= document_x <= rect.x + rect.width and rect.y <= document_y <= rect.y + rect.height:
                return annotation
        return None

    def _deletable_selected_annotation_ids(self) -> list[str]:
        return [
            annotation.id
            for annotation in self.annotation_service.all_annotations()
            if annotation.id in self.selected_annotation_ids
            and annotation.annotation_type in {AnnotationType.HIGHLIGHT, AnnotationType.UNDERLINE}
        ]

    def _visible_launch_annotations(self):
        return [
            annotation
            for annotation in self.annotation_service.all_annotations()
            if annotation.annotation_type in {AnnotationType.HIGHLIGHT, AnnotationType.UNDERLINE}
        ]

    def _has_text_input_focus(self) -> bool:
        focus_widget = QApplication.focusWidget()
        return isinstance(focus_widget, QLineEdit)

    def _viewer_document_view_has_focus(self) -> bool:
        if self.mode != AppMode.VIEWER or self._has_text_input_focus():
            return False
        focus_widget = QApplication.focusWidget()
        if focus_widget is None:
            return False
        return self._is_descendant_of(focus_widget, self.viewer_workspace)

    @staticmethod
    def _is_descendant_of(widget: QWidget, ancestor: QWidget) -> bool:
        current: QWidget | None = widget
        while current is not None:
            if current is ancestor:
                return True
            parent = current.parentWidget()
            current = parent
        return False

    def _open_document_with_password_prompt(self, path: Path) -> bool:
        password: str | None = None
        while True:
            try:
                self.document_manager.open_document(path, password=password)
                return True
            except PdfPasswordRequiredError:
                password = self._prompt_pdf_password(path, action_label="open")
                if password is None:
                    self.status_widget.update_state("Open cancelled")
                    return False
            except PdfInvalidPasswordError:
                QMessageBox.warning(self, "Incorrect password", f"The password for {path.name} was incorrect.")
                password = self._prompt_pdf_password(path, action_label="open", retry=True)
                if password is None:
                    self.status_widget.update_state("Open cancelled")
                    return False

    def _prepare_merge_source(self, path: Path) -> Path | None:
        password: str | None = None
        while True:
            try:
                prepared = self.pdf_access_service.prepare_pdf(path, password=password)
                return prepared.prepared_path
            except PdfPasswordRequiredError:
                password = self._prompt_pdf_password(path, action_label="import for merge")
                if password is None:
                    return None
            except PdfInvalidPasswordError:
                QMessageBox.warning(self, "Incorrect password", f"The password for {path.name} was incorrect.")
                password = self._prompt_pdf_password(path, action_label="import for merge", retry=True)
                if password is None:
                    return None

    def _prompt_pdf_password(self, path: Path, action_label: str, retry: bool = False) -> str | None:
        prompt = f"Enter the password to {action_label} {path.name}:"
        if retry:
            prompt = f"Enter the correct password to {action_label} {path.name}:"
        password, ok = QInputDialog.getText(
            self,
            "PDF password required",
            prompt,
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return None
        return password

    def _confirm_discard_changes(self) -> bool:
        if not self.document_manager.state.is_dirty:
            return True
        reply = QMessageBox.warning(
            self,
            "Unsaved changes",
            "You have unsaved changes in the working copy. Continue without saving?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _refresh_title(self) -> None:
        state = self.document_manager.state
        dirty = "*" if state.is_dirty else ""
        self.setWindowTitle(f"{dirty}{state.display_name} - MyLeaflet")
        self.status_widget.update_page_status(state.current_page, state.page_count)
        self.status_widget.update_zoom(state.zoom_percent)

    def _update_dirty_state(self, is_dirty: bool) -> None:
        self._refresh_title()
        self.status_widget.update_state("Modified" if is_dirty else "Saved")

    def _set_document_controls_enabled(self, enabled: bool) -> None:
        self.toolbar_widget.set_document_controls_enabled(enabled)
        self.left_pane.setEnabled(enabled)
        self.save_as_action.setEnabled(enabled)
        self.undo_action.setEnabled(enabled)
        self.redo_action.setEnabled(enabled)

    def _update_history_ui(self) -> None:
        can_undo = self.unified_history_service.can_undo()
        can_redo = self.unified_history_service.can_redo()
        self.toolbar_widget.set_history_enabled(can_undo, can_redo)
        self.editor_workspace.set_history_state(can_undo, can_redo)
        self.undo_action.setEnabled(can_undo)
        self.redo_action.setEnabled(can_redo)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._confirm_discard_changes():
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        first_path = urls[0].toLocalFile()
        if first_path.lower().endswith(".pdf"):
            self.open_pdf(first_path)
