# Phase 6A Right Pane Audit

Audit target: [pdf_app/ui/right_tool_pane.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/right_tool_pane.py:1)

`RightToolPane` is a `QStackedWidget` host with three stack entries:

1. Placeholder label when no document is open
2. `ViewerToolPane`
3. `EditorToolPane`

`MainWindow.switch_mode()` swaps between these stack entries in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:382).

## Top-Level Stack

| Widget name and type | Mode | Visibility | Signal / connection | MainWindow method or service reached |
| --- | --- | --- | --- | --- |
| `stack` - `QStackedWidget` | Both | Always exists; stack page chosen by mode | Controlled by `show_placeholder()`, `show_viewer()`, `show_editor()` | `MainWindow.switch_mode()` |
| `placeholder` - `QLabel` | Neither active mode; no-document state | Visible only when no document is open | No emitted signal | None |
| `viewer_pane` - `ViewerToolPane` | Viewer | Visible only in Viewer mode with open document | Connected in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:270) | Mixed `MainWindow` methods and `SearchService` |
| `editor_pane` - `EditorToolPane` | Editor | Visible only in Editor mode with open document | Connected in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:279) | `MainWindow` editor operation methods |

## Search Section

| Widget name and type | Mode | Visibility | Signal / connection | MainWindow method or service reached |
| --- | --- | --- | --- | --- |
| `search_toggle` - `QToolButton` | Viewer | Always visible inside `ViewerToolPane` | `toggled -> _set_search_panel_visible` in `ViewerToolPane` | Local pane-only visibility toggle |
| `search_panel` - `QWidget` | Viewer | Conditional; shown when `search_toggle` is checked | Visibility managed by `_set_search_panel_visible()` | Local pane-only visibility toggle |
| `search_input` - `QLineEdit` | Viewer | Visible only when `search_panel` is visible | `returnPressed -> _emit_search -> search_requested` | `MainWindow.perform_search()` via signal connection in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:279), then `SearchService.search()` |
| `prev_button` - `QPushButton` | Viewer | Visible only when `search_panel` is visible; enabled only when multiple results exist | `clicked -> previous_requested` | `SearchService.previous_result()` via [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:271) |
| `next_button` - `QPushButton` | Viewer | Visible only when `search_panel` is visible; enabled only when multiple results exist | `clicked -> next_requested` | `SearchService.next_result()` via [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:272) |
| `result_label` - `QLabel` | Viewer | Visible only when `search_panel` is visible | Updated by `set_results()`, `set_active_result()`, `show_no_results()` | Reflects `SearchService` state via `MainWindow._activate_search_result()` and `MainWindow.perform_search()` |
| `search_hint_label` - `QLabel` | Viewer | Visible only when `search_panel` is visible | Updated by `set_results()`, `set_active_result()`, `show_no_results()` | Reflects `SearchService` state via `MainWindow` |
| `results_list` - `QListWidget` | Viewer | Visible only when `search_panel` is visible | `currentRowChanged -> result_activated` | `SearchService.activate_index()` via [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:273), then `MainWindow._activate_search_result()` |

## Annotations Section

| Widget name and type | Mode | Visibility | Signal / connection | MainWindow method or service reached |
| --- | --- | --- | --- | --- |
| `annotation_box` - `QFrame` | Viewer | Always visible in Viewer pane | Container only | None |
| `Annotations` title - `QLabel` | Viewer | Always visible | No signal | None |
| `annotation_status_label` - `QLabel` | Viewer | Always visible | Updated by `set_annotation_tool()` and `set_annotation_management_state()` | Reflects `MainWindow._update_annotation_ui()` state |
| `highlight_button` - `QPushButton` | Viewer | Always visible | `clicked -> _emit_annotation_tool(HIGHLIGHT, checked) -> annotation_tool_selected/cleared` | `MainWindow.set_active_annotation_tool()` or `MainWindow.clear_active_annotation_tool()` |
| `underline_button` - `QPushButton` | Viewer | Always visible | `clicked -> _emit_annotation_tool(UNDERLINE, checked) -> annotation_tool_selected/cleared` | `MainWindow.set_active_annotation_tool()` or `MainWindow.clear_active_annotation_tool()` |
| `text_box_button` - `QPushButton` | Viewer | Hidden by default with `setVisible(False)` | Would emit annotation tool selection if shown | Currently not reachable in visible MVP flow |
| `clear_tool_button` - `QPushButton` | Viewer | Always visible | `clicked -> _clear_annotation_tool -> annotation_tool_cleared` | `MainWindow.clear_active_annotation_tool()` |
| `delete_annotation_button` - `QPushButton` | Viewer | Always visible; enabled only when selected annotation count > 0 | `clicked -> annotation_delete_requested` | `MainWindow.delete_selected_annotations()` then `AnnotationService.delete_annotations()` |
| `reset_annotations_button` - `QPushButton` | Viewer | Always visible; enabled only when visible launch annotations exist | `clicked -> annotation_reset_requested` | `MainWindow.reset_document_annotations()` then `AnnotationService.clear_annotations_by_type()` |

## Current / Selected Pages Section

