from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DocumentState:
    original_path: Path | None = None
    working_path: Path | None = None
    page_count: int = 0
    current_page: int = 0
    zoom_percent: int = 100
    is_dirty: bool = False
    recent_files: list[Path] = field(default_factory=list)

    @property
    def has_document(self) -> bool:
        return self.working_path is not None

    @property
    def display_name(self) -> str:
        if self.original_path:
            return self.original_path.name
        if self.working_path:
            return self.working_path.name
        return "No document"
