# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'librosa',
        'librosa.core',
        'librosa.feature',
        'librosa.feature.spectral',
        'librosa.util',
        'librosa.display',
        'librosa.filters',
        'numpy',
        'numpy.core',
        'numpy.fft',
        'scipy',
        'scipy.signal',
        'scipy.fftpack',
        'scipy.interpolate',
        'pydub',
        'soundfile',
        'yt_dlp',
        'colorlog',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'audioread',
        'numba',
        'sklearn',
        'scikit-learn',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='G-Code-Radio-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
