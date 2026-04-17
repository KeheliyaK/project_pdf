# Project Status

## Project name

MyLeaflet

## Current phase

Phase W2 - Web foundation vertical slice

## Mini Launch Status (v0.2)

- Desktop MVP prepared for mini launch
- Version updated to v0.2 under MyLeaflet branding
- Core functionality stable
- UI baseline finalized for this release
- No further feature changes in this release cycle

## Current status

- Desktop MVP remains frozen as the reference baseline
- W2 web foundation now defines the first full-stack slice structure in `web/` and `api/`
- Current web slice target is upload -> view -> zoom -> download

## Included in the frozen desktop MVP

- Home screen with open, merge, drag-and-drop open, and recent files
- Viewer mode with page navigation, zoom, full screen, thumbnails, page jump, and current-page tracking
- Editor mode with page organization, multi-selection, drag-and-drop reorder, and page operations
- Search with shared query flow, results list, and next/previous result navigation
- Structural operations: rotate selected, rotate all, extract, split, delete, reorder, and merge
- Highlight and underline annotations in Viewer mode
- Save As / working-copy editing flow with dirty tracking and unsaved-change prompts
- Undo / Redo across structural edits and visible annotation actions
- Password-protected PDF open support
- Keyboard shortcuts and in-app shortcut guide

## Intentionally excluded / deferred

- Web app implementation
- PDF annotation embedding/export
- Rich annotation editing tools beyond the current MVP subset
- Exact in-page search highlight overlays
- Production-grade packaging/distribution polish

## Known limitations summary

- Search navigation is stable, but exact in-page match highlighting is not implemented
- Annotations are visible in-session but are not written back into exported PDFs
- Annotation tooling is intentionally minimal
- Packaging is suitable for local preview/testing, not a finished signed release path
- Manual smoke testing is still part of release readiness

## Release-readiness baseline

Desktop MVP is considered freeze-ready when:

- core open/view/edit workflows still run
- search behaves consistently
- highlight/underline still behave consistently
- rotate/extract/split/delete still target the intended pages
- Save As still exports the working copy honestly
- the smoke checklist has been reviewed for the current build

See [MINI_LAUNCH_SMOKE_CHECKLIST.md](/Users/keheliyak/Documents/New%20project/MINI_LAUNCH_SMOKE_CHECKLIST.md).

## Next phase

The next strategic step after this slice is W3 - core web viewer/editor expansion.

W1 outputs now live in:
- [WEB_PRD.md](/Users/keheliyak/Documents/New%20project/WEB_PRD.md)
- [WEB_ROADMAP.md](/Users/keheliyak/Documents/New%20project/WEB_ROADMAP.md)

The desktop MVP should still be treated as:
- the reference behavior baseline
- the source for feature-scope comparison
- the product snapshot to preserve while web work begins

## Maintenance note

Update this file only when the frozen baseline changes materially or when the project formally enters the web phase.
