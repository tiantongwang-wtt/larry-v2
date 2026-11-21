@echo off
setlocal EnableExtensions
set "demoPython="
for %%R in ("%LocalAppData%\Programs\Python" "%UserProfile%\AppData\Local\Programs\Python") do (
    for /d %%D in ("%%~R\Python3*") do if not defined demoPython if exist "%%~fD\python.exe" call :probe "%%~fD\python.exe"
)
for /f "delims=" %%P in ('where.exe python.exe 2^>nul') do if not defined demoPython call :probe "%%P"
if not defined demoPython (
    echo This example needs Python 3.10 or newer. You can also run demo.py with your Python interpreter.
    pause
    exit /b 1
)
"%demoPython%" -X utf8 -E -S -B "%~dp0demo.py" offline
if errorlevel 1 goto failed
echo.
"%demoPython%" -X utf8 -E -S -B "%~dp0demo.py" history
if errorlevel 1 goto failed
pause
exit /b 0

:probe
if /i "%~dp1"=="%LocalAppData%\Microsoft\WindowsApps\" exit /b 0
"%~1" -E -S -B -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if not errorlevel 1 set "demoPython=%~1"
exit /b 0

:failed
echo The example stopped before completing.
pause
exit /b 1
