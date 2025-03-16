# SplashFOAM
A modular GUI for streamlined CFD workflows across all OpenFOAM versions.

![SplashFOAM-Sep2024](https://github.com/user-attachments/assets/2917aa3c-d02e-40bd-ba4f-bc1f25f445de)

## TOC
- [Overview](#overview)
- [Installation](#installation)
- [Features](#features)
  - [Geometry Import](#geometry-import)
  - [Meshing Tools](#meshing-tools)
  - [Simulation Setup](#simulation-setup)
  - [Run Simulation](#run-simulation)
  - [Post-Processing](#post-processing)
- [Documentation](#documentation)
- [Code Developers](#code-developers)
- [Feedback](#feedback)
- [CFD Dose Album](#cfd-dose-album)

## Overview
SplashFOAM is a modular GUI for the Computational Fluid Dynamics (CFD) code OpenFOAM. The main impetus behind building SplashFOAM has been to increase the efficiency of CFD production, remove unnecessary friction, and allow engineers to focus on the physics of the problem rather than coding syntax. 

Unlike other tools, SplashFOAM is **not confined to a specific OpenFOAM release**. It handles all OpenFOAM versions, whether ESI or Foundation versions, making it both forward and backward-compatible. This flexibility ensures that users can switch between different OpenFOAM versions without any hassle, maintaining a streamlined workflow across different projects. SplashFOAM aims to be a dynamic, intuitive, and efficient pre-processor, streamlining the setup and execution of OpenFOAM simulations.

## Installation

To get started with SplashFOAM, follow the steps below:

### Pre-Installation Script

SplashFOAM includes a pre-installation script to ensure your system is ready:
- **Automated Dependency Installation**: The script checks for required packages and installs them if missing, including OpenFOAM, FreeCAD, Gmsh, and more.
- **WSL Compatibility**: Special considerations for users running SplashFOAM on Windows Subsystem for Linux (WSL), including setting up display configurations.

Whether you are running Ubuntu natively, through VirtualBox, or WSL, you must execute the `Ubuntu_MEL.sh` script before launching SplashFOAM.

Currently, SplashFOAM is supported on **Ubuntu** (recommended to run on **22.04.5 LTS**).

### Step-by-Step Instructions

- **Step 1: Clone the Repository**  

  Clone the SplashFOAM repository to your local machine by running:

  ```bash
  git clone https://github.com/mohamedalysayed/Splash-OpenFOAM.git 

- **Step 2: Switch to the Correct Branch**

   From the cloned code, navigate to the SplashFOAM/Resources/Build_Splash/ directory. 

  ```bash
  cd SplashFOAM/Resources/Build_Splash/


- **Step 3: Install Necessary Packages**


  Run the run_PreInstaller.sh script to install all the necessary dependencies:

  ```bash
  chmod +x run_PreInstaller.sh
  ./run_PreInstaller.sh

- Ensure you have Zenity installed. If not, execute the command below:

  ```bash
  sudo apt-get install -y zenity
![Screenshot from 2024-12-28 01-11-48](https://github.com/user-attachments/assets/b1c41934-9338-412b-b4b7-a0419ff9be51)


This will ensure that all required packages are installed. If needed, the user can install other secondary packages from the suggested list. 

- **Step 4: Launch SplashFOAM**

  After installing the necessary packages, navigate to the Sources directory and launch SplashFOAM using Python 3:

  ```bash
  cd ../../Sources/
  python3 SplashFOAM.py

### Configuration Management
Easily manage configuration files for different versions of OpenFOAM:

- **Automatic Detection of Installed OpenFOAM Versions**: SplashFOAM identifies available versions on your system and sets up the necessary environment variables.
- **Alias Setup**: Aliases for various OpenFOAM versions are added to the _bashrc_ during installation (according to the user's choice), ensuring easy access to different versions.


## Features
### Geometry Import
SplashFOAM allows users to import geometry files from various formats, including:

- **STL** (stereolithography)
- **OBJ** (Wavefront object)
- **STEP** (Standard for the exchange of product data - analytical format)
  
Import Geometry enables the user to view their CAD in one of five options:

- **Splash Viewer**: A local program built into SplashFOAM for quick and efficient CAD visualization.
- **FreeCAD**: Open your geometries directly in FreeCAD for further design modifications.
- **Gmsh**: Utilize Gmsh for meshing or geometry inspection.
- **Blender**: Seamlessly load your CAD files into Blender.
- **ParaView**: Use ParaView to visualize and inspect complex CAD models.

![CAD-Viewers](https://github.com/user-attachments/assets/884eecd2-6f6e-4787-9851-b6c07bafc655)

## Meshing Tools
SplashFOAM offers a range of meshing capabilities:

### Mesh Types
Currently, SplashFOAM supports three types of meshes:

- **Cartesian**: Generate structured hex-dominant meshes.
- **Polyhedral**: Create meshes with polyhedral elements that benefit complex geometries.
- **Tetrahedral**: Flexible tetrahedral meshing for various applications.

When creating a mesh from scratch, these meshes are generated using [_cfMesh_](https://cfmesh.com/). Additionally, SplashFOAM handles cases with SnappyHexMesh scripts, making it versatile in handling different meshing setups.

### Refinement Regions 
Splash Mesher offers the option to add refinement objects to the domain. As shown below, by defining the type of refinement object and the number of objects you can add the corresponding block to the background meshing script then you’ll be asked to provide the relevant info for the chosen type. Once done and mesh is created, Splash will automatically remove the refinement object assignment to avoid accumulating unwanted blocks in the underlying meshDict (or any equivalent) script. 

- **Step 1: From Mesh Controls, click on Add Refinement Objects**

![Screenshot from 2024-11-13 03-23-41](https://github.com/user-attachments/assets/0a904b93-223c-4bf5-ab14-30ee2899e596)

- **Step 2: Choose the refinement objects type and number of repetitions (if any)**

![Screenshot from 2024-11-15 09-11-41](https://github.com/user-attachments/assets/18413058-35e4-43b6-99cc-c914f30071f9)

- **Step 3: Populate the parameters relevant to that object and click add**

![Screenshot from 2024-11-13 03-24-59](https://github.com/user-attachments/assets/93a342f6-9623-4955-9ec9-6d61ee10fe14)

- **Step 4: Create the mesh and review the changes in Paraview**

![Screenshot from 2024-11-13 03-27-19](https://github.com/user-attachments/assets/4ff61616-0f20-47f7-ac4a-2fcf01214ead)


## Simulation Setup

SplashFOAM simplifies the setup of OpenFOAM cases by providing:

- **Case Directory Management**: Seamlessly load, configure, and organize case directories.
- **Mesh Refinement Levels**: Users can specify refinement levels for different regions to improve mesh quality and resolution.
- **Physical Properties**: Easily define physical properties for the simulation, with the option to select from pre-saved fluid property profiles for common fluids.
- **Turbulence Models**: Choose from a wide range of turbulence models tailored to specific flow regimes.
- **Numerical Schemes**: Define numerical schemes for discretization and solution accuracy directly in the GUI.
- **Boundary Conditions**: Seamlessly configure boundary conditions through a guided interface.
- **Simulation Controls**:
  - Start and end time of the simulation.
  - Time-stepping configurations.
  - Solution reports to monitor progress and convergence.
  - Function objects for calculating derived quantities and other post-processing tasks.
- **Initialization and Execution**: Directly initialize and run simulations from within the SplashFOAM environment. These set the simulation to its initial state and set up the necessary parameters to launch the case.
Note: SplashFOAM does not allow direct changes in boundary condition (BC) files. 

## Run Simulation
SplashFOAM can launch a simulation locally or on a remote HPC cluster (Cloud HPC):

- **Local Execution**: Run your simulations directly on your local machine.
- **Remote Execution**: Configure SplashFOAM to submit jobs to a remote HPC environment for more computational power. More information on setting up remote HPC access [can be found here](https://cfddose.substack.com/p/how-to-run-your-cfd-simulations-on).

![image](https://github.com/user-attachments/assets/7159bc8e-3969-49ab-a91b-084c93e92f1f)


## Post-Processing
SplashFOAM integrates with popular post-processing tools to streamline analysis:

- **ParaView**: Currently, results can be analyzed using the visualization tool ParaView. Users can launch ParaView directly from the main SplashFOAM window to post-process simulation results.
- **Grace**: Quick access to plot simulation results in 2D using Xmgrace.
  
  ![Screenshot from 2023-10-31 17-05-51](https://github.com/user-attachments/assets/f33aecd2-8bbb-4213-8626-686fde97b557)
  
  ![Grace-Example](https://github.com/user-attachments/assets/a89c6591-12f6-4d8c-9c42-4c4adf68f338)

## Documentation
The manual is currently under development. In the meantime, please check the repository for updates or contact the [CFD Dose](https://cfddose.substack.com/) community for help.

## Code Developers 
- **[Mohamed Aly Sayed](https://www.linkedin.com/in/mohamedsayedh/)** | muhammmedaly@gmail.com
- **[Thaw Tar](https://www.linkedin.com/in/thaw-tar-8bb34a73/)** | mr.thaw.tar1990@gmail.com 

## Feedback 
Feel free to contribute to SplashFOAM by submitting issues or feature suggestions. Your feedback is super valuable here ;) 

## CFD Dose Album* 
 [*_Please refer to this GitHub repository when using any of the images below (proper referencing is required)_]
 
 - **Motorbike OpenFOAM Case - Steady State**

![Screenshot from 2024-09-27 07-33-48](https://github.com/user-attachments/assets/3ea5904f-aa5d-4489-8027-2e4cbaf22173)
   
![motorbike5](https://github.com/user-attachments/assets/ab5d46b3-7389-41e9-8210-cc619085df60)

 - **Grid wall distance of a 90-degree-bend geometry**
   
![Screenshot from 2024-08-08 23-59-18](https://github.com/user-attachments/assets/1783a07f-5466-4b4e-9e44-b4936660b3c7)

 - **Velocity distribution in a 90-degree-bend at Re=4080**
   
![Screenshot from 2024-10-03 22-10-34](https://github.com/user-attachments/assets/2fdf595c-0f7c-4890-aff8-df732484f090)

 - **Instantaneous velocity and particle distribution at a cross-section of a rectangular channel at shear Re=150**

![641234f5f0f60e00ad86359e_Streamwise_fvel_yz_vel_vectorfield_10e5part_St15_Re150_ts_490k_Vinkovic_comparison](https://github.com/user-attachments/assets/e7660b93-3054-4114-9d9e-49047bc127c0)
