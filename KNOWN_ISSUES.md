# Known Issues

## Non-blocking limitations

- Viewer search panel is not collapsible
  - Description: The detailed search area in the Viewer Tool Pane is always visible instead of collapsible.
  - Affected area/module: `pdf_app/ui/right_tool_pane.py`
  - Suggested next action: Address in post-MVP search/UI polish.

- Search navigation does not highlight the exact in-page match
  - Description: Search jumps to the correct page and keeps result state in sync, but does not visually mark the exact match area on the page.
  - Affected area/module: `pdf_app/services/search_service.py`, `pdf_app/ui/viewer_mode_ui.py`
  - Suggested next action: Add lightweight match highlighting in a later polish pass.

- Recent files are lightweight
  - Description: Recent files are shown, but the feature is intentionally minimal and not yet a richer persisted history implementation.
  - Affected area/module: `pdf_app/services/document_manager.py`, `pdf_app/ui/home_screen.py`
  - Suggested next action: Improve persistence and polish in the next phase if still desired.

- Undo/redo is snapshot-based
  - Description: Structural edit undo/redo works for reorder, rotate, and delete, but uses working-copy snapshots rather than command-granular history.
  - Affected area/module: `pdf_app/services/operation_history.py`, `pdf_app/ui/main_window.py`
  - Suggested next action: Revisit only if performance or behavior becomes an actual problem.

## Deferred next-phase work

- Annotation tools
  - Description: Highlight, underline, text box, and sign are intentionally excluded from the frozen MVP.
  - Affected area/module: Future `annotations/` work and related UI surfaces

- Password-protected PDF support
  - Description: Protected PDF handling is deferred until after the frozen MVP.
  - Affected area/module: Open/import workflow and document services

- Packaging and broader desktop polish
  - Description: Desktop packaging, shortcut coverage, and broader release polish are still future work.
  - Affected area/module: App packaging and command/UI surfaces

## Recently resolved

- Editor reorder commit is working again through explicit index-based drop handling.
- Editor card layout has been corrected to a stable compact three-zone layout.

## Maintenance note

Update this file whenever an issue is fixed, discovered, reprioritized, or intentionally deferred.
