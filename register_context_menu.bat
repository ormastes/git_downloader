@echo off
cd /d "C:\Windows\System32\config\systemprofile" 2>nul
if errorlevel 1 (
    echo You must run this script as an Administrator!
    pause
    exit /b
)
echo Running with Administrator privileges...

setlocal
set "key=HKCU\Software\Classes\*\shell\GitDownloader"
reg add "%key%" /ve /d "Open GitDownloader" /f
reg add "%key%\command" /ve /d "\"C:\\Program Files\\git downloader\\python.exe GitDownloader.py\" \"%1\"" /f
endlocal
