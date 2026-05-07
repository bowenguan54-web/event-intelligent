# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for 智能会议助手 便携版
在 backend/ 目录下执行:  pyinstaller portable.spec
"""
import os, sys

block_cipher = None
ROOT = os.path.abspath('.')

a = Analysis(
    ['run_server.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # 前端构建产物 → 打包后位于 _MEIPASS/frontend_dist/
        ('../frontend/dist', 'frontend_dist'),
        # uploads 目录结构（空目录占位，实际运行时在 exe 旁创建）
    ],
    hiddenimports=[
        # FastAPI / Starlette / Uvicorn 的隐式依赖
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        # 后端自有模块
        'app',
        'app.api',
        'app.api.auth',
        'app.api.meeting',
        'app.api.transcript',
        'app.api.minutes',
        'app.api.todo',
        'app.api.track',
        'app.api.archive',
        'app.api.websocket',
        'app.api.ai',
        'app.api.room',
        'app.core',
        'app.core.config',
        'app.core.database',
        'app.core.security',
        'app.models',
        'app.models.user',
        'app.models.meeting',
        'app.models.todo',
        'app.models.room',
        'app.schemas',
        'app.schemas.schemas',
        'app.services',
        'app.services.llm_service',
        'main',
        # 常见遗漏
        'passlib.handlers.bcrypt',
        'passlib.handlers.pbkdf2',
        'passlib.handlers.des_crypt',
        'passlib.handlers.sha2_crypt',
        'passlib.handlers.sha1_crypt',
        'passlib.handlers.md5_crypt',
        'passlib.handlers.misc',
        'passlib.handlers.argon2',
        'passlib.handlers.scram',
        'jose',
        'multipart',
        'aiofiles',
        'websockets',
        'httpx',
        'dotenv',
        'pydantic_settings',
        'sqlalchemy.dialects.sqlite',
        'engineio.async_drivers.threading',
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
    [],
    exclude_binaries=True,
    name='智能会议助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,          # True → 显示控制台窗口，方便查看日志
    icon=None,             # 可替换为 .ico 图标路径
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='智能会议助手',
)
