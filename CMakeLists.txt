cmake_minimum_required(VERSION 3.16)
project(SimpleCom VERSION 1.0.0 LANGUAGES NONE)

# Find Python
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Custom target for creating virtual environment
add_custom_target(venv
    COMMAND ${Python3_EXECUTABLE} -m venv ${CMAKE_BINARY_DIR}/venv
    COMMENT "Creating Python virtual environment..."
)

# Custom target for installing dependencies
if(WIN32)
    set(PIP_EXECUTABLE ${CMAKE_BINARY_DIR}/venv/Scripts/pip)
    set(PYTHON_VENV ${CMAKE_BINARY_DIR}/venv/Scripts/python)
    set(PYINSTALLER_EXECUTABLE ${CMAKE_BINARY_DIR}/venv/Scripts/pyinstaller)
else()
    set(PIP_EXECUTABLE ${CMAKE_BINARY_DIR}/venv/bin/pip)
    set(PYTHON_VENV ${CMAKE_BINARY_DIR}/venv/bin/python)
    set(PYINSTALLER_EXECUTABLE ${CMAKE_BINARY_DIR}/venv/bin/pyinstaller)
endif()

add_custom_target(deps
    COMMAND ${PIP_EXECUTABLE} install -r ${CMAKE_SOURCE_DIR}/requirements.txt
    DEPENDS venv
    COMMENT "Installing Python dependencies..."
)

# Custom target for running the application
add_custom_target(run
    COMMAND ${PYTHON_VENV} ${CMAKE_SOURCE_DIR}/src/main.py
    DEPENDS deps
    COMMENT "Running SimpleCom..."
)

# Custom target for building executable with PyInstaller
add_custom_target(build_exe
    COMMAND ${PYINSTALLER_EXECUTABLE}
        --name SimpleCom
        --onefile
        --windowed
        --clean
        --paths ${CMAKE_SOURCE_DIR}/src
        --hidden-import main_window
        --hidden-import serial_worker
        --distpath ${CMAKE_BINARY_DIR}/dist
        --workpath ${CMAKE_BINARY_DIR}/build_temp
        --specpath ${CMAKE_BINARY_DIR}
        --icon ${CMAKE_SOURCE_DIR}/assets/icon.ico
        --add-data "${CMAKE_SOURCE_DIR}/assets/icon.ico;assets"
        ${CMAKE_SOURCE_DIR}/src/main.py
    DEPENDS deps
    COMMENT "Building standalone executable..."
)

# Installation
install(DIRECTORY ${CMAKE_BINARY_DIR}/dist/
    DESTINATION bin
    USE_SOURCE_PERMISSIONS
)

message(STATUS "SimpleCom - Cross-platform Serial Debug Tool")
message(STATUS "Usage:")
message(STATUS "  cmake -B build")
message(STATUS "  cmake --build build --target venv    # Create virtual environment")
message(STATUS "  cmake --build build --target deps    # Install dependencies")
message(STATUS "  cmake --build build --target run     # Run application")
message(STATUS "  cmake --build build --target build_exe  # Build standalone executable")

