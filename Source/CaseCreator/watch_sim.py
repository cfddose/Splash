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

import matplotlib.pyplot as plt
import numpy as np
import time
from project import SplashCaseCreatorProject
from primitives import SplashCaseCreatorPrimitives, SplashCaseCreatorIO
from headers import get_SplashCaseCreator_header
import os

# this code is to watch the simulation convergence
def watch_residuals(logfile):
    # read the log file
    with open(logfile) as f:
        lines = f.readlines()
    # extract residuals
    Ux_ = []
    Uy_ = []
    Uz_ = []
    p_ = []
    k_ = []
    epsilon_ = []
    omega_ = []
    #newTimeStep = False
    Ux_added = False
    Uy_added = False
    Uz_added = False
    p_added = False
    k_added = False
    epsilon_added = False
    omega_added = False

    for line in lines:
        

        if 'Time = ' in line:
            #newTimeStep = True # this is a new time step
            #print("Started new time step")
            # reset the flags
            Ux_added = False
            Uy_added = False
            Uz_added = False
            p_added = False
            k_added = False
            epsilon_added = False
            omega_added = False
        if 'Solving for Ux,' in line and not Ux_added:
            Ux = line.split()[7]
            Ux_.append(float(Ux[:-1]))
            Ux_added = True
        if 'Solving for Uy,' in line and not Uy_added:
            Uy = line.split()[7]
            Uy_.append(float(Uy[:-1]))
            Uy_added = True
        if 'Solving for Uz,' in line and not Uz_added:
            Uz = line.split()[7]
            Uz_.append(float(Uz[:-1]))
            Uz_added = True
        if 'Solving for p,' in line and not p_added:
            p = line.split()[7]
            p_.append(float(p[:-1]))
            p_added = True
        if 'Solving for k,' in line and not k_added:
            k = line.split()[7]
            k_.append(float(k[:-1]))
            k_added = True
        if 'Solving for epsilon' in line and not epsilon_added:
            epsilon = line.split()[7]
            epsilon_.append(float(epsilon[:-1]))
            epsilon_added = True
        if 'Solving for omega,' in line and not omega_added:
            omega = line.split()[7]
            omega_.append(float(omega[:-1]))
            omega_added = True
    # plot the residuals
    plt.figure()
    plt.plot(Ux_, label='Ux')
    plt.plot(Uy_, label='Uy')
    plt.plot(Uz_, label='Uz')
    plt.plot(p_, label='p')
    plt.plot(k_, label='k')
    plt.plot(epsilon_, label='epsilon')
    plt.plot(omega_, label='omega')
    plt.yscale('log')
    plt.legend()
    plt.savefig('residuals.png')
    plt.show()
    # save the figure
    

# to watch the field values
def watch_field(U_file, p_file):
    # read the log file
    with open(U_file) as f:
        lines = f.readlines()
    # extract velocity data
    Ux = []
    Uy = []
    Uz = []
    for line in lines:
        if '#' not in line:
            Ux.append(float(line.split()[1][1:]))
            Uy.append(float(line.split()[2]))
            Uz.append(float(line.split()[3][:-1]))

    # read the pressure file
    with open(p_file) as f:
        lines = f.readlines()
    # extract pressure data
    p = []
    for line in lines:
        if '#' not in line:
            p.append(float(line.split()[1]))

    # plot the field values
    plt.figure()
    plt.plot(Ux, label='Ux')
    plt.plot(Uy, label='Uy')
    plt.plot(Uz, label='Uz')
    plt.legend()
    
    # save the figure
    plt.savefig('U_probe.png')
    plt.show()
    # plot the field values
    #plt.figure()
    plt.plot(Ux, label='p')
    plt.legend()
    
    # save the figure
    plt.savefig('p_probe.png')
    plt.show()

def watch_forces(force_file):
    # read the log file
    with open(force_file) as f:
        lines = f.readlines()
    # extract velocity data
    time = []
    Fx = []
    Fy = []
    Fz = []

    
    for line in lines:
        if '#' not in line:
            time.append(float(line.split()[0]))
            Fx.append(float(line.split()[1]))
            Fy.append(float(line.split()[2]))
            Fz.append(float(line.split()[3]))


    # plot the field values
    plt.figure()
    plt.plot(time, Fx, label='Fx')
    plt.plot(time, Fy, label='Fy')
    plt.plot(time, Fz, label='Fz')
    plt.legend()
    
    # save the figure
    plt.savefig('forces.png')
    plt.show()

def watch_residuals_live(logfile, interval=500):
    while True:
        watch_residuals(logfile)
        time.sleep(interval)

            
def watch_sim():
    project = SplashCaseCreatorProject()
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    SplashCaseCreatorIO.printMessage(get_SplashCaseCreator_header())
    SplashCaseCreatorIO.printMessage("Please select the project directory to open")
    projectFound = project.set_project_path(SplashCaseCreatorPrimitives.ask_for_directory())
    SplashCaseCreatorIO.printMessage(f"Project path: {project.project_path}")
    if projectFound==-1:
        SplashCaseCreatorIO.printError("No project found. Exiting the program")
        return -1
    SplashCaseCreatorIO.printMessage("Loading the project")
    project.go_inside_directory()
    
    project.load_settings()
    project.check_0_directory()
    SplashCaseCreatorIO.printMessage("Project loaded successfully")
    project.summarize_project()
    if project.check_log_files():
        watch_residuals('log.simpleFoam')
    if project.check_post_process_files():
        watch_field('postProcessing/probe/0/U', 'postProcessing/probe/0/p')
    if project.check_forces_files():
        watch_forces('postProcessing/forces/0/force.dat')
    return 0

if __name__ == '__main__':
    watch_sim()
    #watch_residuals('log.simpleFoam')
    #watch_field('U', 'p')
    #watch_residuals_live('log.simpleFoam', 1)