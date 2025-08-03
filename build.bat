@echo off
chcp 936 >nul
echo.
echo ==========================================
echo    Go Web Panel - 构建脚本
echo ==========================================
echo.

:: 检查Go是否安装
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo Go未安装，请先安装Go 1.21+
    echo 下载地址: https://golang.org/dl/
    pause
    exit /b 1
)

echo Go已安装
go version
echo.

:: 初始化Go模块（如果需要）
if not exist go.sum (
    echo 初始化Go模块依赖...
    go mod tidy
    if %errorlevel% neq 0 (
        echo 依赖安装失败
        pause
        exit /b 1
    )
    echo 依赖安装完成
    echo.
)

:: 构建应用
echo 开始构建Go Web Panel...
go build -o webserver-panel.exe .
if %errorlevel% neq 0 (
    echo 构建失败
    pause
    exit /b 1
)

echo 构建成功！
echo 可执行文件: webserver-panel.exe
echo.

:: 询问是否立即运行
set /p RUN_NOW="是否立即运行应用？(y/n): "
if /i "%RUN_NOW%"=="y" (
    echo.
    echo 启动Go Web Panel...
    echo 访问地址: http://localhost:5000
    echo 按 Ctrl+C 停止服务器
    echo.
    webserver-panel.exe
) else (
    echo.
    echo 构建完成！运行以下命令启动应用:
    echo webserver-panel.exe
    echo.
    pause
)