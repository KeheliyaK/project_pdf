from __future__ import annotations

from dataclasses import dataclass, field

from pdf_app.state.document_state import DocumentState
from pdf_app.state.mode_state import AppMode
from pdf_app.state.selection_state import SelectionState


@dataclass
class AppState:
    mode: AppMode = AppMode.HOME
    document: DocumentState = field(default_factory=DocumentState)
    selection: SelectionState = field(default_factory=SelectionState)
