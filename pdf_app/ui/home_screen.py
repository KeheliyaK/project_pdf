from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HomeScreen(QWidget):
    open_requested = Signal()
    merge_requested = Signal()
    file_dropped = Signal(str)
    recent_open_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)

        self.title_label = QLabel("PDF App MVP")
        self.title_label.setObjectName("homeTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.open_button = QPushButton("Open PDF")
        self.merge_button = QPushButton("Merge PDFs")
        self.drop_label = QLabel("Drag and drop a PDF here")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setObjectName("dropZone")
        self.recent_list = QListWidget()
        self.recent_list.addItem("Recent files will appear here")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 48, 64, 48)
        layout.setSpacing(16)
        layout.addWidget(self.title_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.merge_button)
        layout.addWidget(self.drop_label, 1)
        layout.addWidget(QLabel("Recent Files"))
        layout.addWidget(self.recent_list)

        self.open_button.clicked.connect(self.open_requested.emit)
        self.merge_button.clicked.connect(self.merge_requested.emit)
        self.recent_list.itemActivated.connect(self._handle_recent_open)

    def set_recent_files(self, paths: list[Path]) -> None:
        self.recent_list.clear()
        if not paths:
            self.recent_list.addItem("No recent files yet")
            return
        for path in paths:
            self.recent_list.addItem(str(path))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        first_path = urls[0].toLocalFile()
        if first_path.lower().endswith(".pdf"):
            self.file_dropped.emit(first_path)

    def _handle_recent_open(self, item) -> None:
        path = item.text()
        if path.lower().endswith(".pdf"):
            self.recent_open_requested.emit(path)
