"""
/*--------------------------------*- C++ -*----------------------------------*\
-------------------------------------------------------------------------------
 *****   ******   *          ***     *****   *     *  
*     *  *     *  *         *   *   *     *  *     *  
*        *     *  *        *     *  *        *     *  
 *****   ******   *        *******   *****   *******  
      *  *        *        *     *        *  *     *  
*     *  *        *        *     *  *     *  *     *  
 *****   *        *******  *     *   *****   *     *  
-------------------------------------------------------------------------------
 * SplashCaseCreator is part of Splash CFD automation tool.
 * Copyright (c) 2024 THAW TAR
 * Copyright (c) 2025 Mohamed Aly Sayed and Thaw Tar
 * All rights reserved.
 *
 * This software is licensed under the GNU Lesser General Public License version 3 (LGPL-3.0).
 * You may obtain a copy of the license at https://www.gnu.org/licenses/lgpl-3.0.en.html
 */
"""

# backend module for the SplashCaseCreatorCFD project
# Description: This file contains the code for managing project structure and
# generate OpenFOAM files


import yaml
import os
import shutil
from headers import get_SplashCaseCreator_header
from primitives import SplashCaseCreatorPrimitives, SplashCaseCreatorIO, SplashCaseCreatorDataInput
from constants import meshSettings, physicalProperties, numericalSettings, inletValues
from constants import solverSettings, boundaryConditions, simulationSettings
from constants import simulationFlowSettings, parallelSettings, postProcessSettings
from stlAnalysis import stlAnalysis
from blockMeshGenerator import generate_blockMeshDict
from decomposeParGenerator import generate_DecomposeParDict
from snappyHexMeshGenerator import generate_snappyHexMeshDict
from surfaceExtractor import generate_surfaceFeatureExtractDict
from transportAndTurbulence import create_transportPropertiesDict, create_turbulencePropertiesDict
from boundaryConditionsGenerator import create_boundary_conditions
from controlDictGenerator import generate_ControlDict
from numericalSettingsGenerator import generate_fvSchemesDict, generate_fvSolutionDict
from changeDictGenerator import generate_ChangeDictionaryDict
from scriptGenerator import ScriptGenerator
from postProcess import postProcess
from mod_project import mod_project
import copy
from stlPreparation import is_stl_binary, convert_binary_to_ascii
from stlPreparation import separate_stl, is_multipatch_stl

from dialogBoxes import yesNoCancelDialogDriver, yesNoDialogDriver


#from ../constants/constants import meshSettings


