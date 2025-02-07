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
from constants import meshSettings, boundaryConditions, inletValues
from stlAnalysis import stlAnalysis

def write_vector_boundary_condition(patch="inlet1", purpose="inlet", property=None):
    """
    Write a vector boundary condition 
    """
    if property is None:
        property = [0, 0, 0]
    #else:
    #    property = [str(property[0]), str(property[1]), str(property[2])]
    bc = f"""
    {patch} 
    {{"""
    # if the purpose is an inlet, then the velocity is specified
    if purpose == "inlet":
        # write the velocity
        bc += f"""
        type            fixedValue;
        value           uniform ({property[0]} {property[1]} {property[2]});"""
    # if the purpose is an outlet, give an inletOutlet boundary condition
    elif purpose == "outlet":
        # write the pressure
        bc += f"""
        type            inletOutlet;
        inletValue      uniform ({property[0]} {property[1]} {property[2]});
        value           uniform ({property[0]} {property[1]} {property[2]});"""
    # if the purpose is a wall, give a fixedValue boundary condition
    elif purpose == "wall":
        bc += f"""
        type            fixedValue;
        value           uniform (0 0 0);"""
    # if the purpose is a symmetry, give a symmetry boundary condition
    elif purpose == "symmetry":
        bc += f"""
        type            symmetry;"""
    else:
        raise ValueError("Invalid boundary condition type")
    bc += f"""
    }}\n"""
    return bc

def create_scalar_file(meshSettings,boundaryConditions,scalarName="k",dimensions=(0,2,-2)):
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="volScalarField", objectName=scalarName)
    dims = SplashCaseCreatorPrimitives.createDimensions(M=dimensions[0],L=dimensions[1],T=dimensions[2])
    internalField = SplashCaseCreatorPrimitives.createInternalFieldScalar(type="uniform", value=0.0)
    s_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""

    if(meshSettings['internalFlow'] == False):
        for boundary_patch in meshSettings['patches']:
            if(scalarName == "k" or scalarName == "epsilon" or scalarName == "omega" or scalarName == "nuTilda"):
                s_file += write_turbulence_boundary_condition(patch=boundary_patch['name'], purpose=boundary_patch['purpose'], property=boundary_patch['property'])
            elif(scalarName == "p"):
                s_file += write_pressure_boundary_condition(patch=boundary_patch['name'], purpose=boundary_patch['purpose'], property=boundary_patch['property'])
            else:
                raise ValueError("Invalid scalar field type")
    # If internal flow, set the boundary conditions for STL patches
    for patch in meshSettings['geometry']:
        
        if(patch['type'] == 'triSurfaceMesh'):
            if(scalarName == "k" or scalarName == "epsilon" or scalarName == "omega" or scalarName == "nuTilda"):
                s_file += write_turbulence_boundary_condition(patch=patch["name"], purpose=patch['purpose'], property=patch['property'])
            elif(scalarName == "p"):
                s_file += write_pressure_boundary_condition(patch=patch["name"], purpose=patch['purpose'], property=patch['property'])
            else:
                raise ValueError("Invalid scalar field type")        
    s_file += """
}"""
    return s_file

def write_turbulence_boundary_condition(patch="inlet1", purpose="inlet", 
                                    property=None, wallFunction="kqRWallFunction"):
    """
    Write a scalar boundary condition
    """
    bc = f"""
    {patch} 
    {{"""
    # if the purpose is an inlet, then the fixedValue is specified
    if purpose == "inlet":
        # write the velocity
        bc += f"""
        type            fixedValue;
        value           uniform {property};"""
    # if the purpose is an outlet, give an inletOutlet boundary condition
    elif purpose == "outlet":
        # write the pressure
        bc += f"""
        type            inletOutlet;
        inletValue      uniform 1e-6;
        value           uniform 1e-6;"""
    # if the purpose is a wall, give a fixedValue boundary condition
    elif purpose == "wall":
        bc += f"""
        type            {wallFunction};
        value           $internalField;"""
    # if the purpose is a symmetry, give a symmetry boundary condition
    elif purpose == "symmetry":
        bc += f"""
        type            symmetry;"""
    else:
        raise ValueError("Invalid boundary condition type")
    bc += f"""
    }}\n"""
    return bc

