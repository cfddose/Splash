# SplashFOAM
A dynamic GUI-based program for OpenFOAM.

![SplashFOAM-Sep2024](https://github.com/user-attachments/assets/2917aa3c-d02e-40bd-ba4f-bc1f25f445de)

- [Overview](#overview)
- [Installation](#installation)
- [Features](#features)
  - [Geometry Import](#geometry-import)
  - [Meshing Tools](#meshing-tools)
  - [Simulation Setup](#simulation-setup)
  - [Configuration Management](#configuration-management)
  - [Post-Processing](#post-processing)
  - [Custom Scripting](#custom-scripting)
  - [Integrated Pre-Installation Script](#integrated-pre-installation-script)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Overview
SplashFOAM is an intuitive GUI pre-processor designed to simplify the use of OpenFOAM. It provides users with a streamlined interface to set up their CFD simulations.

## Installation
To get started with SplashFOAM, follow the steps below:

- Step 1: Clone the Repository
Clone the SplashFOAM repository to your local machine by running:

``` git clone https://github.com/mohamedalysayed/Splash-OpenFOAM.git ```

- Step 2: Switch to the Correct Branch
Ensure you are on the Standard-release branch to access the latest stable version:

``` cd SplashFOAM ```

``` git checkout Standard-release ```


- Step 3: Install Necessary Packages
Navigate to the SplashFOAM/Resources/Build_Splash/ directory and run the Ubuntu_MEL.sh script to install all the necessary dependencies:

``` cd SplashFOAM/Resources/Build_Splash/ ```

``` chmod +x Ubuntu_MEL.sh ```

``` ./Ubuntu_MEL.sh ```

This will ensure that all required packages are installed.

- Step 4: Launch SplashFOAM
After installing the necessary packages, navigate to the Sources directory and launch SplashFOAM using Python 3:

``` cd ../../Sources/ ```

``` python3 SplashFOAM.py ```

## Features

### Geometry Import
SplashFOAM allows users to import geometry files from various formats, including:
- **STL** (stereolithography)
- **OBJ** (Wavefront object)
- **STEP** (Standard for the Exchange of Product Data)

Users can preview and inspect their CAD models directly within the SplashFOAM interface using the **Splash Visualizer**. Additionally, users can choose to open their geometries in external programs like FreeCAD, Gmsh, Blender, and ParaView for further modifications or analysis.

### Meshing Tools
SplashFOAM offers a range of meshing capabilities:
- **Hex-Dominant Meshing**: Generate hex-dominant meshes from STL files using a simple and user-friendly interface.
- **Custom Meshing Parameters**: Users can specify minimum and maximum cell sizes to customize the mesh to their needs.
- **Convert Meshes to Fluent**: An integrated tool that converts OpenFOAM meshes to Fluent-compatible formats, with error handling and user notifications.
- **Mesh Removal**: Easily delete existing meshes and related files through a built-in cleanup tool.

### Simulation Setup
SplashFOAM simplifies the setup of OpenFOAM cases by providing:
- **Case Directory Management**: Seamlessly load, configure and organize case directories.
- **Simulation Configuration**: Adjust boundary conditions, solvers, and other simulation parameters through a graphical interface.
- **Initialization and Execution**: Directly initialize and run simulations from within the SplashFOAM environment.

### Configuration Management
Easily manage configuration files for different versions of OpenFOAM:
- **Automatic Detection of Installed OpenFOAM Versions**: SplashFOAM identifies available versions on your system and sets up the necessary environment variables.
- **Alias Setup**: Aliases for various OpenFOAM versions are added to `.bashrc` during installation, ensuring easy access to different versions.

### Post-Processing
SplashFOAM integrates with popular post-processing tools to streamline analysis:
- **ParaView Integration**: Launch ParaView directly from SplashFOAM to analyze simulation results.
- **2D Plotting with Xmgrace**: Quick access to plot simulation data using Xmgrace.
- **Custom Plotting Scripts**: Run your custom plotting scripts for detailed analysis.

### Custom Scripting
- **Integrated Scripting Environment**: Users can write and run Python scripts for custom workflows.
- **Tkinter and VTK Libraries**: Built-in support for Tkinter-based GUI components and VTK for advanced visualization tasks.

### Integrated Pre-Installation Script
SplashFOAM includes a pre-installation script to ensure your system is ready:
- **Automated Dependency Installation**: The script checks for required packages and installs them if missing, including OpenFOAM, FreeCAD, Gmsh, and more.
- **WSL Compatibility**: Special considerations for users running SplashFOAM on Windows Subsystem for Linux (WSL), including setting up display configurations.
## Documentation
The SplashFOAM manual is currently under development. In the meantime, please take a look at the repository for updates, or feel free to explore the code and get in touch with the [CFD Dose](https://cfddose.substack.com/) community for help.

## Contributing
Feel free to contribute to SplashFOAM by submitting issues, pull requests, or feature suggestions. Contributions are always welcome!
