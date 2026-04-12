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

## Phase 2 - Post-MVP hardening and release preparation (pass 4)

- Added a macOS-first PyInstaller packaging path with `pdf_app_mvp.spec`, a dedicated packaging requirements file, and a repeatable local build script.
- Kept packaging configuration intentionally modest and release-oriented for local `.app` generation instead of overbuilding cross-platform automation.
- Updated application metadata in the Qt entry point so packaged builds have stable application name, display name, version, and organization settings.
- Added a `Help > Keyboard Shortcuts` modal dialog that documents the currently implemented shortcuts grouped by Global, Viewer, and Editor contexts.
- Kept the shortcut guide static and maintainable rather than introducing a new shortcut registry system.
- Preserved normal PDF open, password-protected PDF flow, Viewer/Editor modes, search, recent-file persistence, keyboard shortcuts, dirty tracking, and Save As behavior while preparing packaging.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 3 - Annotation foundation

- Added a minimal internal annotation model with stable ids, typed annotation kinds, page association, geometry, style, and optional text content for upcoming highlight, underline, and text box tools.
- Added `AnnotationService` as the centralized annotation operation layer for add, update, delete, page/document query, and reset-on-document-change behavior.
- Tied annotation state to the current working-copy document session by opening/resetting the annotation service when a different working document is opened.
- Kept current behavior honest: annotation state is prepared for future Save As/export integration, but this phase does not write annotations back into PDFs or claim persistence beyond the current document session.
- Added lightweight Viewer rendering hooks so future annotation overlays can be requested page-by-page and composited without redesigning Viewer mode.
- Preserved normal PDF open, password-protected PDF flow, Viewer/Editor modes, search, recent files, keyboard shortcuts, Save As behavior, and packaging-safe execution while adding the annotation backbone.
- Expanded automated coverage for core annotation service operations and reset behavior.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 4 - First annotation tools

- Added first visible annotation tools for highlight, underline, and text box in Viewer mode through a simple click-to-place workflow.
- Reused the Phase 3 annotation model/service backbone instead of introducing separate tool-specific storage logic.
- Extended the Viewer interaction path so page clicks can be translated into document coordinates for annotation placement.
- Added lightweight Viewer Tool Pane controls for activating highlight, underline, and text box placement without redesigning the Viewer.
- Kept the first text box workflow intentionally simple by prompting for text content during placement instead of adding advanced inline editing controls.
- Ensured created annotations stay visible through page navigation, zoom changes, and mode switches by rendering through the shared overlay path.
- Kept Save As behavior honest: annotations remain session-visible and document-associated for this phase, but are not embedded into output PDFs yet.
- Preserved normal PDF open, password-protected PDF flow, Viewer/Editor modes, search, recent files, keyboard shortcuts, Save As behavior, and packaging-safe execution while exposing the first annotation tools.
- Expanded automated coverage for the annotation service lifecycle and reset behavior.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 4A - Highlight and underline interaction upgrade

- Replaced fixed-size click placement for highlight and underline with drag-based region selection in Viewer mode, while keeping text box on its existing simple click-to-place path.
- Reused the shared annotation service and Viewer overlay rendering path instead of introducing separate highlight and underline interaction code paths.
- Added Viewer-side rubber-band selection and document-coordinate conversion so drag gestures map cleanly onto page geometry without changing the underlying annotation model.
- Added clearer active-tool feedback by switching highlight and underline into a crosshair cursor mode and updating the Viewer tool-pane status text to describe the drag interaction.
- Added document-scoped annotation undo, redo, and clear controls through the centralized annotation service, intentionally keeping this separate from the existing structural edit history.
- Added lightweight Viewer annotation shortcuts for highlight (`H`), underline (`U`), and exiting annotation mode (`Esc`) without overloading existing global undo/redo behavior.
- Preserved normal PDF open, password-protected PDF flow, Viewer/Editor modes, search, recent files, keyboard shortcuts, Save As behavior, and packaging-safe execution while upgrading highlight and underline interactions.
- Expanded automated coverage for annotation history undo/redo and clear/reset behavior.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 4B - Annotation management pass 1

- Added document-scoped reset for the visible annotation launch set so highlight and underline annotations can be cleared predictably with explicit confirmation.
- Added simple Viewer-mode selection for existing highlight and underline annotations by clicking rendered annotations when no creation tool is active.
- Added visible selected-state rendering in the page overlay path so chosen annotations are clearly distinguishable without introducing resize handles or a larger editing framework.
- Added deletion for selected highlight and underline annotations through the Viewer pane and `Delete`, keeping the shortcut scoped to the Viewer workspace.
- Extended the centralized annotation service with grouped deletion and type-filtered reset helpers so annotation management stays in the service layer instead of being scattered across UI code.
- Kept text box support internal and hidden from the visible mini-launch toolset to keep the launch-facing annotation set focused and coherent.
- Preserved normal PDF open, password-protected PDF flow, Viewer/Editor modes, search, recent files, keyboard shortcuts, structural edits, Save As behavior, and packaging-safe execution while adding annotation management.
- Expanded automated coverage for annotation grouped deletion and visible-toolset reset behavior.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 4C - Mini launch annotation undo/redo unification

