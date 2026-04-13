# Known Issues

## Non-blocking limitations

- Exact in-page search highlighting is not implemented
  - Search jumps to the correct page/result and keeps result state aligned, but the exact text match is not visually marked on the page.

- Annotation export/write-back is not implemented
  - Highlight and underline are visible in the current desktop session, but `Save As` does not embed them into the exported PDF yet.

- Annotation tooling is intentionally lightweight
  - The current desktop MVP includes highlight and underline only, with limited editing/management depth by design.

- Packaging is still preview-level
  - The macOS packaging path is suitable for local/manual preview builds, but codesigning, notarization, and installer-level polish are still future work.

- Release readiness still depends on manual smoke checks
  - The repo includes a practical smoke checklist, but there is not yet a full automated desktop release validation pipeline.

## Deferred after the freeze

- Web-version planning and implementation
- Annotation expansion beyond the current MVP subset
- In-page search polish/highlighting
- Production release/distribution polish

## Recently resolved before freeze

- Search result navigation/state synchronization
- Search auto-reactivation after annotation completion
- Editor right-rail action cleanup
- Viewer annotation workflow stabilization
- Editor selection and operation targeting stabilization

## Maintenance note

Keep this file concise and honest. It should list real current limitations of the frozen desktop baseline, not speculative future work.
