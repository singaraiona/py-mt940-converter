#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Create the spec file
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