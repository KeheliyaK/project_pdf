# Phase 6A Action Grouping

Source inventory: [phase6a_control_inventory.md](/Users/keheliyak/Documents/New%20project/phase6a_control_inventory.md:1)

Note on terminology:

- `Fit Page` is included in the requested Persistent utility tier, but there is no current visible `Fit Page` control in the audited Phase 6A code.
- It is therefore noted as a future utility slot, not a current action.

## Tier Classification

| Action | Tier | Notes |
| --- | --- | --- |
| Undo | Primary | Must stay visible in top bar |
| Redo | Primary | Must stay visible in top bar |
| Viewer mode toggle | Primary | Must stay visible in top bar |
| Editor mode toggle | Primary | Must stay visible in top bar |
| Merge PDFs | Primary | Must stay visible in top bar and File menu |
| Search field | Primary | Primary action, but its visible home moves from top toolbar to right-rail Search panel |
| Page jump | Primary | Footer stays unchanged |
| Go | Primary | Footer stays unchanged |
| Search Previous | Secondary | Visible when Search panel is active |
| Search Next | Secondary | Visible when Search panel is active |
| Search result list | Secondary | Visible when Search panel is active |
| Search collapse / expand | Secondary | Search panel-local chrome |
| Highlight | Secondary | Visible when Annotate panel is active |
| Underline | Secondary | Visible when Annotate panel is active |
| Cancel Tool | Secondary | Visible when Annotate panel is active |
| Delete Selected annotation | Secondary | Visible when Annotate panel is active |
| Reset Document Annotations | Secondary | Visible when Annotate panel is active |
| Rotate current / selected 90 CW | Secondary | Visible when Pages panel is active |
| Rotate current / selected 90 CCW | Secondary | Visible when Pages panel is active |
| Rotate current / selected 180 | Secondary | Visible when Pages panel is active |
| Rotate All 90 CW | Secondary | Visible when Pages panel is active |
| Rotate All 90 CCW | Secondary | Visible when Pages panel is active |
| Rotate All 180 | Secondary | Visible when Pages panel is active |
| Delete Selected pages | Secondary | Visible when Organize panel is active in Editor |
| Extract Selected pages | Secondary | Visible when Organize panel is active in Editor |
| Split by Range | Secondary | Visible when Organize panel is active in Editor |
| Zoom In | Persistent utility | Always visible in right rail bottom |
| Zoom Out | Persistent utility | Always visible in right rail bottom |
| Fit Page | Persistent utility | Not currently implemented in Phase 6A UI; reserved future utility slot |
| Open PDF | Persistent utility outside panel model | File menu only after Phase 6 |
| Save As | Persistent utility outside panel model | File menu only after Phase 6 |
| Full Screen | Persistent utility outside panel model | Recommended for View menu |
| Thumbnail navigation | Persistent utility outside panel model | Fixed left pane, unchanged |
| Exit | Persistent utility outside panel model | File menu only |
| Keyboard Shortcuts help | Persistent utility outside panel model | Help menu only |
| Open PDF from Home | Persistent utility outside panel model | Home screen action, outside panel model |
| Merge PDFs from Home | Persistent utility outside panel model | Home screen action, outside panel model |
| Open recent file from Home | Persistent utility outside panel model | Home screen contextual action, outside panel model |
| Drag and drop PDF on Home | Persistent utility outside panel model | Home screen contextual action, outside panel model |
| Viewer page click / focus | Persistent utility outside panel model | Canvas interaction, not a shell panel action |
| Viewer drag to place annotation | Secondary | Depends on active Annotate tool |
| Viewer page click annotation hit-test | Secondary | Depends on Annotate selection context |
| Editor page selection | Persistent utility outside panel model | Canvas interaction, not a shell panel action |
| Editor checkbox selection | Persistent utility outside panel model | Canvas interaction, not a shell panel action |
| Editor drag-and-drop reorder | Persistent utility outside panel model | Canvas interaction, not a shell panel action |
| Select all pages | Persistent utility outside panel model | Keyboard-only Editor utility |
| Viewer page next / previous shortcuts | Persistent utility outside panel model | Keyboard-only Viewer utility |
| Editor local Undo / Redo duplicate buttons | Primary currently, but should collapse into top-bar Primary actions after shell cleanup | Duplicate local chrome |

## Search Panel

| Action | Notes |
| --- | --- |
| Search field | Primary action housed in this panel after Phase 6 |
| Search Previous | Secondary |
| Search Next | Secondary |
| Search result list | Secondary |
| Search collapse / expand | Secondary panel-local control |
| Find / focus search command | Global command that should open this panel and focus this panel's field |
| Find next result | Keyboard command routed here |
| Find previous result | Keyboard command routed here |

## Annotate Panel

| Action | Notes |
| --- | --- |
| Highlight | Viewer only |
| Underline | Viewer only |
| Cancel Tool | Viewer only |
| Delete Selected annotation | Viewer contextual |
| Reset Document Annotations | Viewer contextual |
| Viewer drag region placement | Canvas-side interaction driven by active panel tool |
| Viewer annotation hit-test selection | Canvas-side interaction driven by active annotation context |

## Pages Panel

| Action | Notes |
| --- | --- |
| Rotate current / selected 90 CW | Viewer contextual; uses current page when no thumbnail selection exists |
| Rotate current / selected 90 CCW | Viewer contextual; uses current page when no thumbnail selection exists |
| Rotate current / selected 180 | Viewer contextual; uses current page when no thumbnail selection exists |
| Rotate Selected 90 CW | Editor contextual; requires explicit editor selection |
| Rotate Selected 90 CCW | Editor contextual; requires explicit editor selection |
| Rotate Selected 180 | Editor contextual; requires explicit editor selection |
| Rotate All 90 CW | Shared Viewer and Editor |
| Rotate All 90 CCW | Shared Viewer and Editor |
| Rotate All 180 | Shared Viewer and Editor |
| Thumbnail navigation | Viewer only support surface that influences selected-page rotate behavior; stays fixed left |

## Organize Panel

| Action | Notes |
| --- | --- |
| Delete Selected pages | Editor only |
| Extract Selected pages | Editor only |
| Split by Range | Editor only |
| Drag-and-drop reorder | Editor-only canvas interaction that supports Organize workflow but does not live in the panel itself |
| Editor page selection | Editor-only canvas interaction that feeds panel actions |

## Edge Cases For Phase 6B.2

These actions currently appear in both Viewer and Editor contexts with different behavior and need explicit handling in the shared right-rail panel design:

| Action | Viewer behavior | Editor behavior |
| --- | --- | --- |
| Rotate Selected 90 CW / 90 CCW / 180 | Uses thumbnail selection if present, otherwise falls back to current page | Requires explicit selected pages from the editor grid; no current-page fallback |
| Rotate All 90 CW / 90 CCW / 180 | Exposed in Viewer pane | Exposed in Editor pane; same underlying `MainWindow.rotate_all_pages()` |
| Undo / Redo | Global top toolbar actions plus Viewer-compatible keyboard routing | Global top toolbar actions plus duplicate local Editor mini-toolbar buttons |

## Acceptance Check

- Every current toolbar, right pane, menu, and status bar action from the audited UI appears in Deliverable 1 and is reflected here by tier or panel placement.
- `focus_search()` has been identified as a routing edge case: it currently focuses the top toolbar search field and must be redirected to the right-rail Search panel in Phase 6B.2.
- Zoom In and Zoom Out are confirmed as Persistent utility actions moving to the right-rail bottom.
- The locked shell decisions are preserved here: thumbnails fixed left, rail on the right, page jump in the footer.
