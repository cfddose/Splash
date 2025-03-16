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

from project import SplashCaseCreatorProject
from primitives import SplashCaseCreatorPrimitives, SplashCaseCreatorIO
from headers import get_SplashCaseCreator_header
import os

def open_project():
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
    #project.list_stl_files()
    modify_project = SplashCaseCreatorIO.get_input_bool("Do you want to modify the project settings (y/N)?: ")
    project_modified = False # flag to check if the project has been modified
    while modify_project:
        project.load_settings()
        project.choose_modification_categorized()
        project.modify_project()
        project.write_settings()
        project_modified = True
        modify_project = SplashCaseCreatorIO.get_input_bool("Do you want to modify another settings (y/N)?: ")
    #project.choose_modification()
    #project.modify_project()
    if project_modified: # if the project is modified at least once
        SplashCaseCreatorIO.printMessage("Generating the project files based on the new settings")
        # if everything is successful, write the settings to the project_settings.yaml file
        project.write_settings()
        # Then create the project files with the new settings
        project.create_project_files()
    else:
        SplashCaseCreatorIO.printMessage("No modifications were made to the project settings")
    return 0


if __name__ == '__main__':
    # Specify the output YAML file
    try:
        open_project()
    except KeyboardInterrupt:
        SplashCaseCreatorIO.printMessage("\nKeyboardInterrupt detected! Aborting project creation")
        exit()
    #except Exception as error:
    #    SplashCaseCreatorIO.printError(error)
    #    exit()