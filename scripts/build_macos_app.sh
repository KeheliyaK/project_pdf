#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
SPEC_PATH="$ROOT_DIR/pdf_app_mvp.spec"

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
"$PYTHON_BIN" -m PyInstaller --noconfirm --clean "$SPEC_PATH"

echo
echo "Build complete."
echo "App bundle: $ROOT_DIR/dist/PDF App MVP.app"
