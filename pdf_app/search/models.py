from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SearchResult:
    page_index: int
    snippet: str
    rect: tuple[float, float, float, float]
