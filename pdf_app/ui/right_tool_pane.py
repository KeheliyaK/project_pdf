from __future__ import annotations

from pdf_app.annotations.models import AnnotationType
from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)


class ViewerToolPane(QWidget):
    search_requested = Signal(str)
    previous_requested = Signal()
    next_requested = Signal()
    result_activated = Signal(int)
    compact_close_requested = Signal()
    annotation_tool_selected = Signal(object)
    annotation_tool_cleared = Signal()
    annotation_reset_requested = Signal()
    annotation_delete_requested = Signal()
    rotate_selected_requested = Signal(int)
    rotate_all_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("viewerToolPane")
        self._compact_search_mode = False
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.search_toggle = QToolButton()
        self.search_toggle.setText("Search")
        self.search_toggle.setCheckable(True)
        self.search_toggle.setChecked(True)
        self.search_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.search_toggle.setArrowType(Qt.ArrowType.DownArrow)
        layout.addWidget(self.search_toggle)

        self.search_panel = QWidget()
        self.search_panel.setObjectName("searchPanel")
        self.search_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        search_layout = QVBoxLayout(self.search_panel)
        search_layout.setContentsMargins(12, 12, 12, 12)
        search_layout.setSpacing(8)
        self.compact_header = QWidget()
        self.compact_header.setObjectName("searchHeader")
        self.compact_header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        compact_header_layout = QHBoxLayout(self.compact_header)
        compact_header_layout.setContentsMargins(10, 8, 10, 8)
        compact_header_layout.setSpacing(8)
        self.compact_title_label = QLabel("Search")
        self.compact_title_label.setObjectName("compactTitleLabel")
        self.compact_close_button = QToolButton()
        self.compact_close_button.setText("Close")
        self.compact_close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.compact_close_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.compact_close_button.setAutoRaise(True)
        compact_header_layout.addWidget(self.compact_title_label)
        compact_header_layout.addStretch(1)
        compact_header_layout.addWidget(self.compact_close_button)
        search_layout.addWidget(self.compact_header)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find text")
        search_layout.addWidget(self.search_input)

        nav_row = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        nav_row.addWidget(self.prev_button)
        nav_row.addWidget(self.next_button)
        search_layout.addLayout(nav_row)

        self.result_label = QLabel("No active search")
        self.result_label.setObjectName("searchResultLabel")
        self.search_hint_label = QLabel("Enter a term to search this document.")
        self.search_hint_label.setObjectName("searchHintLabel")
        self.results_list = QListWidget()
        self.results_list.setObjectName("searchResultsList")
        self.results_list.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.results_list.viewport().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        search_layout.addWidget(self.result_label)
        search_layout.addWidget(self.search_hint_label)
        search_layout.addWidget(self.results_list, 1)
        layout.addWidget(self.search_panel, 1)

        self.annotation_box = QFrame()
        annotation_layout = QVBoxLayout(self.annotation_box)
        annotation_layout.addWidget(QLabel("Annotations"))
        self.annotation_status_label = QLabel("No annotation tool active")
        self.annotation_status_label.setStyleSheet("color: #d0d4d9;")
        self.highlight_button = QPushButton("Highlight")
        self.underline_button = QPushButton("Underline")
        self.text_box_button = QPushButton("Text Box")
        self.clear_tool_button = QPushButton("Cancel Tool")
        self.delete_annotation_button = QPushButton("Delete Selected")
        self.reset_annotations_button = QPushButton("Reset Document Annotations")
        for button in (self.highlight_button, self.underline_button, self.text_box_button):
            button.setCheckable(True)
            button.setAutoExclusive(True)
            annotation_layout.addWidget(button)
        self.text_box_button.setVisible(False)
        annotation_layout.addWidget(self.delete_annotation_button)
        annotation_layout.addWidget(self.reset_annotations_button)
        annotation_layout.addWidget(self.clear_tool_button)
        annotation_layout.addWidget(self.annotation_status_label)
        layout.addWidget(self.annotation_box)

        self.selected_box = QFrame()
        selected_layout = QVBoxLayout(self.selected_box)
        selected_layout.addWidget(QLabel("Current / Selected Pages"))
        self.rotate_selected_cw = QPushButton("Rotate 90° CW")
        self.rotate_selected_ccw = QPushButton("Rotate 90° CCW")
        self.rotate_selected_180 = QPushButton("Rotate 180°")
        selected_layout.addWidget(self.rotate_selected_cw)
        selected_layout.addWidget(self.rotate_selected_ccw)
        selected_layout.addWidget(self.rotate_selected_180)
        layout.addWidget(self.selected_box)

        self.all_box = QFrame()
        all_layout = QVBoxLayout(self.all_box)
        all_layout.addWidget(QLabel("Whole Document"))
        self.rotate_all_cw = QPushButton("Rotate All 90° CW")
        self.rotate_all_ccw = QPushButton("Rotate All 90° CCW")
        self.rotate_all_180 = QPushButton("Rotate All 180°")
        all_layout.addWidget(self.rotate_all_cw)
        all_layout.addWidget(self.rotate_all_ccw)
        all_layout.addWidget(self.rotate_all_180)
        layout.addWidget(self.all_box)

        self.search_input.returnPressed.connect(self._emit_search)
        self.prev_button.clicked.connect(self.previous_requested.emit)
        self.next_button.clicked.connect(self.next_requested.emit)
        self.results_list.currentRowChanged.connect(self.result_activated.emit)
        self.rotate_selected_cw.clicked.connect(lambda: self.rotate_selected_requested.emit(90))
        self.rotate_selected_ccw.clicked.connect(lambda: self.rotate_selected_requested.emit(-90))
        self.rotate_selected_180.clicked.connect(lambda: self.rotate_selected_requested.emit(180))
        self.rotate_all_cw.clicked.connect(lambda: self.rotate_all_requested.emit(90))
        self.rotate_all_ccw.clicked.connect(lambda: self.rotate_all_requested.emit(-90))
        self.rotate_all_180.clicked.connect(lambda: self.rotate_all_requested.emit(180))
        self.highlight_button.clicked.connect(lambda checked: self._emit_annotation_tool(AnnotationType.HIGHLIGHT, checked))
        self.underline_button.clicked.connect(lambda checked: self._emit_annotation_tool(AnnotationType.UNDERLINE, checked))
        self.text_box_button.clicked.connect(lambda checked: self._emit_annotation_tool(AnnotationType.TEXT_BOX, checked))
        self.delete_annotation_button.clicked.connect(self.annotation_delete_requested.emit)
        self.reset_annotations_button.clicked.connect(self.annotation_reset_requested.emit)
        self.clear_tool_button.clicked.connect(self._clear_annotation_tool)
        self.compact_close_button.clicked.connect(self.compact_close_requested.emit)
        self.search_toggle.toggled.connect(self._set_search_panel_visible)
        self._set_search_panel_visible(True)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.delete_annotation_button.setEnabled(False)
        self.reset_annotations_button.setEnabled(False)
        self.compact_header.setVisible(False)

    def set_results(self, results: list) -> None:
        blocker = QSignalBlocker(self.results_list)
        self.results_list.clear()
        if not results:
            self.result_label.setText("No active search")
            self.search_hint_label.setText("Enter a term to search this document.")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
        self.result_label.setText(f"{len(results)} results")
        self.search_hint_label.setText("Select a result or use Previous/Next to move through matches.")
        self.prev_button.setEnabled(len(results) > 1)
        self.next_button.setEnabled(len(results) > 1)
        for result in results:
            text = f"Page {result.page_index + 1}: {result.snippet}"
            self.results_list.addItem(QListWidgetItem(text))
        del blocker

    def set_active_result(self, index: int, total: int) -> None:
        self.result_label.setText(f"Result {index} of {total}")
        self.search_hint_label.setText(f"Viewing match {index} of {total}. Navigation wraps at the ends.")
        if 0 < index <= self.results_list.count():
            blocker = QSignalBlocker(self.results_list)
            self.results_list.setCurrentRow(index - 1)
            item = self.results_list.item(index - 1)
            if item is not None:
                self.results_list.scrollToItem(item)
            del blocker

    def set_search_collapsed(self, collapsed: bool) -> None:
        self.search_toggle.setChecked(not collapsed)

    def set_compact_search_mode(self, active: bool) -> None:
        self._compact_search_mode = active
        self.search_toggle.setVisible(not active)
        self.compact_header.setVisible(active)
        self.search_input.setVisible(not active)
        self.annotation_box.setVisible(not active)
        self.selected_box.setVisible(not active)
        self.all_box.setVisible(not active)
        if active:
            self.search_panel.setVisible(True)
        else:
            self._set_search_panel_visible(self.search_toggle.isChecked())

    def show_no_results(self, query: str) -> None:
        self.result_label.setText("No results")
        self.search_hint_label.setText(f"No matches found for '{query}'.")
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

    def set_annotation_tool(self, annotation_type: AnnotationType | None) -> None:
        self.highlight_button.setChecked(annotation_type == AnnotationType.HIGHLIGHT)
        self.underline_button.setChecked(annotation_type == AnnotationType.UNDERLINE)
        self.text_box_button.setChecked(annotation_type == AnnotationType.TEXT_BOX)
        if annotation_type is None:
            self.annotation_status_label.setText("No annotation tool active")
        elif annotation_type == AnnotationType.HIGHLIGHT:
            self.annotation_status_label.setText("Highlight active: drag across the page to place it.")
        elif annotation_type == AnnotationType.UNDERLINE:
            self.annotation_status_label.setText("Underline active: drag across the page to place it.")
        elif annotation_type == AnnotationType.TEXT_BOX:
            self.annotation_status_label.setText("Text Box active: click a page to place it.")

    def set_annotation_management_state(
        self,
        has_annotations: bool,
        selected_count: int,
    ) -> None:
        self.delete_annotation_button.setEnabled(selected_count > 0)
        self.reset_annotations_button.setEnabled(has_annotations)
        if self.highlight_button.isChecked():
            self.annotation_status_label.setText("Highlight active: drag across the page to place it.")
            return
        if self.underline_button.isChecked():
            self.annotation_status_label.setText("Underline active: drag across the page to place it.")
            return
        if selected_count == 1:
            self.annotation_status_label.setText("1 annotation selected. Delete removes the selected mark.")
        elif selected_count > 1:
            self.annotation_status_label.setText(f"{selected_count} annotations selected. Delete removes the selected marks.")
        elif has_annotations:
            self.annotation_status_label.setText("Click a highlight or underline to select it, or reset all document annotations.")
        else:
            self.annotation_status_label.setText("No annotation tool active")

    def _set_search_panel_visible(self, visible: bool) -> None:
        self.search_panel.setVisible(visible)
        self.search_toggle.setArrowType(Qt.ArrowType.DownArrow if visible else Qt.ArrowType.RightArrow)

    def _emit_search(self) -> None:
        self.search_requested.emit(self.search_input.text())

    def _emit_annotation_tool(self, annotation_type: AnnotationType, checked: bool) -> None:
        if checked:
            self.annotation_tool_selected.emit(annotation_type)
        else:
            self.annotation_tool_cleared.emit()

    def _clear_annotation_tool(self) -> None:
        self.set_annotation_tool(None)
        self.annotation_tool_cleared.emit()


