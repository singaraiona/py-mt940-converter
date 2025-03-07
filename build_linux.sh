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
    exit 1
fi

if ! command_exists pip3; then
    echo "pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Check for tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "tkinter is not installed. Installing system dependencies..."
    
    # Detect package manager and install tkinter
    if command_exists apt-get; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y python3-tk
    elif command_exists dnf; then
        # Fedora
        sudo dnf install -y python3-tkinter
    elif command_exists pacman; then
        # Arch Linux
        sudo pacman -S --noconfirm tk
    elif command_exists zypper; then
        # openSUSE
        sudo zypper install -y python3-tk
    else
        echo "Could not detect package manager. Please install python3-tk manually."
        echo "For Debian/Ubuntu: sudo apt-get install python3-tk"
        echo "For Fedora: sudo dnf install python3-tkinter"
        echo "For Arch Linux: sudo pacman -S tk"
        echo "For openSUSE: sudo zypper install python3-tk"
        exit 1
    fi
fi

# Install Python requirements
echo "Installing Python requirements..."
pip3 install -r requirements.txt

# Create the spec file
echo "Building application..."
pyinstaller --name "MT940_Converter" \
            --windowed \
            --add-data "README.md:." \
            --clean \
            --noconfirm \
            mt940_converter.py

# Create a more user-friendly executable
cd dist
rm -rf mt940_converter
mkdir -p mt940_converter
cp -r MT940_Converter/* mt940_converter/
cp MT940_Converter mt940_converter/mt940_converter

# Create a zip file
zip -r "MT940_Converter_Linux.zip" "mt940_converter"

echo "Build complete! The executable is in dist/MT940_Converter_Linux.zip" 