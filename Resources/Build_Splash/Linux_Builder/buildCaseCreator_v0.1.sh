#!/bin/bash

# Stop on errors and undefined variables
set -euo pipefail

# Define constants
MAIN_SCRIPT="SplashCaseCreator_gui.py"
OUTPUT_NAME="SplashCaseCreator_gui"
ADDITIONAL_FILES=(
    "./SplashCaseCreatorInputForm.ui:."
)
HIDDEN_IMPORTS=(
    "vtkmodules.vtkInteractionStyle"
    "vtkmodules.vtkRenderingOpenGL2"
    "vtkmodules.util.data_model"
    "vtkmodules.util.execution_model"
    "vtkmodules.qt.QVTKRenderWindowInteractor"
    "PySide6.QtUiTools"
    "PySide6.QtWidgets"
    "PySide6.QtGui"
    "PySide6.QtCore"
)

# Colors for output
RED="\033[0;31m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

# Fancy progress bar
show_progress() {
    local msg="$1"
    local duration=${2:-2}
    local width=50

    echo -ne "${CYAN}$msg [${NC}"
    for i in $(seq 1 $width); do
        echo -ne "="
        sleep $(bc <<<"scale=2; $duration / $width")
    done
    echo -e "${CYAN}]${NC} Done."
}

# Define cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up old build artifacts...${NC}"
    rm -rf build dist "$OUTPUT_NAME.spec" || true
}

# Ensure correct Python environment
ensure_python_env() {
    echo -e "${BLUE}Ensuring Python environment compatibility...${NC}"
    if ! command -v python3 &>/dev/null; then
        echo -e "${RED}Python 3 is not installed. Please install it and try again.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Python 3 is available.${NC}"
}

# Check and install missing dependencies
ensure_dependencies() {
    echo -e "${BLUE}Checking for required Python modules...${NC}"
    REQUIRED_MODULES=(
        "pyinstaller"
        "PySide6"
        "vtk"
    )
    for MODULE in "${REQUIRED_MODULES[@]}"; do
        if ! python3 -c "import $MODULE" &>/dev/null; then
            echo -e "${YELLOW}$MODULE is not installed. Installing it now...${NC}"
            pip install "$MODULE"
        fi
    done
    echo -e "${GREEN}All dependencies are satisfied.${NC}"
}

# Build the application
build_app() {
    echo -e "${BLUE}Building the application with PyInstaller...${NC}"

    # Prepare hidden-imports flags
    HIDDEN_IMPORTS_FLAGS=""
    for MODULE in "${HIDDEN_IMPORTS[@]}"; do
        HIDDEN_IMPORTS_FLAGS+=" --hidden-import=$MODULE"
    done

    # Prepare add-data flags
    ADD_DATA_FLAGS=""
    for FILE in "${ADDITIONAL_FILES[@]}"; do
        ADD_DATA_FLAGS+=" --add-data=$FILE"
    done

    # Run PyInstaller
    pyinstaller --noconfirm --onedir --windowed --name "$OUTPUT_NAME" \
        $HIDDEN_IMPORTS_FLAGS \
        $ADD_DATA_FLAGS \
        --exclude-module PyQt5 \
        --paths "./" \
        "$MAIN_SCRIPT"

    echo -e "${GREEN}Application build completed.${NC}"
}

# Debugging step: test vtk.qt.QVTKRenderWindowInteractor
test_vtk_qt() {
    echo -e "${CYAN}Testing VTK and vtk.qt compatibility...${NC}"
    python3 -c "
try:
    from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    print('vtk.qt.QVTKRenderWindowInteractor is available.')
except ImportError as e:
    print(f'Error: {e}')
    exit(1)
"
}

# Post-build validation
validate_build() {
    echo -e "${BLUE}Validating the build...${NC}"
    if [ -f "dist/$OUTPUT_NAME/$OUTPUT_NAME" ]; then
        echo -e "${GREEN}=================================================${NC}"
        echo -e "${GREEN} Build completed successfully!${NC}"
        echo -e "${GREEN} Executable is located in the 'dist/$OUTPUT_NAME/' directory.${NC}"
        echo -e "${GREEN}=================================================${NC}"
    else
        echo -e "${RED}=================================================${NC}"
        echo -e "${RED} Build failed. Please check the logs for details.${NC}"
        echo -e "${RED}=================================================${NC}"
        exit 1
    fi
}

# Main execution flow
echo -e "${CYAN}=================================================${NC}"
echo -e "${CYAN} Starting the build process for $OUTPUT_NAME${NC}"
echo -e "${CYAN}=================================================${NC}"

# Show progress for ensuring environment
show_progress "Setting up the Python environment..." 3

# Ensure Python environment
ensure_python_env

# Ensure all dependencies are installed
show_progress "Checking dependencies..." 2
ensure_dependencies

# Cleanup old artifacts
show_progress "Cleaning up old artifacts..." 1
cleanup

# Test vtk.qt compatibility
show_progress "Testing vtk.qt compatibility..." 1
test_vtk_qt

# Build the application
show_progress "Building the application..." 5
build_app

# Validate the build
show_progress "Validating the build..." 1
validate_build

# Final message
echo -e "${GREEN}All tasks completed successfully!${NC}"
