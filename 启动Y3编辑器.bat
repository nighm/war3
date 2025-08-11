@echo off
chcp 65001 >nul
echo 🚀 正在启动Y3编辑器...
echo.

REM 检查Y3编辑器路径
set "Y3_PATH=D:\Program Files\y3\games\2.0\game\Editor.exe"

if exist "%Y3_PATH%" (
    echo ✅ 找到Y3编辑器: %Y3_PATH%
    echo.
    echo 📝 创建新地图步骤:
    echo 1. 在Y3编辑器中点击 '文件' -^> '新建项目'
    echo 2. 选择项目类型（建议选择 '空白项目'）
    echo 3. 设置项目名称和保存路径
    echo 4. 点击 '创建' 开始编辑
    echo.
    echo 正在启动...
    start "" "%Y3_PATH%"
) else (
    echo ❌ 未找到Y3编辑器: %Y3_PATH%
    echo 请检查安装路径是否正确
    pause
)
