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


# Default values for the constants used in the SplashCaseCreatorCFD library
meshSettings = {
    'name': 'meshSettings',
    'scale': 1.0,
    'domain': {'minx': -3.0,
        'maxx': 5.0,
        'miny': -1.0,
        'maxy': 1.0,
        'minz': 0.0,
        'maxz': 2.0,
        'nx': 50,
        'ny': 20,
        'nz': 20},
    'maxCellSize': 0.5,
    'fineLevel': 1,
    'internalFlow': False,
    'onGround': False,
    'halfModel': False,
    # patches are for the construction of the blockMeshDict
    'patches': [
        {'name': 'inlet', 'type': 'patch','faces': [0, 4, 7, 3],'purpose': 'inlet','property': (1,0,0)},
        {'name': 'outlet', 'type': 'patch','faces': [1, 5, 6, 2],'purpose': 'outlet','property': None},
        {'name': 'front', 'type': 'symmetry','faces': [0, 1, 5, 4],'purpose': 'symmetry','property': None},
        {'name': 'back', 'type': 'symmetry','faces': [2, 3, 7, 6],'purpose': 'symmetry','property': None},
        {'name': 'bottom', 'type': 'symmetry','faces': [0, 1, 2, 3],'purpose': 'symmetry','property': None},
        {'name': 'top', 'type': 'symmetry','faces': [4, 5, 6, 7],'purpose': 'symmetry','property': None},
    ],
    # bcPatches are for the boundary conditions and may be changed based on the case
    # 2025/1/23: added faces to the bcPatches 
    # 2025/2/7: bcPatches are completely removed from the meshSettings. Now everything uses patches instead.
#     'bcPatches': {
#         'inlet':    {'type': 'patch','purpose': 'inlet','property': (1,0,0),'faces': [0, 4, 7, 3]},
#         'outlet':   {'type': 'patch','purpose': 'outlet','property': None,'faces': [1, 5, 6, 2]},
#         'front':    {'type': 'symmetry','purpose': 'symmetry','property': None,'faces': [0, 1, 5, 4]},
#         'back':     {'type': 'symmetry','purpose': 'symmetry','property': None,'faces': [2, 3, 7, 6]},
#         'bottom':   {'type': 'symmetry','purpose': 'symmetry','property': None,'faces': [0, 1, 2, 3]},
#         'top':      {'type': 'symmetry','purpose': 'symmetry','property': None,'faces': [4, 5, 6, 7]},
# },
    'snappyHexSteps': {'castellatedMesh': True,
                       'snap': True,
                        'addLayers': True,},

    'geometry': [], #[{'name': 'stl1.stl','type':'triSurfaceMesh', 'refineMin': 1, 'refineMax': 3, 
                #     'featureEdges':'true','featureLevel':3,'nLayers':3},
                #{'name': 'box','type':'searchableBox', 'min': [0, 0, 0], 'max': [1, 1, 1]}],

    'castellatedMeshControls': {'maxLocalCells': 10_000_000,
                                'maxGlobalCells': 50_000_000,
                                'minRefinementCells': 10,
                                'maxLoadUnbalance': 0.10,
                                'nCellsBetweenLevels': 5,
                                'features': [],
                                'refinementSurfaces': [],
                                'resolveFeatureAngle': 25,
                                'refinementRegions': [],
                                'locationInMesh': [0, 0, 0],
                                'allowFreeStandingZoneFaces': 'false'},

    'snapControls': {'nSmoothPatch': 3,
                        'tolerance': 2.0,
                        'nSolveIter': 50,
                        'nRelaxIter': 5,
                        'nFeatureSnapIter': 10,
                        'implicitFeatureSnap': False,
                        'explicitFeatureSnap': True,
                        'multiRegionFeatureSnap': False,},

    'addLayersControls': {'relativeSizes': True,
                            'expansionRatio': 1.2,
                            'finalLayerThickness': 0.5,
                            'firstLayerThickness': 0.001,
                            'minThickness': 1e-7,
                            'nGrow': 0,
                            'featureAngle': 130,
                            'slipFeatureAngle': 30,
                            'nRelaxIter': 3,
                            'nSmoothSurfaceNormals': 1,
                            'nSmoothNormals': 3,
                            'nSmoothThickness': 10,
                            'maxFaceThicknessRatio': 0.5,
                            'maxThicknessToMedialRatio': 0.3,
                            'minMedianAxisAngle': 90,
                            'nBufferCellsNoExtrude': 0,
                            'nLayerIter': 50,
                            'nOuterIter': 1,
                            },

    'meshQualityControls': {'maxNonOrtho': 70,
                            'maxBoundarySkewness': 20,
                            'maxInternalSkewness': 4,
                            'maxConcave': 80,
                            'minTetQuality': 1.0e-30,
                            'minVol': 1e-30,
                            'minArea': 1e-30,
                            'minTwist': 0.001,
                            'minDeterminant': 0.001,
                            'minFaceWeight': 0.001,
                            'minVolRatio': 0.001,
                            'minTriangleTwist': -1,
                            'nSmoothScale': 4,
                            'errorReduction': 0.75},
    'mergeTolerance': 1e-6,
    'debug': 0,
}


