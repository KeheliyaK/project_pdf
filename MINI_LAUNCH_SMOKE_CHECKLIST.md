# Mini Launch Smoke Checklist

Use this checklist before sharing a desktop build or treating the frozen MVP as ready for handoff/review.

## Launch and open

- Launch the app successfully
- Open a normal PDF
- Open a password-protected PDF and confirm the password prompt works
- Confirm recent files still open correctly

## Viewer smoke test

- Confirm thumbnails, page jump, zoom, and full screen still work
- Confirm search returns results and next/previous navigation works
- Confirm highlight and underline can still be created and selected
- Confirm annotation delete/reset still works

## Editor smoke test

- Switch to `Editor` mode and confirm page cards render correctly
- Reorder pages and confirm Undo/Redo still works
- Confirm rotate, extract, split, and delete still launch/work as expected from the current Editor controls

## Save/export honesty

- Run `Save As` after structural edits and confirm output is written
- Run `Save As` after annotation work and confirm the app still does not imply annotations were embedded if they were not

## Freeze check

- Confirm the documented MVP feature set in `README.md` still matches the app
- Confirm no unreviewed desktop feature additions slipped in during freeze work
- Confirm the next phase is still documented as web planning/implementation
