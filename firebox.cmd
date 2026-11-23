@echo off
rem ============================================================================
rem FireBox Portable Windows Command Launcher
rem Ignite Your Code. Burn Through Tasks.
rem ============================================================================

setlocal
set "SCRIPT_DIR=%~dp0"
set "FIREBOX_ROOT=%SCRIPT_DIR%.."

rem Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3.10+ is required to launch FireBox.
    echo Please install Python from https://python.org or Microsoft Store.
    exit /b 1
)

set "PYTHONPATH=%FIREBOX_ROOT%;%PYTHONPATH%"
python -m firebox.cli %*
endlocal