physicalProperties = {
    'name': 'physicalProperties',
    'fluid': 'Air',
    'rho': 1.0,
    'nu': 1.0e-6,
    'g': [0, 0, -9.81],
    'pRef': 0,
    'Cp': 1000,
    'thermo': 'hPolynomial',
    'Pr': 0.7,
    'TRef': 300,
    'turbulenceModel': 'kOmegaSST',
}

numericalSettings = {
    'mode': 0,
    'ddtSchemes': {'default': 'steadyState',},
    'gradSchemes': {'default': 'cellLimited Gauss linear 0.5',
                    'grad(p)': 'Gauss linear',
                    'grad(U)': 'cellLimited Gauss linear 0.5',},
    'divSchemes': {'default': 'Gauss linear',
                   'div(phi,U)': 'Gauss linearUpwind grad(U)',
                   'div(phi,k)': 'Gauss upwind',
                   'div(phi,omega)': 'Gauss upwind',
                   'div(phi,epsilon)': 'Gauss upwind',
                   'div(phi,nuTilda)': 'Gauss upwind',
                   'div(phi,nut)': 'Gauss upwind',
                   'div(nuEff*dev(T(grad(U))))': 'Gauss linear',
                   },
    'laplacianSchemes': {'default': 'Gauss linear limited corrected 0.5',},
    'interpolationSchemes': {'default': 'linear'},
    'snGradSchemes': {'default': 'limited corrected 0.5',},
    'fluxRequired': {'default': 'no'},
    'wallDist': 'meshWave',
    'pimpleDict': {'nOuterCorrectors': 20, 'nCorrectors': 1, 
                   'nNonOrthogonalCorrectors': 1, 
                   'pRefCell': 0, 'pRefValue': 0,
                   'residualControl': {'p': 1e-3, 'U': 1e-3, 
                                       'k': 1e-3, 'omega': 1e-3, 'epsilon': 1e-3, 
                                       'nuTilda': 1e-3,
                                       'nut': 1e-3},
                   },

    'relaxationFactors': {'U': 0.7, 'k': 0.7, 'omega': 0.7, 'epsilon': 0.7, 'nut': 0.7, 'nuTilda':0.7, 'p': 0.3}, 
    'simpleDict':{'nNonOrthogonalCorrectors': 2, 'consistent': 'false','pRefCell': 0, 'pRefValue': 0,
                   'residualControl': {'U': 1e-4, 'p': 1e-3, 'k': 1e-4, 'omega': 1e-4, 'epsilon': 1e-4, 'nut': 1e-4, 'nuTilda': 1e-4}},
    'potentialFlowDict':{'nonOrthogonalCorrectors': 10},
}

inletValues = {
    'U': [1, 0, 0],
    'p': 0,
    'k': 0.1,
    'omega': 1,
    'epsilon': 0.1,
    'nut': 1e-6,
}

