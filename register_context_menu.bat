
setlocal
set original_dir=%cd%
cd /d "C:\Windows\System32\config\systemprofile" 2>nul
if errorlevel 1 (
    echo You must run this script as an Administrator!
    pause
    exit /b
)
cd /d %original_dir%

mkdir "C:\\Program Files\\git downloader"
copy GitDownloader.py "C:\\Program Files\\git downloader\\GitDownloader.py"


REM Define the minimum Python version
set MIN_PYTHON_MAJOR=3
set MIN_PYTHON_MINOR=11

REM Find the Python path
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i

REM Check if Python is found
if not defined PYTHON_PATH (
    echo Python not found!
    exit /b
)

REM Check Python version
for /f "tokens=2 delims= " %%v in ('"%PYTHON_PATH%" --version') do set PYTHON_VERSION=%%v
for /f "tokens=1,2 delims=." %%a in ('echo %PYTHON_VERSION%') do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

REM Check if Python version is greater than the minimum version
if %PYTHON_MAJOR% lss %MIN_PYTHON_MAJOR% (
    echo Python version is not greater than %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%!
    exit /b
)
if %PYTHON_MAJOR% equ %MIN_PYTHON_MAJOR% if %PYTHON_MINOR% lss %MIN_PYTHON_MINOR% (
    echo Python version is not greater than %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR%!
    exit /b
)
echo Found Python "%PYTHON_PATH%

REM Create a temporary VBScript file to replace single backslashes with double backslashes
echo Set regex = New RegExp > replace.vbs
echo regex.Pattern = "\\" >> replace.vbs
echo regex.Global = True >> replace.vbs
echo WScript.StdOut.Write regex.Replace(WScript.Arguments(0), "\\") >> replace.vbs

REM Use the VBScript file to replace single backslashes with double backslashes
for /f "delims=" %%j in ('cscript //nologo replace.vbs "%PYTHON_PATH%"') do set PYTHON_PATH=%%j

REM Delete the temporary VBScript file
del replace.vbs

REM Register the script in the context menu for all files
REM set "key=HKCU\Software\Classes\*\shell\GitDownloader"
REM reg add "%key%" /ve /d "Open GitDownloader" /f
REM reg add "%key%\command" /ve /d "\"%PYTHON_PATH%\" \"C:\\Program Files\\git downloader\\GitDownloader.py\" \"%1\"" /f

REM Register the script in the context menu for directories
REM set "key=HKCU\Software\Classes\Directory\shell\GitDownloader"
REM reg add "%key%" /ve /d "Open GitDownloader" /f
REM reg add "%key%\command" /ve /d "\"%PYTHON_PATH%\" \"C:\\Program Files\\git downloader\\GitDownloader.py\" \"%1\"" /f

REM Register the script in the context menu for directory background
set "key=HKCU\Software\Classes\Directory\Background\shell\GitDownloader"
reg add "%key%" /ve /d "Open GitDownloader" /f
reg add "%key%\command" /ve /d "\"%PYTHON_PATH%\" \"C:\\Program Files\\git downloader\\GitDownloader.py\" \"%V\"" /f

endlocal

