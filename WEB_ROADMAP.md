# Web Roadmap And Technical Direction

## Product framing

The web app is not a direct port of the desktop UI.

It should reuse validated desktop behaviors where helpful:
- viewer/editor separation
- thumbnail-driven navigation
- structural page operations
- search behavior

But it should use web-native interaction patterns and architecture.

## Feature prioritization

## Web v1

- upload/open PDF
- page viewer with PDF rendering
- left thumbnail rail
- top toolbar with zoom and mode controls
- page navigation/current-page tracking
- text search with results and next/previous navigation
- page organization/editor mode
- drag-reorder pages
- rotate selected page(s)
- delete selected page(s)
- extract selected page(s)
- split by range
- download/export result PDF

## Web v1.5

- merge PDFs
- password-protected PDF handling
- lightweight recent-document session history
- stronger loading/progress states for large files
- exact in-page search highlight overlays
- basic keyboard shortcut layer

## Later / deferred

- highlight and underline annotations
- annotation export/write-back
- accounts and cloud storage
- collaboration/sharing
- OCR
- AI workflows
- granular operation history
- offline-first support

## Recommended architecture

## Frontend

Recommendation:
- Next.js
- TypeScript
- React App Router

Why:
- good developer velocity
- strong routing and deployment story
- easy API integration
- good fit for a document-oriented SPA-style workflow

## Backend

Recommendation:
- FastAPI
- Python

Why:
- aligns with the existing Python PDF-processing foundation
- easy to reuse or adapt desktop-side PDF logic
- strong fit for async upload/job endpoints without overcomplication

## PDF rendering/viewing

Recommendation:
- PDF.js in the frontend for page rendering, text layer, and searchable page viewing

Why:
- standard browser PDF rendering path
- proven ecosystem support
- avoids shipping page images from the backend for every viewer update

## PDF processing/editing

Recommendation:
- server-side PDF processing in Python
- reuse/adapt current `pypdf` and PyMuPDF-backed logic where practical

Why:
- structural edits are already modeled in Python
- server-side processing avoids heavy browser-only mutation complexity
- easier to keep exported PDFs authoritative and consistent

## File handling strategy for MVP

Recommendation:
- upload PDF to backend
- store it temporarily in local dev storage or S3-compatible object storage
- create a server-side working copy/session document
- apply operations against that working copy
- return processed file on export/download
- expire temporary files automatically

Constraints:
- no account system in v1
- no permanent user library in v1

## Deployment direction for MVP

Recommendation:
- Next.js frontend deployed separately from FastAPI backend
- use a simple single-region deployment setup
- use object storage for temporary files in hosted environments

Practical MVP options:
- Vercel for Next.js + Render/Railway/Fly for FastAPI
- or a single-container/full-stack deployment platform if team preference is simplicity over separation

Recommended default:
- Vercel for frontend
- Render or Railway for backend
- S3-compatible bucket for temp files

## Why this stack is a good fit

- Fast path to an implementation-ready web MVP
- Reuses Python PDF-processing strengths from the desktop codebase
- Keeps rendering client-side and mutations server-side, which is a clean split
- Avoids forcing browser-only PDF mutation logic too early
- Leaves room for later accounts/storage/collaboration without requiring them now

## Recommended web UI structure

Use a web-native three-area layout:

- Top toolbar
  - upload/open
  - mode switch: View / Edit
  - zoom controls
  - search entry
  - export/download

- Left thumbnail rail
  - page thumbnails
  - current page indicator
  - selected pages in edit mode

- Center document viewport
  - PDF page rendering
  - continuous or paged viewing depending on implementation preference

- Right tools panel
  - search results in viewer context
  - page actions in editor context
  - operation controls such as rotate/delete/extract/split

Use modal or drawer flows for:
- file upload errors
- split range input
- export confirmation/progress

## W2 implementation scope

W2 should build the technical foundation, not the full product.

Recommended W2 deliverables:
- create web workspace structure
  - `web/` Next.js app
  - `api/` FastAPI app
- establish shared API contract for:
  - upload/open document
  - fetch page/document metadata
  - search
  - rotate/delete/extract/split/reorder
  - export/download
- integrate PDF.js viewer shell in the frontend
- implement basic upload flow
- implement temporary file/session handling in backend
- port the first server-side structural operations into web API endpoints
- build the base web layout:
  - toolbar
  - thumbnail rail
  - main viewport
  - right panel shell
- document local dev/run instructions

W2 should not yet try to finish:
- annotations
- collaboration
- cloud accounts/storage
- OCR/AI
- polished production deployment

## Major open questions

- Do we want continuous-scroll viewing or single-page-first viewing in the initial web viewer?
- Should reorder be available in the very first interactive W2 slice, or land immediately after base viewer/edit shell?
- Do we want password-protected PDFs in Web v1 or move them to v1.5 to reduce early complexity?
- Which hosted storage/service choice best fits expected file sizes and privacy expectations for MVP testing?
