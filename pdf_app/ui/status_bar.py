from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


class AppStatusBar(QWidget):
    page_jump_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self.page_label = QLabel("Page 0 / 0")
        self.zoom_label = QLabel("Zoom 100%")
        self.state_label = QLabel("Ready")
        self.page_jump_input = QLineEdit()
        self.page_jump_input.setPlaceholderText("Page #")
        self.page_jump_input.setFixedWidth(80)
        self.jump_button = QPushButton("Go")

        layout.addWidget(self.page_label)
        layout.addStretch(1)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.state_label)
        layout.addWidget(self.page_jump_input)
        layout.addWidget(self.jump_button)

        self.jump_button.clicked.connect(self._emit_jump)
        self.page_jump_input.returnPressed.connect(self._emit_jump)

    def update_page_status(self, current_page: int, page_count: int) -> None:
        self.page_label.setText(f"Page {current_page + 1 if page_count else 0} / {page_count}")

    def update_zoom(self, zoom_percent: int) -> None:
        self.zoom_label.setText(f"Zoom {zoom_percent}%")

    def update_state(self, message: str) -> None:
        self.state_label.setText(message)

    def _emit_jump(self) -> None:
        text = self.page_jump_input.text().strip()
        if text.isdigit():
            self.page_jump_requested.emit(int(text) - 1)
