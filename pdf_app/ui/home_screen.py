from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
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
        self.setObjectName("homeScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.title_label = QLabel("MyLeaflet")
        self.title_label.setObjectName("homeTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.open_button = QPushButton("Open PDF")
        self.merge_button = QPushButton("Merge PDFs")
        self.drop_label = QLabel("Drag and drop a PDF here")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setObjectName("dropZone")
        self.recent_label = QLabel("Recent Files")
        self.recent_label.setObjectName("recentFilesLabel")
        self.recent_list = QListWidget()
        self.recent_list.setObjectName("recentFilesList")
        self.recent_list.addItem("Recent files will appear here")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 48, 64, 48)
        layout.setSpacing(16)
        layout.addWidget(self.title_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.merge_button)
        layout.addWidget(self.drop_label, 1)
        layout.addWidget(self.recent_label)
        layout.addWidget(self.recent_list)

        self.setStyleSheet(
            """
            QWidget#homeScreen {
                background-color: #3a3f46;
            }
            QLabel#homeTitle {
                color: #f1f3f5;
                font-size: 28px;
                font-weight: 600;
                padding-bottom: 8px;
            }
            QLabel#dropZone {
                color: #d0d4d9;
                background-color: #2f343b;
                border: 1px dashed #5a616b;
                border-radius: 12px;
                padding: 28px;
            }
            QLabel#recentFilesLabel {
                color: #f1f3f5;
                font-weight: 600;
            }
            QPushButton {
                color: #f1f3f5;
                background-color: #4a5058;
                border: 1px solid #5a616b;
                border-radius: 8px;
                padding: 10px 14px;
            }
            QPushButton:hover {
                background-color: #5a616b;
            }
            QListWidget#recentFilesList {
                color: #d0d4d9;
                background-color: #2f343b;
                border: 1px solid #4a5058;
                border-radius: 10px;
                padding: 8px;
            }
            QListWidget#recentFilesList::item {
                color: #d0d4d9;
                padding: 8px 10px;
                border-radius: 6px;
            }
            QListWidget#recentFilesList::item:selected {
                color: #f1f3f5;
                background-color: #4a5058;
            }
            """
        )

        self.open_button.clicked.connect(self.open_requested.emit)
        self.merge_button.clicked.connect(self.merge_requested.emit)
        self.recent_list.itemActivated.connect(self._handle_recent_open)

    def set_recent_files(self, paths: list[Path]) -> None:
        self.recent_list.clear()
        if not paths:
            self.recent_list.addItem("No recent files yet")
            return
        for path in paths:
            item = self._build_recent_item(path)
            self.recent_list.addItem(item)

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
        path = item.data(Qt.ItemDataRole.UserRole) or item.text()
        if path.lower().endswith(".pdf"):
            self.recent_open_requested.emit(path)

    def _build_recent_item(self, path: Path) -> QListWidgetItem:
        item = QListWidgetItem(path.name)
        item.setData(Qt.ItemDataRole.UserRole, str(path))
        item.setToolTip(str(path))
        if path.exists():
            item.setText(f"{path.name}\n{path}")
        else:
            item.setText(f"{path.name} (missing)\n{path}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            item.setForeground(Qt.GlobalColor.gray)
            item.setToolTip(f"Missing file:\n{path}")
        return item
