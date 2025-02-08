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

import yaml
from primitives import SplashCaseCreatorPrimitives
from constants import meshSettings

def create_surfaceFeatureExtractDict(meshSettings):
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="dictionary", objectName="surfaceFeatureExtractDict")
    surfaceFeatureExtractDict = f""+header
    for anEntry in meshSettings['geometry']:
        if anEntry['type'] == 'triSurfaceMesh':
            surfaceFeature = f"""\n{anEntry['name']}
{{
    extractionMethod    extractFromSurface; 
    includedAngle   170;
    subsetFeatures
    {{
        nonManifoldEdges       no;
        openEdges       yes;
    }}
    writeObj            yes;
    writeSets           no;
}}"""
            surfaceFeatureExtractDict += surfaceFeature
    

    return surfaceFeatureExtractDict


if __name__ == "__main__":
    meshSettings = SplashCaseCreatorPrimitives.yaml_to_dict('meshSettings.yaml')
    surfaceFeatureExtractDict = create_surfaceFeatureExtractDict(meshSettings)
    #print(surfaceFeatureExtractDict)
    with open('surfaceFeatureExtractDict', 'w') as file:
        file.write(surfaceFeatureExtractDict)