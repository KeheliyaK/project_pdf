# Phase 6A Control Inventory

This inventory covers the current UI controls defined in:

- [pdf_app/ui/main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:1)
- [pdf_app/ui/toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:1)
- [pdf_app/ui/right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:1)
- [pdf_app/ui/viewer_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/viewer_mode_ui.py:1)
- [pdf_app/ui/edit_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/edit_mode_ui.py:1)
- [pdf_app/ui/home_screen.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/home_screen.py:1)
- [pdf_app/ui/status_bar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/status_bar.py:1)

Locked Phase 6 shell decisions reflected here:

- Thumbnails stay fixed left.
- Rail moves to the right side.
- Page jump stays in the footer.
- Zoom In and Zoom Out move to the right-rail bottom area.

## Control Table

| Action name | Current widget and file location | Mode scope | New destination after Phase 6 | Shortcut |
| --- | --- | --- | --- | --- |
| Open PDF | `QPushButton open_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:31) | Global | File menu only | Standard Open |
| Merge PDFs | `QPushButton merge_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:32) | Global | File menu + stays in top bar | None |
| Save As | `QPushButton save_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:33) | Global | File menu only | Standard Save As |
| Viewer mode toggle | `QPushButton viewer_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:34) | Global | Top bar | None |
| Editor mode toggle | `QPushButton editor_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:35) | Global | Top bar | None |
| Undo | `QPushButton undo_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:38) | Global | Top bar | Standard Undo |
| Redo | `QPushButton redo_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:39) | Global | Top bar | Standard Redo |
| Zoom Out | `QPushButton zoom_out_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:40) | Global | Right rail bottom below divider | Standard Zoom Out |
| Zoom In | `QPushButton zoom_in_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:41) | Global | Right rail bottom below divider | Standard Zoom In, `Ctrl+=` |
| Full Screen | `QPushButton fullscreen_button` in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:42) | Global | View menu | `F11` |
| Toolbar search submit | `QLineEdit search_input` return in [toolbar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/toolbar.py:43) | Global | Rail -> Search panel | Standard Find routes focus, submit has no separate shortcut |
| File > Open PDF | `QAction open_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:142) | Global | File menu only | Standard Open |
| File > Merge PDFs | `QAction merge_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:143) | Global | File menu + stays in top bar | None |
| File > Save As | `QAction save_as_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:144) | Global | File menu only | Standard Save As |
| File > Exit | `QAction exit_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:145) | Global | File menu | Standard Quit |
| Edit > Undo | `QAction undo_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:146) | Global | Edit menu + mirrored in top bar | Standard Undo |
| Edit > Redo | `QAction redo_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:147) | Global | Edit menu + mirrored in top bar | Standard Redo |
| Help > Keyboard Shortcuts | `QAction shortcuts_guide_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:148) | Global | Help menu | None |
| Find / focus search | `QAction find_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:167) | Global | Global command routed to Rail -> Search panel | Standard Find |
| Find next result | `QAction find_next_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:172) | Viewer | Rail -> Search panel | Standard Find Next |
| Find previous result | `QAction find_previous_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:177) | Viewer | Rail -> Search panel | Standard Find Previous |
| Toggle Full Screen | `QAction fullscreen_action` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:182) | Global | View menu | `F11` |
| Viewer next page | `QShortcut next_page_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:196) | Viewer | No new visible control required; keep keyboard-only viewer navigation | `Page Down` |
| Viewer previous page | `QShortcut previous_page_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:198) | Viewer | No new visible control required; keep keyboard-only viewer navigation | `Page Up` |
| Viewer next page by arrow | `QShortcut next_page_arrow_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:203) | Viewer | No new visible control required; keep keyboard-only viewer navigation | `Right Arrow` |
| Viewer previous page by arrow | `QShortcut previous_page_arrow_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:200) | Viewer | No new visible control required; keep keyboard-only viewer navigation | `Left Arrow` |
| Delete selected pages shortcut | `QShortcut delete_pages_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:207) | Editor | Rail -> Organize panel | `Delete` |
| Select all editor pages | `QShortcut select_all_pages_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:210) | Editor | No new visible control required; keep keyboard-only editor utility | Standard Select All |
| Highlight tool shortcut | `QShortcut highlight_tool_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:217) | Viewer | Rail -> Annotate panel | `H` |
| Underline tool shortcut | `QShortcut underline_tool_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:222) | Viewer | Rail -> Annotate panel | `U` |
| Cancel annotation tool shortcut | `QShortcut clear_annotation_tool_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:227) | Viewer | Rail -> Annotate panel | `Esc` |
| Delete selected annotation shortcut | `QShortcut delete_annotation_shortcut` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:230) | Contextual | Rail -> Annotate panel | `Delete` |
| Open PDF from Home | `QPushButton open_button` in [home_screen.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/home_screen.py:31) | Global | Home screen unchanged for Phase 6 | None |
| Merge PDFs from Home | `QPushButton merge_button` in [home_screen.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/home_screen.py:32) | Global | Home screen unchanged for Phase 6; also File menu + top bar | None |
| Drag and drop PDF on Home | `dropEvent` via `drop_label` area in [home_screen.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/home_screen.py:33) | Global | Home screen unchanged for Phase 6 | None |
| Open recent file from Home | `QListWidget recent_list` activation in [home_screen.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/home_screen.py:36) | Contextual | Home screen unchanged for Phase 6 | None |
| Viewer thumbnail navigation | `QListWidget left_pane` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:77) | Viewer | Left pane unchanged | None |
| Viewer thumbnail multi-select for page-targeted rotate | `QListWidget left_pane` in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:77) | Contextual | Left pane unchanged | None |
| Viewer page click / set current page | `ClickablePageLabel.clicked` in [viewer_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/viewer_mode_ui.py:14) | Viewer | Viewer canvas unchanged | None |
| Viewer page click for annotation hit-test / text-box placement routing | `ClickablePageLabel.position_clicked` in [viewer_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/viewer_mode_ui.py:15) | Contextual | Viewer canvas unchanged | None |
| Viewer drag region selection for highlight / underline placement | `ClickablePageLabel.selection_drag_completed` in [viewer_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/viewer_mode_ui.py:16) | Contextual | Viewer canvas unchanged with tools coming from Rail -> Annotate panel | None |
| Search collapse / expand | `QToolButton search_toggle` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:37) | Viewer | Rail -> Search panel as panel header control | None |
| Search field | `QLineEdit search_input` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:49) | Viewer | Rail -> Search panel | Standard Find focuses search flow; no direct widget shortcut |
| Search Previous | `QPushButton prev_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:54) | Viewer | Rail -> Search panel | Standard Find Previous |
| Search Next | `QPushButton next_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:55) | Viewer | Rail -> Search panel | Standard Find Next |
| Search result selection | `QListWidget results_list` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:64) | Viewer | Rail -> Search panel | None |
| Highlight | `QPushButton highlight_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:76) | Viewer | Rail -> Annotate panel | `H` |
| Underline | `QPushButton underline_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:77) | Viewer | Rail -> Annotate panel | `U` |
| Text Box | `QPushButton text_box_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:78) | Viewer | Not in current visible MVP shell; keep hidden and out of Phase 6 visible mapping | None |
| Cancel Tool | `QPushButton clear_tool_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:79) | Viewer | Rail -> Annotate panel | `Esc` |
| Delete Selected annotation | `QPushButton delete_annotation_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:80) | Contextual | Rail -> Annotate panel | `Delete` |
| Reset Document Annotations | `QPushButton reset_annotations_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:81) | Contextual | Rail -> Annotate panel | None |
| Rotate current / selected 90 CW | `QPushButton rotate_selected_cw` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:96) | Contextual | Rail -> Pages panel | None |
| Rotate current / selected 90 CCW | `QPushButton rotate_selected_ccw` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:97) | Contextual | Rail -> Pages panel | None |
| Rotate current / selected 180 | `QPushButton rotate_selected_180` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:98) | Contextual | Rail -> Pages panel | None |
| Rotate All 90 CW | `QPushButton rotate_all_cw` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:107) | Viewer or Editor contextual | Rail -> Pages panel | None |
| Rotate All 90 CCW | `QPushButton rotate_all_ccw` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:108) | Viewer or Editor contextual | Rail -> Pages panel | None |
| Rotate All 180 | `QPushButton rotate_all_180` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:109) | Viewer or Editor contextual | Rail -> Pages panel | None |
| Delete Selected pages | `QPushButton delete_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:240) | Contextual | Rail -> Organize panel (Editor only) | `Delete` |
| Extract Selected pages | `QPushButton extract_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:241) | Contextual | Rail -> Organize panel (Editor only) | None |
| Split by Range | `QPushButton split_button` in [right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:242) | Editor | Rail -> Organize panel (Editor only) | None |
| Editor mini-toolbar Undo | `QPushButton undo_button` in [edit_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/edit_mode_ui.py:166) | Editor | Top bar only after Phase 6; remove duplicate local chrome later | Standard Undo |
| Editor mini-toolbar Redo | `QPushButton redo_button` in [edit_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/edit_mode_ui.py:167) | Editor | Top bar only after Phase 6; remove duplicate local chrome later | Standard Redo |
| Editor page selection by click | `QListWidget grid` item selection in [edit_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/edit_mode_ui.py:265) | Editor | Editor canvas unchanged | None |
| Editor checkbox selection | `EditorPageItemDelegate.checkbox_clicked` in [edit_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/edit_mode_ui.py:29) | Editor | Editor canvas unchanged | None |
| Editor drag-and-drop reorder | `PageGridWidget` internal move in [edit_mode_ui.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/edit_mode_ui.py:187) | Editor | Editor canvas unchanged | None |
| Page jump input | `QLineEdit page_jump_input` in [status_bar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/status_bar.py:24) | Global | Status bar footer unchanged | None |
| Go page jump button | `QPushButton jump_button` in [status_bar.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/status_bar.py:27) | Global | Status bar footer unchanged | None |

