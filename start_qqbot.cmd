@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"
set "PYTHONPATH=%ROOT%src"

if not exist "%PY%" (
    call "%ROOT%setup.cmd"
    if errorlevel 1 exit /b %ERRORLEVEL%
)
if not exist "%PY%" (
    echo Python environment is missing. Run setup.cmd first.
    exit /b 1
)

"%PY%" -m sekai_toolkit.bot.server %*
exit /b %ERRORLEVEL%
