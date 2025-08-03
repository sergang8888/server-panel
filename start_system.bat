@echo off 
chcp 936 >nul 
title Helmet Detection System - Port:5000 
cd /d "%~dp0" 
echo ==========================================
echo    Helmet Detection System 
echo ==========================================
echo Starting system... 
echo Server port: 5000 
echo Admin username: admin 
echo Access URL: http://localhost:5000 
echo ==========================================
echo. 
call venv\Scripts\activate.bat 
python app.py 
echo. 
echo System stopped 
pause 
