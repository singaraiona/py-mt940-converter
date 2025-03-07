#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Create the spec file
pyinstaller --name "MT940_Converter" \
            --windowed \
            --add-data "README.md:." \
            --icon "icon.png" \
            --clean \
            --noconfirm \
            mt940_converter.py

# Create a more user-friendly executable
cd dist
mv "MT940_Converter" "mt940_converter"

# Create a zip file
zip -r "MT940_Converter_Linux.zip" "mt940_converter"

echo "Build complete! The executable is in dist/MT940_Converter_Linux.zip" 