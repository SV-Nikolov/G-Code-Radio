@echo off
REM Build script for G-Code Radio - Builds all executable versions

echo.
echo ======================================================
echo G-Code Radio - Build Script
echo ======================================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller --quiet
)

REM Build CLI version
echo.
echo Building CLI version ^(G-Code-Radio.exe^)...
python -m PyInstaller G-Code-Radio.spec --distpath dist --workpath build --clean >nul 2>&1
if errorlevel 1 (
    echo Failed to build CLI version
    exit /b 1
)
echo ✓ CLI version built: dist\G-Code-Radio.exe

REM Build GUI version
echo.
echo Building GUI version ^(G-Code-Radio-GUI.exe^)...
python -m PyInstaller G-Code-Radio-GUI.spec --distpath dist --workpath build --clean >nul 2>&1
if errorlevel 1 (
    echo Failed to build GUI version
    exit /b 1
)
echo ✓ GUI version built: dist\G-Code-Radio-GUI.exe

REM Print summary
echo.
echo ======================================================
echo Build Complete!
echo ======================================================
echo.
echo Output files:
echo   CLI:  dist\G-Code-Radio.exe
echo   GUI:  dist\G-Code-Radio-GUI.exe
echo.
echo Usage:
echo   CLI version: G-Code-Radio.exe --help
echo   GUI version: G-Code-Radio-GUI.exe
echo.
pause