class EditorToolPane(QWidget):
    delete_requested = Signal()
    rotate_selected_requested = Signal(int)
    rotate_all_requested = Signal(int)
    extract_requested = Signal()
    split_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Edit Actions"))

        self.rotate_selected_cw = QPushButton("Rotate Selected 90° CW")
        self.rotate_selected_ccw = QPushButton("Rotate Selected 90° CCW")
        self.rotate_selected_180 = QPushButton("Rotate Selected 180°")
        self.rotate_all_cw = QPushButton("Rotate All 90° CW")
        self.rotate_all_ccw = QPushButton("Rotate All 90° CCW")
        self.rotate_all_180 = QPushButton("Rotate All 180°")
        self.delete_button = QPushButton("Delete Selected")
        self.extract_button = QPushButton("Extract Selected")
        self.split_button = QPushButton("Split by Range")

        for widget in (
            self.rotate_selected_cw,
            self.rotate_selected_ccw,
            self.rotate_selected_180,
            self.rotate_all_cw,
            self.rotate_all_ccw,
            self.rotate_all_180,
            self.delete_button,
            self.extract_button,
            self.split_button,
        ):
            layout.addWidget(widget)
        layout.addStretch(1)

        self.rotate_selected_cw.clicked.connect(lambda: self.rotate_selected_requested.emit(90))
        self.rotate_selected_ccw.clicked.connect(lambda: self.rotate_selected_requested.emit(-90))
        self.rotate_selected_180.clicked.connect(lambda: self.rotate_selected_requested.emit(180))
        self.rotate_all_cw.clicked.connect(lambda: self.rotate_all_requested.emit(90))
        self.rotate_all_ccw.clicked.connect(lambda: self.rotate_all_requested.emit(-90))
        self.rotate_all_180.clicked.connect(lambda: self.rotate_all_requested.emit(180))
        self.delete_button.clicked.connect(self.delete_requested.emit)
        self.extract_button.clicked.connect(self.extract_requested.emit)
        self.split_button.clicked.connect(self.split_requested.emit)