solverSettings = {
    'U': {'type': 'smoothSolver',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-08,
           'relTol': 0.1},
    'p': {'type': 'GAMG',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-07,
           'relTol': 0.01,
           'maxIter': 100,
           'agglomerator': 'faceAreaPair',
           'nCellsInCoarsestLevel': 10,
           'mergeLevels': 1,
           'cacheAgglomeration': 'true',
           'nSweeps': 1,
           'nPreSweeps': 0,
           'nPostSweeps': 0},
    'k': {'type': 'smoothSolver',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-08,
           'relTol': 0.1},
    'omega':{'type': 'smoothSolver',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-08,
           'relTol': 0.1},
    'epsilon': {'type': 'smoothSolver',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-08,
           'relTol': 0.1},
    'nuTilda': {'type': 'smoothSolver',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-08,
           'relTol': 0.1},
    'nut': {'type': 'smoothSolver',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-08,
           'relTol': 0.1},
    'Phi': {'type': 'GAMG',
           'smoother': 'GaussSeidel',
           'tolerance': 1e-08,
           'relTol': 0.01,
           'maxIter': 100,
           'agglomerator': 'faceAreaPair',
           'nCellsInCoarsestLevel': 10,
           'mergeLevels': 1,
           'cacheAgglomeration': 'true',
           'nSweeps': 1,
           'nPreSweeps': 0,
           'nPostSweeps': 0},
}


boundaryConditions = {
    'velocityInlet': 
    {'u_type': 'fixedValue','u_value': inletValues['U'],
     'p_type': 'zeroGradient','p_value': inletValues['p'],
     'k_type': 'fixedValue','k_value': inletValues['k'],
     'omega_type': 'fixedValue','omega_value': inletValues['omega'],
     'epsilon_type': 'fixedValue','epsilon_value': inletValues['epsilon'],
     'nut_type': 'calculated','nut_value': inletValues['nut'],
     'nutilda_type': 'fixedValue','nutilda_value': inletValues['nut']*3.0},
    
    'pressureOutlet':
    {'u_type': 'inletOutlet','u_value': [0, 0, 0],
     'p_type': 'fixedValue','p_value': 0,
     'k_type': 'zeroGradient','k_value': 1.0e-6,
     'omega_type': 'zeroGradient','omega_value': 1.0e-6,
     'epsilon_type': 'zeroGradient','epsilon_value': 1.0e-6,
     'nut_type': 'calculated','nut_value': 0,
     'nutilda_type': 'zeroGradient','nutilda_value': '$internalField'},

    'wall':
    {'u_type': 'fixedValue','u_value': [0, 0, 0],
     'p_type': 'zeroGradient','p_value': 0,
     'k_type': 'kqRWallFunction','k_value': '$internalField',
     'omega_type': 'omegaWallFunction','omega_value': '$internalField',
     'epsilon_type': 'epsilonWallFunction','epsilon_value': '$internalField',
     'nut_type': 'nutkWallFunction','nut_value': '$internalField',
     'nutilda_type': 'fixedValue','nutilda_value': '$internalField'},

    'movingWall':
    {'u_type': 'movingWallVelocity','u_value': [0, 0, 0],
     'p_type': 'zeroGradient','p_value': 0,
     'k_type': 'kqRWallFunction','k_value': '$internalField',
     'omega_type': 'omegaWallFunction','omega_value': '$internalField',
     'epsilon_type': 'epsilonWallFunction','epsilon_value': '$internalField',
     'nut_type': 'nutkWallFunction','nut_value': '$internalField',
     'nutilda_type': 'fixedValue','nutilda_value':'$internalField'},
}

simulationSettings = {
    'transient': False,
    'application': 'simpleFoam',
    'startTime': 0,
    'endTime': 1000,
    'deltaT': 1,
    'startFrom': 'startTime',
    'stopAt': 'endTime',
    'writeControl': 'runTime',
    'writeInterval': 100,
    'purgeWrite': 0,
    'writeFormat': 'binary',
    'writePrecision': 8,
    'writeCompression': 'off',
    'timeFormat': 'general',
    'timePrecision': 8,
    'runTimeModifiable': 'true',
    'adjustTimeStep': 'no',
    'maxCo': 0.9,
    'functions': [],
    'libs': [],
    'allowSystemOperations': 'true',
    'runTimeControl': 'adjustableRunTime',
}

parallelSettings = {
    'parallel': True,
    'numberOfSubdomains': 4,
    'method': 'scotch',
    'x': 2,
    'y': 2,
    'z': 1,
    
}

simulationFlowSettings = {
    'parallel': True,
    "snappyHexMesh": True,
    'initialize': True,
    'potentialFoam': True,
    'solver': 'simpleFoam',
    'postProc': True,
    'functionObjects': [],
}

postProcessSettings = {
    'FOs': True,
    'minMax': True,
    'massFlow': True,
    'yPlus': True,
    'forces': True,
    'probeLocations': [],
}

