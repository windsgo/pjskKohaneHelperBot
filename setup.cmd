@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"
set "PY=%VENV%\Scripts\python.exe"

if exist "%PY%" (
    "%PY%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 goto install
)

set "PY_CMD="
call :probe py -3.12
if not defined PY_CMD call :probe py -3.13
if not defined PY_CMD call :probe py -3.11
if not defined PY_CMD call :probe py -3.10
if not defined PY_CMD call :probe py -3
if not defined PY_CMD call :probe python

if not defined PY_CMD (
    echo Python 3.10+ was not found.
    echo Install Python 3.12 and enable "Add Python to PATH" or the py launcher.
    exit /b 1
)

echo Creating .venv with %PY_CMD% ...
%PY_CMD% -m venv --clear "%VENV%"
if errorlevel 1 (
    echo Failed to create .venv.
    echo Install Python 3.12, then delete .venv and retry.
    exit /b 1
)
if not exist "%PY%" (
    echo .venv was created but python.exe is missing.
    exit /b 1
)

:install
echo Installing locked dependencies ...
"%PY%" -m pip install -r "%ROOT%requirements.lock.txt"
if errorlevel 1 (
    echo Dependency installation failed.
    exit /b 1
)

set "PYTHONPATH=%ROOT%src"
"%PY%" -c "import sys, sekai_toolkit, PIL, aiohttp, cryptography, msgpack; print(sys.executable)"
if errorlevel 1 exit /b 1

echo.
echo Setup complete.
echo   run.cmd start         start the QQ bot
echo   run.cmd report FILE   generate a report
echo   run.cmd decode FILE   decode only
echo   run.cmd clean         clean cache
exit /b 0

:probe
%* -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 exit /b 1
set "PY_CMD=%*"
exit /b 0
