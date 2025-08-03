@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 测试Go安装脚本的基本功能
REM 这个脚本用于验证安装环境和依赖

echo ======================================
echo     Go Web Panel 安装环境测试
echo ======================================
echo.

REM 检查网络连接
echo [测试] 检查网络连接...
ping -n 1 golang.org >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] 网络连接正常
) else (
    echo [✗] 网络连接失败，请检查网络设置
)

REM 检查curl或PowerShell
echo [测试] 检查下载工具...
curl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] curl 可用
) else (
    powershell -Command "Get-Command Invoke-WebRequest" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [✓] PowerShell 可用
    ) else (
        echo [✗] 缺少下载工具
    )
)

REM 检查Git
echo [测试] 检查Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Git 已安装
) else (
    echo [✗] Git 未安装，请从 https://git-scm.com/download/win 下载
)

REM 检查Go
echo [测试] 检查Go环境...
go version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('go version') do set GO_VERSION=%%i
    echo [✓] Go 已安装: !GO_VERSION!
) else (
    echo [i] Go 未安装，安装脚本将自动安装
)

REM 检查磁盘空间
echo [测试] 检查磁盘空间...
for /f "tokens=3" %%i in ('dir /-c %USERPROFILE% ^| find "bytes free"') do set FREE_SPACE=%%i
if defined FREE_SPACE (
    echo [✓] 磁盘空间充足
) else (
    echo [i] 无法检测磁盘空间
)

REM 检查管理员权限
echo [测试] 检查管理员权限...
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] 具有管理员权限
) else (
    echo [!] 建议以管理员身份运行安装脚本
)

echo.
echo ======================================
echo 测试完成！如果所有项目都显示 [✓]，
echo 则可以正常运行安装脚本。
echo ======================================
echo.
echo 运行安装脚本:
echo   install_go.bat
echo.
echo 或一键在线安装:
echo   curl -L https://raw.githubusercontent.com/your-repo/webserver-panel/main/install_go.bat -o install_go.bat ^&^& install_go.bat
echo.
pause