class RightToolPane(QWidget):
    close_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.stack = QStackedWidget()
        self.viewer_pane = ViewerToolPane()
        self.editor_pane = EditorToolPane()
        self.placeholder = QLabel("Open a PDF to use the Tool Pane")

        self.stack.addWidget(self.placeholder)
        self.stack.addWidget(self.viewer_pane)
        self.stack.addWidget(self.editor_pane)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.stack)
        self.viewer_pane.compact_close_requested.connect(self.close_requested.emit)
        self._escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self._escape_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._escape_shortcut.activated.connect(self.close_requested.emit)
        self.setFixedWidth(320)
        self.setMaximumHeight(340)
        self.setStyleSheet(
            """
            RightToolPane {
                background-color: #3a3f46;
                border: 1px solid #4a5058;
                border-radius: 12px;
            }
            RightToolPane QLabel {
                color: #f1f3f5;
                background: transparent;
            }
            RightToolPane #compactTitleLabel {
                font-weight: 600;
                color: #f1f3f5;
            }
            RightToolPane #searchResultLabel {
                color: #d0d4d9;
            }
            RightToolPane #searchHintLabel {
                color: #d0d4d9;
            }
            RightToolPane QLineEdit,
            RightToolPane QListWidget,
            RightToolPane QPushButton,
            RightToolPane QToolButton,
            RightToolPane QFrame,
            RightToolPane QWidget {
                background: transparent;
            }
            RightToolPane QLineEdit,
            RightToolPane QListWidget {
                color: #f1f3f5;
                background-color: #2f343b;
                border: 1px solid #4a5058;
                border-radius: 8px;
                padding: 6px;
                selection-background-color: #5a616b;
            }
            RightToolPane QPushButton,
            RightToolPane QToolButton {
                color: #f1f3f5;
                border: 1px solid #5a616b;
                border-radius: 8px;
                background-color: #4a5058;
                padding: 6px 8px;
            }
            RightToolPane QPushButton:hover,
            RightToolPane QToolButton:hover {
                background-color: #5a616b;
            }
            RightToolPane[contextPanel="true"] {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
            }
            RightToolPane[contextPanel="true"] #viewerToolPane,
            RightToolPane[contextPanel="true"] QStackedWidget,
            RightToolPane[contextPanel="true"] QStackedWidget > QWidget {
                background: transparent;
            }
            RightToolPane[contextPanel="true"] #searchPanel {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 10px;
            }
            RightToolPane[contextPanel="true"] #searchHeader {
                background-color: #0b1220;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
            RightToolPane[contextPanel="true"] QLabel {
                color: #e5edf7;
            }
            RightToolPane[contextPanel="true"] #compactTitleLabel {
                color: #f8fafc;
            }
            RightToolPane[contextPanel="true"] #searchResultLabel {
                color: #dbe7f5;
            }
            RightToolPane[contextPanel="true"] #searchHintLabel {
                color: #9fb0c7;
            }
            RightToolPane[contextPanel="true"] QLineEdit {
                background-color: #020617;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px 10px;
                selection-background-color: #2563eb;
            }
            RightToolPane[contextPanel="true"] #searchResultsList {
                background-color: #3a3f46;
                color: #f1f3f5;
                border: 1px solid #4a5058;
                border-radius: 8px;
                padding: 6px;
                outline: none;
                show-decoration-selected: 1;
            }
            RightToolPane[contextPanel="true"] #searchResultsList::item {
                background-color: #444b52;
                color: #f1f3f5;
                border-radius: 8px;
                margin: 0 0 6px 0;
                padding: 6px;
            }
            RightToolPane[contextPanel="true"] #searchResultsList::item:selected {
                background-color: #5a616b;
                color: #f1f3f5;
            }
            RightToolPane[contextPanel="true"] QPushButton,
            RightToolPane[contextPanel="true"] QToolButton {
                background-color: #162033;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px 8px;
            }
            RightToolPane[contextPanel="true"] QPushButton:hover,
            RightToolPane[contextPanel="true"] QToolButton:hover {
                background-color: #1d2b44;
            }
            """
        )
        self._set_context_panel_active(False)
        self.hide()

    def show_placeholder(self) -> None:
        self.stack.setCurrentWidget(self.placeholder)

    def show_viewer(self) -> None:
        self._set_context_panel_active(False)
        self.viewer_pane.set_compact_search_mode(False)
        self.stack.setCurrentWidget(self.viewer_pane)

    def show_editor(self) -> None:
        self._set_context_panel_active(False)
        self.stack.setCurrentWidget(self.editor_pane)

    def show_search_context(self) -> None:
        self._set_context_panel_active(True)
        self.stack.setCurrentWidget(self.viewer_pane)
        self.viewer_pane.set_compact_search_mode(True)
        self.show()
        self.raise_()

    def hide_context_panel(self) -> None:
        self._set_context_panel_active(False)
        self.viewer_pane.set_compact_search_mode(False)
        self.hide()

    def _set_context_panel_active(self, active: bool) -> None:
        self.setProperty("contextPanel", active)
        style = self.style()
        style.unpolish(self)
        style.polish(self)
        self.update()
