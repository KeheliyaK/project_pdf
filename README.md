# PDF App MVP

A desktop PDF viewer and structural editor MVP built with Python, PySide6, PyMuPDF, and pypdf.

This repository is the current frozen MVP baseline.

## MVP scope

The current MVP focuses on:
- local PDF viewing and navigation
- shared Viewer and Editor modes in one main window
- text search
- structural page editing
- safe local export with a Save As first workflow

The MVP intentionally stops before annotation tools.

## Implemented features

- Home screen with `Open PDF`, `Merge PDFs`, drag-and-drop open, and a lightweight recent-files list
- Shared main window with `Viewer` and `Editor` modes
- Viewer mode with continuous scroll, zoom, full screen, page jump, page tracking, and left thumbnail navigation
- Shared text search used by both the top toolbar search field and the Viewer Tool Pane
- Editor page-organization grid with multi-selection and drag-and-drop reorder
- Structural operations: reorder, delete, rotate selected, rotate all, extract selected pages, split by range, and merge PDFs
- Save As first export flow with working-copy editing, dirty tracking, unsaved-changes prompts, and write-error handling
- Undo/redo foundation for structural edits: reorder, rotate, and delete

## Deferred / post-MVP features

- Annotation tools and annotation UI
- Password-protected PDF support
- Keyboard shortcuts and packaging polish
- Richer recent-files persistence
- More advanced in-page search highlighting and search-panel polish

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
source .venv/bin/activate
python -m pdf_app.app.main
```

## Test

```bash
source .venv/bin/activate
pytest
python3 -m compileall pdf_app tests
```

## Current known limitations

- The Viewer search panel is functional but not collapsible
- Search navigation jumps to the correct page/result, but does not visually mark the exact in-page match
- Recent files are lightweight rather than a polished persisted history feature
- Undo/redo is snapshot-based for the current structural edit set and is not command-granular

## Project structure overview

```text
pdf_app/
  app/            Application entry point
  pdf_ops/        PDF structural operations
  pdf_render/     Page and thumbnail rendering
  search/         Search models and engine
  services/       Document, export, history, and search services
  state/          Basic application and document state
  ui/             Main window, home screen, viewer/editor UIs, dialogs
tests/            Minimal PDF operation tests
```

## Notes

- The app edits a temporary working copy and does not modify the original PDF in place.
- This repository should be treated as the frozen MVP baseline for the next phase of work.
