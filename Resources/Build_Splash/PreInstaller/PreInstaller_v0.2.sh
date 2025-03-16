#!/bin/bash

# Splash Pre-Installer Run Script 
# Author: Mohamed Aly Sayed (muhammmedaly@gmail.com) 
# Version: v0.2

# Define required system and Python packages
SYSTEM_PACKAGES=("python3" "python3-pip" "python3-setuptools" "python3-wheel" "gedit" "pipx" "gedit-plugins")
PYTHON_PACKAGES=("PySide6" "vtk" "scipy" "pillow" "meshio")  # Python packages to be installed
PIP3_PACKAGES=("openpyxl")
SCRIPT_NAME="PreInstaller_v0.2.py"

# Check if a system package is installed
is_package_installed() {
    dpkg -l | grep -qw "$1"
}

# Check for and resolve APT conflicts
resolve_apt_conflicts() {
    echo "Resolving APT source conflicts..."
    sudo rm -f /etc/apt/sources.list.d/kitware.list
    sudo rm -f /etc/apt/sources.list.d/archive_uri-https_apt_kitware_com_ubuntu_-noble.list
    sudo apt-get update
}

# Configure pip to allow breaking system packages
configure_pip() {
    echo "Configuring pip to allow breaking system packages..."
    python3 -m pip config set global.break-system-packages true
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to configure pip. Exiting."
        zenity --error --title="Configuration Failed" --text="Failed to configure pip. Please check your Python environment."
        exit 1
    fi
}

# Install system packages
install_system_packages() {
    for pkg in "${SYSTEM_PACKAGES[@]}"; do
        if ! is_package_installed "$pkg"; then
            echo "Installing $pkg..."
            sudo apt-get install -y "$pkg"
            if [[ $? -ne 0 ]]; then
                echo "Error: Failed to install $pkg. Exiting."
                zenity --error --title="Installation Failed" --text="Failed to install $pkg. Please check your system configuration."
                exit 1
            fi
        else
            echo "$pkg is already installed."
        fi
    done
}

# Install Python packages
install_python_package() {
    if ! python3 -c "import $1" &> /dev/null; then
        echo "Installing Python package: $1..."
        python3 -m pip install "$1"
        if [[ $? -ne 0 ]]; then
            echo "Error: Failed to install Python package $1. Exiting."
            zenity --error --title="Installation Failed" --text="Failed to install Python package $1. Please check your Python environment."
            exit 1
        fi
    else
        echo "Python package $1 is already installed."
    fi
}

# Install Pip3 packages
install_pip3_package() {
    echo "Installing Pip3 package: $1..."
    if pip3 install "$1"; then
        echo "Pip3 package $1 installed successfully."
    else
        echo "Error: Failed to install Pip3 package $1. Exiting."
        zenity --error --title="Installation Failed" --text="Failed to install Pip3 package $1. Please check your environment."
        exit 1
    fi
}

# Install pipx and ensure PATH updates
install_pipx() {
    if ! command -v pipx &> /dev/null; then
        echo "pipx is not installed. Attempting to install..."
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath

        # Source the shell configuration to apply the PATH change dynamically
        if [[ -f "$HOME/.bashrc" ]]; then
            source "$HOME/.bashrc"
        elif [[ -f "$HOME/.zshrc" ]]; then
            source "$HOME/.zshrc"
        fi

        # Verify pipx installation
        if ! command -v pipx &> /dev/null; then
            echo "Error: pipx installation failed. Exiting."
            zenity --error --title="Installation Failed" --text="pipx installation failed. Please check your Python environment and PATH settings."
            exit 1
        fi
    else
        echo "pipx is already installed."
    fi
}

# Launch the Python GUI script
launch_gui() {
    if [[ -f "$SCRIPT_NAME" ]]; then
        echo "Launching $SCRIPT_NAME..."
        python3 "$SCRIPT_NAME"
    else
        echo "Error: $SCRIPT_NAME not found. Please ensure it exists in the current directory."
        exit 1
    fi
}

# Main script execution
main() {
    # Resolve APT conflicts
    resolve_apt_conflicts

    # Configure pip
    configure_pip

    # Combine the list of packages into a single string
    ALL_PACKAGES=$(printf "%s\n" "${SYSTEM_PACKAGES[@]}" "${PYTHON_PACKAGES[@]}" "${PIP3_PACKAGES[@]}")

    # Show a Zenity confirmation dialog
    zenity --question \
        --title="Splash Installer" \
        --width=400 \
        --height=300 \
        --text="The following packages will be installed:\n\n<b>System Packages:</b>\n$(printf '%s\n' "${SYSTEM_PACKAGES[@]}")\n\n<b>Python Packages:</b>\n$(printf '%s\n' "${PYTHON_PACKAGES[@]}")\n\n<b>Pip3 Packages:</b>\n$(printf '%s\n' "${PIP3_PACKAGES[@]}")\n\nDo you want to proceed?"

    # Check if the user clicked "Yes" or "No"
    if [[ $? -ne 0 ]]; then
        echo "Installation canceled by the user."
        zenity --info --title="Installation Canceled" --text="The installation has been canceled. You can restart this script at any time to proceed."
        exit 0
    fi

    # Install system packages
    install_system_packages

    # Install pipx
    install_pipx

    # Install Python packages
    for pkg in "${PYTHON_PACKAGES[@]}"; do
        install_python_package "$pkg"
    done

    # Install Pip3 packages
    for pkg in "${PIP3_PACKAGES[@]}"; do
        install_pip3_package "$pkg"
    done

    # Launch the Python GUI
    launch_gui
}

# Execute the main function
main

