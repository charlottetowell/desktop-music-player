@echo off
REM Build script for Windows
echo Building Desktop Music Player for Windows...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller
pyinstaller build.spec

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo.
echo Build complete! Executable located at:
echo dist\DesktopMusicPlayer\DesktopMusicPlayer.exe
echo.
