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

# This script generates the boundary conditions files for an OpenFOAM pimpleFoam simulation.
# The boundary conditions are specified in the meshSettings.yaml file.
# This is an early version of the script and will be updated in the future.
# Brute force writing is used instead of a more elegant solution.
#import yaml
from primitives import SplashCaseCreatorPrimitives, SplashCaseCreatorIO
from database import boundary_conditions_scalars as SCALARS
#from constants import meshSettings, boundaryConditions
#from stlAnalysis import stlAnalysis
import copy
import os

def find_patch(patchName, meshSettings):
    """
    Find a patch in meshSettings.

    Parameters:
    patchName (str): Name of the patch.
    meshSettings (dict): Dictionary specifying mesh settings.
    """
    # Check whether the patch name is inside the boundary conditions
    patchFound = False
    # for added stl patches
    for patch in meshSettings['geometry']:
        if patch['name'] == patchName:
            patchFound = True
            break
    # for domain boundary patches
    for patch in meshSettings['patches']:
        if patch['name'] == patchName:
            patchFound = True
            break
    return patchFound

def write_vector_boundary_condition(boundaryConditions,meshSettings,patch="inlet1",):
    patchFound = find_patch(patch, meshSettings)
    if patchFound == False:
        raise ValueError("Patch name not found in boundary conditions")
    if '.stl' in patch:
        patchName = patch.replace('.stl','')
    bc = f"""
    {patchName} 
    {{"""
    if boundaryConditions[patch]['u_type'] == "fixedValue":
        bc += f"""
        type            {boundaryConditions[patch]['u_type']};
        value           uniform ({boundaryConditions[patch]['u_value'][0]} {boundaryConditions[patch]['u_value'][1]} {boundaryConditions[patch]['u_value'][2]});"""
    elif boundaryConditions[patch]['u_type'] == "surfaceNormalFixedValue": # this is for the inlets with normal velocity
        bc += f"""
        type            {boundaryConditions[patch]['u_type']};
        value           uniform (0 0 0);
        refValue        uniform ({boundaryConditions[patch]['u_value']});"""
    elif boundaryConditions[patch]['u_type'] == "inletOutlet":
        bc += f"""
        type            {boundaryConditions[patch]['u_type']};
        inletValue      uniform ({boundaryConditions[patch]['u_value'][0]} {boundaryConditions[patch]['u_value'][1]} {boundaryConditions[patch]['u_value'][2]});
        value           uniform ({boundaryConditions[patch]['u_value'][0]} {boundaryConditions[patch]['u_value'][1]} {boundaryConditions[patch]['u_value'][2]});"""
    elif boundaryConditions[patch]['u_type'] == "zeroGradient":
        bc += f"""
        type            {boundaryConditions[patch]['u_type']};"""
    elif boundaryConditions[patch]['u_type'] == "symmetry":
        bc += f"""
        type            {boundaryConditions[patch]['u_type']};"""
    else:
        pass # dont write anything. We rely on default values
    bc += f"""
    }}\n"""
    return bc

def write_scalar_boundary_condition(boundaryConditions,meshSettings,patch="inlet1",scalarName="k"):
    """
    Write a scalar boundary condition
    """
    patchFound = find_patch(patch, meshSettings)
    if patchFound == False:
        raise ValueError("Patch name not found in boundary conditions")
    if '.stl' in patch:
        patchName = patch.replace('.stl','')
    scalar_type = scalarName+"_type"
    scalar_value = scalarName+"_value"
    bc = f"""
    {patchName} 
    {{"""
    if boundaryConditions[patch][scalar_type] == "inletOutlet":
        bc += f"""
        type            {boundaryConditions[patch][scalar_type]};
        inletValue      uniform {boundaryConditions[patch][scalar_value]};
        value           uniform {boundaryConditions[patch][scalar_value]};"""
    elif boundaryConditions[patch][scalar_type] == "zeroGradient":
        bc += f"""
        type            {boundaryConditions[patch][scalar_type]};"""
    elif boundaryConditions[patch][scalar_type] == "symmetry":
        bc += f"""
        type            {boundaryConditions[patch][scalar_type]};"""
    else:
        # to deal with the case where the boundary condition is specified as $internalField
        if boundaryConditions[patch][scalar_value] == '$internalField':
            bc += f"""
        type            {boundaryConditions[patch][scalar_type]};
        value           $internalField;"""
        else:
            bc += f"""
        type            {boundaryConditions[patch][scalar_type]};
        value           uniform {boundaryConditions[patch][scalar_value]};"""
    bc += f"""
    }}\n"""
    return bc

