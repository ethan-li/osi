@echo off
REM Windows batch launcher for OSI
REM This script handles Python detection and launches OSI on Windows systems

setlocal enabledelayedexpansion

REM Get the directory containing this script
set "SCRIPT_DIR=%~dp0"
set "OSI_ROOT=%SCRIPT_DIR%.."

REM Try to find Python executable
set "PYTHON_EXE="

REM Check for python3 first
where python3 >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_EXE=python3"
    goto :found_python
)

REM Check for python
where python >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_EXE=python"
    goto :found_python
)

REM Check for py launcher
where py >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_EXE=py"
    goto :found_python
)

REM Python not found
echo Error: Python not found in PATH
echo Please install Python 3.11 or later and ensure it's in your PATH
echo You can download Python from: https://www.python.org/downloads/
exit /b 1

:found_python
REM Verify Python version
%PYTHON_EXE% -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if !errorlevel! neq 0 (
    echo Error: Python 3.11 or later is required
    %PYTHON_EXE% --version
    exit /b 1
)

REM Launch OSI
%PYTHON_EXE% "%SCRIPT_DIR%osi.py" %*
exit /b !errorlevel!
