@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0"
set "KEEP_JOBS="
set "KEEP_OUTPUT="
set "INCLUDE_LOGS="
set "INCLUDE_RESEARCH="
set "DRY_RUN="
set "YES="

:parse
if "%~1"=="" goto ready
if /I "%~1"=="-KeepJobs" (set "KEEP_JOBS=1" & shift & goto parse)
if /I "%~1"=="-KeepOutput" (set "KEEP_OUTPUT=1" & shift & goto parse)
if /I "%~1"=="-IncludeLogs" (set "INCLUDE_LOGS=1" & shift & goto parse)
if /I "%~1"=="-IncludeResearch" (set "INCLUDE_RESEARCH=1" & shift & goto parse)
if /I "%~1"=="-DryRun" (set "DRY_RUN=1" & shift & goto parse)
if /I "%~1"=="-Yes" (set "YES=1" & shift & goto parse)
if /I "%~1"=="--yes" (set "YES=1" & shift & goto parse)
if /I "%~1"=="/?" goto usage
if /I "%~1"=="-?" goto usage
if /I "%~1"=="--help" goto usage
echo Unknown option: %~1
:usage
echo Usage: clean_cache.cmd [-KeepJobs] [-KeepOutput] [-IncludeLogs] [-IncludeResearch] [-DryRun] [-Yes]
exit /b 2

:ready
echo.
echo === MySekai cache cleanup ===
echo Project: %ROOT%
echo.

if exist "%ROOT%runtime\temp" echo   clear  runtime\temp
if exist "%ROOT%runtime\cache" echo   clear  runtime\cache
if exist "%ROOT%runtime\decoded" echo   clear  runtime\decoded
if not defined KEEP_JOBS if exist "%ROOT%runtime\jobs" echo   clear  runtime\jobs
if not defined KEEP_OUTPUT if exist "%ROOT%output" echo   clear  output
if defined INCLUDE_LOGS if exist "%ROOT%logs" echo   clear  logs
for /d %%D in ("%ROOT%runtime\mp-debug*") do if exist "%%D" echo   delete %%D
if defined INCLUDE_RESEARCH (
    for %%N in (OpenQQ LLOneBot milky NapCatQQ) do if exist "%ROOT%runtime\%%N" echo   delete runtime\%%N
)

echo.
echo Will not delete: runtime\state, assets, masterdata, samples, src.
echo.

if defined DRY_RUN (
    echo Dry-run: nothing was deleted.
    exit /b 0
)
if not defined YES (
    choice /C YN /N /M "Clean these caches? [Y/N] "
    if errorlevel 2 (
        echo Cancelled.
        exit /b 0
    )
)

call :clear_dir "%ROOT%runtime\temp" "runtime\temp"
call :clear_dir "%ROOT%runtime\cache" "runtime\cache"
call :clear_dir "%ROOT%runtime\decoded" "runtime\decoded"
if not defined KEEP_JOBS call :clear_dir "%ROOT%runtime\jobs" "runtime\jobs"
if not defined KEEP_OUTPUT call :clear_dir "%ROOT%output" "output"
if defined INCLUDE_LOGS call :clear_dir "%ROOT%logs" "logs"

for /d %%D in ("%ROOT%runtime\mp-debug*") do call :remove_dir "%%D" "%%~nxD"
if defined INCLUDE_RESEARCH (
    for %%N in (OpenQQ LLOneBot milky NapCatQQ) do call :remove_dir "%ROOT%runtime\%%N" "runtime\%%N"
)

if exist "%ROOT%src" for /d /r "%ROOT%src" %%D in (__pycache__) do call :remove_dir "%%D" "src\__pycache__"
if exist "%ROOT%tests" for /d /r "%ROOT%tests" %%D in (__pycache__) do call :remove_dir "%%D" "tests\__pycache__"
if exist "%ROOT%scripts" for /d /r "%ROOT%scripts" %%D in (__pycache__) do call :remove_dir "%%D" "scripts\__pycache__"
call :remove_dir "%ROOT%.pytest_cache" ".pytest_cache"

echo.
echo Cleanup complete.
exit /b 0

:clear_dir
if not exist "%~1" exit /b 0
rmdir /s /q "%~1" >nul 2>&1
if not exist "%~1" mkdir "%~1" >nul 2>&1
echo Cleared: %~2
exit /b 0

:remove_dir
if not exist "%~1" exit /b 0
rmdir /s /q "%~1" >nul 2>&1
echo Removed: %~2
exit /b 0