- Removed the visible annotation-specific undo/redo buttons from the Viewer annotation pane so the launch-facing toolset stays centered on highlight, underline, delete, reset, and cancel.
- Added a thin unified history router on top of the existing structural and annotation history systems instead of rewriting them into one engine.
- Routed the existing top-level Undo/Redo toolbar actions, Edit-menu actions, and standard shortcuts through that unified decision layer so the most recent structural or visible annotation action is undone/redone predictably.
- Kept structural history and annotation history separate internally for safety, while making the user-facing mini-launch workflow feel like one coherent undo/redo system.
- Preserved Reset Document Annotations as the explicit annotation-specific bulk action in the Viewer pane.
- Kept text box support internal/deferred and out of the visible launch-facing undo/redo scope.
- Expanded automated coverage for the unified history router service.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.

## Phase 5 - Mini launch preparation (macOS .app)

- Treated the current repository as the launch-preparation baseline for an early macOS `.app` preview instead of expanding the product surface further.
- Kept the visible annotation scope intentionally limited to highlight and underline, with text box still hidden from the launch-facing UI.
- Tightened launch-facing documentation so the preview scope, session-only annotation behavior, Save As honesty, and macOS packaging target are explicit and easy for early users to understand.
- Added a concise `MINI_LAUNCH_SMOKE_CHECKLIST.md` covering launch, normal/protected open, Viewer, Editor, search, highlight, underline, annotation selection/delete/reset, unified undo/redo, and Save As honesty.
- Slightly hardened the PyInstaller spec for preview packaging by disabling optional UPX compression in the macOS bundle path.
- Updated the macOS build script output so successful preview builds point directly to the generated `.app` and the smoke checklist to run next.
- Confirmed shell-script validity with `bash -n scripts/build_macos_app.sh`.
- Confirmed the current verification baseline in the project venv: `./.venv/bin/pytest` passes and `./.venv/bin/python -m compileall pdf_app tests` passes.
- Confirmed that PyInstaller is still a separately installed packaging dependency and documented that preview-build requirement honestly.

## Phase 5A - Packaged-app bug fix: Editor checkbox multi-selection

- Fixed a launch-blocking Editor regression where checkbox toggles no longer preserved the shared multi-selection state even though Cmd-click selection still worked.
- Kept the existing Editor architecture intact and fixed the current selection flow rather than redesigning the card layout or selection model.
- Updated the Editor highlight-selection path so checkbox-selected pages remain part of the shared selection state instead of being overwritten by a later highlight-selection refresh.
- Preserved synchronization between checkbox state, card highlight, selected count, and selected-page operation targets.
- Added regression coverage for checkbox select, checkbox deselect, checkbox multi-select preservation, mixed checkbox plus card selection, and operation targeting via the shared selected-pages state.
- Polished the custom Editor checkbox rendering so the checked state now uses a clearer accent fill and a thicker high-contrast white checkmark for faster visual scanning in both dev and packaged macOS runs.

## Phase 5A - Final release-artifact fix: macOS tester-ready bundle output

- Fixed the macOS packaging regression so the build now produces the intended `dist/PDF App MVP.app` bundle again instead of leaving only the folder-style onedir artifact as the usable output.
- Restored the spec to use a stable repo-relative root through PyInstaller's spec configuration instead of a brittle runtime path assumption.
- Added a packaged `.icns` app icon asset and wired the bundle to that icon so the macOS app metadata again points to a real icon resource.
- Updated the build script to use workspace-local PyInstaller config and work directories, avoiding cache-cleanup permission failures during preview builds.
- Rebuilt the macOS preview artifact successfully and verified the `.app` bundle metadata reports `CFBundlePackageType=APPL`, the expected executable name, and the packaged icon file.
- Confirmed the launched process is the app bundle executable, preserving direct GUI launch behavior for early tester sharing.

## Phase and requirement coverage

- Covered the MVP boundary through Phase 5 only
- Preserved the required architecture: shared `MainWindow`, Viewer/Editor modes, central workspace swapping, shared search service, working-copy editing, and Save As first behavior

## Assumptions made

- Search navigation is usable at MVP level without exact in-page highlight overlays
- Undo/redo uses working-copy snapshot history as the current practical MVP implementation

## Deferred items

- PDF annotation write-back/export integration
- Annotation editing, deletion UI, resizing, and richer formatting controls
- Packaging polish, codesigning, notarization, and installer work
- Advanced in-page search highlighting
