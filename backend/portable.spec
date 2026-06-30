# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = [
    "main",
    "app",
    "app.api",
    "app.api.ai",
    "app.api.archive",
    "app.api.auth",
    "app.api.meeting",
    "app.api.minutes",
    "app.api.room",
    "app.api.todo",
    "app.api.track",
    "app.api.transcript",
    "app.api.websocket",
    "app.core",
    "app.core.config",
    "app.core.database",
    "app.core.security",
    "app.models",
    "app.models.meeting",
    "app.models.room",
    "app.models.todo",
    "app.models.user",
    "app.schemas",
    "app.schemas.schemas",
    "app.services",
    "app.services.llm_service",
    "aiofiles",
    "dotenv",
    "httpx",
    "jose",
    "multipart",
    "passlib.handlers.argon2",
    "passlib.handlers.bcrypt",
    "passlib.handlers.des_crypt",
    "passlib.handlers.md5_crypt",
    "passlib.handlers.misc",
    "passlib.handlers.pbkdf2",
    "passlib.handlers.scram",
    "passlib.handlers.sha1_crypt",
    "passlib.handlers.sha2_crypt",
    "pydantic_settings",
    "sqlalchemy.dialects.sqlite",
    "uvicorn.lifespan",
    "uvicorn.lifespan.off",
    "uvicorn.lifespan.on",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "websockets",
]

hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("passlib.handlers")

a = Analysis(
    ["run_server.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("../frontend/dist", "frontend_dist"),
    ],
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
    name="event-intelligent-server",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="event-intelligent-server",
)
