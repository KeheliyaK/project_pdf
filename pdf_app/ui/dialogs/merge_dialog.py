from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)


class MergeDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Merge PDFs")
        self.resize(520, 380)
        self.file_list = QListWidget()
        self.file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        add_button = QPushButton("Add PDFs")
        remove_button = QPushButton("Remove Selected")
        merge_button = QPushButton("Merge")
        cancel_button = QPushButton("Cancel")

        button_row = QHBoxLayout()
        button_row.addWidget(add_button)
        button_row.addWidget(remove_button)
        button_row.addStretch(1)
        button_row.addWidget(merge_button)
        button_row.addWidget(cancel_button)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Add PDFs, reorder them, and confirm the merge output."))
        layout.addWidget(self.file_list, 1)
        layout.addLayout(button_row)

        add_button.clicked.connect(self._add_files)
        remove_button.clicked.connect(self._remove_selected)
        merge_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def _add_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        for path in paths:
            self.file_list.addItem(QListWidgetItem(path))

    def _remove_selected(self) -> None:
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def selected_paths(self) -> list[Path]:
        return [Path(self.file_list.item(index).text()) for index in range(self.file_list.count())]
