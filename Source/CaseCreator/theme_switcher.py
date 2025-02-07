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

def apply_theme(window, vtk_manager, dark_mode):
    """
    Apply the selected theme to the specified UI elements and VTK widget.

    Parameters:
        window: The main application window.
        vtk_manager: Instance of VTKManager managing the VTK widget.
        dark_mode: Boolean indicating if dark mode should be applied.
    """
    if dark_mode:
        # Dark mode stylesheet
        dark_stylesheet = """
        QMainWindow {
            background-color: #2E3440;
            color: #D8DEE9;
        }
        QWidget {
            background-color: #3B4252;
            color: #ECEFF4;
        }
        QPlainTextEdit {
            background-color: #2E3440;
            color: #D8DEE9;
            border: 1px solid #4C566A;
        }
        QTableWidget {
            background-color: #3B4252;
            color: #ECEFF4;
            border: 1px solid #4C566A;
        }
        QListWidget {
            background-color: #3B4252;
            color: #ECEFF4;
            border: 1px solid #4C566A;
        }
        """
        window.setStyleSheet(dark_stylesheet)

        # Update VTKManager's background for dark mode
        vtk_manager.set_background(
            background=(0.18, 0.2, 0.25),   # Dark gray
            gradient_background=True,
            background2=(0.0, 1.0, 1.0)    # Cyan
        )
    else:
        # Light mode stylesheet
        light_stylesheet = """
        QMainWindow {
            background-color: #FFFFFF;
            color: #000000;
        }
        QWidget {
            background-color: #F0F0F0;
            color: #000000;
        }
        QPlainTextEdit {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        QTableWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        QListWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        """
        window.setStyleSheet(light_stylesheet)

        # Update VTKManager's background for light mode
        vtk_manager.set_background(
            background=(1.0, 1.0, 1.0),   # White
            gradient_background=False
        )

def apply_theme_dialog_boxes(window, dark_mode):
    """
    Apply the selected theme to the specified UI elements in the dialog boxes.

    Parameters:
        window: The main application window.
        
        dark_mode: Boolean indicating if dark mode should be applied.
    """
    if dark_mode:
        # Dark mode stylesheet
        dark_stylesheet = """
        QMainWindow {
            background-color: #2E3440;
            color: #D8DEE9;
        }
        QWidget {
            background-color: #3B4252;
            color: #ECEFF4;
        }
        QPlainTextEdit {
            background-color: #2E3440;
            color: #D8DEE9;
            border: 1px solid #4C566A;
        }
        QTableWidget {
            background-color: #3B4252;
            color: #ECEFF4;
            border: 1px solid #4C566A;
        }
        QListWidget {
            background-color: #3B4252;
            color: #ECEFF4;
            border: 1px solid #4C566A;
        }
        QTabWidget {
            background-color: #3B4252;
            color: #000000;  
            border: 1px solid #4C566A;
        }
        QTabWidget::pane {
            background-color: #3B4252;
            color: #ECEFF4;
            border: #4C566A;
        }
        QTabBar::tab {
            background-color: #3B4252;
            color: #000000; 
            #border: 3px solid #000000;
        }
        """
        window.setStyleSheet(dark_stylesheet)

        
    else:
        # Light mode stylesheet
        light_stylesheet = """
        QMainWindow {
            background-color: #FFFFFF;
            color: #000000;
        }
        QWidget {
            background-color: #F0F0F0;
            color: #000000;
        }
        QPlainTextEdit {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        QTableWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        QListWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        QTabWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        """
        window.setStyleSheet(light_stylesheet)
