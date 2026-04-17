# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.config import CONF
from PyInstaller.utils.hooks import collect_submodules

project_root = Path(CONF["specpath"]).resolve()
icon_path = project_root / "assets" / "myleaflet.icns"
ui_icons_dir = project_root / "pdf_app" / "ui" / "icons"

hiddenimports = collect_submodules("fitz") + collect_submodules("pypdf")


a = Analysis(
    ["pdf_app/app/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(ui_icons_dir), "pdf_app/ui/icons"),
    ],
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
    name="MyLeaflet",
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
    name="MyLeaflet",
)

app = BUNDLE(
    coll,
    name="MyLeaflet.app",
    icon=str(project_root / "assets" / "myleaflet.icns"),
    bundle_identifier="local.myleaflet",
)
