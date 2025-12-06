@echo off
setlocal
REM Build script for G-Code Radio - Builds CLI and GUI executables

REM Ensure we run from the script directory
pushd "%~dp0"

echo.
echo ======================================================
echo G-Code Radio - Build Script
echo ======================================================
echo.

set LOGDIR=build\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller --quiet
)

REM Build CLI version
echo.
echo Building CLI version ^(G-Code-Radio.exe^)...
python -m PyInstaller G-Code-Radio.spec --distpath dist --workpath build --clean >"%LOGDIR%\cli.log" 2>&1
if errorlevel 1 (
    echo Failed to build CLI version. See %LOGDIR%\cli.log
    popd
    exit /b 1
)
if not exist "dist\G-Code-Radio.exe" (
    echo CLI build finished but executable missing. See %LOGDIR%\cli.log
    popd
    exit /b 1
)
echo ✓ CLI version built: dist\G-Code-Radio.exe

REM Build GUI version
echo.
echo Building GUI version ^(G-Code-Radio-GUI.exe^)...
python -m PyInstaller G-Code-Radio-GUI.spec --distpath dist --workpath build --clean >"%LOGDIR%\gui.log" 2>&1
if errorlevel 1 (
    echo Failed to build GUI version. See %LOGDIR%\gui.log
    popd
    exit /b 1
)
if not exist "dist\G-Code-Radio-GUI.exe" (
    echo GUI build finished but executable missing. See %LOGDIR%\gui.log
    popd
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
echo Logs:
echo   CLI build log: %LOGDIR%\cli.log
echo   GUI build log: %LOGDIR%\gui.log
echo.
echo Usage:
echo   CLI version: G-Code-Radio.exe --help
echo   GUI version: G-Code-Radio-GUI.exe
echo.
popd
endlocal
pause
