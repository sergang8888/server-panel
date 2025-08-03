@echo off 
set SCRIPT="%USERPROFILE%\Desktop\Helmet Detection System.lnk" 
set TARGET="C:\Users\Administrator\Desktop\Webserver-panel\start_system.bat" 
set PWS=powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile 
%PWS% -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SCRIPT%'); $S.TargetPath = '%TARGET%'; $S.Save()" 
echo Desktop shortcut created 
echo You can find "Helmet Detection System" shortcut on desktop 
pause 
