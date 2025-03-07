#!/bin/bash

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

# Install Python requirements
echo "Installing Python requirements..."
pip3 install -r requirements.txt

# Create the spec file
echo "Building application..."
pyinstaller --name "MT940 Converter" \
            --windowed \
            --add-data "README.md:." \
            --icon "icon.icns" \
            --clean \
            --noconfirm \
            mt940_converter.py

# Create a more user-friendly app bundle
cd dist
mv "MT940 Converter.app" "MT940_Converter.app"

# Create a zip file
zip -r "MT940_Converter_Mac.zip" "MT940_Converter.app"

echo "Build complete! The application bundle is in dist/MT940_Converter_Mac.zip" 