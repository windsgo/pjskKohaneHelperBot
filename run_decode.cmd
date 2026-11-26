@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"
set "PYTHONPATH=%ROOT%src"

set "INPUT=%~1"
if not defined INPUT set /p "INPUT=Capture file path: "
if not defined INPUT (
    echo Usage: run_decode.cmd FILE
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

"%PY%" -m sekai_toolkit.decoder.decode_sekai "%INPUT%" --out "%ROOT%runtime\decoded"
if errorlevel 1 exit /b %ERRORLEVEL%
"%PY%" "%ROOT%scripts\asset_tools\extract_resources.py"
exit /b %ERRORLEVEL%
