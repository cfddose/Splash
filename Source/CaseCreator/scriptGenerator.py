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

import os
import sys

class ScriptGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate_mesh_script(simulationFlowSettings):
        cmdMesh = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        if(simulationFlowSettings['parallel']):
            cmdMesh += f"""
foamCleanTutorials
#cp -r 0 0.orig
rm -rf log.*
runApplication blockMesh
touch case.foam
runApplication surfaceFeatureExtract
runApplication decomposePar -force
runParallel snappyHexMesh -overwrite
runApplication reconstructParMesh -constant -latestTime
runApplication changeDictionary 
#rm -rf processor*
#rm log.decomposePar
#runApplication decomposePar -force
"""
        else:
            cmdMesh += f"""
runApplication blockMesh
touch case.foam
runApplication surfaceFeatureExtract
runApplication snappyHexMesh -overwrite
    """
        return cmdMesh

    # Generate run script for incompressible flow simulations (simpleFoam, pimpleFoam, etc.)
    @staticmethod
    def generate_simulation_script(simulationFlowSettings):
        cmdSimulation = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        if(simulationFlowSettings['parallel']):
            cmdSimulation += f"""
#rm -rf 0
#cp -r 0.orig 0
rm -rf log.decomposePar log.simpleFoam log.pimpleFoam log.reconstructParMesh log.potentialFoam log.renumberMesh
runApplication decomposePar -force
touch case.foam
runParallel renumberMesh -overwrite
"""
            if(simulationFlowSettings['potentialFoam']):
                cmdSimulation += f"""
runParallel potentialFoam
runParallel {simulationFlowSettings['solver']}
"""
            else:
                cmdSimulation += f"""
runParallel {simulationFlowSettings['solver']}
"""
            
        else:
            if simulationFlowSettings['potentialFoam']:
                cmdSimulation += f"""
runApplication potentialFoam
runApplication {simulationFlowSettings['solver']}
"""
            else:
                cmdSimulation += f"""   
runApplication {simulationFlowSettings['solver']}
"""
        return cmdSimulation

    # Generate postprocessing script
    @staticmethod
    def generate_postprocessing_script(simulationFlowSettings):
        cmdPostProcessing = f"""#!/bin/sh
cd "${{0%/*}}" || exit                                # Run from this directory
. ${{WM_PROJECT_DIR:?}}/bin/tools/RunFunctions        # Tutorial run functions
#-----------------------------------------------------
"""
        if(simulationFlowSettings['parallel']):
            cmdPostProcessing += f"""
runParallel {simulationFlowSettings['solver']} -postProcess
"""
        else:
            cmdPostProcessing += f"""
runApplication {simulationFlowSettings['solver']} -postProcess
"""
        return cmdPostProcessing
    
    