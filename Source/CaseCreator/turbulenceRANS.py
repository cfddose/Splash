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

# this consists of the class TurbulenceRANS, to compute RANS turbulence boundary conditions

import numpy as np

# available turbulence models: kOmegaSST, kEpsilon, SpalartAllmaras
class turbulenceRANS:
    def __init__(self,U=1.0,nu=1.0,rho=1.0,L=1.0):
        self.mesh = None
        self.nu = None
        self.k = None
        self.epsilon = None
        self.omega = None
        self.U = U
        self.rho = rho
        self.L = L
        self.Re = U*L/nu


        self.I = None # turbulence intensity
        # Constants
        self.Cmu = 0.09
        self.sigma_k = 1.0
        self.sigma_epsilon = 1.3
        self.C1 = 1.44
        self.C2 = 1.92
        self.kappa = 0.41
    
    def set_intensity(self, intensity):
        self.I = intensity

    def calc_intensity(self):
        self.I = 0.16*self.Re**(-1./8.)


    def calc_k(self):
        self.k = 1.5*(self.U*self.I)**2

# input: U, nu, turbulence intensity, eddy viscosity ratio
# output: k, epsilon, omega
def kEpsilon(U,nu,I=0.16,nu_t_ratio=1.0):
    k = 1.5*(U*I)**2
    epsilon = 1.5*k**1.5/(0.09*nu)
    omega = 0.09*k/epsilon
    print(f"k: {k}, epsilon: {epsilon}, omega: {omega}")
    return k, epsilon, omega

# calculate turbulent intnsity for pipe flow
# input: flow velocity (U), nu, D
def calc_intensity(U,nu,D):
    Re = U*L/nu
    I = 0.16*Re**(-1./8.)
    return I

# calculate turbulent length scale for pipe flow
# input: D
def calc_length_scale(D):
    return 0.07*D

# calculate turbulent length scale for channel flow
# input: channel width (W), channel depth (H)
def calc_length_scale_channel(U,nu,W,H):
    A = W*H
    P = 2*(W+H)
    D = 4*A/P
    l = 0.07*D
    return l

# calculate turbulent kinetic energy 
# input: U, I
def calc_k(U,I):
    return 1.5*(U*I)**2

# calculate turbulent dissipation rate
# input: k, nu
def calc_epsilon(k,l):
    Cmu = 0.09
    eps = Cmu**(3./4.)*k**(3./2.)/l
    return eps

# calculate turbulent dissipation rate
# input: k, l
def calc_omega(k,l):
    Cmu = 0.09
    omega = Cmu**(-1./4.)*k**0.5/l
    return omega


