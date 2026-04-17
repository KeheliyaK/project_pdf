#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
SPEC_PATH="$ROOT_DIR/pdf_app_mvp.spec"
PYI_CONFIG_DIR="${PYI_CONFIG_DIR:-$ROOT_DIR/.pyinstaller}"
PYI_WORK_DIR="${PYI_WORK_DIR:-$ROOT_DIR/build/pyinstaller}"
PYI_DIST_DIR="${PYI_DIST_DIR:-$ROOT_DIR/dist}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python interpreter not found at: $PYTHON_BIN" >&2
  echo "Create the project venv first, or set PYTHON_BIN to a Python with the packaging dependencies installed." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c "import PyInstaller" >/dev/null 2>&1; then
  echo "PyInstaller is not installed for $PYTHON_BIN" >&2
  echo "Install packaging dependencies first:" >&2
  echo "  $PYTHON_BIN -m pip install -r $ROOT_DIR/requirements-packaging.txt" >&2
  exit 1
fi

cd "$ROOT_DIR"
mkdir -p "$PYI_CONFIG_DIR" "$PYI_WORK_DIR" "$PYI_DIST_DIR"
PYINSTALLER_CONFIG_DIR="$PYI_CONFIG_DIR" \
    "$PYTHON_BIN" -m PyInstaller --noconfirm --clean \
    --workpath "$PYI_WORK_DIR" \
    --distpath "$PYI_DIST_DIR" \
    "$SPEC_PATH"

echo
echo "Build complete."
echo "App bundle: $ROOT_DIR/dist/MyLeaflet.app"
echo "Smoke checklist: $ROOT_DIR/MINI_LAUNCH_SMOKE_CHECKLIST.md"
echo "Open for manual preview testing with:"
echo "  open \"$ROOT_DIR/dist/MyLeaflet.app\""
