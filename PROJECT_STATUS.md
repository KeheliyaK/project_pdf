# Project Status

## Project name
PDF App MVP

## Current phase
MVP frozen baseline

## MVP status
Frozen

## What is working now

- Shared main window with Home, Viewer, and Editor workflows
- Open PDF, drag-and-drop open, and a lightweight recent-files list
- Viewer mode with continuous scroll, zoom, full screen, thumbnails, page jump, and current-page tracking
- Shared PDF text search wired to both the toolbar search field and the Viewer Tool Pane
- Editor page-organization workspace with multi-selection and drag-and-drop reorder
- Structural operations: reorder, delete, rotate selected, rotate all, extract, split, and dedicated merge workflow
- Save As first export flow with working-copy editing, dirty tracking, unsaved-change prompts, and write-error handling
- Undo/redo foundation for structural edits: reorder, rotate, and delete
- Current automated tests for PDF operations are passing

## Latest completed fixes

- Separated rendering by context for main viewer pages, sidebar thumbnails, and Editor thumbnails
- Stabilized Editor selection so card highlight, checkbox state, count, and action targets stay synchronized
- Repaired Editor reorder commit so drag-and-drop produces a real reordered page sequence
- Restored a simpler compact Editor grid layout
- Corrected internal Editor card layout so thumbnail, checkbox, and page number use a stable structure

## Current non-blocking limitations

- Viewer search panel is not collapsible
- Search results do not visually highlight the exact in-page match region
- Recent files are still lightweight
- Undo/redo is snapshot-based rather than command-granular

## Immediate next phase after freeze

Post-MVP polish and hardening:
- password-protected PDF support
- search UX polish
- recent-files persistence improvements
- keyboard shortcuts
- packaging/release preparation for desktop distribution

## Maintenance note

Update this file whenever the frozen baseline changes or a new implementation phase begins.
