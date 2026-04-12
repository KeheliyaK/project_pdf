from __future__ import annotations

from pathlib import Path

import fitz

from pdf_app.search.models import SearchResult


class SearchEngine:
    def search(self, pdf_path: Path, query: str) -> list[SearchResult]:
        cleaned = query.strip()
        if not cleaned:
            return []

        document = fitz.open(pdf_path)
        results: list[SearchResult] = []
        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            matches = page.search_for(cleaned)
            if not matches:
                continue
            text = page.get_text("text")
            snippet = self._build_snippet(text, cleaned)
            for rect in matches:
                results.append(
                    SearchResult(
                        page_index=page_index,
                        snippet=snippet,
                        rect=(rect.x0, rect.y0, rect.x1, rect.y1),
                    )
                )
        document.close()
        return results

    @staticmethod
    def _build_snippet(page_text: str, query: str) -> str:
        lower_text = page_text.lower()
        lower_query = query.lower()
        idx = lower_text.find(lower_query)
        if idx == -1:
            return page_text[:90].strip() or query
        start = max(0, idx - 35)
        end = min(len(page_text), idx + len(query) + 35)
        return " ".join(page_text[start:end].split())
