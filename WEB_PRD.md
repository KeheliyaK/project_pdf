# Web PRD

## Product goal

Build a web-native PDF viewer and lightweight page editor that reuses the validated desktop MVP behaviors where they make sense, while adopting a browser-friendly architecture and UI.

The web app should let a user upload a PDF, review pages, make common structural changes, and download the result without needing to install the desktop app.

## Target users and use cases

Primary users:
- individual users who need quick PDF cleanup/editing in the browser
- internal/demo users validating the product direction before broader expansion

Primary use cases:
- open a PDF in the browser
- review pages with thumbnails and zoom
- navigate quickly across the document
- rotate, delete, extract, and split pages
- reorder pages
- download the edited result
- search within the PDF

## Web v1 scope

Must-have scope for the first working web release:
- upload/open a PDF
- browser-based PDF viewing
- thumbnail rail
- page navigation and current-page tracking
- zoom in/out/reset
- text search with result list and next/previous navigation
- Editor workspace for page organization
- reorder pages
- rotate selected page(s)
- delete selected page(s)
- extract selected page(s)
- split by page range
- download/export the result PDF
- basic session-based document handling with no account requirement

## Deferred from Web v1

Not required for the first working web release:
- highlight and underline annotations
- merge PDFs
- password-protected PDF support
- recent files/history across sessions
- persistent cloud storage
- multi-user collaboration
- OCR
- AI-assisted workflows
- command-granular undo/redo
- mobile-optimized advanced editing

## Core user flows

### Flow 1: Upload and review

1. User uploads a PDF.
2. App renders the document viewer with thumbnails and toolbar controls.
3. User navigates pages, zooms, and searches text.

### Flow 2: Structural edit

1. User switches into page-editing mode.
2. User selects pages and performs reorder, rotate, delete, extract, or split actions.
3. App updates the working document state and preview.

### Flow 3: Export

1. User reviews the modified PDF.
2. User clicks download/export.
3. App returns the processed PDF file.

## Major constraints and risks

- Browser PDF rendering and server PDF processing must stay in sync.
- Large files can create upload, memory, and processing pressure.
- Drag-reorder and page preview performance need careful implementation for multi-page PDFs.
- Search UX should stay clear even if exact in-page highlight is deferred initially.
- File lifecycle and cleanup need to be explicit so temporary uploads do not accumulate.

## Success criteria for the first working web release

- A user can upload a PDF, view it, perform core structural edits, and download the result.
- Viewer and Editor flows feel consistent with the frozen desktop baseline where behavior overlaps.
- The app is stable for normal single-user MVP usage on common desktop browsers.
- The codebase has a clear frontend/backend boundary and is ready for iterative web feature expansion in W2+.
