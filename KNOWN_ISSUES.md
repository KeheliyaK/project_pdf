# Known Issues

## Non-blocking limitations

- Search navigation does not highlight the exact in-page match
  - Description: Search jumps to the correct page and keeps result state in sync, but does not visually mark the exact match area on the page.
  - Affected area/module: `pdf_app/services/search_service.py`, `pdf_app/ui/viewer_mode_ui.py`
  - Suggested next action: Add lightweight match highlighting in a later polish pass.

- Undo/redo is snapshot-based
  - Description: Structural edit undo/redo works for reorder, rotate, and delete, but uses working-copy snapshots rather than command-granular history.
  - Affected area/module: `pdf_app/services/operation_history.py`, `pdf_app/ui/main_window.py`
  - Suggested next action: Revisit only if performance or behavior becomes an actual problem.

## Deferred next-phase work

- Annotation tools
  - Description: Highlight, underline, text box, and sign are intentionally excluded from the frozen MVP.
  - Affected area/module: Future `annotations/` work and related UI surfaces

- Packaging and broader desktop polish
  - Description: Desktop packaging, shortcut coverage, and broader release polish are still future work.
  - Affected area/module: App packaging and command/UI surfaces

## Recently resolved

- Editor reorder commit is working again through explicit index-based drop handling.
- Editor card layout has been corrected to a stable compact three-zone layout.
- Password-protected PDFs can now be unlocked during open and merge import without changing the working-copy editing model.
- Structural edit validation now rejects malformed reorder/delete/rotate/extract/split inputs before they corrupt the working copy or history state.
- Page-count-changing edits now clamp the current page correctly so delete/undo/redo reloads stay in range.
- Viewer search controls are now collapsible and show clearer result-position guidance during navigation.
- Recent files are now stored persistently across restarts and missing/unavailable entries are handled without crashing the Home screen flow.

## Maintenance note

Update this file whenever an issue is fixed, discovered, reprioritized, or intentionally deferred.
