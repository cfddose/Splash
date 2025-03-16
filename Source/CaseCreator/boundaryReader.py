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

# This file reads the boundary file and extracts the boundary patches

from primitives import SplashCaseCreatorIO
import os

def check_boundary_file(boundary_file="constant/polyMesh/boundary"):
    # check if the boundary file exists
    if not os.path.exists(boundary_file):
        SplashCaseCreatorIO.printError(f"Boundary file {boundary_file} does not exist")
        return False
    return True

def read_boundary(boundary_file="constant/polyMesh/boundary"):
    if not check_boundary_file(boundary_file):
        return -1
    def get_boundary_patches(boundary_file):
        with open(boundary_file) as f:
            lines = f.readlines()
            
        nPatches = None
        in_boundary = False
        boundary_patches = {}
        current_patch = None
        
        for line in lines:
            data = line.strip()
            # check if the data is a number
            try:
                # if there is only one word in the line, 
                # probably it is the number of patches
                if len(data.split()) == 1:
                    nPatches = int(data[0])
                #continue
            except:
                if len(data.split()) == 1 and data != "(" and data != ")" and data != "{" and data != "}":
                    current_patch = data.split()[0]
            if data == "":
                continue
            if data == "(":
                in_boundary = True
                #continue
            if data == ")":
                in_boundary = False
                #continue
            if in_boundary:
                if "{" in data:
                    
                    boundary_patches[current_patch] = None
                elif "type" in data:
                    boundary_patches[current_patch] = data.split()[1].strip(";")
            #print(line)
        return boundary_patches

    patches = get_boundary_patches(boundary_file)
    return patches

def list_patches(boundary_patches):
    patchNames = boundary_patches.keys()
    SplashCaseCreatorIO.printMessage("Patch name\tType")
    SplashCaseCreatorIO.printMessage("---------\t----")
    for patch in patchNames:
        SplashCaseCreatorIO.printMessage(f"{patch}\t\t{boundary_patches[patch]}")

if __name__ == '__main__':
    boundary_file = "boundary"
    boundary_patches = read_boundary(boundary_file)
    list_patches(boundary_patches)
