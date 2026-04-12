from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)


class ViewerToolPane(QWidget):
    search_requested = Signal(str)
    previous_requested = Signal()
    next_requested = Signal()
    result_activated = Signal(int)
    rotate_selected_requested = Signal(int)
    rotate_all_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Search"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find text")
        layout.addWidget(self.search_input)

        nav_row = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        nav_row.addWidget(self.prev_button)
        nav_row.addWidget(self.next_button)
        layout.addLayout(nav_row)

        self.result_label = QLabel("0 results")
        self.results_list = QListWidget()
        layout.addWidget(self.result_label)
        layout.addWidget(self.results_list, 1)

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

    def set_results(self, results: list) -> None:
        self.results_list.clear()
        self.result_label.setText(f"{len(results)} results")
        for result in results:
            text = f"Page {result.page_index + 1}: {result.snippet}"
            self.results_list.addItem(QListWidgetItem(text))

    def set_active_result(self, index: int, total: int) -> None:
        self.result_label.setText(f"Result {index} of {total}")
        if 0 < index <= self.results_list.count():
            self.results_list.setCurrentRow(index - 1)

    def _emit_search(self) -> None:
        self.search_requested.emit(self.search_input.text())


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
