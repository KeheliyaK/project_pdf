# MyLeaflet - Mini Launch v0.2

Desktop PDF viewer and structural editor MVP built with Python, PySide6, PyMuPDF, and pypdf.

This repository contains the MyLeaflet desktop MVP mini launch release, version v0.2.

## Release status

- Release: MyLeaflet - Mini Launch v0.2
- Version: v0.2
- Status: desktop MVP frozen
- Baseline intent: stable, reviewable reference for future web planning and implementation
- Scope: document the current desktop product honestly without adding new feature claims

## Frozen feature set

- Open local PDFs, including password-protected PDFs after password prompt
- Home screen with recent files and drag-and-drop open
- Viewer mode with:
  - continuous page scroll
  - thumbnail sidebar
  - page jump and current-page tracking
  - zoom controls and full screen
  - text search with result list and next/previous navigation
  - highlight and underline annotations
- Editor mode with:
  - page organization grid
  - multi-selection
  - drag-and-drop reorder
  - rotate selected pages
  - rotate all pages
  - extract selected pages
  - split by page range
  - delete selected pages
- Merge PDFs workflow
- Save As / working-copy flow with dirty tracking and unsaved-change prompts
- Undo / Redo for structural edits and visible annotation actions
- Keyboard shortcuts for the current core Viewer and Editor workflows
- In-app shortcut guide

## Deferred / intentionally excluded

- Web version implementation
- PDF annotation write-back/export
- Rich annotation editing beyond the current highlight/underline MVP
- Advanced in-page search highlighting
- Production packaging/distribution polish such as codesigning, notarization, and installer work

## Current known limitations

- Search navigates correctly but does not visually highlight the exact in-page match region
- Highlight and underline are session-visible only and are not embedded into exported PDFs by `Save As`
- Annotation editing remains intentionally lightweight
- Desktop packaging exists for preview/manual testing, not polished release distribution
- Verification is still primarily compile/test/manual smoke-check based, not a full release automation pipeline

## Recommended next phase

The next major phase is web-version planning and implementation.

The desktop app should now be treated as the reference behavior baseline:
- feature scope should be compared against this desktop MVP
- workflow differences in the web version should be intentional and documented
- desktop documentation should remain the source of truth until web planning replaces it with a broader product plan

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

## Packaging

For local macOS preview packaging only:

```bash
source .venv/bin/activate
pip install -r requirements-packaging.txt
bash scripts/build_macos_app.sh
open "dist/MyLeaflet.app"
```

The packaging path is for preview/manual testing and is not yet a production release pipeline.

## Smoke checklist

Use [MINI_LAUNCH_SMOKE_CHECKLIST.md](/Users/keheliyak/Documents/New%20project/MINI_LAUNCH_SMOKE_CHECKLIST.md) before sharing a desktop build or treating a change as baseline-safe.

## Verification commands

```bash
source .venv/bin/activate
pytest
python3 -m compileall pdf_app tests
```

## Web W2 local development

Backend:

```bash
source .venv/bin/activate
pip install -r api/requirements.txt
uvicorn api.app.main:app --reload --port 8000
```

Frontend:

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

Expected local ports:
- frontend: `http://localhost:3000`
- backend: `http://localhost:8000`

Current web W2 flow:
- upload PDF
- render/view PDF in browser
- zoom in/out/reset
- download the current PDF back from the backend

## Project docs

- [PROJECT_STATUS.md](/Users/keheliyak/Documents/New%20project/PROJECT_STATUS.md): current freeze status and next phase
- [KNOWN_ISSUES.md](/Users/keheliyak/Documents/New%20project/KNOWN_ISSUES.md): honest non-blocking limitations and deferred work
- [IMPLEMENTATION_LOG.md](/Users/keheliyak/Documents/New%20project/IMPLEMENTATION_LOG.md): implementation and freeze history
- [MINI_LAUNCH_SMOKE_CHECKLIST.md](/Users/keheliyak/Documents/New%20project/MINI_LAUNCH_SMOKE_CHECKLIST.md): release-readiness/manual smoke checklist
- [WEB_PRD.md](/Users/keheliyak/Documents/New%20project/WEB_PRD.md): web product definition for the next phase
- [WEB_ROADMAP.md](/Users/keheliyak/Documents/New%20project/WEB_ROADMAP.md): web feature prioritization, architecture, and W2 scope
