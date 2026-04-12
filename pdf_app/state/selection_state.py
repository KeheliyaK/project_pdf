from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SelectionState:
    viewer_selected_pages: set[int] = field(default_factory=set)
    editor_selected_pages: set[int] = field(default_factory=set)
