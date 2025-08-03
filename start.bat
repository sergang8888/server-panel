@echo off
chcp 65001 >nul
echo === Ubuntu Web管理面板启动脚本 (Windows版) ===
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 检测到Python版本:
python --version
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 错误: 激活虚拟环境失败
    pause
    exit /b 1
)

REM 安装依赖
echo 安装Python依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 安装依赖失败
    pause
    exit /b 1
)

REM 创建日志目录
if not exist "logs" mkdir logs

echo.
echo === 启动Web管理面板 ===
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.

REM 启动应用
python app.py

echo.
echo 应用已停止
pause