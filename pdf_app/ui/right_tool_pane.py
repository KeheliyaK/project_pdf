from __future__ import annotations

from pdf_app.annotations.models import AnnotationType
from PySide6.QtCore import Qt, Signal
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
    annotation_tool_selected = Signal(object)
    annotation_tool_cleared = Signal()
    annotation_reset_requested = Signal()
    annotation_delete_requested = Signal()
    rotate_selected_requested = Signal(int)
    rotate_all_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
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
        search_layout = QVBoxLayout(self.search_panel)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)
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
        self.result_label.setStyleSheet("color: #475569;")
        self.search_hint_label = QLabel("Enter a term to search this document.")
        self.search_hint_label.setStyleSheet("color: #64748b;")
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        search_layout.addWidget(self.result_label)
        search_layout.addWidget(self.search_hint_label)
        search_layout.addWidget(self.results_list, 1)
        layout.addWidget(self.search_panel, 1)

        annotation_box = QFrame()
        annotation_layout = QVBoxLayout(annotation_box)
        annotation_layout.addWidget(QLabel("Annotations"))
        self.annotation_status_label = QLabel("No annotation tool active")
        self.annotation_status_label.setStyleSheet("color: #475569;")
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
        layout.addWidget(annotation_box)

        selected_box = QFrame()
        selected_layout = QVBoxLayout(selected_box)
        selected_layout.addWidget(QLabel("Current / Selected Pages"))
        self.rotate_selected_cw = QPushButton("Rotate 90° CW")
        self.rotate_selected_ccw = QPushButton("Rotate 90° CCW")
        self.rotate_selected_180 = QPushButton("Rotate 180°")
        selected_layout.addWidget(self.rotate_selected_cw)
        selected_layout.addWidget(self.rotate_selected_ccw)
        selected_layout.addWidget(self.rotate_selected_180)
        layout.addWidget(selected_box)

        all_box = QFrame()
        all_layout = QVBoxLayout(all_box)
        all_layout.addWidget(QLabel("Whole Document"))
        self.rotate_all_cw = QPushButton("Rotate All 90° CW")
        self.rotate_all_ccw = QPushButton("Rotate All 90° CCW")
        self.rotate_all_180 = QPushButton("Rotate All 180°")
        all_layout.addWidget(self.rotate_all_cw)
        all_layout.addWidget(self.rotate_all_ccw)
        all_layout.addWidget(self.rotate_all_180)
        layout.addWidget(all_box)

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
        self.search_toggle.toggled.connect(self._set_search_panel_visible)
        self._set_search_panel_visible(True)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.delete_annotation_button.setEnabled(False)
        self.reset_annotations_button.setEnabled(False)

    def set_results(self, results: list) -> None:
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

    def set_active_result(self, index: int, total: int) -> None:
        self.result_label.setText(f"Result {index} of {total}")
        self.search_hint_label.setText(f"Viewing match {index} of {total}. Navigation wraps at the ends.")
        if 0 < index <= self.results_list.count():
            self.results_list.setCurrentRow(index - 1)

    def set_search_collapsed(self, collapsed: bool) -> None:
        self.search_toggle.setChecked(not collapsed)

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
    def __init__(self) -> None:
        super().__init__()
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

    def show_placeholder(self) -> None:
        self.stack.setCurrentWidget(self.placeholder)

    def show_viewer(self) -> None:
        self.stack.setCurrentWidget(self.viewer_pane)

    def show_editor(self) -> None:
        self.stack.setCurrentWidget(self.editor_pane)
