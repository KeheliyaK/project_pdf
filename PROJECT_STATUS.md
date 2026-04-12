# Project Status

## Project name
PDF App MVP

## Current phase
Phase 5 - Mini launch preparation (macOS .app)

## MVP status
Frozen baseline prepared for a macOS early-preview `.app` mini launch

## What is working now

- Shared main window with Home, Viewer, and Editor workflows
- Open PDF, drag-and-drop open, and a persisted recent-files list across app restarts
- Viewer mode with continuous scroll, zoom, full screen, thumbnails, page jump, and current-page tracking
- Viewer mode supports page-wise left/right arrow navigation when the document view itself has focus
- Shared PDF text search wired to both the toolbar search field and the Viewer Tool Pane, with collapsible search controls and clearer result-position feedback
- Editor page-organization workspace with multi-selection and drag-and-drop reorder
- Structural operations: reorder, delete, rotate selected, rotate all, extract, split, and dedicated merge workflow
- Conventional keyboard shortcuts now cover core open/save/find, full screen, page navigation, search navigation, zoom, undo/redo, and stable editor selection/delete actions
- Help menu now includes a simple in-app keyboard shortcut guide grouped by context
- A repeatable macOS-first packaging path now exists for local `.app` builds and manual distribution testing
- Highlight and underline annotations now use drag-based placement in Viewer mode and support selection, delete, top-level undo/redo, and document-level reset
- Viewer annotation mode now provides clearer active-tool feedback, lightweight annotation shortcuts, and a focused mini-launch-ready visible annotation set
- A concise mini-launch smoke checklist now exists for preview build verification before sharing a macOS `.app`
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
- Added a basic Help-menu shortcut guide and a practical PyInstaller-based macOS packaging path for local build/testing
- Added an internal annotation foundation covering data models, centralized document-scoped annotation service state, and lightweight Viewer overlay rendering hooks
- Added click-to-select support for existing highlight and underline annotations in Viewer mode, with visible selection styling in the page overlay
- Added deletion for selected highlight and underline annotations through the Viewer pane and `Delete` when the Viewer document surface has focus
- Added document-scoped reset for the visible highlight/underline toolset without changing structural edit undo/redo behavior
- Kept text box support internal/deprioritized instead of exposing it as part of the current launch-facing annotation subset
- Removed visible annotation-specific undo/redo buttons from the Viewer pane so the launch-facing annotation UI stays focused on create/select/delete/reset actions
- Unified top-level Undo/Redo routing so the existing toolbar, Edit menu, and keyboard shortcuts now cover both structural edits and visible highlight/underline annotation actions
- Tightened launch-facing documentation around the macOS preview target, visible annotation scope, Save As honesty, and early-user limitations
- Hardened the PyInstaller spec slightly for preview packaging by avoiding optional UPX compression in the macOS `.app` build path
- Restored Editor checkbox-based multi-selection so checkbox toggles once again feed the same shared selection state as card selection and Cmd-click workflows
- Improved Editor checkbox checked-state visibility so selected pages are easier to scan quickly during multi-page editing

## Current non-blocking limitations

- Search panel collapse/expand control could use minor icon refinement in a later UI polish pass
- Search results do not visually highlight the exact in-page match region
- Annotation tools are still first-pass overall: text box remains deferred from the visible launch set, per-annotation editing is still minimal, and PDF annotation write-back/export is still pending
- Local macOS packaging is preview-ready for manual distribution/testing only and does not yet include codesigning, notarization, or installer polish
- Undo/redo is snapshot-based rather than command-granular

## Launch validation note

- Editor checkbox multi-selection regression has been revalidated through automated coverage for checkbox select, deselect, multi-select preservation, mixed selection, and selected-page operation targeting.
- Editor checkbox checked-state visibility has been polished without changing the compact grid layout or shared selection behavior.

## Immediate next phase after freeze

Next annotation work:
- annotation editing polish, better text box handling, and explicit PDF export/write-back integration

Next launch-prep work:
- packaged-app smoke execution on a built macOS `.app`, followed by codesigning/notarization work when the preview is ready to move beyond early users

## Maintenance note

Update this file whenever the frozen baseline changes or a new implementation phase begins.
