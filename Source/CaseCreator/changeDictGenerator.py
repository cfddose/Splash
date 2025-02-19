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

# This file generates the changeDict file for the case

from primitives import SplashCaseCreatorIO
import os
from primitives import SplashCaseCreatorPrimitives

def generateForOnePatch(patch="inlet",patch_type="patch"):
    output = f""
    output += f"    {patch}\n"
    output += f"    {{\n"
    output += f"        type            {patch_type};\n"
    output += f"        inGroups        {patch_type};\n"
    output += f"     }}\n"
    return output


def generate_ChangeDictionaryDict(meshSettings):
    changeDict = f""
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="dictionary", objectName="changeDictionaryDict")
    changeDict += header
    changeDict += f"\nboundary\n{{"
    if(meshSettings['internalFlow'] == False):
        for patch in meshSettings['patches']:
            changeDict += generateForOnePatch(patch["name"], patch_type=patch["type"])
    for patch in meshSettings['geometry']:
        if(patch['type'] == 'triSurfaceMesh'):
            changeDict += generateForOnePatch(patch["name"], patch_type=patch["type"])
    changeDict += f"\n}}"
    return changeDict

def writeChangeDictionaryDict(meshSettings):
    changeDict = generateChangeDictionaryDict(meshSettings)
    SplashCaseCreatorPrimitives.write_to_file("changeDictionaryDict", changeDict)




