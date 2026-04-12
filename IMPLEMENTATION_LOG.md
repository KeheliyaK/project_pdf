# Implementation Log

## Completed work

- Phase 0: Created the modular project structure, app entry point, shared main window shell, home screen, mode state, and layout skeleton.
- Phase 1: Implemented PDF open, drag-and-drop open, viewer rendering, thumbnails, continuous scroll, zoom, full screen, current-page tracking, page jump, and status updates.
- Phase 2: Implemented one shared search engine and wired it to the toolbar quick search and detailed Tool Pane search panel with result navigation.
- Phase 3: Implemented Editor mode with a shared window, central page organization workspace, multi-page selection, drag-and-drop reorder, right-pane edit actions, and working-copy document flow.
- Phase 4: Implemented structural operations for reorder, delete, rotate selected, rotate all, extract, split, and dedicated merge workflow.
- Phase 5: Implemented dirty-state tracking, Save As flow, unsaved-changes warnings, output naming suggestions, write failure handling, and success feedback for merge/split/extract.

## Stabilization work completed after Phase 5

- Improved main viewer sharpness with separate high-quality viewport-aware rendering for the document view
- Added separate render handling for sidebar thumbnails and Editor thumbnails
- Wired Merge PDFs into the home screen, toolbar, and File menu
- Added structural edit undo/redo foundation for reorder, rotate, and delete
- Stabilized Editor selection so checkbox state, card highlight, selected count, and operation targets stay synchronized
- Repaired Editor reorder so drop commits a real reordered page sequence
- Restored a simpler compact Editor grid layout
- Corrected the internal Editor card structure so thumbnail, checkbox, and page number are aligned consistently
- Added a reorder test covering the underlying PDF rewrite path

## Final MVP freeze entry

- Finalized the current repository as the frozen MVP baseline for GitHub/public use
- Updated the public-facing documentation and project-memory files to reflect the current codebase truth
- Confirmed the current verification baseline: `pytest` passes and `python3 -m compileall pdf_app tests` passes
- Intentionally deferred the next phase of work to:
  - annotation tools
  - richer recent-files persistence
  - search UX polish and in-page highlighting
  - keyboard shortcuts and packaging/release polish

## Phase 2 - Post-MVP hardening and release preparation (pass 1)

- Reviewed the structural edit path across reorder, delete, rotate, extract, split, undo/redo, and Save As to keep changes incremental on top of the frozen MVP architecture.
- Added `PdfAccessService` to centralize password-protected PDF handling without rewriting Viewer/Editor workflows or the working-copy model.
- Wired protected-PDF password prompting into standard open flow and merge import flow, with retry-on-error handling and clean cancel behavior.
- Kept protected documents compatible with Viewer mode, Editor mode, search, structural edits, dirty tracking, undo/redo, and Save As by unlocking into the existing temporary working copy.
- Hardened `PdfOperationService` with validation for malformed reorder sequences, duplicate page targets, out-of-range indices, split bounds, and encrypted merge inputs.
- Fixed page-count refresh behavior so delete/undo/redo clamps the current page after structural edits that remove pages.
- Fixed failed structural operations so a pre-operation undo snapshot is discarded when the operation does not complete, preventing false undo availability.
- Expanded automated coverage for protected-PDF unlock behavior, structural validation, page-count clamping, and failed-history cleanup.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 2 - Post-MVP hardening and release preparation (pass 2)

- Kept the existing shared search service and Viewer workflow intact while making the Viewer Tool Pane search section collapsible.
- Improved search result feedback with clearer idle, no-result, count, and active-position messaging in the Tool Pane and status bar.
- Replaced the in-memory recent-files list with `RecentFilesService`, backed by persisted JSON storage under the app config directory.
- Loaded persisted recents during `DocumentManager` startup and continued updating them through the same document-open path so working-copy editing and Save As behavior were unaffected.
- Added graceful handling for missing or inaccessible recent files by warning the user, removing stale entries from persistence, and refreshing the Home screen list.
- Kept the Home screen simple by continuing to surface a single recent-files list, now with missing entries clearly marked instead of crashing or silently failing.
- Expanded automated coverage for persisted recent-files behavior and blank-query search handling.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 2 - Post-MVP hardening and release preparation (pass 3)

- Added a focused keyboard shortcut layer on top of the existing `MainWindow` actions instead of introducing a larger shortcut framework.
- Bound conventional global shortcuts for open, save as, find, full screen, undo, and redo.
- Added practical Viewer shortcuts for next/previous page, next/previous search result, zoom in, zoom out, and zoom reset.
- Added practical Editor shortcuts for deleting selected pages and selecting all pages in the editor workspace.
- Kept shortcut behavior context-sensitive so Viewer navigation only runs in Viewer mode, Editor selection/edit shortcuts stay in the editor workspace, and text inputs keep normal typing/editing behavior.
- Preserved password-protected PDF open/import handling, recent-files persistence, shared search behavior, dirty tracking, working-copy edits, and Save As flow while adding shortcuts.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 2 - Post-MVP hardening and release preparation (focused Viewer navigation update)

- Added left/right arrow page-wise navigation for Viewer mode using the existing `jump_to_page()` path so current page state, thumbnail selection, status updates, and page tracking stay synchronized.
- Scoped the new arrow shortcuts to the Viewer workspace subtree only, so they do not trigger while typing in search inputs or while using the thumbnail list.
- Added focus handling for the Viewer document surface so page widgets and the scroll viewport can own focus cleanly when the user interacts with the main document view.
- Preserved the existing soft-scroll behavior, search navigation, password-protected PDF flow, undo/redo, and Save As behavior while adding page-wise arrow navigation.

## Phase and requirement coverage

- Covered the MVP boundary through Phase 5 only
- Preserved the required architecture: shared `MainWindow`, Viewer/Editor modes, central workspace swapping, shared search service, working-copy editing, and Save As first behavior

## Assumptions made

- Search navigation is usable at MVP level without exact in-page highlight overlays
- Undo/redo uses working-copy snapshot history as the current practical MVP implementation

## Deferred items

- Annotation tools and annotation UI
- Packaging polish
- Advanced in-page search highlighting
