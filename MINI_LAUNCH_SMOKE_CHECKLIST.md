# Mini Launch Smoke Checklist

Use this checklist before sharing a new macOS preview `.app` build.

## Build and launch

- Build the app with `bash scripts/build_macos_app.sh`
- Launch the packaged app with `open "dist/PDF App MVP.app"`
- Confirm the app window opens without needing `python -m ...`

## Open flows

- Open a normal PDF from `File > Open PDF`
- Open a password-protected PDF and confirm the password prompt works
- Confirm canceling the password prompt returns cleanly without a broken document state
- Confirm Home recent files still open correctly after restart

## Viewer basics

- Confirm page thumbnails, page jump, zoom, and left/right page navigation still work
- Confirm search still finds results, navigates next/previous, and updates result feedback
- Confirm full screen still toggles correctly

## Editor basics

- Switch to `Editor` mode and confirm page cards load correctly
- Reorder pages and confirm Undo/Redo restores the expected page order
- Delete and rotate pages, then confirm Save As still exports the working copy

## Annotation mini-launch scope

- In `Viewer`, activate `Highlight` and drag to create a highlight
- Activate `Underline` and drag to create an underline
- Click an existing highlight or underline to select it
- Use `Delete Selected` and keyboard `Delete` to remove a selected annotation
- Use `Reset Document Annotations` and confirm the reset prompt appears
- Confirm top-level `Undo` / `Redo` reverses and reapplies highlight/underline add, delete, and reset actions

## Save As honesty

- Use `Save As` after structural edits and confirm output is written
- Use `Save As` after highlight/underline work and confirm the app still makes it clear annotations are not embedded into the exported PDF yet

## Launch-facing scope check

- Confirm only `Highlight` and `Underline` are visible as annotation tools
- Confirm unfinished text box functionality is not exposed in the visible mini-launch UI
- Confirm `Help > Keyboard Shortcuts` reflects the current visible shortcut set
