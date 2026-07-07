# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

project_root = Path(SPECPATH).parent
datas = [
    (
        str(project_root / "src" / "resources" / "builtin_dictionary.sqlite3"),
        "src/resources",
    )
]

a = Analysis(
    [str(project_root / "src" / "app.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "ruff", "tests", "tools"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="自动选词记录单词本",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=str(project_root / "assets" / "word_notebook_icon.ico"),
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