# Assign boundary condition for a given patch and assign initial conditions.
# These conditions can be modified later.
# This can be used to change the boundary conditions for a specific patch.
def assign_boundary_condition(boundaryConditions,meshSettings, patchName='inlet', purpose="inlet"):
    # Check whether the patch name is inside the boundary conditions
    patchFound = find_patch(patchName, meshSettings)

    # If the patch name is not found in STL list nor in the domain boundary patches
    if patchFound == False:
        raise ValueError("Patch name not found in boundary conditions")
    # Change the boundary condition
    if purpose == "inlet":
        # copy the velocity inlet boundary conditions
        boundaryConditions[patchName] = copy.deepcopy(boundaryConditions['velocityInlet'])
    elif purpose == "outlet":
        # copy the pressure outlet boundary conditions
        boundaryConditions[patchName] = copy.deepcopy(boundaryConditions['pressureOutlet'])
    elif purpose == "wall":
        # copy the wall boundary conditions
        boundaryConditions[patchName] = copy.deepcopy(boundaryConditions['wall'])
    elif purpose == "symmetry":
        # copy the symmetry boundary conditions
        boundaryConditions[patchName] = copy.deepcopy(boundaryConditions['symmetry'])
    elif purpose == "empty":
        boundaryConditions[patchName] = copy.deepcopy(boundaryConditions['empty'])
    else:
        #raise ValueError("Invalid boundary condition type")
        print("Invalid boundary condition type found (Example: cyclic, symmetryPlane)")
        pass
    return boundaryConditions

def assign_boundary_value_vector(boundaryConditions,meshSettings, patchName='inlet', value=[1,0,0]):
    patchFound = find_patch(patchName, meshSettings)
    if patchFound == False:
        raise ValueError("Patch name not found in boundary conditions")
    boundaryConditions[patchName]['u_value'] = value
    return boundaryConditions

def assign_boundary_value_scalar(boundaryConditions,meshSettings, patchName='inlet',value_type='p_value', value=0.0):
    patchFound = find_patch(patchName, meshSettings)
    if patchFound == False:
        raise ValueError("Patch name not found in boundary conditions")
    boundaryConditions[patchName][value_type] = value
    return boundaryConditions
    
def assign_initial_boundary_conditions(meshSettings, boundaryConditions):
    """
    Assign boundary conditions to patches in meshSettings.

    Parameters:
    meshSettings (dict): Dictionary specifying mesh settings.
    boundaryConditions (dict): Dictionary specifying boundary conditions for U, p, k, and omega.
    """
    #patchFound = False
    for patch in meshSettings['patches']:
        patchName = patch['name']
        purpose = patch['purpose']
        boundaryConditions = assign_boundary_condition(boundaryConditions, patchName, purpose)
    return boundaryConditions

def create_scalar_file(meshSettings,boundaryConditions,scalarName="k",dimensions=(0,2,-2)):
    scalarName = scalarName.lower()
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="volScalarField", objectName=scalarName)
    dims = SplashCaseCreatorPrimitives.createDimensions(M=dimensions[0],L=dimensions[1],T=dimensions[2])
    internalField = SplashCaseCreatorPrimitives.createInternalFieldScalar(type="uniform", value=1e-6)
    s_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""

    if(meshSettings['internalFlow'] == False):
        for boundary_patch in meshSettings['patches']:
            #scalarValue = boundaryConditions[boundary_patch['name']][scalarName+"_value"]
            if(scalarName in SCALARS):
                s_file += write_scalar_boundary_condition(boundaryConditions,meshSettings,patch=boundary_patch['name'],scalarName=scalarName)
            else:
                raise ValueError("Invalid scalar field type")
    # If internal flow, set the boundary conditions for STL patches
    for patch in meshSettings['geometry']:
        if patch['purpose'] != 'wall' and patch['purpose'] != 'inlet' and patch['purpose'] != 'outlet':
            continue
        if(patch['type'] == 'triSurfaceMesh'):
            if(scalarName in SCALARS):
                s_file += write_scalar_boundary_condition(boundaryConditions,meshSettings,patch=patch['name'],scalarName=scalarName)
            else:
                raise ValueError("Invalid scalar field type")      
    s_file += """
}"""
    return s_file


