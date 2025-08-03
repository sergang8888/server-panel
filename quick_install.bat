@echo off
chcp 936 >nul
echo.
echo ==========================================
echo    Helmet Detection System - Quick Install
echo ==========================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found, please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python installed
echo.

:: Check pip availability
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip not available, trying to fix...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo pip fix failed, please install pip manually
        pause
        exit /b 1
    )
)

echo pip available
echo.

:: System configuration input
echo ==========================================
echo           System Configuration
echo ==========================================
echo.
echo Please enter system configuration (press Enter for default):
echo.

:: Input server port
set /p SERVER_PORT="Server port [default: 5000]: "
if "%SERVER_PORT%"=="" set SERVER_PORT=5000
echo Server port: %SERVER_PORT%
echo.

:: Input admin username
set /p ADMIN_USER="Admin username [default: admin]: "
if "%ADMIN_USER%"=="" set ADMIN_USER=admin
echo Admin username: %ADMIN_USER%
echo.

:: Input admin password
set /p ADMIN_PASS="Admin password [default: admin123]: "
if "%ADMIN_PASS%"=="" set ADMIN_PASS=admin123
echo Admin password: %ADMIN_PASS%
echo.

:: Set default camera configuration
set CAMERA_IP=192.168.1.100
set CAMERA_PORT=554
set CAMERA_USER=admin
set CAMERA_PASS=123456

echo ==========================================
echo           Configuration Confirmation
echo ==========================================
echo Server port: %SERVER_PORT%
echo Admin username: %ADMIN_USER%
echo Admin password: %ADMIN_PASS%
echo ==========================================
echo.

set /p CONFIRM="Confirm configuration? (y/n) [default: y]: "
if "%CONFIRM%"=="" set CONFIRM=y
if /i not "%CONFIRM%"=="y" (
    echo Installation cancelled
    pause
    exit /b 0
)

echo.
echo Starting installation...
echo.

:: Create virtual environment
echo Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Virtual environment creation failed
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)
echo.

:: Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Dependencies installation failed
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
) else (
    echo requirements.txt not found, skipping dependency installation
)
echo.

:: Create configuration file
echo Creating configuration file...
echo # Helmet Detection System - User Configuration > config_user.py
echo. >> config_user.py
echo # Server Configuration >> config_user.py
echo HOST = '0.0.0.0' >> config_user.py
echo PORT = %SERVER_PORT% >> config_user.py
echo DEBUG = False >> config_user.py
echo. >> config_user.py
echo # Admin Account Configuration >> config_user.py
echo ADMIN_USERNAME = '%ADMIN_USER%' >> config_user.py
echo ADMIN_PASSWORD = '%ADMIN_PASS%' >> config_user.py
echo. >> config_user.py
echo # Default Camera Configuration >> config_user.py
echo DEFAULT_CAMERA_IP = '%CAMERA_IP%' >> config_user.py
echo DEFAULT_CAMERA_PORT = %CAMERA_PORT% >> config_user.py
echo DEFAULT_CAMERA_USERNAME = '%CAMERA_USER%' >> config_user.py
echo DEFAULT_CAMERA_PASSWORD = '%CAMERA_PASS%' >> config_user.py
echo DEFAULT_STREAM_URL = '/stream' >> config_user.py
echo. >> config_user.py
echo # AI Model Configuration >> config_user.py
echo MODEL_PATH = 'models' >> config_user.py
echo CONFIDENCE_THRESHOLD = 0.5 >> config_user.py
echo NMS_THRESHOLD = 0.4 >> config_user.py
echo. >> config_user.py
echo # Logging Configuration >> config_user.py
echo LOG_LEVEL = 'INFO' >> config_user.py
echo LOG_FILE = 'logs/app.log' >> config_user.py
echo Configuration file created
echo.