## Actions Not Covered By The Locked Mapping

| Action | Reason not directly covered | Proposed destination |
| --- | --- | --- |
| Full Screen | Mapping asked for an audit-based decision between top bar icon-only and View menu | View menu |
| Exit | Not part of shell mapping | File menu |
| Keyboard Shortcuts help | Not part of shell mapping | Help menu |
| Viewer page navigation via arrow and page keys | Keyboard-only navigation, not a visible shell action | Keep keyboard-only in Viewer |
| Select All pages | Keyboard-only editor utility, not part of rail mapping | Keep keyboard-only in Editor |
| Editor local Undo / Redo duplicate buttons | Duplicates locked top-bar global Undo / Redo | Consolidate to top bar in Phase 6 cleanup |
| Text Box hidden annotation control | Hidden, not launch-facing, outside current visible Phase 6 mapping | Remain hidden / excluded |

## Acceptance Check

- Every current action surfaced from the toolbar, right pane, menus, and status bar is listed above.
- `focus_search()` currently targets the toolbar search field first, so search routing must move to the new right-rail Search panel in Phase 6B.2.
- Zoom In and Zoom Out are explicitly mapped to the right-rail bottom area.
- The locked decisions are reflected: thumbnails fixed left, rail on the right, page jump stays in the footer.