def create_u_file(meshSettings,boundaryConditions):
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="volVectorField", objectName="U")
    dims = SplashCaseCreatorPrimitives.createDimensions(M=0,L=1,T=-1)
    internalField = SplashCaseCreatorPrimitives.createInternalFieldVector(type="uniform", value=boundaryConditions['velocityInlet']['u_value'])
    U_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""

    if(meshSettings['internalFlow'] == False):
        for boundary_patch in meshSettings['patches']:
            U_file += write_vector_boundary_condition(boundaryConditions,meshSettings,patch=boundary_patch['name'])
       
    # If internal flow, set the boundary conditions for STL patches
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            U_file += write_vector_boundary_condition(boundaryConditions,meshSettings,patch=patch['name'])
    U_file += """
}"""
    return U_file


def create_p_file(meshSettings,boundaryConditions):
    p_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="p",dimensions=(0,2,-2))
    return p_file

def create_k_file(meshSettings,boundaryConditions):
    k_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="k",dimensions=(0,2,-2))
    return k_file

def create_epsilon_file(meshSettings,boundaryConditions):
    epsilon_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="epsilon",dimensions=(0,2,-3))
    return epsilon_file

def create_omega_file(meshSettings,boundaryConditions):
    omega_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="omega",dimensions=(0,0,-1))
    return omega_file

def create_nut_file(meshSettings,boundaryConditions=None):
    nut_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="nut",dimensions=(0,2,-1))
    return nut_file

def create_nuTiida_file(meshSettings,boundaryConditions=None):
    nut_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="nuTilda",dimensions=(0,2,-1))
    return nut_file


def create_boundary_conditions(meshSettings, boundaryConditions):
    """
    Create boundary condition files for an OpenFOAM pimpleFoam simulation.

    Parameters:
    meshSettings (dict): Dictionary specifying mesh settings.
    boundaryConditions (dict): Dictionary specifying boundary conditions for U, p, k, and omega.
    inletValues (dict): Dictionary specifying inlet values for U, p, k, and omega.
    """
    
    u_file = create_u_file(meshSettings, boundaryConditions)
    p_file = create_p_file(meshSettings, boundaryConditions)
    k_file = create_k_file(meshSettings, boundaryConditions)
    omega_file = create_omega_file(meshSettings, boundaryConditions)
    epsilon_file = create_epsilon_file(meshSettings, boundaryConditions)
    nut_file = create_nut_file(meshSettings, boundaryConditions)
    nuTilda_file = create_nuTiida_file(meshSettings,boundaryConditions)
    SplashCaseCreatorPrimitives.write_to_file("U", u_file)
    SplashCaseCreatorPrimitives.write_to_file("p", p_file)
    SplashCaseCreatorPrimitives.write_to_file("k", k_file)
    SplashCaseCreatorPrimitives.write_to_file("omega", omega_file)
    SplashCaseCreatorPrimitives.write_to_file("epsilon", epsilon_file)
    SplashCaseCreatorPrimitives.write_to_file("nut", nut_file)
    SplashCaseCreatorPrimitives.write_to_file("nuTilda", nuTilda_file)
    return

def main():
    settingsFile = "/Users/thawtar/Desktop/Work/03_Splash/02_Run/pipe/project_settings.yaml"
    # Load mesh settings from settings file
    project_settings = SplashCaseCreatorPrimitives.yaml_to_dict(settingsFile)
    #print(project_settings)
    if not os.path.exists("./testCaseFolder"):
        os.mkdir("./testCaseFolder")
    os.chdir("./testCaseFolder")
    print(f"Currrent working directory: {os.getcwd()}")
    # Update boundary conditions with inlet values
    #boundaryConditions = update_boundary_conditions(boundaryConditions, inletValues)
    # Create boundary conditions files
    create_boundary_conditions(project_settings['meshSettings'], project_settings['boundaryConditions'])
    return

if __name__ == "__main__":
    main()