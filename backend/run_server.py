"""
智能会议助手 - 便携式启动入口
PyInstaller 打包后，双击 exe 即可一键启动前后端。
"""
import sys
import os
import webbrowser
import threading

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# ── PyInstaller 冻结后的路径修正 ──
if getattr(sys, 'frozen', False):
    # 打包后: exe 所在目录
    BASE_DIR = os.path.dirname(sys.executable)
    # PyInstaller 解压临时目录 (_MEIPASS)
    BUNDLE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

# 将工作目录切到 exe 旁边，让 SQLite DB、uploads 落在同级
os.chdir(BASE_DIR)

# Portable mode should not inherit a non-boolean DEBUG value from the host.
os.environ["DEBUG"] = "false"
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# 确保 uploads 目录存在
os.makedirs("uploads", exist_ok=True)

# ── 前端静态文件目录 ──
FRONTEND_DIST = os.path.join(BUNDLE_DIR, "frontend_dist")

# ── 导入 FastAPI 应用 ──
from main import app                       # noqa: E402
from app.core.config import settings        # noqa: E402
from fastapi.staticfiles import StaticFiles # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

# ── 便携模式：移除 main.py 中的 JSON 根路由，改由前端接管 ──
app.routes[:] = [r for r in app.routes if not (hasattr(r, 'path') and r.path == '/' and hasattr(r, 'methods') and 'GET' in r.methods)]

# 挂载前端静态资源 (js/css/images 等)
if os.path.isdir(FRONTEND_DIST):
    # 所有 /assets/* 请求走静态文件
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    # images 目录（如果存在）
    images_dir = os.path.join(FRONTEND_DIST, "images")
    if os.path.isdir(images_dir):
        app.mount("/images", StaticFiles(directory=images_dir), name="frontend-images")

    # favicon.ico
    favicon_path = os.path.join(FRONTEND_DIST, "favicon.ico")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)

    # 所有非 /api、/ws、/docs、/uploads 的 GET 请求 → index.html（SPA fallback）
    index_html = os.path.join(FRONTEND_DIST, "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        # 先看是否是静态文件
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(index_html)

    print(f"✅ 前端静态文件已挂载: {FRONTEND_DIST}")
else:
    print(f"⚠️ 未找到前端构建目录: {FRONTEND_DIST}，仅启动 API 服务")


def open_browser():
    """延迟 1.5 秒后自动打开浏览器"""
    import time
    time.sleep(1.5)
    url = f"http://127.0.0.1:{settings.PORT}"
    print(f"🌐 正在打开浏览器: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    import uvicorn

    port = settings.PORT

    print("=" * 56)
    print(f"   智能会议助手 v{settings.APP_VERSION}  便携版")
    print(f"   地址: http://127.0.0.1:{port}")
    print(f"   按 Ctrl+C 停止服务")
    print("=" * 56)

    # 自动打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        app,           # 直接传 app 对象，不用字符串
        host="127.0.0.1",
        port=port,
        log_level="info",
    )
