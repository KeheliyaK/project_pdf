from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
STORAGE_DIR = Path(os.getenv("PDF_WEB_STORAGE_DIR", ROOT_DIR / "api" / ".tmp" / "documents"))
MAX_UPLOAD_BYTES = int(os.getenv("PDF_WEB_MAX_UPLOAD_BYTES", str(20 * 1024 * 1024)))
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("PDF_WEB_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
