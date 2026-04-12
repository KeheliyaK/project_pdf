# Project Status

## Project name
PDF App MVP

## Current phase
Phase 2 hardening and release preparation - pass 3

## MVP status
Frozen baseline with pass 3 hardening applied plus focused Viewer navigation update

## What is working now

- Shared main window with Home, Viewer, and Editor workflows
- Open PDF, drag-and-drop open, and a persisted recent-files list across app restarts
- Viewer mode with continuous scroll, zoom, full screen, thumbnails, page jump, and current-page tracking
- Viewer mode supports page-wise left/right arrow navigation when the document view itself has focus
- Shared PDF text search wired to both the toolbar search field and the Viewer Tool Pane, with collapsible search controls and clearer result-position feedback
- Editor page-organization workspace with multi-selection and drag-and-drop reorder
- Structural operations: reorder, delete, rotate selected, rotate all, extract, split, and dedicated merge workflow
- Conventional keyboard shortcuts now cover core open/save/find, full screen, page navigation, search navigation, zoom, undo/redo, and stable editor selection/delete actions
- Save As first export flow with working-copy editing, dirty tracking, unsaved-change prompts, and write-error handling
- Undo/redo foundation for structural edits: reorder, rotate, and delete
- Password-protected PDFs can be opened after prompting for a password, and protected PDFs can be imported into merge flow after unlock
- Structural edit services now validate page targets and keep page-count-changing edits, undo/redo, and Save As aligned with the working copy
- Current automated tests for PDF operations are passing

## Latest completed fixes

- Separated rendering by context for main viewer pages, sidebar thumbnails, and Editor thumbnails
- Stabilized Editor selection so card highlight, checkbox state, count, and action targets stay synchronized
- Repaired Editor reorder commit so drag-and-drop produces a real reordered page sequence
- Restored a simpler compact Editor grid layout
- Corrected internal Editor card layout so thumbnail, checkbox, and page number use a stable structure
- Added password prompt and unlock handling for protected PDFs in document open and merge import workflows
- Clamped current page after page-count-changing edits so delete/undo/redo reloads do not leave stale page focus
- Prevented failed structural operations from leaving behind a bogus undo entry
- Added validation guards for reorder, delete, rotate, extract, split, and locked merge inputs
- Replaced in-memory recent files with persisted recent-file storage and graceful cleanup of missing or inaccessible entries
- Made the Viewer search pane collapsible and improved active-result feedback in the Tool Pane and status bar
- Added essential keyboard shortcuts for core Viewer and Editor workflows without changing the existing document model or password-protected PDF flow
- Added left/right arrow page-wise navigation in Viewer mode, scoped to the main document view so thumbnails and text inputs keep their existing behavior

## Current non-blocking limitations

- Search panel collapse/expand control could use minor icon refinement in a later UI polish pass
- Search results do not visually highlight the exact in-page match region
- Undo/redo is snapshot-based rather than command-granular

## Immediate next phase after freeze

Post-MVP polish and hardening:
- packaging/release preparation for desktop distribution

## Maintenance note

Update this file whenever the frozen baseline changes or a new implementation phase begins.
