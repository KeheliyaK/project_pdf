# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import os
from PyInstaller.utils.hooks import collect_submodules

project_root = Path(os.getcwd()).resolve()

#from pathlib import Path

#project_root = Path(__file__).resolve().parent

hiddenimports = collect_submodules("fitz") + collect_submodules("pypdf")


a = Analysis(
    ["pdf_app/app/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDF App MVP",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="PDF App MVP",
)

app = BUNDLE(
    coll,
    name="PDF App MVP.app",
    icon=None,
    bundle_identifier="local.pdf-app-mvp",
)