| Widget name and type | Mode | Visibility | Signal / connection | MainWindow method or service reached |
| --- | --- | --- | --- | --- |
| `selected_box` - `QFrame` | Viewer | Always visible in Viewer pane | Container only | None |
| `Current / Selected Pages` title - `QLabel` | Viewer | Always visible | No signal | None |
| `rotate_selected_cw` - `QPushButton` | Viewer | Always visible | `clicked -> rotate_selected_requested.emit(90)` | `MainWindow.rotate_current_or_selected_pages(90)` then `PdfOperationService.rotate_pages()` |
| `rotate_selected_ccw` - `QPushButton` | Viewer | Always visible | `clicked -> rotate_selected_requested.emit(-90)` | `MainWindow.rotate_current_or_selected_pages(-90)` then `PdfOperationService.rotate_pages()` |
| `rotate_selected_180` - `QPushButton` | Viewer | Always visible | `clicked -> rotate_selected_requested.emit(180)` | `MainWindow.rotate_current_or_selected_pages(180)` then `PdfOperationService.rotate_pages()` |

## Whole Document Section

| Widget name and type | Mode | Visibility | Signal / connection | MainWindow method or service reached |
| --- | --- | --- | --- | --- |
| `all_box` - `QFrame` | Viewer | Always visible in Viewer pane | Container only | None |
| `Whole Document` title - `QLabel` | Viewer | Always visible | No signal | None |
| `rotate_all_cw` - `QPushButton` | Viewer | Always visible | `clicked -> rotate_all_requested.emit(90)` | `MainWindow.rotate_all_pages(90)` then `PdfOperationService.rotate_all_pages()` |
| `rotate_all_ccw` - `QPushButton` | Viewer | Always visible | `clicked -> rotate_all_requested.emit(-90)` | `MainWindow.rotate_all_pages(-90)` then `PdfOperationService.rotate_all_pages()` |
| `rotate_all_180` - `QPushButton` | Viewer | Always visible | `clicked -> rotate_all_requested.emit(180)` | `MainWindow.rotate_all_pages(180)` then `PdfOperationService.rotate_all_pages()` |

## Editor Actions Section

| Widget name and type | Mode | Visibility | Signal / connection | MainWindow method or service reached |
| --- | --- | --- | --- | --- |
| `Edit Actions` title - `QLabel` | Editor | Always visible in Editor pane | No signal | None |
| `rotate_selected_cw` - `QPushButton` | Editor | Always visible | `clicked -> rotate_selected_requested.emit(90)` | `MainWindow.rotate_selected_pages_editor(90)` then `PdfOperationService.rotate_pages()` |
| `rotate_selected_ccw` - `QPushButton` | Editor | Always visible | `clicked -> rotate_selected_requested.emit(-90)` | `MainWindow.rotate_selected_pages_editor(-90)` then `PdfOperationService.rotate_pages()` |
| `rotate_selected_180` - `QPushButton` | Editor | Always visible | `clicked -> rotate_selected_requested.emit(180)` | `MainWindow.rotate_selected_pages_editor(180)` then `PdfOperationService.rotate_pages()` |
| `rotate_all_cw` - `QPushButton` | Editor | Always visible | `clicked -> rotate_all_requested.emit(90)` | `MainWindow.rotate_all_pages(90)` then `PdfOperationService.rotate_all_pages()` |
| `rotate_all_ccw` - `QPushButton` | Editor | Always visible | `clicked -> rotate_all_requested.emit(-90)` | `MainWindow.rotate_all_pages(-90)` then `PdfOperationService.rotate_all_pages()` |
| `rotate_all_180` - `QPushButton` | Editor | Always visible | `clicked -> rotate_all_requested.emit(180)` | `MainWindow.rotate_all_pages(180)` then `PdfOperationService.rotate_all_pages()` |
| `delete_button` - `QPushButton` | Editor | Always visible | `clicked -> delete_requested` | `MainWindow.delete_selected_pages()` then `PdfOperationService.delete_pages()` |
| `extract_button` - `QPushButton` | Editor | Always visible | `clicked -> extract_requested` | `MainWindow.extract_selected_pages()` then `PdfOperationService.extract_pages()` |
| `split_button` - `QPushButton` | Editor | Always visible | `clicked -> split_requested` | `MainWindow.split_by_range()` then `PdfOperationService.split_range()` |

## Current Search Routing Note

`focus_search()` lives in [main_window.py](/Users/keheliyak/Documents/New%20project/pdf_app/ui/main_window.py:869). Its current routing is:

1. Force `Viewer` mode
2. Expand the Viewer search pane with `right_pane.viewer_pane.set_search_collapsed(False)`
3. Focus the top toolbar field with `self.toolbar_widget.search_input.setFocus()`
4. Select all existing text in the top toolbar field

This is the routing that must be updated in Phase 6B.2, because the long-term destination for search entry is the right-rail Search panel, not the top toolbar field.

## Widgets Shown In Both Viewer And Editor Contexts

No single widget instance inside `RightToolPane` is rendered in both modes at the same time. The stack swaps entire pane subtrees.

However, these action groups appear in both mode contexts with different originating widgets and partially different behavior:

- `Rotate Selected 90 CW / 90 CCW / 180`
  - Viewer pane targets current page if no thumbnail selection exists.
  - Editor pane targets explicit editor selection only.
- `Rotate All 90 CW / 90 CCW / 180`
  - Appears in both Viewer and Editor panes.
  - Both route to the same `MainWindow.rotate_all_pages()` method.

These overlapping rotate actions need explicit handling during Phase 6B.2 when the new right-side rail panels are consolidated.