def write_pressure_boundary_condition(patch="inlet1", purpose="inlet", 
                                    property=0.0):
    """
    Write a scalar boundary condition
    """
    bc = f"""
    {patch} 
    {{"""
    # if the purpose is an inlet, then the fixedValue is specified
    if purpose == "inlet":
        # write the velocity
        bc += f"""
        type            zeroGradient;"""
    # if the purpose is an outlet, give an inletOutlet boundary condition
    elif purpose == "outlet":
        # write the pressure
        if property is None:
            property = 0.0
        bc += f"""
        type            fixedValue;
        value           uniform {property};""" # to define reference pressure
    # if the purpose is a wall, give a fixedValue boundary condition
    elif purpose == "wall":
        bc += f"""
        type            zeroGradient;"""
    # if the purpose is a symmetry, give a symmetry boundary condition
    elif purpose == "symmetry":
        bc += f"""
        type            symmetry;"""
    else:
        raise ValueError("Invalid boundary condition type")
    bc += f"""
    }}\n"""
    return bc


def create_u_file(meshSettings,boundaryConditions):
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="volVectorField", objectName="U")
    dims = SplashCaseCreatorPrimitives.createDimensions(M=0,L=1,T=-1)
    internalField = SplashCaseCreatorPrimitives.createInternalFieldVector(type="uniform", value=boundaryConditions['velocityInlet']['u_value'])
    U_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""

    if(meshSettings['internalFlow'] == False):
        for boundary_patch in meshSettings['patches']:
            U_file += write_vector_boundary_condition(patch=boundary_patch['name'], purpose=boundary_patch['purpose'], property=boundary_patch['property'])
       
    # If internal flow, set the boundary conditions for STL patches
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            U_file += write_vector_boundary_condition(patch=patch['name'], purpose=patch['purpose'], property=patch['property'])
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
    epsilon_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="epsilon",dimensions=(0,2,-2))
    return epsilon_file

def create_omega_file(meshSettings,boundaryConditions):
    omega_file = create_scalar_file(meshSettings,boundaryConditions,scalarName="omega",dimensions=(0,2,-2))
    return omega_file

def create_nut_file(meshSettings,boundaryConditions=None):
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="volScalarField", objectName="nut")
    dims = SplashCaseCreatorPrimitives.createDimensions(M=0,L=2,T=-1)
    internalField = SplashCaseCreatorPrimitives.createInternalFieldScalar(type="calculated", value=0.0)
    nut_file = f""+header+dims+internalField+"\n"+"""\nboundaryField 
{"""

    if(meshSettings['internalFlow'] == False):
        for boundary_patch in meshSettings['patches']:
            if(boundary_patch['purpose'] == 'wall'):
                nut_file += write_turbulence_boundary_condition(patch=boundary_patch['name'], purpose=boundary_patch['purpose'], property=boundary_patch['property'], wallFunction="nutkWallFunction")
            else:
                # Need more detailed check
                nut_file += write_turbulence_boundary_condition(patch=boundary_patch['name'], purpose=boundary_patch['purpose'], property=boundary_patch['property'])
    # If internal flow, set the boundary conditions for STL patches
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            nut_file += write_turbulence_boundary_condition(patch=patch['name'], purpose=patch['purpose'], property=patch['property'], wallFunction="nutkWallFunction")
    nut_file += """
}"""
    return nut_file

def update_boundary_conditions(boundaryConditions, inletValues):
    """
    Update boundary conditions with inlet values.

    Parameters:
    boundaryConditions (dict): Dictionary specifying boundary conditions for U, p, k, and omega.
    inletValues (dict): Dictionary specifying inlet values for U, p, k, and omega.
    """
    boundaryConditions['velocityInlet']['u_value'] = inletValues['U']
    boundaryConditions['velocityInlet']['p_value'] = inletValues['p']
    boundaryConditions['velocityInlet']['k_value'] = inletValues['k']
    boundaryConditions['velocityInlet']['omega_value'] = inletValues['omega']
    boundaryConditions['velocityInlet']['epsilon_value'] = inletValues['epsilon']
    boundaryConditions['velocityInlet']['nut_value'] = inletValues['nut']
    return boundaryConditions

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
    #print(p_file)
    #print(u_file)
    #print("Creating boundary conditions files")
    SplashCaseCreatorPrimitives.write_to_file("U", u_file)
   
    SplashCaseCreatorPrimitives.write_to_file("p", p_file)
    
    SplashCaseCreatorPrimitives.write_to_file("k", k_file)
   
    SplashCaseCreatorPrimitives.write_to_file("omega", omega_file)

    SplashCaseCreatorPrimitives.write_to_file("epsilon", epsilon_file)

    SplashCaseCreatorPrimitives.write_to_file("nut", nut_file)