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

from constants import numericalSettings, solverSettings
from primitives import SplashCaseCreatorPrimitives

def create_algorithmDict(numericalSettings):
    #header = SplashCaseCreatorPrimitives.createFoamHeader(className="dictionary", objectName="pimpleDict")
    algorithmDict = f""
    algorithmDict += f"""
PIMPLE
{{
    nOuterCorrectors {numericalSettings['pimpleDict']['nOuterCorrectors']};
    nCorrectors {numericalSettings['pimpleDict']['nCorrectors']};
    nNonOrthogonalCorrectors {numericalSettings['pimpleDict']['nNonOrthogonalCorrectors']};
    pRefCell {numericalSettings['pimpleDict']['pRefCell']};
    pRefValue {numericalSettings['pimpleDict']['pRefValue']};
    residualControl
    {{
        "(U|k|omega|epsilon|nuTilda)" 
        {{
            tolerance {numericalSettings['pimpleDict']['residualControl']['U']};
            relTol 0;
        }}
        p
        {{
            tolerance {numericalSettings['pimpleDict']['residualControl']['p']};
            relTol 0;
        }}
    }}
}}
SIMPLE
{{
    nNonOrthogonalCorrectors {numericalSettings['simpleDict']['nNonOrthogonalCorrectors']};
    consistent {numericalSettings['simpleDict']['consistent']};
    residualControl
    {{
        U {numericalSettings['simpleDict']['residualControl']['U']};
        p {numericalSettings['simpleDict']['residualControl']['p']};
        k {numericalSettings['simpleDict']['residualControl']['k']};
        omega {numericalSettings['simpleDict']['residualControl']['omega']};
        epsilon {numericalSettings['simpleDict']['residualControl']['epsilon']};
        nuTilda {numericalSettings['simpleDict']['residualControl']['nuTilda']};
    }}
}}
potentialFlow
{{
    nNonOrthogonalCorrectors {numericalSettings['potentialFlowDict']['nonOrthogonalCorrectors']};
}}
relaxationFactors
{{
    equations
    {{
        U {numericalSettings['relaxationFactors']['U']};
        
        k {numericalSettings['relaxationFactors']['k']};
        omega {numericalSettings['relaxationFactors']['omega']};
        epsilon {numericalSettings['relaxationFactors']['epsilon']};
        nuTilda {numericalSettings['relaxationFactors']['nuTilda']};
    }}
    fields
    {{
        p {numericalSettings['relaxationFactors']['p']};
    }}
}}
"""
    return algorithmDict

def create_solverDict(solverSettings,solverName="U"):
    
    solverDict = f""
    if(solverName=="p" or solverName=="Phi" or solverName=="p_rgh"):
        solverDict += f"""
{solverName}
{{
    solver {solverSettings[solverName]['type']};
    smoother {solverSettings[solverName]['smoother']};
    
    agglomerator {solverSettings[solverName]['agglomerator']};
    nCellsInCoarsestLevel {solverSettings[solverName]['nCellsInCoarsestLevel']};
    mergeLevels {solverSettings[solverName]['mergeLevels']};
    cacheAgglomeration {solverSettings[solverName]['cacheAgglomeration']};
    tolerance {solverSettings[solverName]['tolerance']};
    relTol {solverSettings[solverName]['relTol']};
    maxIter {solverSettings[solverName]['maxIter']};
    nSweeps {solverSettings[solverName]['nSweeps']};
    nPreSweeps {solverSettings[solverName]['nPreSweeps']};
}}
"""
    else:
        solverDict += f"""
{solverName}
{{
    solver {solverSettings[solverName]['type']};
    smoother {solverSettings[solverName]['smoother']};
    tolerance {solverSettings[solverName]['tolerance']};
    relTol {solverSettings[solverName]['relTol']};
    maxIter 100;
}}
"""
    return solverDict

def create_solverFinalDict(solverSettings,solverName="U"):
    
    solverDict = f""
    solverDict += f"""
{solverName}Final
{{
    ${solverName}
    tolerance {solverSettings[solverName]['tolerance']/100.};
    relTol 0;  
}}
"""
    return solverDict

def create_fvSolutionDict(numericalSettings,solverSettings):
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="dictionary", objectName="fvSolution")
    fvSolutionDict = f""+header
    fvSolutionDict += f"""
solvers
{{
    """
    for solver in solverSettings.keys():
        fvSolutionDict += create_solverDict(solverSettings,solver)
        fvSolutionDict += create_solverFinalDict(solverSettings,solver)
    fvSolutionDict += f"""
}}
    """
    fvSolutionDict += create_algorithmDict(numericalSettings)
    return fvSolutionDict

def create_fvSchemesDict(numericalSettings):
    header = SplashCaseCreatorPrimitives.createFoamHeader(className="dictionary", objectName="fvSchemes")
    fvSchemesDict = f""+header
    fvSchemesDict += f"""
ddtSchemes
{{
    default {numericalSettings['ddtSchemes']['default']};
}}
gradSchemes
{{
    default {numericalSettings['gradSchemes']['default']};
    grad(p) {numericalSettings['gradSchemes']['grad(p)']};
    grad(U) {numericalSettings['gradSchemes']['grad(U)']};
}}
divSchemes
{{
    default {numericalSettings['divSchemes']['default']};
    div(phi,U) {numericalSettings['divSchemes']['div(phi,U)']}; 
    div(phi,k) {numericalSettings['divSchemes']['div(phi,k)']};
    div(phi,omega) {numericalSettings['divSchemes']['div(phi,omega)']};
    div(phi,epsilon) {numericalSettings['divSchemes']['div(phi,epsilon)']};
    div(phi,nuTilda) {numericalSettings['divSchemes']['div(phi,nuTilda)']};
    div(nuEff*dev(T(grad(U)))) {numericalSettings['divSchemes']['div(nuEff*dev(T(grad(U))))']};
}}
laplacianSchemes
{{
    default {numericalSettings['laplacianSchemes']['default']};
}}
interpolationSchemes
{{
    default {numericalSettings['interpolationSchemes']['default']};
}}
snGradSchemes
{{
    default {numericalSettings['snGradSchemes']['default']};
}}
fluxRequired
{{
    default {numericalSettings['fluxRequired']['default']};
}}
wallDist
{{
    method {numericalSettings['wallDist']};
}}
"""
    return fvSchemesDict

