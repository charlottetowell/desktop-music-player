#!/bin/bash
# Build script for Linux

echo "Building Desktop Music Player for Linux..."

# Clean previous builds
rm -rf build dist

# Run PyInstaller
pyinstaller build.spec

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo ""
echo "Build complete! Executable located at:"
echo "dist/DesktopMusicPlayer/DesktopMusicPlayer"
echo ""
