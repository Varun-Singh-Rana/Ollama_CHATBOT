--COMMAND TO INSTALL ALL REQUIRED MODULES FOR PYTHON TO RUN THIS CODE
pip install -r requirements.txt

spec file---
# -*- mode: python ; coding: utf-8 -*-
import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)


a = Analysis(
    ['ChatbotApp.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pydantic', 'pydantic.v1','pydantic.deprecated.decorator','kivymd.icon_definitions','comtypes', 'comtypes.gen'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ChatbotApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)