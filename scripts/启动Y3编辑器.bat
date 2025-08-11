@echo off
chcp 65001 >nul
echo 🚀 正在启动Y3编辑器...
echo.

REM 设置Y3编辑器路径
set Y3_PATH=D:\Program Files\y3

REM 检查路径是否存在
if not exist "%Y3_PATH%" (
    echo ❌ Y3编辑器路径不存在: %Y3_PATH%
    echo 请检查安装路径是否正确
    pause
    exit /b 1
)

echo ✅ 找到Y3编辑器目录: %Y3_PATH%
echo.

REM 尝试启动Y3编辑器
cd /d "%Y3_PATH%"

REM 尝试不同的可执行文件
if exist "y3.exe" (
    echo 🚀 启动 y3.exe...
    start "" "y3.exe"
    goto :success
)

if exist "Y3.exe" (
    echo 🚀 启动 Y3.exe...
    start "" "Y3.exe"
    goto :success
)

if exist "y3_editor.exe" (
    echo 🚀 启动 y3_editor.exe...
    start "" "y3_editor.exe"
    goto :success
)

if exist "Y3Editor.exe" (
    echo 🚀 启动 Y3Editor.exe...
    start "" "Y3Editor.exe"
    goto :success
)

REM 尝试在子目录中查找
if exist "bin\y3.exe" (
    echo 🚀 启动 bin\y3.exe...
    start "" "bin\y3.exe"
    goto :success
)

if exist "app\y3.exe" (
    echo 🚀 启动 app\y3.exe...
    start "" "app\y3.exe"
    goto :success
)

if exist "editor\y3.exe" (
    echo 🚀 启动 editor\y3.exe...
    start "" "editor\y3.exe"
    goto :success
)

if exist "games\2.0\game\y3.exe" (
    echo 🚀 启动 games\2.0\game\y3.exe...
    start "" "games\2.0\game\y3.exe"
    goto :success
)

echo ❌ 未找到Y3编辑器可执行文件
echo 请检查以下路径:
echo   - %Y3_PATH%\y3.exe
echo   - %Y3_PATH%\Y3.exe
echo   - %Y3_PATH%\bin\y3.exe
echo   - %Y3_PATH%\app\y3.exe
echo   - %Y3_PATH%\editor\y3.exe
echo   - %Y3_PATH%\games\2.0\game\y3.exe
pause
exit /b 1

:success
echo.
echo ✅ Y3编辑器启动成功！
echo.
echo 📋 接下来请:
echo 1. 等待Y3编辑器完全加载
echo 2. 点击"新建项目"按钮
echo 3. 选择"空白模板"或"基础模板"
echo 4. 输入项目名称和保存路径
echo 5. 点击"创建"开始你的地图制作之旅！
echo.
echo 💡 建议保存到项目的 maps/ 目录下
echo.
pause
