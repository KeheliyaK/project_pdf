# PDF App MVP

Early preview for a macOS mini launch.

A desktop PDF viewer and structural editor MVP built with Python, PySide6, PyMuPDF, and pypdf.

This repository is the current frozen MVP baseline and the source for the current macOS `.app` preview target.

## MVP scope

The current MVP focuses on:
- local PDF viewing and navigation
- shared Viewer and Editor modes in one main window
- text search
- structural page editing
- safe local export with a Save As first workflow

The MVP intentionally stops before a full annotation suite, although the repository now includes a mini-launch-ready highlight/underline annotation subset built on the internal annotation foundation.

## Early Preview Scope

Current launch-facing scope:
- stable PDF viewing and structural editing
- password-protected PDF open
- persisted recent files
- mini-launch annotation preview with `Highlight` and `Underline` only
- top-level Undo/Redo shared across structural edits and visible annotation actions

Deferred from the visible preview scope:
- text box annotation UI
- PDF annotation write-back/export
- advanced annotation editing

## Implemented features

- Home screen with `Open PDF`, `Merge PDFs`, drag-and-drop open, and a persisted recent-files list
- Shared main window with `Viewer` and `Editor` modes
- Viewer mode with continuous scroll, zoom, full screen, page jump, page tracking, and left thumbnail navigation
- Shared text search used by both the top toolbar search field and the Viewer Tool Pane, including collapsible search controls and clearer result-position feedback
- Editor page-organization grid with multi-selection and drag-and-drop reorder
- Structural operations: reorder, delete, rotate selected, rotate all, extract selected pages, split by range, and merge PDFs
- Password-protected PDF open support with password prompt, plus protected-PDF import support for merge workflow
- Keyboard shortcuts for common workflows such as open, save as, find, search next/previous, page navigation, zoom, full screen, unified undo/redo, and core editor selection/delete actions
- Help menu entry for a simple in-app keyboard shortcut guide
- Mini-launch annotation tools in Viewer mode: drag-to-place highlight and underline with selection, delete, top-level undo/redo, and reset support
- Save As first export flow with working-copy editing, dirty tracking, unsaved-changes prompts, and write-error handling
- Undo/redo foundation for structural edits: reorder, rotate, and delete

## Deferred / post-MVP features

- Advanced annotation editing and PDF annotation write-back/export integration
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

## Package For macOS Preview

This repository includes a macOS-first local packaging path using PyInstaller for the preview `.app`.

1. Install the packaging dependency set:

```bash
source .venv/bin/activate
pip install -r requirements-packaging.txt
```

2. Build the app bundle:

```bash
bash scripts/build_macos_app.sh
```

3. Launch the packaged app for manual testing:

```bash
open "dist/PDF App MVP.app"
```

4. Run the smoke checklist before sharing the build:

```bash
cat MINI_LAUNCH_SMOKE_CHECKLIST.md
```

The generated bundle is intended for early-user preview and local distribution testing. It is not yet codesigned, notarized, or wrapped in an installer.

## Test

```bash
source .venv/bin/activate
pytest
python3 -m compileall pdf_app tests
```

## Current known limitations

- Search navigation jumps to the correct page/result, but does not visually mark the exact in-page match
- Search panel collapse/expand control icon polish is intentionally deferred
- Undo/redo is snapshot-based for the current structural edit set and is not command-granular
- The macOS packaging path is intended for local testing and is not yet signed or notarized
- Annotations are currently session-visible only and are not embedded into PDFs by `Save As` yet

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
- Password-protected PDFs are unlocked into the temporary working copy after the password is accepted, so Save As exports the currently unlocked working copy.
- Recent files are persisted locally across restarts, and stale entries are removed if a file is missing or no longer accessible.
- A simple keyboard shortcut reference is available from `Help > Keyboard Shortcuts`.
- Highlight and underline now use a drag selection interaction in Viewer mode, with `H`, `U`, and `Esc` shortcuts for quick tool control.
- Highlight and underline can be selected in Viewer mode and removed with the Viewer pane or `Delete`, and the visible annotation set supports document-level reset.
- Top-level `Undo` / `Redo` from the toolbar, Edit menu, and standard shortcuts now cover both structural edits and the visible highlight/underline annotation workflow.
- Text box support remains internal and is intentionally not part of the current visible mini-launch toolset.
- Annotations are session-visible only for now and are not embedded into exported PDFs by `Save As`.
- PDF annotation write-back/export integration is not implemented yet.
- This repository should be treated as the frozen MVP baseline for the next phase of work.
