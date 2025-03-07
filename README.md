# MT940 to CSV Converter

A simple GUI application that converts MT940 bank statement files (.sta) to CSV format.

## Features

- User-friendly graphical interface
- Converts MT940 files to CSV format
- Preserves all transaction details including:
  - Date
  - Amount
  - Currency
  - Bank Reference
  - Description

## Requirements

- Python 3.6 or higher
- Required packages:
  - pandas
  - tkinter (usually comes with Python)
  - pyinstaller (for building the application)
  - pillow (for icon creation)

## Installation

### Running from Source

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python mt940_converter.py
   ```

### Building macOS Application Bundle

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the build script:
   ```bash
   ./build_mac.sh
   ```
3. The application bundle will be created in the `dist` folder as `MT940_Converter_Mac.zip`
4. Extract the zip file and move the application to your Applications folder
5. Double-click to run the application

## Usage

1. Launch the application
2. Click "Select .sta File" to choose your MT940 file
3. The application will automatically convert the file and save the CSV in the same folder
4. A success message will appear when the conversion is complete

## Output Format

The CSV file will contain the following columns:
- Date (YYYY-MM-DD format)
- Amount (with 2 decimal places)
- Currency
- Bank Reference
- Description (cleaned and formatted)

## Notes

- The application supports both debit (D) and credit (C) transactions
- Credit transactions are shown as negative amounts
- The output CSV will be created in the same folder as the input file
- The output filename will be the same as the input file but with a .csv extension

## Building from Source

The application can be built into a standalone bundle using PyInstaller. The build process includes:
1. Creating an application icon
2. Bundling all dependencies
3. Creating a macOS application bundle
4. Packaging the application into a zip file

The resulting application bundle will be a native macOS application that can be run without Python installed 