#!/bin/bash

# Author: Mohamed Aly Sayed (muhammmedaly@gmail.com) 
# Version: v0.2
# Script to install the required CFD-related packages on Arch Linux

echo "_________________________________________________________________________________"
echo "                                                                                 "
echo "__________________ Splash Pre-Installation Script ____  07.11.2024 | MS  ____"
echo "                      Minimum Equipment List (MEL)                               "
echo "_________________________________________________________________________________"
echo "                                                                                 "
echo ".%%...%%..%%%%%%..%%...............%%%%....%%%%...%%%%%...%%%%%%..%%%%%...%%%%%%."
echo ".%%%.%%%..%%......%%..............%%......%%..%%..%%..%%....%%....%%..%%....%%..."
echo ".%%.%.%%..%%%%....%%...............%%%%...%%......%%%%%.....%%....%%%%%.....%%..."
echo ".%%...%%..%%......%%..................%%..%%..%%..%%..%%....%%....%%........%%..."
echo ".%%...%%..%%%%%%..%%%%%%...........%%%%....%%%%...%%..%%..%%%%%%..%%........%%..."
echo "................................................................................."
echo "_________________________________________________________________________________"

# Install curl if not already installed
echo "Checking if curl is installed..."
if ! [ -x "$(command -v curl)" ]; then
  echo "curl is not installed. Installing..."
  sudo pacman -Syu --noconfirm curl
else
  echo "curl is already installed."
fi

# Install Git if not already installed
echo "Checking if Git is installed..."
if ! [ -x "$(command -v git)" ]; then
  echo "Git is not installed. Installing..."
  sudo pacman -Syu --noconfirm git
else
  echo "Git is already installed."
fi

# Install OpenFOAM from AUR
echo "Installing OpenFOAM from AUR..."
yay -S openfoam-org

# Install other required packages
echo "Installing FreeCAD..."
sudo pacman -Syu --noconfirm freecad
echo "Installing vim..."
sudo pacman -Syu --noconfirm vim
echo "Installing gmsh..."
sudo pacman -Syu --noconfirm gmsh
echo "Installing grace..."
sudo pacman -Syu --noconfirm grace
echo "Installing ShellCheck..."
sudo pacman -Syu --noconfirm shellcheck
echo "Installing cloc..."
sudo pacman -Syu --noconfirm cloc
echo "Installing python tkinter libraries..."
sudo pacman -Syu --noconfirm tk
echo "Installing pip..."
sudo pacman -Syu --noconfirm python-pip
echo "Installing or upgrading VTK via pip..."
pip3 install vtk --upgrade
echo "Installing or upgrading pyinstaller, Pillow, and matplotlib via pip3..."
pip3 install Pillow==9.5.0 matplotlib pyinstaller --upgrade

# Install custom tkinter using pip3
echo "Installing custom tkinter using pip3..."
pip3 install customtkinter --upgrade

# Install GNOME for GTK-based applications
echo "Installing GNOME..."
sudo pacman -Syu --noconfirm gnome

# Install X11 apps for GUI support
echo "Installing X11 apps for GUI testing (xeyes)..."
sudo pacman -Syu --noconfirm xorg-xeyes

# Install matplotlib, numpy, numpy-stl, meshio, and gmsh via pip
echo "Installing Python dependencies (matplotlib, numpy, numpy-stl, meshio, gmsh)..."
pip3 install matplotlib numpy numpy-stl meshio gmsh

# Configure DISPLAY variable for WSL or native Linux
echo "Configuring DISPLAY variable..."
if grep -q Microsoft /proc/version; then
    # WSL-specific configuration
    echo "Detected WSL environment."
    export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
    echo "export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0" >> "$HOME/.bashrc"
else
    # Native Linux
    export DISPLAY=localhost:0
    echo "export DISPLAY=localhost:0" >> "$HOME/.bashrc"
fi

# Function to add an alias if it doesn't already exist in .bashrc
add_alias_to_bashrc() {
    local alias_command="$1"
    if ! grep -Fxq "$alias_command" "$HOME/.bashrc"; then
        echo "$alias_command" >> "$HOME/.bashrc"
        echo "Added alias: $alias_command"
    else
        echo "Alias already exists: $alias_command"
    fi
}

# Add aliases for OpenFOAM versions in .bashrc
echo "Adding aliases for OpenFOAM versions in .bashrc..."
add_alias_to_bashrc "alias of8='source /opt/OpenFOAM-8/etc/bashrc'"
add_alias_to_bashrc "alias of9='source /opt/OpenFOAM-9/etc/bashrc'"
add_alias_to_bashrc "alias of10='source /opt/OpenFOAM-10/etc/bashrc'"
add_alias_to_bashrc "alias of11='source /opt/OpenFOAM-11/etc/bashrc'"
add_alias_to_bashrc "alias of12='source /opt/OpenFOAM-12/etc/bashrc'"

# Reload .bashrc to apply changes
source "$HOME/.bashrc" 2>/dev/null || . "$HOME/.bashrc"

echo "______________________________________________________________________________________________"
echo " 												                                                "
echo "	  	      ..%%%%...%%%%%%..%%%%%...........%%%%%....%%%%....%%%%...%%%%%%.                  "
echo "		      .%%..%%..%%......%%..%%..........%%..%%..%%..%%..%%......%%.....                  "
echo "		      .%%......%%%%....%%..%%..........%%..%%..%%..%%...%%%%...%%%%...                  "
echo "		      .%%..%%..%%......%%..%%..........%%..%%..%%..%%......%%..%%.....                  "
echo "		      ..%%%%...%%......%%%%%...........%%%%%....%%%%....%%%%...%%%%%%.                  "
echo "		      ................................................................                  "
echo "______________________________________________________________________________________________"
echo "     _____                                                                                    "
echo "    (, /  |   /) /)               /)                     /)                 /)                "
echo "      /---|  // //    __   _   _ (/_  _   _    _  _     (/   _  _ _   _    (/_  _   _ __      "
echo "   ) /    |_(/_(/_    /_)_(_(_(__/(__(_(_(_/__(/_/_)_   / )_(_(_(/___(/_  /_) _(/__(/_/ (_    "
echo "  (_/              .-/                  .-/                                                   "
echo "                  (_/                  (_/                                                    "
echo "                                                                                     /        "
echo "    ,                 /) /)      /)                              /)     /) /)       /         "
echo "     __   _  _/_ _   // //  _  _(/    _       _  _   _  _   _   //     // //       /          "
echo "  _(_/ (_/_)_(__(_(_(/_(/__(/_(_(_   /_)_(_(_(__(___(/_/_)_/_)_/(_(_(_(/_(/_ (_/_ o           "
echo "                                                              /)            .-/               "
echo "                                                             (/            (_/                "
echo "______________________________________________________________________________________________"
