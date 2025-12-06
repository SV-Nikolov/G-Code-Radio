@echo off
REM Build script for G-Code Radio executable

echo.
echo ================================
echo G-Code Radio - Build Script
echo ================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building executable...
echo.

REM Run PyInstaller
pyinstaller G-Code-Radio.spec --distpath dist --buildpath build

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ================================
echo Build Complete!
echo ================================
echo.
echo Executable location: dist\G-Code-Radio.exe
echo.
echo Usage:
echo   G-Code-Radio.exe "https://www.youtube.com/watch?v=..."
echo   G-Code-Radio.exe "song.mp3" --output "output.gcode"
echo   G-Code-Radio.exe --help
echo.
pause
