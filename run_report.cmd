@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"
set "PYTHONPATH=%ROOT%src"

set "INPUT=%~1"
if not defined INPUT set /p "INPUT=Capture file path: "
if not defined INPUT (
    echo Usage: run_report.cmd FILE [report options]
    exit /b 2
)
set "INPUT=%INPUT:"=%"
if not exist "%INPUT%" (
    echo Input not found: %INPUT%
    exit /b 1
)

if not exist "%PY%" (
    call "%ROOT%setup.cmd"
    if errorlevel 1 exit /b %ERRORLEVEL%
)

"%PY%" -m sekai_toolkit.cli.report "%INPUT%" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%
