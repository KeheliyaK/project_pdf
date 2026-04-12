from __future__ import annotations

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ShortcutGuideDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.resize(620, 520)

        outer_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(18)

        self._add_section(
            content_layout,
            "Global",
            [
                ("Open PDF", self._native_standard(QKeySequence.StandardKey.Open)),
                ("Save As", self._native_standard(QKeySequence.StandardKey.SaveAs)),
                ("Find / focus search", self._native_standard(QKeySequence.StandardKey.Find)),
                ("Find next result", self._native_standard(QKeySequence.StandardKey.FindNext)),
                ("Find previous result", self._native_standard(QKeySequence.StandardKey.FindPrevious)),
                ("Toggle full screen", "F11"),
                ("Undo last action", self._native_standard(QKeySequence.StandardKey.Undo)),
                ("Redo last action", self._native_standard(QKeySequence.StandardKey.Redo)),
            ],
        )
        self._add_section(
            content_layout,
            "Viewer",
            [
                ("Next page", "Right Arrow, Page Down"),
                ("Previous page", "Left Arrow, Page Up"),
                ("Zoom in", self._join_shortcuts(self._native_standard(QKeySequence.StandardKey.ZoomIn), "Ctrl+=")),
                ("Zoom out", self._native_standard(QKeySequence.StandardKey.ZoomOut)),
                ("Reset zoom", "Ctrl+0"),
                ("Highlight tool", "H"),
                ("Underline tool", "U"),
                ("Delete selected annotation", "Delete"),
                ("Exit annotation mode", "Esc"),
            ],
        )
        self._add_section(
            content_layout,
            "Editor",
            [
                ("Delete selected pages", "Delete"),
                ("Select all pages", self._native_standard(QKeySequence.StandardKey.SelectAll)),
            ],
        )
        content_layout.addStretch(1)

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area, 1)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_row.addWidget(close_button)
        outer_layout.addLayout(button_row)

    def _add_section(self, layout: QVBoxLayout, title: str, rows: list[tuple[str, str]]) -> None:
        section_title = QLabel(title)
        section_title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(section_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)
        for row, (action_text, shortcut_text) in enumerate(rows):
            action_label = QLabel(action_text)
            shortcut_label = QLabel(shortcut_text)
            shortcut_label.setStyleSheet("color: #334155;")
            grid.addWidget(action_label, row, 0)
            grid.addWidget(shortcut_label, row, 1)
        layout.addLayout(grid)

    @staticmethod
    def _native_standard(standard_key: QKeySequence.StandardKey) -> str:
        return QKeySequence(standard_key).toString(QKeySequence.SequenceFormat.NativeText)

    @staticmethod
    def _join_shortcuts(*shortcuts: str) -> str:
        return ", ".join(shortcut for shortcut in shortcuts if shortcut)
