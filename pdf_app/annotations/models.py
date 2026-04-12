from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum


class AnnotationType(str, Enum):
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    TEXT_BOX = "text_box"


@dataclass(frozen=True)
class AnnotationRect:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class AnnotationStyle:
    color: str = "#facc15"
    opacity: float = 0.35
    stroke_width: float = 1.5


@dataclass(frozen=True)
class Annotation:
    id: str
    annotation_type: AnnotationType
    page_index: int
    rect: AnnotationRect
    style: AnnotationStyle = field(default_factory=AnnotationStyle)
    text_content: str | None = None

    def updated(self, **changes) -> Annotation:
        return replace(self, **changes)