class SplashCaseCreatorProject: # SplashCaseCreatorProject class to handle the project creation and manipulation
    # this class will contain the methods to handle the logic and program flow
    def __init__(self,GUIMode=False,window=None):
        # project path = project_directory_path/user_name/project_name
        self.GUIMode = GUIMode
        if GUIMode and window != None:
            self.window = window
        else:
            self.window = None
        self.current_stl_file = None   # current stl file being processed
        self.project_directory_path = None
        self.project_name = None
        self.user_name = None
        self.caseSettings = None
        self.meshSettings = None
        self.physicalProperties = None
        self.numericalSettings = None
        self.simulationSettings = None
        self.solverSettings = None
        self.inletValues = None
        self.boundaryConditions = None
        self.simulationSettings = None
        self.simulationFlowSettings = None
        self.parallelSettings = None
        self.postProcessSettings = None
        self.settings = None
        self.project_path = None
        self.existing_project = False # flag to check if the project is already existing
        self.stl_files = [] # list to store the settings for stl files
        self.stl_names = [] # list to store the names of the stl files
        self.geometries = [] # list to store the settings for non-STL geometries such as spheres, boxes, etc.
        self.stl_paths = [] # list to store the paths of the stl files
        self.internalFlow = False # default is external flow
        self.onGround = False # default is off the ground
        self.halfModel = False # default is full model
        self.parallel = True # default is parallel simulation
        self.snap = True # default is to use snappyHexMesh
        self.transient = False # default is steady state
        self.refinement = 0 # 0: coarse, 1: medium, 2: fine
        self.characteristicLength = None # default characteristic length
        self.useFOs = False # default is not to use function objects
        self.current_modification = None # current modification to the project settings
        self.inside_project_directory = False # flag to check if the current working directory is the project directory
        self.mod_options = ["Background Mesh","Add Geometry","Refinement Levels","Mesh Point","Boundary Conditions","Fluid Properties", "Numerical Settings", 
                   "Simulation Control Settings","Turbulence Model","Post Processing Settings"]
        self.minX, self.maxX, self.minY, self.maxY, self.minZ, self.maxZ = -1e-3, 1e-3, -1e-3, 1e-3, -1e-3, 1e-3
        self.lenX, self.lenY, self.lenZ = 2e-3, 2e-3, 2e-3

    #--------------------------------------------------------------------
    # Methods to handle the project summary and changes
    #--------------------------------------------------------------------
    def summarize_boundary_conditions(self):
        bcs = SplashCaseCreatorPrimitives.list_boundary_conditions(self.meshSettings)
        return bcs
    
    def ask_boundary_type(self):
        bcTypes = ["inlet","outlet","wall","symmetry","cyclic","empty","movingWall",]
        SplashCaseCreatorIO.printMessage("List of boundary types")
        SplashCaseCreatorIO.print_numbered_list(bcTypes)
        bcType = SplashCaseCreatorIO.get_input_int("Enter the number of the boundary type: ")
        if bcType <= 0 or bcType > len(bcTypes):
            SplashCaseCreatorIO.printMessage("Invalid boundary type. Setting to wall")
            return "wall"
        return bcTypes[bcType-1]

    def summarize_project(self):
        trueFalse = {True: 'Yes', False: 'No'}
        SplashCaseCreatorIO.show_title("Project Summary",GUIMode=self.GUIMode,window=self.window)
        #SplashCaseCreatorIO.printMessage(f"Project directory: {self.project_directory_path}")
        SplashCaseCreatorIO.printFormat("Project name", self.project_name, GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printFormat("Project path", self.project_path, GUIMode=self.GUIMode,window=self.window)
        
        SplashCaseCreatorIO.printMessage(f"Internal Flow: {trueFalse[self.internalFlow]}",GUIMode=self.GUIMode,window=self.window)
        if(self.internalFlow==False):
            SplashCaseCreatorIO.printMessage(f"On Ground: {trueFalse[self.onGround]}",GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printMessage(f"Transient: {trueFalse[self.transient]}",GUIMode=self.GUIMode,window=self.window)
        self.summarize_background_mesh()
        self.list_stl_files()
        # if external flow, we may have inlet, outlet, front, back, etc.
        # Need to show these boundary conditions, too
        if self.internalFlow:
            self.summarize_boundary_conditions()
        
    # this will show the details of the background mesh
    def summarize_background_mesh(self):
        minX = self.meshSettings['domain']["minx"]
        maxX = self.meshSettings['domain']["maxx"]
        minY = self.meshSettings['domain']["miny"]
        maxY = self.meshSettings['domain']["maxy"]
        minZ = self.meshSettings['domain']["minz"]
        maxZ = self.meshSettings['domain']["maxz"]
        nx = self.meshSettings['domain']['nx']
        ny = self.meshSettings['domain']['ny']
        nz = self.meshSettings['domain']['nz']
        SplashCaseCreatorIO.printMessage(f"Domain size:{'X':>10}{'Y':>10}{'Z':>10}",GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printMessage(f"Min         {minX:>10.3f}{minY:>10.3f}{minZ:>10.3f}",GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printMessage(f"Max         {maxX:>10.3f}{maxY:>10.3f}{maxZ:>10.3f}",GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printMessage(f"Background mesh size: {nx}x{ny}x{nz} cells",GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printMessage(f"Background cell size: {self.meshSettings['maxCellSize']} m",GUIMode=self.GUIMode,window=self.window)
    
    def print_numerical_settings(self):
        print("\n----------------------Numerical Settings----------------------")
        print("ddtScheme",self.numericalSettings['ddtSchemes']['default'])
        print("grad",self.numericalSettings['gradSchemes']['default'])
        print("gradU",self.numericalSettings['gradSchemes']['grad(U)'])
        print("div",self.numericalSettings['divSchemes']['default'])
        print("div, convection",self.numericalSettings['divSchemes']['div(phi,U)'])
        print("div, k",self.numericalSettings['divSchemes']['div(phi,k)'])
        print("laplacian",self.numericalSettings['laplacianSchemes']['default'])
        print("snGrad",self.numericalSettings['snGradSchemes']['default'])
        print("----------------------------------------------------------------")
    # --------------------------------------------------------------------
    # Core methods necessary for the project backend
    # --------------------------------------------------------------------
    # Create the project directory in the specified location.
    # 0, constant, system, constant/triSurface directories are created.
    def create_project(self):
        # check if the project path exists
        if self.project_path is None:
            SplashCaseCreatorIO.printError("No project path selected. Aborting project creation.",GUIMode=self.GUIMode)
            return -1
        if os.path.exists(self.project_path):
            SplashCaseCreatorIO.printWarning("Project already exists. Skipping the creation of directories",GUIMode=self.GUIMode)
            self.existing_project = True
        else:
            SplashCaseCreatorIO.printMessage("Creating project directory")
            try:
                os.makedirs(self.project_path)
                
            except OSError as error:
                SplashCaseCreatorIO.printError(error)
        try:
            os.chdir(self.project_path)
        except OSError as error:
                SplashCaseCreatorIO.printError(error)
        cwd = os.getcwd()
        SplashCaseCreatorIO.printMessage(f"Working directory: {cwd}",GUIMode=self.GUIMode,window=self.window)

        # create 0, constant and system directory
        try:
            os.mkdir("0")
            os.mkdir("constant")
            os.mkdir("system")
            os.mkdir("constant/triSurface")
        except OSError as error:
            SplashCaseCreatorIO.printError("File system already exists. Skipping the creation of directories",GUIMode=self.GUIMode)   
            return -1
        return 0 # return 0 if the project is created successfully 

    # write current settings to the project_settings.yaml file inside the project directory
    def write_settings(self):
        self.meshSettings['onGround'] = self.onGround
        settings = {
            'meshSettings': self.meshSettings,
            'physicalProperties': self.physicalProperties,
            'numericalSettings': self.numericalSettings,
            'inletValues': self.inletValues,
            'boundaryConditions': self.boundaryConditions,
            'solverSettings': self.solverSettings,
            'simulationSettings': self.simulationSettings,
            'parallelSettings': self.parallelSettings,
            'simulationFlowSettings': self.simulationFlowSettings,
            'postProcessSettings': self.postProcessSettings
        }
        #print(self.meshSettings)
        #print(self.physicalProperties)
        #print(self.numericalSettings)
        #print(self.inletValues)
        #print(self.boundaryConditions)
        SplashCaseCreatorIO.printMessage("Writing settings to project_settings.yaml",GUIMode=self.GUIMode,window=self.window)
        settings_file_path = os.path.join(self.project_path, 'project_settings.yaml')
        SplashCaseCreatorPrimitives.dict_to_yaml(settings, settings_file_path)

    # If the project is already existing, load the settings from the project_settings.yaml file
    def load_settings(self):
        SplashCaseCreatorIO.printMessage("Loading project settings",GUIMode=self.GUIMode,window=self.window)
        settings_file_path = os.path.join(self.project_path, 'project_settings.yaml')
        settings = SplashCaseCreatorPrimitives.yaml_to_dict(settings_file_path)
        self.meshSettings = settings['meshSettings']
        
        self.physicalProperties = settings['physicalProperties']
        self.numericalSettings = settings['numericalSettings']
        self.inletValues = settings['inletValues']
        self.boundaryConditions = settings['boundaryConditions']
        self.solverSettings = settings['solverSettings']
        self.simulationSettings = settings['simulationSettings']
        self.parallelSettings = settings['parallelSettings']
        self.simulationFlowSettings = settings['simulationFlowSettings']
        self.postProcessSettings = settings['postProcessSettings']
        for geometry in self.meshSettings['geometry']:
            if(geometry['type']=='triSurfaceMesh'):
                if(geometry['name'] in self.stl_names):
                    SplashCaseCreatorIO.printMessage(f"STL file {geometry['name']} already exists in the project, skipping the addition")
                else:
                    self.stl_files.append(geometry)
                    self.stl_names.append(geometry['name'])
        # Change project settings based on loaded settings
        #print(self.meshSettings)
        #print(self.physicalProperties)
        #print(self.numericalSettings)
        #print(self.simulationSettings)
        self.internalFlow = self.meshSettings['internalFlow']
        self.onGround = self.meshSettings['onGround']
        self.transient = self.simulationSettings['transient']
        
        #self.parallel = self.parallelSettings['parallel']
        #self.snap = self.meshSettings['snap']
        self.refinement = self.meshSettings['fineLevel']
        #self.characteristicLength = self.meshSettings['characteristicLength']
        self.useFOs = self.postProcessSettings['FOs']
        project_name = self.project_path.split("/")[-1]
        self.project_name = project_name
        # treat bounds as tuple
        self.meshSettings["geometry"] = SplashCaseCreatorPrimitives.treat_bounds(self.meshSettings["geometry"])

        
    def show_settings(self):
        SplashCaseCreatorIO.printMessage("Project settings")
        SplashCaseCreatorIO.printMessage("Mesh Settings")
        SplashCaseCreatorIO.print_dict(self.meshSettings)
        SplashCaseCreatorIO.printMessage("Physical Properties")
        SplashCaseCreatorIO.print_dict(self.physicalProperties)
        SplashCaseCreatorIO.printMessage("Numerical Settings")
        SplashCaseCreatorIO.print_dict(self.numericalSettings)
        SplashCaseCreatorIO.printMessage("Inlet Values")
        SplashCaseCreatorIO.print_dict(self.inletValues)
        SplashCaseCreatorIO.printMessage("Boundary Conditions")
        SplashCaseCreatorIO.print_dict(self.boundaryConditions)
        SplashCaseCreatorIO.printMessage("Solver Settings")
        SplashCaseCreatorIO.print_dict(self.solverSettings)
        SplashCaseCreatorIO.printMessage("Simulation Settings")
        SplashCaseCreatorIO.print_dict(self.simulationSettings)
        SplashCaseCreatorIO.printMessage("Parallel Settings")
        SplashCaseCreatorIO.print_dict(self.parallelSettings)
        SplashCaseCreatorIO.printMessage("Simulation Flow Settings")
        SplashCaseCreatorIO.print_dict(self.simulationFlowSettings)
        SplashCaseCreatorIO.printMessage("Post Process Settings")
        SplashCaseCreatorIO.print_dict(self.postProcessSettings)

    # If the project is not existing, load the default settings
    def load_default_settings(self):
        # It is necessary to reload these default settings for a new project
        from constants import meshSettings, physicalProperties, numericalSettings, inletValues
        from constants import solverSettings, boundaryConditions, simulationSettings
        from constants import simulationFlowSettings, parallelSettings, postProcessSettings

        
        self.meshSettings = copy.deepcopy(meshSettings)
        print(self.meshSettings['geometry'])
        self.physicalProperties = copy.deepcopy(physicalProperties)
        self.numericalSettings = copy.deepcopy(numericalSettings)
        self.inletValues = copy.deepcopy(inletValues)
        self.boundaryConditions = copy.deepcopy(boundaryConditions)
        self.simulationSettings = copy.deepcopy(simulationSettings)
        self.solverSettings = copy.deepcopy(solverSettings)
        self.parallelSettings = copy.deepcopy(parallelSettings)
        self.simulationFlowSettings = copy.deepcopy(simulationFlowSettings)
        self.postProcessSettings = copy.deepcopy(postProcessSettings)
        #self.settings = (self.meshSettings, self.physicalProperties, 
        #                 self.numericalSettings, self.inletValues, self.boundaryConditions, self.simulationSettings, self.solverSettings)

    # Create the settings for the project or load the existing settings
    def create_settings(self):
        if self.existing_project:
            SplashCaseCreatorIO.printMessage("Project already exists. Loading project settings")
            try:
                self.load_settings()
            except FileNotFoundError:
                SplashCaseCreatorIO.printMessage("Settings file not found. Loading default settings")
                self.load_default_settings()
                self.write_settings()
        else:
            self.load_default_settings()
            self.write_settings()

    # --------------------------------------------------------------------
    # Methods related to Command Line I/O
    # --------------------------------------------------------------------
    def choose_modification(self):
        current_modification = SplashCaseCreatorIO.get_option_choice(prompt="Choose any option for project modification: ",
                                      options=self.mod_options,title="\nModify Project Settings")
        self.current_modification = self.mod_options[current_modification]
        SplashCaseCreatorIO.printMessage(f"Current modification: {self.current_modification}",GUIMode=self.GUIMode,window=self.window)
        
    def choose_modification_categorized(self):
        options = ['Mesh','Boundary Conditions','Fluid Properties','Numerical Settings','Simulation Control Settings','Turbulence Model','Post Processing Settings']
        current_modification = SplashCaseCreatorIO.get_option_choice(prompt="Choose any option for project modification: ",
                                      options=options,title="\nModify Project Settings")
        mesh_options = ['Background Mesh','Mesh Point','Add Geometry','Refinement Levels']
        
        if current_modification < 0 or current_modification > len(options)-1:
            SplashCaseCreatorIO.printMessage("Invalid option. Aborting operation")
            return -1
        if current_modification == 0:
            self.current_modification = mesh_options[SplashCaseCreatorIO.get_option_choice(prompt="Choose any option for mesh modification: ",
                                      options=mesh_options,title="\nModify Mesh Settings")]
        else:
            self.current_modification = options[current_modification]

    #--------------------------------------------------------------------
    # Methods to STLs and geometry and boundary conditions
    #-------------------------------------------------------------------- 

    def change_stl_refinement_level(self,stl_file_number=0):
        SplashCaseCreatorIO.printMessage("Changing refinement level")
        refMin = SplashCaseCreatorIO.get_input_int("Enter new refMin: ")
        refMax = SplashCaseCreatorIO.get_input_int("Enter new refMax: ")
        self.stl_files[stl_file_number]['refineMin'] = refMin
        self.stl_files[stl_file_number]['refineMax'] = refMax
        #stl_name = project.stl_files[stl_file_number]['name']
        
        fileFound = False
        for stl in self.meshSettings['geometry']:
            if stl['name'] == self.stl_files[stl_file_number]['name']:
                fileFound = True
                stl['refineMin'] = refMin
                stl['refineMax'] = refMax
                stl['featureLevel'] = refMax
                break
        if not fileFound:
            SplashCaseCreatorIO.printMessage("STL file not found in the geometry list")
        return 0
    
    def remove_duplicate_stl_files(self):
        # detect duplicate dictionaries in the list
        seen = set()
        new_list = []
        for d in self.stl_files:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_list.append(d)
        self.stl_files = new_list
        self.meshSettings['geometry'] = SplashCaseCreatorPrimitives.remove_duplicate_dicts(self.meshSettings['geometry'])
        
    def change_stl_property(self,stl_file_name,property):
        for stl in self.meshSettings['geometry']:
            if stl['name'] == stl_file_name: 
                stl['property'] = property
        
    def get_stl_properties(self,stl_file_name):
        #print(stl_file_name)
        
        for stl in self.stl_files:
            #print(stl)
            if stl['name'] == stl_file_name:
                #print("Found")
                purpose = stl['purpose']
                refMin = stl['refineMin']
                refMax = stl['refineMax']
                featureEdges = stl['featureEdges']
                featureLevel = stl['featureLevel']
                
                if isinstance(stl['nLayers'],int):
                    nLayers = stl['nLayers']
                else:
                    nLayers = 0
                property = stl['property']
                bounds = stl['bounds']
                return purpose,refMin,refMax,featureEdges,featureLevel,nLayers,property,bounds
        return None

    def get_boundary_properties(self,boundary_name):
        for boundary in self.meshSettings['patches']:
            if boundary['name'] == boundary_name:
                purpose = boundary['purpose']
                refMin = 0
                refMax = 0
                featureEdges = False
                featureLevel = 0
                nLayers = 0
                property = boundary['property']
                bounds = None
                return purpose,refMin,refMax,featureEdges,featureLevel,nLayers,property,bounds
        return None
    
    def show_stl_properties(self,stl_file_name):
        purpose,refMin,refMax,featureEdges,featureLevel,nLayers,property,bounds = self.get_stl_properties(stl_file_name)
        SplashCaseCreatorIO.printMessage(f"STL file: {stl_file_name}")
        SplashCaseCreatorIO.printMessage(f"Purpose: {purpose}")
        SplashCaseCreatorIO.printMessage(f"Refinement Min: {refMin}")
        SplashCaseCreatorIO.printMessage(f"Refinement Max: {refMax}")
        SplashCaseCreatorIO.printMessage(f"Feature Edges: {featureEdges}")
        SplashCaseCreatorIO.printMessage(f"Feature Level: {featureLevel}")
        SplashCaseCreatorIO.printMessage(f"Number of Layers: {nLayers}")
        SplashCaseCreatorIO.printMessage(f"Property: {property}")
        SplashCaseCreatorIO.printMessage(f"Bounds: {bounds}")
    
    def get_stl(self,stl_file_name):
        for stl in self.stl_files:
            if stl['name'] == stl_file_name:
                return stl
        return None
    
    def get_boundary(self,boundary_name):
        boundary_names = [boundary['name'] for boundary in self.meshSettings['patches']]
        if boundary_name in boundary_names:
            for boundary in self.meshSettings['patches']:
                if boundary['name'] == boundary_name:
                    return boundary
        return None

    def remove_stl_from_mesh_settings(self,stl_name):
        idx = 0
        for stl in self.meshSettings['geometry']:
            if stl['name'] == stl_name:
                self.meshSettings['geometry'].pop(idx)
                return 0
            idx += 1
        return -1
    
    def set_stl_properties(self,stl_file_name,stl_properties):
        refMin,refMax,refLevel,nLayers,usage,edgeRefine,ami,property = stl_properties
        #refMin,refMax,featureLevel,nLayers,property,bounds = stl_properties
        usageToPurpose = {'Wall':'wall', 'Inlet':'inlet','Outlet':'outlet','Refinement_Region':'refinementRegion',
                          'Refinement_Surface':'refinementSurface','Cell_Zone':'cellZone','Baffles':'baffles',
                          'Symmetry':'symmetry','Cyclic':'cyclic','Empty':'empty'}
        for stl in self.meshSettings['geometry']:
            if stl['name'] == stl_file_name:
                stl['purpose'] = usageToPurpose[usage]
                stl['refineMin'] = refMin
                stl['refineMax'] = refMax
                stl['featureEdges'] = edgeRefine
                stl['featureLevel'] = refMin
                stl['nLayers'] = nLayers
                
                #stl['bounds'] = bounds
                if usage == 'Cell_Zone':
                    stl['property'] = (refLevel,ami)
                elif usage == 'Refinement_Region':
                    stl['property'] = refLevel
                elif usage == 'Refinement_Surface':
                    stl['property'] = refLevel
                else:
                    stl['property'] = property
                return 0
        return -1
    
    def set_boundary_condition(self,stl_file_name,boundary_condition):
        for stl in self.meshSettings['geometry']:
            if stl['name'] == stl_file_name:
                if stl['purpose'] == 'inlet':
                    # set the inlet values
                    stl['property'] = list(boundary_condition[0])
                return 0
            
        print("Failed setting boundary condition. STL file not found")
        return -1
    
    def set_boundary_type(self,patch_name,boundary_type):
        for patch in self.meshSettings['patches']:
            if patch['name'] == patch_name:
                patch['type'] = boundary_type
                return 0
        return -1
    
    def set_boundary_properties(self,boundary_name,boundary_properties):
        refMin,refMax,refLevel,nLayers,usage,edgeRefine,ami,property = boundary_properties
        usageToPurpose = {'Wall':'wall', 'Inlet':'inlet','Outlet':'outlet','Refinement_Region':'refinementRegion',
                          'Refinement_Surface':'refinementSurface','Cell_Zone':'cellZone','Baffles':'baffles',
                          'Symmetry':'symmetry','Cyclic':'cyclic','Empty':'empty'}
        for boundary in self.meshSettings['patches']:
            if boundary['name'] == boundary_name:
                boundary['purpose'] = usageToPurpose[usage]
                boundary['property'] = property
                if usageToPurpose[usage] in ['wall','symmetry','cyclic','empty']:
                    boundary['type'] = usageToPurpose[usage]
                    boundary['property'] = None

                
                return 0
        return -1
    
    def set_external_boundary_condition(self,patch_name,boundary_condition):
        for patch in self.meshSettings['patches']:
            if patch['name'] == patch_name:
                if patch['purpose'] == 'inlet':
                    # set the inlet values
                    patch['property'] = list(boundary_condition[0])
                return 0

    # This is the parent function to add a predefined VTK object to the project
    # If there is already a VTK object with the same name, it will not be added
    def add_geometry_to_project(self,geometry):
        #print("Adding geometry to project")
        geometry_name = geometry['name']
        if geometry_name in self.stl_names or geometry_name in self.geometries:
            SplashCaseCreatorIO.printMessage(f"Geometry {geometry_name} already exists in the project")
            return -1
        else:
            self.meshSettings['geometry'].append(geometry)
            self.geometries.append(geometry_name)
            return 0
        
    def add_stl_to_project(self,geometry):
        #print("Adding geometry to project")
        geometry_name = geometry['name']
        if geometry_name in self.stl_names or geometry_name in self.geometries:
            SplashCaseCreatorIO.printMessage(f"STL {geometry_name} already exists in the project")
            return -1
        for stl_file in self.stl_files:
            if stl_file['name'] == geometry_name:
                SplashCaseCreatorIO.printMessage(f"STL {geometry_name} already exists in the project")
                return -1
        self.meshSettings['geometry'].append(geometry)
        self.stl_names.append(geometry_name)
        self.stl_files.append(geometry)
        return 0
            
    # To add predefined VTK objects to the project such as spheres or boxes
    # This object will be used for meshing and possibly for boundary conditions
    def add_vtk_object_to_project(self,obj_name="sphere1",obj_properties={},obj_type="sphere"):
        if obj_type == "sphere":
            x, y, z, radius = obj_properties['x'], obj_properties['y'], obj_properties['z'], obj_properties['radius']
            geometry = {'name': obj_name, 'type':'searchableSphere','center':[x,y,z],'radius':radius,'purpose':'refinementRegion','featureEdges':False,'refineMin':obj_properties['refineMin'],
                        'refineMax':obj_properties['refineMax'],'property':obj_properties['property']}
            self.add_geometry_to_project(geometry)
        elif obj_type == "box":
            minx, maxx, miny, maxy, minz, maxz = obj_properties['minx'], obj_properties['maxx'], obj_properties['miny'], obj_properties['maxy'], obj_properties['minz'], obj_properties['maxz']
            geometry = {'name': obj_name, 'type':'searchableBox','min':[minx,miny,minz],'max':[maxx,maxy,maxz],'purpose':'refinementRegion','featureEdges':False,
                        'refineMin':obj_properties['refineMin'],'refineMax':obj_properties['refineMax'],'property':obj_properties['property']}
            self.add_geometry_to_project(geometry)
        elif obj_type == "cylinder":
            x, y, z, radius, height = obj_properties['x'], obj_properties['y'], obj_properties['z'], obj_properties['radius'], obj_properties['height']
            geometry = {'name': obj_name, 'type':'searchableCylinder','center':[x,y,z],'radius':radius,'height':height,'purpose':'refinementRegion','featureEdges':False,
                        'refineMin':obj_properties['refineMin'],'refineMax':obj_properties['refineMax'],'property':obj_properties['property']}
            self.add_geometry_to_project(geometry)
        elif obj_type == "stl":
            geometry = {'name': obj_name, 'type':'triSurfaceMesh','purpose':'wall','featureEdges':True,'refineMin':obj_properties['refineMin'],
                        'refineMax':obj_properties['refineMax'],'property':obj_properties['property'],'bounds':obj_properties['bounds']}
            self.add_geometry_to_project(geometry)
        else:
            SplashCaseCreatorIO.printMessage("Invalid object type")
            return -1
        
    # to add refinement box to mesh settings
    def addRefinementBoxToMesh(self,stl_path,boxName='refinementBox',refLevel=2,internalFlow=False):
        if(internalFlow):
            return #meshSettings
        stlBoundingBox = stlAnalysis.compute_bounding_box(stl_path)
        box = stlAnalysis.getRefinementBox(stlBoundingBox)
        obj_properties = {'minx':box[0],'maxx':box[1],'miny':box[2],'maxy':box[3],'minz':box[4],'maxz':box[5],'refineMin':0,'refineMax':refLevel,'property':None}
        self.add_vtk_object_to_project(obj_name=boxName,obj_properties=obj_properties,obj_type="box")
    
    def addFineBoxToMesh(self,stl_path,boxName='fineBox',refLevel=2,internalFlow=False):

        stlBoundingBox = stlAnalysis.compute_bounding_box(stl_path)
        fineBox = stlAnalysis.getRefinementBoxClose(stlBoundingBox)
        obj_properties = {'minx':fineBox[0],'maxx':fineBox[1],'miny':fineBox[2],'maxy':fineBox[3],'minz':fineBox[4],'maxz':fineBox[5],'refineMin':0,'refineMax':refLevel,'property':None}
        self.add_vtk_object_to_project(obj_name=boxName,obj_properties=obj_properties,obj_type="box")
        
    # refinement box for the ground for external automotive flows
    
    def addGroundRefinementBoxToMesh(self,stl_path,refLevel=2):
        #if(internalFlow):
        #    return meshSettings
        boxName = 'groundBox'
        stlBoundingBox = stlAnalysis.compute_bounding_box(stl_path)
        xmin, xmax, ymin, ymax, zmin, zmax = stlBoundingBox
        z = meshSettings['domain']['minz']
        z_delta = 0.2*(zmax-zmin)
        box = [-1000.0,1000.,-1000,1000,z-z_delta,z+z_delta]
        obj_properties = {'minx':box[0],'maxx':box[1],'miny':box[2],'maxy':box[3],'minz':box[4],'maxz':box[5],'refineMin':0,'refineMax':refLevel,'property':None}
        self.add_vtk_object_to_project(obj_name=boxName,obj_properties=obj_properties,obj_type="box") 
    
    def add_multipatch_stl_file(self,stl_file):
        # first, copy the file to the project directory
        if stl_file is None:
            SplashCaseCreatorIO.printMessage("No file selected. Please select STL file if necessary.",GUIMode=self.GUIMode,window=self.window)
            return -1
        stl_name = stl_file.split("/")[-1]
        #print("Adding stl file:",stl_name)
        if stl_name in self.stl_names:
            SplashCaseCreatorIO.printMessage(f"STL file {stl_name} already exists in the project",GUIMode=self.GUIMode,window=self.window)
            return -1
        # create a temp directory to store the stl file
        temp_dir = os.path.join(self.project_path,"temp")
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        temp_stl_path = os.path.join(temp_dir,stl_name)
        try:
            shutil.copy(stl_file,temp_stl_path)
            separate_stl(temp_stl_path)
            # list all files in the temp directory
            files = os.listdir(temp_dir)
            for file in files:
                if file.endswith(".stl"):
                    #print(file)
                    stl_path = os.path.join(temp_dir,file)
                    if stl_path == temp_stl_path:
                        continue
                    self.add_single_stl_file(stl_path)
        except OSError as error:
            SplashCaseCreatorIO.printError(error,GUIMode=self.GUIMode)
            return -1
        return 3 # 3 means multiple STL files added
        
    def add_single_stl_file(self,stl_file):
        if stl_file is None:
            SplashCaseCreatorIO.printMessage("No file selected. Please select STL file if necessary.",GUIMode=self.GUIMode,window=self.window)
            return -1
        #print("Existing stl files")
        #print(self.stl_names)
        
        stl_name = stl_file.split("/")[-1]
        #print("Adding stl file:",stl_name)
        if stl_name in self.stl_names:
            SplashCaseCreatorIO.printMessage(f"STL file {stl_name} already exists in the project",GUIMode=self.GUIMode,window=self.window)
            return -1
        
        purpose = 'wall'
        property = None
        bounds = stlAnalysis.compute_bounding_box(stl_file)
        bounds = tuple(bounds)
        # this is the path to the constant/triSurface inside project directory where STL will be copied
        stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
        try:
            SplashCaseCreatorIO.printMessage(f"Copying {stl_name} to the project directory",GUIMode=self.GUIMode,window=self.window)
            shutil.copy(stl_file, stl_path)
        except OSError as error:
            SplashCaseCreatorIO.printError(error,GUIMode=self.GUIMode)
            return -1
        try:
            stlAnalysis.set_stl_solid_name(stl_path)
            # If everything is successful, add the stl file to the project
            stl_geometry = {'name': stl_name, 'type':'triSurfaceMesh','purpose':purpose, 'refineMin': 0, 'refineMax': 0, 
                            'featureEdges':True, 'featureLevel':1, 'nLayers':3, 'property':property, 'bounds':bounds}
            status = self.add_stl_to_project(stl_geometry)
            if status == -1:
                return -1
            #self.stl_names.append(stl_name)
            #self.stl_files.append(stl_geometry)
        except Exception as error:
            SplashCaseCreatorIO.printError(error,GUIMode=self.GUIMode)
            return -1
        self.current_stl_file = stl_path
        self.stl_paths.append(stl_path)
        return 0
        
    # this is the main STL file addition function

    def add_stl_file(self,stl_file):
        if stl_file is None:
            SplashCaseCreatorIO.printMessage("No file selected. Please select STL file if necessary.",GUIMode=self.GUIMode,window=self.window)
            return -1
        #print("Existing stl files")
        #print(self.stl_names)
        
        stl_name = stl_file.split("/")[-1]
        #print("Adding stl file:",stl_name)
        if stl_name in self.stl_names:
            SplashCaseCreatorIO.printMessage(f"STL file {stl_name} already exists in the project",GUIMode=self.GUIMode,window=self.window)
            return -1
        
        # check if the stl file is in binary format
        if is_stl_binary(stl_file):
            # create a temp directory in the project directory
            temp_dir = os.path.join(self.project_path,"temp")
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)
            temp_stl_path = os.path.join(temp_dir,stl_name)
            try:
                shutil.copy(stl_file,temp_stl_path)
            except OSError as error:
                SplashCaseCreatorIO.printError(error,GUIMode=self.GUIMode)
                return -1
            # convert the binary stl file to ascii format
            ascii_stl_path = os.path.join(temp_dir,stl_name.split(".")[0]+".stl")
            try:
                convert_binary_to_ascii(input_file_path=temp_stl_path,output_file_path=ascii_stl_path)
            except Exception as error:
                SplashCaseCreatorIO.printError(error,GUIMode=self.GUIMode)
                return -1
            # add the ascii stl file to the project
            status = self.add_single_stl_file(ascii_stl_path)
            return status
        else:
            # check if the stl file is a multi-patch stl file
            if is_multipatch_stl(stl_file):
                # ask the user if they want to add all the patches separately or as a single solid
                yesNo = yesNoDialogDriver("Multiple patches detected. Do you want to add all the patches separately?")
                if yesNo:
                    SplashCaseCreatorIO.printMessage("Adding multiple patches separately")
                    status = self.add_multipatch_stl_file(stl_file)
                    return status
                else:
                    SplashCaseCreatorIO.printMessage("Adding all patches as a single solid")
                    status = self.add_single_stl_file(stl_file)
                    return status
                #status = self.add_multipatch_stl_file(stl_file)
                #return status
            else:
                status = self.add_single_stl_file(stl_file)
                return status
        
            
            
    # this is a wrapper of the primitives 
    def list_stl_files(self):
        SplashCaseCreatorPrimitives.list_stl_files(self.stl_files,self.GUIMode,self.window)

    def list_stl_paths(self):
        stl_paths = []
        for stl_file in self.stl_files:
            stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_file['name'])
            #SplashCaseCreatorIO.printMessage(stl_path)
            stl_paths.append(stl_path)
        return stl_paths
    
    def remove_stl_file_by_name(self,stl_name):
        print("Before removing")
        self.list_stl_files()
        for stl in self.stl_files:
            if stl['name'] == stl_name:
                self.stl_files.remove(stl)
                self.remove_stl_from_mesh_settings(stl_name)
                if stl_name in self.stl_names:
                    self.stl_names.remove(stl_name)
                #stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
                #try:
                #    os.remove(stl_path)
                #except OSError as error:
                #    SplashCaseCreatorIO.printError(error)
                #    return -1
                #print(f"STL file {stl_name} removed from the project")
                #self.list_stl_files()
                #print(self.stl_files)
                return 0
        self.list_stl_files()
        return -1
    
    # check if the stl file is already in the project
    def check_stl_file(self,stl_name):
        stl_exists = False
        for stl in self.stl_files:
            if stl['name'] == stl_name:
                stl_exists = True
                break
        return stl_exists

    def remove_stl_file(self,stl_file_number=0):
        #self.list_stl_files()
        #stl_file_number = SplashCaseCreatorIO.get_input("Enter the number of the file to remove: ")
        try:
            stl_file_number = int(stl_file_number)
        except ValueError:
            SplashCaseCreatorIO.printMessage("Invalid input. Aborting operation")
            return -1
        if stl_file_number < 0 or stl_file_number > len(self.stl_files):
            SplashCaseCreatorIO.printMessage("Invalid file number. Aborting operation")
            return -1
        stl_file = self.stl_files[stl_file_number]
        stl_name = stl_file['name']
        self.stl_files.remove(stl_file)
        self.stl_names.remove(stl_name)
        stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
        try:
            os.remove(stl_path)
        except OSError as error:
            SplashCaseCreatorIO.printError(error)
            return -1
        return 0

    def analyze_stl_file(self,stl_file_number=0):
        rho = self.physicalProperties['rho']
        nu = self.physicalProperties['nu']
        U = max(self.inletValues['U'])
        ER = self.meshSettings['addLayersControls']['expansionRatio']
        try:
            stl_file_number = int(stl_file_number)
        except ValueError:
            SplashCaseCreatorIO.printError("Invalid input. Aborting operation",GUIMode=self.GUIMode)
            return -1
        if stl_file_number < 0 or stl_file_number > len(self.stl_files):
            SplashCaseCreatorIO.printError("Invalid file number. Aborting operation",GUIMode=self.GUIMode)
            return -1
        stl_file = self.stl_files[stl_file_number]
        stl_name = stl_file['name']
        SplashCaseCreatorIO.printMessage(f"Analyzing {stl_name}",GUIMode=self.GUIMode,window=self.window)
        stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
        stlBoundingBox = stlAnalysis.compute_bounding_box(stl_path)
        domain_size, nx, ny, nz, refLevel,target_y,nLayers = stlAnalysis.calc_mesh_settings(stlBoundingBox, nu, rho,U=U,maxCellSize=2.0,expansion_ratio=ER,
                                                                           onGround=self.onGround,internalFlow=self.internalFlow,
                                                                           refinement=self.refinement,halfModel=self.halfModel,
                                                                           GUI=self.GUIMode,window=self.window)
        self.update_max_stl_length(stlBoundingBox)
        featureLevel = max(refLevel,1)
        self.meshSettings = stlAnalysis.set_mesh_settings(self.meshSettings, domain_size, nx, ny, nz, refLevel, featureLevel,nLayers=nLayers) 
        # update the max cell size for reference and later use
        self.meshSettings['maxCellSize'] = self.get_mesh_size()
        self.set_max_domain_size(domain_size,nx,ny,nz)
        self.meshSettings = stlAnalysis.set_mesh_location(self.meshSettings, stl_path,self.internalFlow)
        refinementBoxLevel = max(2,refLevel-3)
        self.addRefinementBoxToMesh(stl_path=stl_path,refLevel=refinementBoxLevel,internalFlow=self.internalFlow)
        self.addFineBoxToMesh(stl_path=stl_path,refLevel=refinementBoxLevel)
        if(self.internalFlow==False and self.onGround==True):
            # if the flow is external and the geometry is on the ground, add a ground refinement box
            self.addGroundRefinementBoxToMesh(stl_path=stl_path,refLevel=refinementBoxLevel)
        self.meshSettings = stlAnalysis.set_layer_thickness(self.meshSettings, 0.5) # set the layer thickness to 0.5 times the cell size
        # store the background mesh size for future reference
        maxCellSize = abs((domain_size[1]-domain_size[0])/nx)
        self.meshSettings['maxCellSize'] = maxCellSize
        #self.meshSettings = stlAnalysis.set_min_vol(self.meshSettings, minVol)
        return 0
    
    def analyze_stl_by_name(self,stl_name):
        idx = self.get_stl_index(stl_name)
        if idx == -1:
            SplashCaseCreatorIO.printError("STL file not found. Aborting operation",GUIMode=self.GUIMode)
            return -1
        self.analyze_stl_file(idx)
    
    def adjust_domain_size(self):
        # adjust the domain size based on the bounding box of the stl files
        SplashCaseCreatorIO.printMessage("Adjusting domain size based on the bounding box of the stl files",GUIMode=self.GUIMode,window=self.window)
        for stl_file in self.stl_files:
            stl_name = stl_file['name']
            stl_path = os.path.join(self.project_path, "constant", "triSurface", stl_name)
            stlBoundingBox = stlAnalysis.compute_bounding_box(stl_path)
            xmin, xmax, ymin, ymax, zmin, zmax = stlBoundingBox                                                    
            self.minX = min(xmin,self.minX)
            self.maxX = max(xmax,self.maxX)
            self.minY = min(ymin,self.minY)
            self.maxY = max(ymax,self.maxY)
            self.minZ = min(zmin,self.minZ)
            self.maxZ = max(zmax,self.maxZ)
            #self.meshSettings = stlAnalysis.set_mesh_location(self.meshSettings, stl_path,self.internalFlow)
        # if the flow is internal, the domain size should be adjusted to include the entire geometry
        
        self.meshSettings['domain']['minX'] = self.minX
        self.meshSettings['domain']['maxX'] = self.maxX
        self.meshSettings['domain']['minY'] = self.minY
        self.meshSettings['domain']['maxY'] = self.maxY
        self.meshSettings['domain']['minZ'] = self.minZ
        self.meshSettings['domain']['maxZ'] = self.maxZ
    # --------------------------------------------------------------------
    # Methods to handle project directory and file structure 
    # --------------------------------------------------------------------
    def set_project_directory(self, project_directory_path):
        if self.GUIMode:
            stopWhenError = False
        else:
            stopWhenError = True
        if project_directory_path is None:
            if stopWhenError:
                SplashCaseCreatorIO.printMessage("No directory selected. Aborting project creation.")
                exit()
            else:
                return -1
        #assert os.path.exists(project_directory_path), "The chosen directory does not exist"
        if not os.path.exists(project_directory_path):
            if stopWhenError:
                SplashCaseCreatorIO.printMessage("The chosen directory does not exist. Aborting project creation.")
                exit()
            else:
                self.project_directory_path = None
                return -1
        self.project_directory_path = project_directory_path

    def set_project_name(self, project_name):
        self.project_name = project_name

    def set_user_name(self, user_name):
        self.user_name = user_name

    # create the project path for the user and project name
    def create_project_path_user(self):
        if not self.project_directory_path:
            SplashCaseCreatorIO.printWarning("No directory selected. Aborting project creation.",GUIMode=self.GUIMode)
            return -1
        self.project_path = os.path.join(self.project_directory_path, self.user_name, self.project_name)
        
    # To create the project path for a new project with the project name
    def create_project_path(self):
        if not self.project_directory_path:
            SplashCaseCreatorIO.printWarning("No directory selected. Aborting project creation.")
            return -1
        self.project_path = os.path.join(self.project_directory_path, self.project_name)
    
    # this is to set the project path if the project is already existing
    # useful for opening existing projects and modifying the settings
    def set_project_path(self,project_path):
        if project_path is None:
            if self.GUIMode==False:
                SplashCaseCreatorIO.printWarning("No project path selected. Aborting project creation.",GUIMode=self.GUIMode)   
            #SplashCaseCreatorIO.printWarning("No project path selected. Aborting project creation/modification.",GUIMode=self.GUIMode)
            return -1
            #exit()
        if os.path.exists(project_path):
            settings_file = os.path.join(project_path, "project_settings.yaml")
            if os.path.exists(settings_file):
                SplashCaseCreatorIO.printMessage("Project found, loading project settings",GUIMode=self.GUIMode,window=self.window)
                self.existing_project = True
                self.project_path = project_path
                return 0
            else:
                if self.GUIMode==False:
                    SplashCaseCreatorIO.printWarning("Settings file not found. Please open an SplashCaseCreator case directory.",GUIMode=self.GUIMode)
                #SplashCaseCreatorIO.printWarning("Settings file not found. Please open an SplashCaseCreator case directory.",GUIMode=self.GUIMode)
                # TO DO: Add the code socket to create a new project here
                return -1
        else:
            if self.GUIMode==False:
                SplashCaseCreatorIO.printWarning("Project path does not exist. Aborting project creation/opening.",GUIMode=self.GUIMode)
            #SplashCaseCreatorIO.printWarning("Project path does not exist. Aborting project creation/opening.",GUIMode=self.GUIMode)
            return -1

    def check_project_path(self): # check if the project path exists and if the project is already existing
        if os.path.exists(self.project_path):
            settings_file = os.path.join(self.project_path, "project_settings.yaml")
            if os.path.exists(settings_file):
                SplashCaseCreatorIO.printWarning("Project already exists, loading project settings",GUIMode=self.GUIMode)
                self.existing_project = True
                return 0
            else:
                self.existing_project = False
                return -1
        else:
            self.existing_project = False
            return -1
        
    # Wrapper of cwd with error handling
    def go_inside_directory(self):
        try:
            os.chdir(self.project_path)
        except OSError as error:
                SplashCaseCreatorIO.printError(error)
        cwd = os.getcwd()
        SplashCaseCreatorIO.printMessage(f"Working directory: {cwd}",GUIMode=self.GUIMode,window=self.window)
        self.inside_project_directory = True

    # Check if the 0 directory exists in the project directory
    def check_0_directory(self):
        if not os.path.exists("0"):
            SplashCaseCreatorIO.printWarning("0 directory does not exist.",GUIMode=self.GUIMode)
            SplashCaseCreatorIO.printMessage("Checking for 0.orig directory",GUIMode=self.GUIMode,window=self.window)
            if os.path.exists("0.orig"):
                SplashCaseCreatorIO.printMessage("0.orig directory found. Copying to 0 directory",GUIMode=self.GUIMode,window=self.window)
                shutil.copytree("0.orig", "0")
            else:
                SplashCaseCreatorIO.printWarning("0.orig directory not found. Aborting project creation.",GUIMode=self.GUIMode)
                return -1
        return 0
    
    # Check if the constant directory exists in the project directory
    def check_constant_directory(self):
        if not os.path.exists("constant"):
            SplashCaseCreatorIO.printWarning("constant directory does not exist.",GUIMode=self.GUIMode)
            #SplashCaseCreatorIO.printError("constant directory is necessary for the project")
            return -1
        return 0
    
    # Check if the system directory exists in the project directory
    def check_system_directory(self):
        if not os.path.exists("system"):
            SplashCaseCreatorIO.printWarning("system directory does not exist.",GUIMode=self.GUIMode)
            #SplashCaseCreatorIO.printError("system directory is necessary for the project")
            return -1
        return 0
    
    # Check if the constant/triSurface directory exists in the project directory
    def check_triSurface_directory(self):
        if not os.path.exists("constant/triSurface"):
            SplashCaseCreatorIO.printWarning("triSurface directory does not exist.",GUIMode=self.GUIMode)
            #SplashCaseCreatorIO.printError("triSurface directory is necessary for the project")
            return -1
        # if exists, check if the stl files are present
        stl_files = os.listdir("constant/triSurface")

    # to check whether log files are present in the project directory
    def check_log_files(self):
        log_files = os.listdir()
        if 'log.simpleFoam' in log_files:
            SplashCaseCreatorIO.printMessage("Simulation log file found",GUIMode=self.GUIMode,window=self.window)
            return 1
        if 'log.pimpleFoam' in log_files:
            SplashCaseCreatorIO.printMessage("Simulation log file found",GUIMode=self.GUIMode,window=self.window)
            return 1
        return 0
    
    # to check whether the U and p files are present in the postProcess directory
    def check_post_process_files(self):
        if(not os.path.exists("postProcessing/probe/0")):
            SplashCaseCreatorIO.printWarning("postProcess directory does not exist",GUIMode=self.GUIMode)
            return 0
        postProcess_files = os.listdir("postProcessing/probe/0")
        if 'U' in postProcess_files and 'p' in postProcess_files:
            SplashCaseCreatorIO.printMessage("U and p files found in postProcess directory",GUIMode=self.GUIMode,window=self.window)
            return 1
        return 0
    
    def check_forces_files(self):
        if(not os.path.exists("postProcessing/forces/0")):
            SplashCaseCreatorIO.printWarning("forces directory does not exist",GUIMode=self.GUIMode)
            return 0
        forces_files = os.listdir("postProcessing/forces/0")
        if 'force.dat' in forces_files:
            SplashCaseCreatorIO.printMessage("force.dat found in forces directory")
            return 1
        return 0
    
    def create_project_files(self):
        #(meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions)=caseSettings
        # check if the current working directory is the project directory
        if not os.path.exists(self.project_path):
            SplashCaseCreatorIO.printMessage("Project directory does not exist. Aborting project creation.")
            return -1
        if os.getcwd() != self.project_path:
            os.chdir(self.project_path)

        # Remove the existing 0.orig directory if it exists.
        # This is to prevent the error of copying the old 0.orig directory to 0 directory
        if os.path.exists("0.orig"):
            shutil.rmtree("0.orig")
        # create the initial conditions file
        SplashCaseCreatorIO.printMessage("Creating boundary conditions",GUIMode=self.GUIMode,window=self.window)
        # check if the 0 directory exists
        if not os.path.exists("0"):
            # create the 0 directory
            os.mkdir("0")
        # go inside the 0 directory
        os.chdir("0")
        create_boundary_conditions(self.meshSettings, self.boundaryConditions)    
        # go back to the main directory 
        os.chdir("..")
        # go inside the constant directory
        os.chdir("constant")
        SplashCaseCreatorIO.printMessage("Creating physical properties and turbulence properties",GUIMode=self.GUIMode,window=self.window)
        # create transportProperties file
        tranP = create_transportPropertiesDict(self.physicalProperties)
        # create turbulenceProperties file
        turbP = create_turbulencePropertiesDict(self.physicalProperties)
        SplashCaseCreatorPrimitives.write_dict_to_file("transportProperties", tranP)
        SplashCaseCreatorPrimitives.write_dict_to_file("turbulenceProperties", turbP)
        # go back to the main directory
        os.chdir("..")
        
        # go inside the system directory
        os.chdir("system")
        # create the controlDict file
        SplashCaseCreatorIO.printMessage("Creating the system files",GUIMode=self.GUIMode,window=self.window)
        controlDict = generate_ControlDict(self.simulationSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("controlDict", controlDict)
        blockMeshDict = generate_blockMeshDict(self.meshSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("blockMeshDict", blockMeshDict)
        snappyHexMeshDict = generate_snappyHexMeshDict(self.meshSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("snappyHexMeshDict", snappyHexMeshDict)
        surfaceFeatureExtractDict = generate_surfaceFeatureExtractDict(self.meshSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("surfaceFeatureExtractDict", surfaceFeatureExtractDict)
        fvSchemesDict = generate_fvSchemesDict(self.numericalSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("fvSchemes", fvSchemesDict)
        fvSolutionDict = generate_fvSolutionDict(self.numericalSettings, self.solverSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("fvSolution", fvSolutionDict)
        decomposeParDict = generate_DecomposeParDict(self.parallelSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("decomposeParDict", decomposeParDict)
        FODict = postProcess.create_FOs(self.meshSettings,self.postProcessSettings,useFOs=self.useFOs)
        SplashCaseCreatorPrimitives.write_dict_to_file("FOs", FODict)
        changeDictionaryDict = generate_ChangeDictionaryDict(self.meshSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("changeDictionaryDict", changeDictionaryDict)
        # go back to the main directory
        os.chdir("..")
        # create mesh script
        SplashCaseCreatorIO.printMessage("Creating scripts for meshing and running the simulation",GUIMode=self.GUIMode,window=self.window)
        meshScript = ScriptGenerator.generate_mesh_script(self.simulationFlowSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("mesh", meshScript)
        # create simulation script
        simulationScript = ScriptGenerator.generate_simulation_script(self.simulationFlowSettings)
        SplashCaseCreatorPrimitives.write_dict_to_file("run", simulationScript)
        SplashCaseCreatorPrimitives.crlf_to_LF("mesh")
        SplashCaseCreatorPrimitives.crlf_to_LF("run")
        if os.name != 'nt':
            os.chmod("mesh", 0o755)
            os.chmod("run", 0o755)
        # go back to the main directory
        os.chdir("..")
        SplashCaseCreatorIO.printMessage("\n-----------------------------------",GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printMessage("Project files created successfully!",GUIMode=self.GUIMode,window=self.window)
        SplashCaseCreatorIO.printMessage("-----------------------------------\n",GUIMode=self.GUIMode,window=self.window)
        return 0
    # --------------------------------------------------------------------


    def ask_purpose(self):
        purposes = ['wall', 'inlet','outlet', 'refinementRegion', 'refinementSurface', 
                    'cellZone', 'baffles','symmetry','cyclic','empty',]
        SplashCaseCreatorIO.printMessage(f"Enter purpose for this STL geometry")
        SplashCaseCreatorIO.print_numbered_list(purposes)
        purpose_no = SplashCaseCreatorIO.get_input_int("Enter purpose number: ")-1
        if(purpose_no < 0 or purpose_no > len(purposes)-1):
                SplashCaseCreatorIO.printMessage("Invalid purpose number. Setting purpose to wall")
                purpose = 'wall'
        else:
            purpose = purposes[purpose_no]
        return purpose
    
    def set_property(self,purpose='wall'):
        if purpose == 'inlet':
            U = SplashCaseCreatorDataInput.get_inlet_values()
            property = tuple(U)
            SplashCaseCreatorIO.printMessage(f"Setting property of {purpose} to {property}")
        elif purpose == 'refinementRegion' :
            refLevel = SplashCaseCreatorIO.get_input_int("Enter refinement level: ")
            property = refLevel
        elif purpose == 'cellZone':
            refLevel = SplashCaseCreatorIO.get_input_int("Enter refinement level: ")
            createPatches = SplashCaseCreatorIO.get_input_bool("Create patches for this cellZone? (y/N): ")
            property = (refLevel, createPatches,0) # 0 is just a placeholder for listing the patches
        elif purpose == 'refinementSurface':
            refLevel = SplashCaseCreatorIO.get_input_int("Enter refinement level: ")
            property = refLevel
        else:
            property = None
        return property
    
    def set_numerical_settings(self,numericalSettings):
        self.numericalSettings = numericalSettings
    
        
    def get_stl_index(self,stl_file_name):
        for idx,stl in enumerate(self.stl_files):
            if stl['name'] == stl_file_name:
                return idx
        return -1
    
    def get_location_in_mesh(self):
        return self.meshSettings["castellatedMeshControls"]["locationInMesh"]
    
    def set_location_in_mesh(self,locationInMesh):
        print(locationInMesh)
        self.meshSettings["castellatedMeshControls"]["locationInMesh"] = locationInMesh
    

    def ask_flow_type(self):
        flow_type = SplashCaseCreatorIO.get_input("Internal or External Flow (I/E)?: ")
        if flow_type.lower() == 'i':
            self.internalFlow = True
        else:
            self.internalFlow = False
        self.meshSettings['internalFlow'] = self.internalFlow

    def set_flow_type(self,internalFlow=False):
        self.internalFlow = internalFlow
        self.meshSettings['internalFlow'] = self.internalFlow

    def ask_transient(self):
        transient = SplashCaseCreatorIO.get_input("Transient or Steady State (T/S)?: ")
        if transient.lower() == 't':
            self.transient = True
        else:
            self.transient = False

    def ask_half_model(self):
        half_model = SplashCaseCreatorIO.get_input_bool("Half Model (y/N)?: ")
        if half_model==True:
            self.halfModel = True
            self.meshSettings['halfModel'] = True
            # if the model is half, the back patch should be symmetry
            SplashCaseCreatorPrimitives.change_patch_type(self.meshSettings['patches'],patch_name='back'
                                                  ,new_type='symmetry')
        else:
            self.halfModel = False
            self.meshSettings['halfModel'] = False

    def get_domain_size(self):
        minx = self.meshSettings['domain']['minx']
        maxx = self.meshSettings['domain']['maxx']
        miny = self.meshSettings['domain']['miny']
        maxy = self.meshSettings['domain']['maxy']
        minz = self.meshSettings['domain']['minz']
        maxz = self.meshSettings['domain']['maxz']
        nx = self.meshSettings['domain']['nx']
        ny = self.meshSettings['domain']['ny']
        nz = self.meshSettings['domain']['nz']
        return minx,maxx,miny,maxy,minz,maxz,nx,ny,nz
    
    def get_mesh_size(self):
        dX = self.meshSettings['domain']['maxx'] - self.meshSettings['domain']['minx']
        dY = self.meshSettings['domain']['maxy'] - self.meshSettings['domain']['miny']
        dZ = self.meshSettings['domain']['maxz'] - self.meshSettings['domain']['minz']
        dX = dX/self.meshSettings['domain']['nx']
        dY = dY/self.meshSettings['domain']['ny']
        dZ = dZ/self.meshSettings['domain']['nz']
        return max(dX,dY,dZ)
    
    def set_mesh_size(self,dL=0.01):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = self.get_domain_size()
        dX = maxx - minx
        dY = maxy - miny
        dZ = maxz - minz
        nx = int(dX/dL)
        ny = int(dY/dL)
        nz = int(dZ/dL)
        # make sure the number of cells is at least 1 in every direction
        nx = max(nx,1)
        ny = max(ny,1)
        nz = max(nz,1)
        self.meshSettings['domain']['nx'] = nx
        self.meshSettings['domain']['ny'] = ny
        self.meshSettings['domain']['nz'] = nz

    def update_mesh_size(self,dL=0.01):
        self.meshSettings['maxCellSize'] = dL
        self.set_mesh_size(dL)
    
    def update_max_lengths(self):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = self.get_domain_size()
        self.lenX = maxx - minx
        self.lenY = maxy - miny
        self.lenZ = maxz - minz

    def set_max_domain_size(self,domain_size,nx,ny,nz):
        # self.minX = min(domain_size[0],self.minX)
        # self.maxX = max(domain_size[1],self.maxX)
        # self.minY = min(domain_size[2],self.minY)
        # self.maxY = max(domain_size[3],self.maxY)
        # self.minZ = min(domain_size[4],self.minZ)
        # self.maxZ = max(domain_size[5],self.maxZ)
        self.meshSettings['domain']['minx'] = domain_size[0]
        self.meshSettings['domain']['maxx'] = domain_size[1]
        self.meshSettings['domain']['miny'] = domain_size[2]
        self.meshSettings['domain']['maxy'] = domain_size[3]
        self.meshSettings['domain']['minz'] = domain_size[4]
        self.meshSettings['domain']['maxz'] = domain_size[5]

        self.meshSettings['domain']['nx'] = nx
        self.meshSettings['domain']['ny'] = ny
        self.meshSettings['domain']['nz'] = nz

    def update_max_stl_length(self,bounds):
        # update the characteristic length based on the bounding box of the stl files
        # the characteristic length is the maximum dimension of the bounding box
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        dx = xmax - xmin
        dy = ymax - ymin
        dz = zmax - zmin
        self.lenX = max(dx,self.lenX)
        self.lenY = max(dy,self.lenY)
        self.lenZ = max(dz,self.lenZ)
        
           
    def set_inlet_values(self):
        if(not self.internalFlow): # external flow
            U = SplashCaseCreatorDataInput.get_inlet_values()
            self.inletValues['U'] = U
            self.boundaryConditions['velocityInlet']['u_value'] = U
        else: # internal flow
            # Use inlet values from the stl file
            SplashCaseCreatorIO.printMessage("Setting inlet values for various inlet boundaries")
            for stl_file in self.stl_files:
                if stl_file['purpose'] == 'inlet':
                    U = list(stl_file['property'])
                    self.boundaryConditions['velocityInlet']['u_value'] = U
                    self.inletValues['U'] = U
        

    def set_fluid_properties(self):
        fluid = SplashCaseCreatorDataInput.choose_fluid_properties()
        if fluid == -1:
            rho, nu = SplashCaseCreatorDataInput.get_physical_properties()
            fluid = {'rho':rho, 'nu':nu}
        self.physicalProperties['rho'] = fluid['rho']
        self.physicalProperties['nu'] = fluid['nu']

    #def set_transient(self):
    #    self.transient = SplashCaseCreatorIO.get_input_bool("Transient simulation (y/N)?: ")

    def set_parallel(self):
        n_core = SplashCaseCreatorIO.get_input_int("Number of cores for parallel simulation: ")
        self.parallelSettings['numberOfSubdomains'] = n_core

    # setting the purpose of a patch. Used for setting the boundary conditions
    def set_purpose(self,patch,purpose='wall'):
        purposes = ['wall', 'inlet','outlet', 'refinementRegion', 'refinementSurface', 
                    'cellZone', 'baffles','symmetry','cyclic','empty',]
        #purposes = ['wall', 'inlet','outlet', 'refinementRegion', 'refinementSurface', 'cellZone', 'baffles']
        if purpose not in purposes:
            SplashCaseCreatorIO.printMessage("Invalid purpose. Setting purpose to wall")
            purpose = 'wall'
        patch['purpose'] = purpose

    # choose turbulence model for the simulation
    def choose_turbulence_model(self):
        turbulence_models = ['kOmegaSST', 'kEpsilon', 'SpalartAllmaras']
        turbulence_model = SplashCaseCreatorDataInput.get_option_choice("Choose turbulence model: ", turbulence_models)
        self.solverSettings['turbulenceModel'] = turbulence_model

    # set the turbulence model for the simulation
    def set_turbulence_model(self,turbulence_model='kOmegaSST'):
        turbulence_model = SplashCaseCreatorDataInput.choose_turbulence_model()
        self.solverSettings['turbulenceModel'] = turbulence_model
    
    def ask_transient_settings(self):
        self.simulationSettings['endTime'] = SplashCaseCreatorIO.get_input_float("End time: ")
        self.simulationSettings['writeInterval'] = SplashCaseCreatorIO.get_input_float("Write interval: ")
        self.simulationSettings['deltaT'] = SplashCaseCreatorIO.get_input_float("Time step: ")
    
    def set_transient_settings(self):
        #self.ask_transient()
        if self.transient:
            SplashCaseCreatorIO.printMessage("Transient simulation settings")
            self.simulationSettings['transient'] = True
            self.simulationSettings['application'] = 'pimpleFoam'
            self.simulationFlowSettings['solver'] = 'pimpleFoam'
            if not self.GUIMode:
                self.ask_transient_settings()
            else:
                pass
                #self.simulationSettings['endTime'] = SplashCaseCreatorIO.get_input_float("End time: ")
                #self.simulationSettings['writeInterval'] = SplashCaseCreatorIO.get_input_float("Write interval: ")
                #self.simulationSettings['deltaT'] = SplashCaseCreatorIO.get_input_float("Time step: ")
            self.simulationSettings['adjustTimeStep'] = 'no'
            self.simulationSettings['maxCo'] = 0.9
            self.simulationSettings['endTime'] = 10.0
            self.simulationSettings['writeInterval'] = 0.1
            self.simulationSettings['deltaT'] = 0.01
            #self.numericalSettings['ddtSchemes']['default'] = 'Euler'
            # if steady state, SIMPLEC is used. If transient, PIMPLE is used
            # for PIMPLE, the relaxation factors are set to 0.7 and p = 0.3
            self.numericalSettings['relaxationFactors']['p'] = 0.3
        else:  
            self.simulationSettings['transient'] = False
            self.simulationSettings['application'] = 'simpleFoam'
            self.simulationFlowSettings['solver'] = 'simpleFoam'
            self.simulationSettings['endTime'] = 1000
            self.simulationSettings['writeInterval'] = 100
            self.simulationSettings['deltaT'] = 1
            self.simulationSettings['adjustTimeStep'] = 'no'
            self.simulationSettings['maxCo'] = 0.9
            

    def ask_ground_type(self):
        ground_type = SplashCaseCreatorIO.get_input_bool("Is the ground touching the body (y/N): ")
        if ground_type:
            self.onGround = True
            self.meshSettings['onGround'] = True
            SplashCaseCreatorPrimitives.change_patch_type(self.meshSettings['patches'],patch_name='ground',
                                                    new_type='wall')
        else:
            self.onGround = False
            self.meshSettings['onGround'] = False

    def ask_refinement_level(self):
        self.refinement = SplashCaseCreatorDataInput.get_mesh_refinement_level()
        self.meshSettings['fineLevel'] = self.refinement

    def set_global_refinement_level(self,refinement=0):
        self.refinement = refinement
        self.meshSettings['fineLevel'] = refinement


    def set_post_process_settings(self):
        if self.useFOs:
            self.postProcessSettings['FOs'] = True
        meshPoint = list(self.meshSettings['castellatedMeshControls']['locationInMesh'])
        self.postProcessSettings['massFlow'] = True
        self.postProcessSettings['minMax'] = True
        self.postProcessSettings['yPlus'] = True
        self.postProcessSettings['forces'] = True
        # the default probe location for monitoring of flow variables
        self.postProcessSettings['probeLocations'].append(meshPoint)

    def get_probe_location(self):
        point = postProcess.get_probe_location()
        # for internal flows, the point should be inside stl
        # for external flows, the point should be outside stl
        # TO DO
        self.postProcessSettings['probeLocations'].append(point)
     


def main():
    project = SplashCaseCreatorProject()
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    SplashCaseCreatorIO.printMessage(get_SplashCaseCreator_header())
    project.set_project_directory(SplashCaseCreatorPrimitives.ask_for_directory())
    project_name = SplashCaseCreatorIO.get_input("Enter the project name: ")
    project.set_project_name(project_name)
    #user_name = input("Enter the user name: ")
    #project.set_user_name(user_name)
    project.create_project_path()
    SplashCaseCreatorIO.printMessage("Creating the project")
    SplashCaseCreatorIO.printMessage(f"Project path: {project.project_path}")
    #project.project_path = r"C:\Users\Ridwa\Desktop\CFD\SplashCaseCreatorTests\drivAer2"
    project.create_project()
    project.create_settings()
    yN = SplashCaseCreatorIO.get_input("Add STL file to the project (y/N)?: ")
    while yN.lower() == 'y':
        project.add_stl_file()
        yN = SplashCaseCreatorIO.get_input("Add another STL file to the project (y/N)?: ")
    #project.add_stl_to_project()
    # Before creating the project files, the settings are flushed to the project_settings.yaml file
    project.list_stl_files()
    project.ask_flow_type()
    if(project.internalFlow!=True):
        project.ask_ground_type()
    if(len(project.stl_files)>0):
        project.analyze_stl_file()

    #project.analyze_stl_file()
    project.write_settings()
    project.create_project_files()

if __name__ == '__main__':
    # Specify the output YAML file
    try:
        main()
    except KeyboardInterrupt:
        SplashCaseCreatorIO.printMessage("\nKeyboardInterrupt detected! Aborting project creation")
        exit()
    except Exception as error:
        SplashCaseCreatorIO.printError(error)
        exit()
