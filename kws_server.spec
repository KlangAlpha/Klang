# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['server/kws_server.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'eventlet.hubs.epolls', 'eventlet.hubs.kqueue', 'eventlet.hubs.selects', 'dns', 'dns.asyncbackend', 'dns.asyncquery',
    'dns.dnssec','dns.e164','dns.hash','dns.namedict','dns.tsigkeyring','dns.update','dns.version','dns.zone','dns.asyncresolver',
    'dns.versioned','engineio', 'socketio', 'threading', 'time', 'queue','engineio.async_drivers.eventlet',
    'talib','talib.stream','ply.yacc'
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='kws_server',
    console=True,
    runtime_tmpdir=None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
