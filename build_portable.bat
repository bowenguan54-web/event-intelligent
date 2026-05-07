@echo off
chcp 65001 >nul
echo ============================================
echo   智能会议助手 - 一键打包便携版
echo ============================================
echo.

set ROOT=%~dp0
set FRONTEND=%ROOT%frontend
set BACKEND=%ROOT%backend

:: ─── Step 1: 构建前端 ───
echo [1/3] 构建前端静态文件...
cd /d "%FRONTEND%"
if not exist node_modules (
    echo   安装前端依赖...
    call npm install
    if errorlevel 1 (
        echo ❌ npm install 失败
        pause
        exit /b 1
    )
)
call npm run build
if errorlevel 1 (
    echo ❌ 前端构建失败
    pause
    exit /b 1
)
echo ✅ 前端构建完成 → frontend\dist

:: ─── Step 2: 安装后端依赖 + pyinstaller ───
echo.
echo [2/3] 安装后端依赖...
cd /d "%BACKEND%"
pip install -r requirements.txt -q
pip install pyinstaller -q
if errorlevel 1 (
    echo ❌ pip install 失败
    pause
    exit /b 1
)
echo ✅ 后端依赖就绪

:: ─── Step 3: PyInstaller 打包 ───
echo.
echo [3/3] PyInstaller 打包中 (可能需要数分钟)...
cd /d "%BACKEND%"
pyinstaller portable.spec --noconfirm --clean
if errorlevel 1 (
    echo ❌ PyInstaller 打包失败
    pause
    exit /b 1
)

:: ─── 完成 ───
echo.
echo ============================================
echo ✅ 打包完成!
echo.
echo 输出目录: backend\dist\智能会议助手\
echo 启动方式: 双击 "智能会议助手.exe"
echo.
echo 如需部署到其他电脑，将整个
echo "智能会议助手" 文件夹复制过去即可。
echo ============================================
echo.
pause
