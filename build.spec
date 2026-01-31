# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Desktop Music Player
Builds a standalone executable with all dependencies bundled
"""

import sys
from pathlib import Path

block_cipher = None

# Collect all assets (icons, fonts)
datas = [
    ('assets/icons', 'assets/icons'),
    ('assets/fonts', 'assets/fonts'),
]

# Hidden imports for dynamic modules
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'miniaudio',
    'numpy',
    'librosa',
    'soundfile',
    'mutagen',
]

# Platform-specific imports
if sys.platform == 'win32':
    hiddenimports.append('winsdk')
elif sys.platform == 'linux':
    hiddenimports.append('dbus')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DesktopMusicPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico' if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DesktopMusicPlayer',
)
