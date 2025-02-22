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

"""
This file contains the dictionaries connecting the GUI text to the OpenFOAM dictionary entries.

"""
grad_schemes = {"Gauss Linear":"Gauss linear","Gauss Linear (Cell Limited)":"cellLimited Gauss linear 0.5",
                "Gauss Linear (Face Limited)":"faceLimited Gauss linear 1","Gauss Linear (Cell MD Limited)":"cellMDLimited Gauss linear 1",
                "Gauss Linear (Face MD Limited)":"faceMDLimited Gauss linear 1",
               "Least Squares":"leastSquares"}

div_schemes = {"Gauss Linear":"Gauss linear","Gauss Upwind":"Gauss upwind","Gauss Linear Upwind":"Gauss linearUpwind",
               "Gauss Limited Linear":"Gauss limitedLinear 1",}
temporal_schemes = {"Steady State":"steadyState","Euler":"Euler","Backward Euler (2nd Order)":"backward","Crank-Nicolson (Blended 2nd Order)":"crankNicolson 0.5","Crank-Nicolson (2nd Order)":"crankNicolson 1.0"}

laplacian_schemes = {"corrected ":"Gauss linear limited corrected 1","limited 0.333":"Gauss linear limited corrected 0.333",
                     "limited 0.5":"Gauss linear limited corrected 0.5","uncorrected":"Gauss linear limited corrected 0",}

snGrad_schemes = {"corrected ":"limited corrected 1","limited 0.333":"limited corrected 0.333",
                     "limited 0.5":"limited corrected 0.5","uncorrected":"limited corrected 0",}

boundary_conditions = {"Fixed Value":"fixedValue","Zero Gradient":"zeroGradient",
                        "Inlet Outlet":"inletOutlet",}
                          
def value_to_key(dict,value):
    """
    This function returns the key of a dictionary given a value.

    Args:
        dict: Dictionary to search.
        value: Value to search for.

    Returns:
        key: Key of the value in the dictionary.

    """
    for key in dict:
        if dict[key] == value:
            return key
    return None

def key_to_value(dict,key):
    """
    This function returns the value of a dictionary given a key.

    Args:
        dict: Dictionary to search.
        key: Key to search for.

    Returns:
        value: Value of the key in the dictionary.

    """
    return dict[key]
