from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from pdf_app.annotations.models import Annotation, AnnotationRect, AnnotationStyle, AnnotationType


@dataclass(frozen=True)
class AnnotationHistoryEntry:
    annotations: dict[str, Annotation]
    description: str


class AnnotationService(QObject):
    annotations_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._document_key: str | None = None
        self._annotations: dict[str, Annotation] = {}
        self._page_index: dict[int, list[str]] = defaultdict(list)
        self._undo_stack: list[AnnotationHistoryEntry] = []
        self._redo_stack: list[AnnotationHistoryEntry] = []

    def open_document(self, working_path: Path | None, force_reset: bool = False) -> None:
        new_key = str(working_path.resolve()) if working_path else None
        if new_key == self._document_key and not force_reset:
            return
        self._document_key = new_key
        self.clear(reset_history=True)

    def clear(self, reset_history: bool = True) -> None:
        self._annotations.clear()
        self._page_index.clear()
        if reset_history:
            self._undo_stack.clear()
            self._redo_stack.clear()
        self.annotations_changed.emit()

    def add_annotation(
        self,
        annotation_type: AnnotationType,
        page_index: int,
        rect: AnnotationRect,
        style: AnnotationStyle | None = None,
        text_content: str | None = None,
    ) -> Annotation:
        self._ensure_document_open()
        self._push_undo_state(f"Add {annotation_type.value.replace('_', ' ')}")
        annotation = Annotation(
            id=str(uuid.uuid4()),
            annotation_type=annotation_type,
            page_index=page_index,
            rect=rect,
            style=style or self._default_style(annotation_type),
            text_content=text_content,
        )
        self._annotations[annotation.id] = annotation
        self._page_index[page_index].append(annotation.id)
        self.annotations_changed.emit()
        return annotation

    def update_annotation(self, annotation_id: str, **changes) -> Annotation:
        self._ensure_document_open()
        self._push_undo_state("Update annotation")
        annotation = self._annotations[annotation_id]
        updated = annotation.updated(**changes)
        if updated.page_index != annotation.page_index:
            self._page_index[annotation.page_index] = [
                item_id for item_id in self._page_index[annotation.page_index] if item_id != annotation_id
            ]
            self._page_index[updated.page_index].append(annotation_id)
        self._annotations[annotation_id] = updated
        self.annotations_changed.emit()
        return updated

    def delete_annotation(self, annotation_id: str) -> None:
        self._ensure_document_open()
        self._push_undo_state("Delete annotation")
        annotation = self._annotations.pop(annotation_id)
        self._page_index[annotation.page_index] = [
            item_id for item_id in self._page_index[annotation.page_index] if item_id != annotation_id
        ]
        self.annotations_changed.emit()

    def delete_annotations(self, annotation_ids: list[str]) -> int:
        self._ensure_document_open()
        normalized_ids = [annotation_id for annotation_id in annotation_ids if annotation_id in self._annotations]
        if not normalized_ids:
            return 0
        description = "Delete annotations" if len(normalized_ids) > 1 else "Delete annotation"
        self._push_undo_state(description)
        for annotation_id in normalized_ids:
            annotation = self._annotations.pop(annotation_id)
            self._page_index[annotation.page_index] = [
                item_id for item_id in self._page_index[annotation.page_index] if item_id != annotation_id
            ]
        self.annotations_changed.emit()
        return len(normalized_ids)

    def clear_document_annotations(self) -> bool:
        self._ensure_document_open()
        if not self._annotations:
            return False
        self._push_undo_state("Clear annotations")
        self._annotations.clear()
        self._page_index.clear()
        self.annotations_changed.emit()
        return True

    def clear_annotations_by_type(self, annotation_types: set[AnnotationType], description: str = "Clear annotations") -> int:
        self._ensure_document_open()
        matching_ids = [
            annotation.id
            for annotation in self._annotations.values()
            if annotation.annotation_type in annotation_types
        ]
        if not matching_ids:
            return 0
        self._push_undo_state(description)
        for annotation_id in matching_ids:
            annotation = self._annotations.pop(annotation_id)
            self._page_index[annotation.page_index] = [
                item_id for item_id in self._page_index[annotation.page_index] if item_id != annotation_id
            ]
        self.annotations_changed.emit()
        return len(matching_ids)

    def annotations_for_page(self, page_index: int) -> list[Annotation]:
        return [
            self._annotations[annotation_id]
            for annotation_id in self._page_index.get(page_index, [])
            if annotation_id in self._annotations
        ]

    def annotations_for_document(self) -> list[Annotation]:
        return list(self._annotations.values())

    def all_annotations(self) -> list[Annotation]:
        return self.annotations_for_document()

    def has_annotations(self) -> bool:
        return bool(self._annotations)

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def undo(self) -> str | None:
        self._ensure_document_open()
        if not self._undo_stack:
            return None
        self._redo_stack.append(AnnotationHistoryEntry(self._snapshot_annotations(), self._undo_stack[-1].description))
        previous = self._undo_stack.pop()
        self._restore_annotations(previous.annotations)
        self.annotations_changed.emit()
        return previous.description

    def redo(self) -> str | None:
        self._ensure_document_open()
        if not self._redo_stack:
            return None
        self._undo_stack.append(AnnotationHistoryEntry(self._snapshot_annotations(), self._redo_stack[-1].description))
        upcoming = self._redo_stack.pop()
        self._restore_annotations(upcoming.annotations)
        self.annotations_changed.emit()
        return upcoming.description

    @staticmethod
    def _default_style(annotation_type: AnnotationType) -> AnnotationStyle:
        if annotation_type == AnnotationType.UNDERLINE:
            return AnnotationStyle(color="#2563eb", opacity=1.0, stroke_width=2.0)
        if annotation_type == AnnotationType.TEXT_BOX:
            return AnnotationStyle(color="#f97316", opacity=1.0, stroke_width=1.5)
        return AnnotationStyle(color="#facc15", opacity=0.35, stroke_width=1.5)

    def _ensure_document_open(self) -> None:
        if self._document_key is None:
            raise ValueError("No document is open for annotations.")

    def _push_undo_state(self, description: str) -> None:
        self._undo_stack.append(AnnotationHistoryEntry(self._snapshot_annotations(), description))
        self._redo_stack.clear()

    def _snapshot_annotations(self) -> dict[str, Annotation]:
        return dict(self._annotations)

    def _restore_annotations(self, annotations: dict[str, Annotation]) -> None:
        self._annotations = dict(annotations)
        self._page_index.clear()
        for annotation in self._annotations.values():
            self._page_index[annotation.page_index].append(annotation.id)
