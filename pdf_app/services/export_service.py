from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


class ExportService:
    @staticmethod
    def suggest_output_path(source_path: Path | None, suffix: str) -> str:
        if not source_path:
            return f"output_{suffix}.pdf"
        stem = source_path.stem
        return str(source_path.with_name(f"{stem}_{suffix}.pdf"))

    @staticmethod
    def open_output(path: Path) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
