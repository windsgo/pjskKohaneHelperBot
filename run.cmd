@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "MENU_MODE="
if "%~1"=="" set "MENU_MODE=1"

:dispatch
if defined MENU_MODE goto menu
if /I "%~1"=="setup" goto setup
if /I "%~1"=="start" goto start
if /I "%~1"=="report" goto report
if /I "%~1"=="decode" goto decode
if /I "%~1"=="clean" goto clean
if /I "%~1"=="help" goto help
echo Unknown command: %~1
echo Use: run.cmd setup^|start^|report^|decode^|clean
set "EXIT_CODE=2"
goto done

:menu
echo.
echo === MySekai Toolbox ===
echo   1. Setup environment
echo   2. Start QQBot
echo   3. Generate a report
echo   4. Decode a capture only
echo   5. Clean cache
echo   0. Exit
echo.
choice /C 123450 /N /M "Select [0-5]: "
if errorlevel 255 goto invalid
if errorlevel 6 goto done
if errorlevel 5 goto clean
if errorlevel 4 goto decode
if errorlevel 3 goto report
if errorlevel 2 goto start
if errorlevel 1 goto setup
goto menu

:invalid
echo Invalid choice.
pause
goto menu

:setup
call "%~dp0setup.cmd"
set "EXIT_CODE=%ERRORLEVEL%"
goto done

:start
call "%~dp0start_qqbot.cmd"
set "EXIT_CODE=%ERRORLEVEL%"
goto done

:report
set "INPUT=%~2"
if not defined INPUT set /p "INPUT=Capture file path: "
if not defined INPUT goto done
set "INPUT=%INPUT:"=%"
call "%~dp0run_report.cmd" "%INPUT%" %3 %4 %5 %6 %7 %8 %9
set "EXIT_CODE=%ERRORLEVEL%"
goto done

:decode
set "INPUT=%~2"
if not defined INPUT set /p "INPUT=Capture file path: "
if not defined INPUT goto done
set "INPUT=%INPUT:"=%"
call "%~dp0run_decode.cmd" "%INPUT%"
set "EXIT_CODE=%ERRORLEVEL%"
goto done

:clean
call "%~dp0clean_cache.cmd" %2 %3 %4 %5 %6 %7 %8 %9
set "EXIT_CODE=%ERRORLEVEL%"
goto done

:help
echo.
echo Usage:
echo   run.cmd              open the interactive menu
echo   run.cmd setup        create .venv and install dependencies
echo   run.cmd start        start the QQBot
echo   run.cmd report FILE  generate a report
echo   run.cmd decode FILE  decode only
echo   run.cmd clean        clean cache
echo.
set "EXIT_CODE=0"
goto done

:done
if defined MENU_MODE pause
endlocal & exit /b %EXIT_CODE%
