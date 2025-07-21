@echo off
REM Windows build script for OSI PyInstaller executable
REM This script builds OSI into a standalone .exe file for Windows

echo Building OSI for Windows...
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "osi_main.py" (
    echo Error: osi_main.py not found. Please run this script from the OSI project root.
    pause
    exit /b 1
)

REM Install PyInstaller if not available
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller>=5.0.0
)

REM Run the build
python build_scripts/build_pyinstaller.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable should be in the dist/ directory
pause
