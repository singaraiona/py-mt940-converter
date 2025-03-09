#!/bin/bash

# Exit on error
set -e

# Check for system dependencies
echo "Checking system dependencies..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python3 and pip3
if ! command_exists python3; then
    echo "Python3 is not installed. Please install Python3 first."
    echo "You can install it using Homebrew: brew install python3"
    exit 1
fi

if ! command_exists pip3; then
    echo "pip3 is not installed. Please install pip3 first."
    echo "You can install it using Homebrew: brew install python3"
    exit 1
fi

# Check for tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "tkinter is not installed. Installing system dependencies..."
    
    # Check for Homebrew
    if ! command_exists brew; then
        echo "Homebrew is not installed. Please install Homebrew first:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install python-tk using Homebrew
    brew install python-tk
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
rm -f *.spec

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
echo "Installing Python requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade pyinstaller
python3 -m pip install --upgrade -r requirements.txt

# Check if icon file exists and create it if needed
if [ ! -f "icon.icns" ]; then
    echo "Warning: icon.icns not found. Creating default icon..."
    python3 create_icon.py
fi

# Create the spec file
echo "Building application..."
python3 -m PyInstaller \
    --name "MT940 Converter" \
    --windowed \
    --add-data "README.md:." \
    --add-data "requirements.txt:." \
    --add-data "f.mt940:." \
    --add-data "conv.py:." \
    --icon "icon.icns" \
    --clean \
    --noconfirm \
    --hidden-import tkinter \
    --hidden-import PIL \
    --hidden-import PIL._tkinter_finder \
    --hidden-import pandas \
    --collect-all pandas \
    --collect-all pillow \
    mt940_converter.py

# Create a more user-friendly app bundle
cd dist
mv "MT940 Converter.app" "MT940_Converter.app"

# Create a zip file
zip -r "MT940_Converter_Mac.zip" "MT940_Converter.app"

# Deactivate virtual environment
deactivate

echo "Build complete! The application bundle is in dist/MT940_Converter_Mac.zip"
echo "To use on another Mac:"
echo "1. Unzip MT940_Converter_Mac.zip"
echo "2. Right-click on MT940_Converter.app and select Open" 