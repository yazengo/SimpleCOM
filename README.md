# SimpleCom - Cross-platform Serial Debug Tool

A modern, cross-platform serial port debug tool built with Python 3 and PyQt6.

## Features

- **Auto Port Detection**: Automatically scans and lists available serial ports
- **Configurable Baudrate**: Supports common baudrates from 300 to 921600 (default: 115200)
- **Real-time Data Display**: View received data in a terminal-style display
- **Command History**: Track and reuse previously sent commands
- **Line Ending Options**: Support for None, CR, LF, and CR+LF line endings
- **Multi-threaded**: Non-blocking serial communication ensures responsive UI
- **Modern UI**: Clean, dark-themed interface with Catppuccin-inspired colors
- **Settings Persistence**: Remembers your preferences between sessions

## Requirements

- Python 3.9+
- PyQt6
- pyserial

## Installation

### Option 1: Using CMake (Recommended)

```bash
# Configure the project
cmake -B build

# Create virtual environment
cmake --build build --target venv

# Install dependencies
cmake --build build --target deps

# Run the application
cmake --build build --target run
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## Building Standalone Executable

### Build for Current Platform

To create a standalone executable for your current platform:

```bash
# Using CMake
cmake --build build --target build_exe

# Or manually with PyInstaller
pyinstaller --name SimpleCom --onefile --windowed src/main.py
```

The executable will be created in the `build/dist` directory.

### Build for Windows

PyInstaller does not support cross-compilation. To build a Windows executable:

**Option A: Build on Windows**

```powershell
cmake -B build
cmake --build build --target deps
cmake --build build --target build_exe
```

**Option B: Use GitHub Actions (Recommended)**

This project includes a GitHub Actions workflow that automatically builds
executables for both Windows and Linux:

1. Push your code to GitHub
2. Create a tag: `git tag v1.0.0 && git push --tags`
3. The workflow will build and create a release with both executables

Or manually trigger the workflow from GitHub Actions tab.

## Usage

1. **Connect to a Serial Port**:
   - Select a port from the dropdown list (click "Refresh" to update)
   - Choose the appropriate baudrate
   - Click "Connect" to establish connection

2. **Send Data**:
   - Type your command in the input field
   - Press Enter or click "Send" to transmit
   - Select the appropriate line ending option if needed

3. **View Received Data**:
   - Incoming data appears in the main text area in real-time
   - Click "Clear" to reset the display

4. **Use Command History**:
   - Previously sent commands are listed in the history panel
   - Double-click any item to populate the send input field

## Project Structure

```
simple-com/
├── .github/
│   └── workflows/
│       └── build.yml      # GitHub Actions CI/CD workflow
├── CMakeLists.txt         # CMake build configuration
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── src/
    ├── main.py            # Application entry point
    ├── main_window.py     # Main UI window
    └── serial_worker.py   # Serial communication thread
```

## License

MIT License

