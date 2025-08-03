@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Go Web Panel - 一键安装脚本 (无Python依赖)
REM 支持 Windows 系统

REM 配置变量
set GO_VERSION=1.21.0
set PROJECT_NAME=webserver-panel
REM 请将下面的仓库地址替换为实际的GitHub仓库地址
set GITHUB_REPO=your-username/webserver-panel
set INSTALL_DIR=%USERPROFILE%\webserver-panel
set GO_INSTALL_DIR=%USERPROFILE%\go

REM 颜色定义 (Windows 10+)
for /f %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

echo ======================================
echo     Go Web Panel 一键安装脚本
echo ======================================
echo.

REM 检测系统架构
echo %BLUE%[INFO]%NC% 检测系统架构...
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set ARCH=amd64
) else if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    set ARCH=386
) else (
    echo %RED%[ERROR]%NC% 不支持的架构: %PROCESSOR_ARCHITECTURE%
    pause
    exit /b 1
)

echo %BLUE%[INFO]%NC% 检测到系统: windows-%ARCH%

REM 检查Go是否已安装
echo %BLUE%[INFO]%NC% 检查Go环境...
go version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('go version') do set GO_VERSION_INSTALLED=%%i
    echo %BLUE%[INFO]%NC% 检测到Go版本: !GO_VERSION_INSTALLED!
    goto :download_source
) else (
    echo %YELLOW%[WARNING]%NC% 未检测到Go环境
)

REM 询问是否安装Go
set /p INSTALL_GO="是否安装Go环境? (y/N): "
if /i "!INSTALL_GO!"=="y" (
    goto :install_go
) else (
    echo %RED%[ERROR]%NC% 需要Go环境才能继续安装
    pause
    exit /b 1
)

:install_go
echo %BLUE%[INFO]%NC% 开始安装Go %GO_VERSION%...

REM 创建临时目录
set TEMP_DIR=%TEMP%\go_install_%RANDOM%
mkdir "%TEMP_DIR%"
cd /d "%TEMP_DIR%"

REM 下载Go
set GO_ZIP=go%GO_VERSION%.windows-%ARCH%.zip
set GO_URL=https://golang.org/dl/%GO_ZIP%

echo %BLUE%[INFO]%NC% 下载Go安装包...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GO_URL%' -OutFile '%GO_ZIP%'}"
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% 下载失败
    pause
    exit /b 1
)

REM 解压并安装
echo %BLUE%[INFO]%NC% 安装Go到 %GO_INSTALL_DIR%...
if exist "%GO_INSTALL_DIR%" rmdir /s /q "%GO_INSTALL_DIR%"
mkdir "%GO_INSTALL_DIR%"
powershell -Command "Expand-Archive -Path '%GO_ZIP%' -DestinationPath '%GO_INSTALL_DIR%' -Force"

REM 移动文件到正确位置
move "%GO_INSTALL_DIR%\go\*" "%GO_INSTALL_DIR%\"
rmdir "%GO_INSTALL_DIR%\go"

REM 设置环境变量
echo %BLUE%[INFO]%NC% 设置环境变量...
setx PATH "%GO_INSTALL_DIR%\bin;%PATH%" >nul
setx GOPATH "%USERPROFILE%\go-workspace" >nul
setx GOROOT "%GO_INSTALL_DIR%" >nul

REM 更新当前会话的环境变量
set PATH=%GO_INSTALL_DIR%\bin;%PATH%
set GOPATH=%USERPROFILE%\go-workspace
set GOROOT=%GO_INSTALL_DIR%

REM 清理临时文件
cd /d %USERPROFILE%
rmdir /s /q "%TEMP_DIR%"

echo %GREEN%[SUCCESS]%NC% Go安装完成!

:download_source
REM 检查git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% 需要git来下载源码
    echo %BLUE%[INFO]%NC% 请从 https://git-scm.com/download/win 下载并安装git
    pause
    exit /b 1
)

echo %BLUE%[INFO]%NC% 下载项目源码...

if exist "%INSTALL_DIR%" (
    echo %YELLOW%[WARNING]%NC% 目录已存在，正在更新...
    cd /d "%INSTALL_DIR%"
    if exist ".git" (
        git pull
    ) else (
        cd /d "%USERPROFILE%"
        rmdir /s /q "%INSTALL_DIR%"
        git clone https://github.com/%GITHUB_REPO%.git "%INSTALL_DIR%"
    )
) else (
    git clone https://github.com/%GITHUB_REPO%.git "%INSTALL_DIR%"
)

cd /d "%INSTALL_DIR%"
echo %GREEN%[SUCCESS]%NC% 源码下载完成!

REM 构建应用
echo %BLUE%[INFO]%NC% 构建Go应用...

REM 下载依赖
go mod tidy
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% 依赖下载失败
    pause
    exit /b 1
)

REM 构建应用
go build -o %PROJECT_NAME%.exe .
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% 构建失败
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% 应用构建完成!

REM 创建配置文件
echo %BLUE%[INFO]%NC% 创建配置文件...

if not exist "config.json" (
    (
        echo {
        echo     "port": 5000,
        echo     "camera_ip": "192.168.1.100",
        echo     "camera_username": "admin",
        echo     "camera_password": "admin123",
        echo     "log_level": "info",
        echo     "max_log_size": 10,
        echo     "max_log_files": 5
        echo }
    ) > config.json
    echo %GREEN%[SUCCESS]%NC% 配置文件创建完成!
) else (
    echo %BLUE%[INFO]%NC% 配置文件已存在，跳过创建
)

REM 创建启动脚本
echo %BLUE%[INFO]%NC% 创建启动脚本...

(
    echo @echo off
    echo chcp 65001 ^>nul
    echo.
    echo echo 启动 Go Web Panel...
    echo echo 访问地址: http://localhost:5000
    echo echo 按 Ctrl+C 停止服务
    echo echo.
    echo.
    echo cd /d "%%~dp0"
    echo %PROJECT_NAME%.exe
    echo.
    echo pause
) > start.bat

REM 创建桌面快捷方式
echo %BLUE%[INFO]%NC% 创建桌面快捷方式...

set SHORTCUT_SCRIPT=%TEMP%\create_shortcut_%RANDOM%.vbs
(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = "%USERPROFILE%\Desktop\Go Web Panel.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "%INSTALL_DIR%\start.bat"
    echo oLink.WorkingDirectory = "%INSTALL_DIR%"
    echo oLink.Description = "Go Web Panel 管理面板"
    echo oLink.Save
) > "%SHORTCUT_SCRIPT%"

cscript //nologo "%SHORTCUT_SCRIPT%"
del "%SHORTCUT_SCRIPT%"

echo %GREEN%[SUCCESS]%NC% 启动脚本创建完成!

echo.
echo %GREEN%[SUCCESS]%NC% 安装完成!
echo.
echo 使用方法:
echo   启动服务: 双击桌面 "Go Web Panel" 快捷方式
echo   或运行: %INSTALL_DIR%\start.bat
echo   或直接运行: %INSTALL_DIR%\%PROJECT_NAME%.exe
echo   访问地址: http://localhost:5000
echo.

REM 询问是否立即启动
set /p START_NOW="是否立即启动服务? (y/N): "
if /i "!START_NOW!"=="y" (
    echo %BLUE%[INFO]%NC% 启动服务...
    start "Go Web Panel" cmd /k "%INSTALL_DIR%\start.bat"
    echo %GREEN%[SUCCESS]%NC% 服务已在新窗口中启动!
    echo 访问地址: http://localhost:5000
)

echo.
echo 按任意键退出...
pause >nul