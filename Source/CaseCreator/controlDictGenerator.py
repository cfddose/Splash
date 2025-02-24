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

from constants import meshSettings, physicalProperties, numericalSettings, inletValues, boundaryConditions
from primitives import SplashCaseCreatorPrimitives
from constants import simulationSettings

def generate_ControlDict(simulationSettings):
    controlDict = SplashCaseCreatorPrimitives.createFoamHeader(className='dictionary', objectName='controlDict')
    controlDict += f"""
application     {simulationSettings['application']};
startFrom       {simulationSettings['startFrom']};
startTime       {simulationSettings['startTime']};
stopAt          {simulationSettings['stopAt']};
endTime         {simulationSettings['endTime']};
deltaT          {simulationSettings['deltaT']};
writeControl    {simulationSettings['writeControl']};
writeInterval   {simulationSettings['writeInterval']};
purgeWrite      {simulationSettings['purgeWrite']};
writeFormat     {simulationSettings['writeFormat']};
writePrecision  {simulationSettings['writePrecision']};
writeCompression {simulationSettings['writeCompression']};
timeFormat      {simulationSettings['timeFormat']};
timePrecision   {simulationSettings['timePrecision']};
runTimeModifiable {simulationSettings['runTimeModifiable']};
adjustTimeStep  {simulationSettings['adjustTimeStep']};
maxCo           {simulationSettings['maxCo']};
functions
{{
    #include "FOs"
}};
libs
(
);
"""
    return controlDict


# Generate controlDict
if __name__ == '__main__':
    controlDict = createControlDict(simulationSettings)
    print(controlDict)