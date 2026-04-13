from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class MainToolbar(QWidget):
    open_requested = Signal()
    merge_requested = Signal()
    save_as_requested = Signal()
    viewer_mode_requested = Signal()
    editor_mode_requested = Signal()
    undo_requested = Signal()
    redo_requested = Signal()
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    fullscreen_requested = Signal()
    search_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.merge_button = QPushButton("Merge PDFs")
        self.viewer_button = QPushButton("Viewer")
        self.editor_button = QPushButton("Editor")
        self.viewer_button.setCheckable(True)
        self.editor_button.setCheckable(True)
        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")
        self.fullscreen_button = QPushButton("Full Screen")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in document")

        for button in (self.viewer_button, self.editor_button):
            button.setAutoExclusive(True)

        layout.addWidget(self.merge_button)
        layout.addWidget(self.viewer_button)
        layout.addWidget(self.editor_button)
        layout.addWidget(self.undo_button)
        layout.addWidget(self.redo_button)
        layout.addStretch(1)
        layout.addWidget(self.fullscreen_button)
        layout.addWidget(self.search_input, 1)

        self.merge_button.clicked.connect(self.merge_requested.emit)
        self.viewer_button.clicked.connect(self.viewer_mode_requested.emit)
        self.editor_button.clicked.connect(self.editor_mode_requested.emit)
        self.undo_button.clicked.connect(self.undo_requested.emit)
        self.redo_button.clicked.connect(self.redo_requested.emit)
        self.fullscreen_button.clicked.connect(self.fullscreen_requested.emit)
        self.search_input.returnPressed.connect(self._emit_search)

    def set_mode(self, mode: str) -> None:
        self.viewer_button.setChecked(mode == "viewer")
        self.editor_button.setChecked(mode == "editor")

    def set_document_controls_enabled(self, enabled: bool) -> None:
        for widget in (
            self.viewer_button,
            self.editor_button,
            self.undo_button,
            self.redo_button,
            self.fullscreen_button,
            self.search_input,
        ):
            widget.setEnabled(enabled)

    def set_history_enabled(self, can_undo: bool, can_redo: bool) -> None:
        self.undo_button.setEnabled(can_undo)
        self.redo_button.setEnabled(can_redo)

    def _emit_search(self) -> None:
        self.search_requested.emit(self.search_input.text())