:: Create startup script
echo Creating startup script...
echo @echo off > start_system.bat
echo chcp 936 ^>nul >> start_system.bat
echo title Helmet Detection System - Port:%SERVER_PORT% >> start_system.bat
echo cd /d "%%~dp0" >> start_system.bat
echo echo ==========================================>> start_system.bat
echo echo    Helmet Detection System >> start_system.bat
echo echo ==========================================>> start_system.bat
echo echo Starting system... >> start_system.bat
echo echo Server port: %SERVER_PORT% >> start_system.bat
echo echo Admin username: %ADMIN_USER% >> start_system.bat
echo echo Access URL: http://localhost:%SERVER_PORT% >> start_system.bat
echo echo ==========================================>> start_system.bat
echo echo. >> start_system.bat
echo call venv\Scripts\activate.bat >> start_system.bat
echo python app.py >> start_system.bat
echo echo. >> start_system.bat
echo echo System stopped >> start_system.bat
echo pause >> start_system.bat
echo Startup script created
echo.

:: Create desktop shortcut script
echo Creating desktop shortcut script...
echo @echo off > create_shortcut.bat
echo set SCRIPT="%%USERPROFILE%%\Desktop\Helmet Detection System.lnk" >> create_shortcut.bat
echo set TARGET="%cd%\start_system.bat" >> create_shortcut.bat
echo set PWS=powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile >> create_shortcut.bat
echo %%PWS%% -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%%SCRIPT%%'); $S.TargetPath = '%%TARGET%%'; $S.Save()" >> create_shortcut.bat
echo echo Desktop shortcut created >> create_shortcut.bat
echo echo You can find "Helmet Detection System" shortcut on desktop >> create_shortcut.bat
echo pause >> create_shortcut.bat
echo Shortcut script created
echo.

:: Create configuration modification script
echo Creating configuration modification script...
echo @echo off > modify_config.bat
echo chcp 936 ^>nul >> modify_config.bat
echo echo ==========================================>> modify_config.bat
echo echo       Modify System Configuration >> modify_config.bat
echo echo ==========================================>> modify_config.bat
echo echo Current configuration: >> modify_config.bat
echo echo Server port: %SERVER_PORT% >> modify_config.bat
echo echo Admin username: %ADMIN_USER% >> modify_config.bat
echo echo Camera IP: %CAMERA_IP% >> modify_config.bat
echo echo ==========================================>> modify_config.bat
echo echo To modify configuration, edit config_user.py file >> modify_config.bat
echo echo Restart system after modification >> modify_config.bat
echo pause >> modify_config.bat
echo Configuration modification script created
echo.

:: Check key files
echo Checking system files...
set missing_files=0
if not exist "app.py" (
    echo app.py missing
    set missing_files=1
)
if not exist "templates\index.html" (
    echo templates\index.html missing
    set missing_files=1
)
if not exist "static" (
    echo static directory missing
    set missing_files=1
)

if %missing_files%==1 (
    echo Some system files are missing, system may not work properly
) else (
    echo System files check completed
)
echo.

:: Create models directory
if not exist "models" (
    mkdir models
    echo Created models directory
)

:: Create logs directory
if not exist "logs" (
    mkdir logs
    echo Created logs directory
)

echo ==========================================
echo           Installation Complete!
echo ==========================================
echo.
echo System Information:
echo Server port: %SERVER_PORT%
echo Admin username: %ADMIN_USER%
echo Admin password: %ADMIN_PASS%
echo Access URL: http://localhost:%SERVER_PORT%
echo.
echo Usage Instructions:
echo 1. Double-click start_system.bat to start system
echo 2. Double-click create_shortcut.bat to create desktop shortcut
echo 3. Double-click modify_config.bat to view configuration
echo 4. Access http://localhost:%SERVER_PORT% in browser
echo.
echo Important Files:
echo - Startup script: start_system.bat
echo - User configuration: config_user.py
echo - Model files: models\
echo - Log files: logs\
echo.
echo System Functions:
echo - Camera management: Configure IP cameras
echo - AI configuration: Load detection models
echo - Network management: Configure network parameters
echo - System monitoring: View system status
echo.
echo Login Information:
echo Username: %ADMIN_USER%
echo Password: %ADMIN_PASS%
echo.
echo Press any key to start system...
pause >nul

:: Auto start system
echo Starting system...
start "Helmet Detection System" start_system.bat

echo.
echo System started in background
echo Please access: http://localhost:%SERVER_PORT%
echo Login with username %ADMIN_USER% and password %ADMIN_PASS%
echo.
echo To stop system, close the startup window
echo To modify configuration, run modify_config.bat
echo.
pause