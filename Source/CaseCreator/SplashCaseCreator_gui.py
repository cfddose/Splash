#  *-----------------------------------------------------------------------------*
#  *      SplashCaseCreator - A Module of the Splash CFD Automation Suite
#  * ----------------------------------------------------------------------------*
#  *
#  * Copyright (c) 2024 THAW TAR
#  * Copyright (c) 2025 Mohamed Aly Sayed and Thaw Tar
#  * All rights reserved.
#  *
#  * Licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).
#  * You may obtain a copy of the license at:
#  *     https://www.gnu.org/licenses/lgpl-3.0.en.html
#  *
#  DISCLAIMER:
#  This software is provided "AS IS", without any express or implied warranties,
#  including, but not limited to, the implied warranties of merchantability,
#  fitness for a particular purpose, and noninfringement. Under no circumstances
#  shall the authors, of the contributors be liable for any direct, indirect 
#  incidental, special, or consequential damages, or any other damages whatsoever
#  arising out of or in connection with the use or performance of this software,
#  including any engineering design or implementation decisions.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
# * ----------------------------------------------------------------------------*
# *  SplashCaseCreator is an application of the Splash CFD automation program.
# * ----------------------------------------------------------------------------*

# Importing system-related libs  
import sys
import os
import subprocess
from time import sleep # maybe this line can be deleted
import time

# Connection to the SplashCaseCreator Backend
from project import SplashCaseCreatorProject
from primitives import SplashCaseCreatorPrimitives, SplashCaseCreatorIO

#Importing separate classes and functions
from vtk_manager import VTKManager, vtkMode
from theme_switcher import apply_theme

# Keyboard shortcuts
from PySide6.QtGui import QShortcut, QKeySequence

# Run on a separate thread
from PySide6.QtCore import QThread, Signal

# Importing PySide components 
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QTimer, QTime # for Timer
from PySide6.QtCore import Qt
from PySide6 import QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# Importing Dialog Boxes
from dialogBoxes import yesNoDialogDriver, yesNoCancelDialogDriver
from dialogBoxes import sphereDialogDriver, boxDialogDriver, cylinderDialogDriver
from dialogBoxes import vectorInputDialogDriver, STLDialogDriver, physicalModelsDialogDriver
from dialogBoxes import boundaryConditionDialogDriver, numericsDialogDriver, controlsDialogDriver
from dialogBoxes import set_src, meshPointDialogDriver,postProcessDialogDriver
from dialogBoxes import global_darkmode, set_global_darkmode
from dialogBoxes import advancedMeshDialogDriver

# VTK Libraries
import vtk
import vtkmodules.vtkInteractionStyle

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

# get the absolute path of the current directory
src = os.path.dirname(os.path.abspath(__file__))

# set the source directory for the dialog boxes
set_src(src)


class SplashLauncherThread(QThread):
    error_signal = Signal(str)  # Signal to send messages to GUI

    def run(self):
        self.error_signal.emit("Launching Splash v0.2. Please hang on...")  # Send update to terminal
        try:
            # Change directory to one level up and launch Splash
            process = subprocess.Popen(
            ["python3", "../Splash.py"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,  # Merge stderr with stdout
            text=True
            )


            # Read process output and forward it to terminal
            for line in process.stdout:
                self.error_signal.emit(line.strip())

            process.wait()  # Ensure the process runs properly

        except Exception as e:
            self.error_signal.emit(f"Error launching Splash: {e}")


    
# This is the main window class
class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.surfaces = []
        self.project_opened = False
        self.project = None
        self.app_start_time = time.time()
        self.setup_timer()
        self.minx, self.miny, self.minz = 0.0, 0.0, 0.0
        self.maxx, self.maxy, self.maxz = 0.0, 0.0, 0.0
        self.nx, self.ny, self.nz = 0, 0, 0
        self.lenX, self.lenY, self.lenZ = 1e-3, 1e-3, 1e-3
        self.current_obj = None
        self.colorCounter = 0
        self.current_mode = 0 # balanced
        self.disableButtons()
        
        # Default to Dark Theme
        self.window.themeToggle.setChecked(True)  # Set theme toggle to dark mode by default
        self.apply_default_theme()

        # to store VTK mode
        self.vtk_mode = vtkMode.VTK_SURFACE # initial mode is surface
        
        # Create a QShortcut for saving a case setup quickly 
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.setContext(Qt.WindowShortcut)  # optional: sets the scope
        self.shortcut_save.activated.connect(self.saveCase)
        
        # A QShortcut for opening a case
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_open.setContext(Qt.WindowShortcut)  
        self.shortcut_open.activated.connect(self.openCase)
        
        # A QShortcut for generating a case
        self.shortcut_generate = QShortcut(QKeySequence("Ctrl+G"), self)
        self.shortcut_generate.setContext(Qt.WindowShortcut)  
        self.shortcut_generate.activated.connect(self.generateCase)
                
    def setup_timer(self):
        """
        Sets up a timer to update the timer label every second.
        """
        self.timer = QTimer(self)  # Create a QTimer instance
        self.timer.timeout.connect(self.update_timer_label)  # Connect the timeout signal
        self.timer.start(1000)  # Update every 1 second (1000 ms)

    def update_timer_label(self):
        """
        Updates the timer label with the elapsed time since app launch.
        """
        if not self.timerLabel:
            return  # Prevent errors if timerLabel is not found
        elapsed_time = int(time.time() - self.app_start_time)  # Calculate elapsed time in seconds
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"  # Format as HH:MM:SS
        self.timerLabel.setText(formatted_time)  # Update the label text

    def disableButtons(self):
        self.window.pushButtonSTLImport.setEnabled(False)
        self.window.pushButtonSphere.setEnabled(False)
        self.window.pushButtonBox.setEnabled(False)
        self.window.pushButtonCylinder.setEnabled(False)
        self.window.radioButtonInternal.setEnabled(False)
        self.window.radioButtonExternal.setEnabled(False)
        self.window.checkBoxOnGround.setEnabled(False)
        self.window.pushButtonSTLProperties.setEnabled(False)
        self.window.pushButtonPhysicalProperties.setEnabled(False)
        self.window.pushButtonBoundaryCondition.setEnabled(False)
        self.window.pushButtonNumerics.setEnabled(False)
        self.window.pushButtonControls.setEnabled(False)
        self.window.pushButtonDomainAuto.setEnabled(False)
        self.window.pushButtonDomainManual.setEnabled(False)
        self.window.checkBoxSteadyTransient.setEnabled(False)
        self.window.pushButtonSummarize.setEnabled(False)
        self.window.pushButtonFitAll.setEnabled(False)
        self.window.pushButtonPlusX.setEnabled(False)
        self.window.pushButtonPlusY.setEnabled(False)
        self.window.pushButtonPlusZ.setEnabled(False)
        self.window.pushButtonMinusX.setEnabled(False)
        self.window.pushButtonMinusY.setEnabled(False)
        self.window.pushButtonMinusZ.setEnabled(False)
        self.window.pushButtonShowWire.setEnabled(False)
        self.window.pushButtonShowSurface.setEnabled(False)
        self.window.pushButtonShowEdges.setEnabled(False)
        self.window.pushButtonAddSTL.setEnabled(False)
        self.window.pushButtonRemoveSTL.setEnabled(False)
        self.window.pushButtonMeshPoint.setEnabled(False)
        self.window.pushButtonMeshSettings.setEnabled(False)

        self.window.pushButtonGenerate.setEnabled(False)
        self.window.pushButtonPostProc.setEnabled(False)
        self.window.lineEditMinX.setEnabled(False)
        self.window.lineEditMinY.setEnabled(False)
        self.window.lineEditMinZ.setEnabled(False)
        self.window.lineEditMaxX.setEnabled(False)
        self.window.lineEditMaxY.setEnabled(False)
        self.window.lineEditMaxZ.setEnabled(False)
        self.window.lineEdit_nX.setEnabled(False)
        self.window.lineEdit_nY.setEnabled(False)
        self.window.lineEdit_nZ.setEnabled(False)
        
        # change color of widget 
        self.window.widget.setStyleSheet('''background-color: lightgrey;''')
        self.window.plainTextTerminal.appendPlainText("Welcome to Splash Case Creator")
       
    def enableButtons(self):
        self.window.pushButtonSTLImport.setEnabled(True)
        self.window.pushButtonSphere.setEnabled(True)
        self.window.pushButtonBox.setEnabled(True)
        self.window.pushButtonCylinder.setEnabled(True)
        self.window.radioButtonInternal.setEnabled(True)
        self.window.radioButtonExternal.setEnabled(True)
        self.window.checkBoxOnGround.setEnabled(True)
        self.window.pushButtonSTLProperties.setEnabled(True)
        self.window.pushButtonPhysicalProperties.setEnabled(True)
        self.window.pushButtonBoundaryCondition.setEnabled(True)
        self.window.pushButtonNumerics.setEnabled(True)
        self.window.pushButtonControls.setEnabled(True)
        self.window.pushButtonCreate.setEnabled(True)
        # Now in the menubar -> self.window.pushButtonOpen.setEnabled(True)
        self.window.pushButtonGenerate.setEnabled(True)
        # Post-processing capabilities are disabled in this version
        #self.window.pushButtonPostProc.setEnabled(True)
        self.window.pushButtonDomainAuto.setEnabled(True)
        self.window.pushButtonDomainManual.setEnabled(True)
        self.window.checkBoxSteadyTransient.setEnabled(True)
        self.window.pushButtonSummarize.setEnabled(True)
        self.window.pushButtonFitAll.setEnabled(True)
        self.window.pushButtonPlusX.setEnabled(True)
        self.window.pushButtonPlusY.setEnabled(True)
        self.window.pushButtonPlusZ.setEnabled(True)
        self.window.pushButtonMinusX.setEnabled(True)
        self.window.pushButtonMinusY.setEnabled(True)
        self.window.pushButtonMinusZ.setEnabled(True)
        self.window.pushButtonShowWire.setEnabled(True)
        self.window.pushButtonShowSurface.setEnabled(True)
        self.window.pushButtonShowEdges.setEnabled(True)
        self.window.pushButtonAddSTL.setEnabled(True)
        self.window.pushButtonRemoveSTL.setEnabled(True)
        self.window.pushButtonMeshPoint.setEnabled(True)
        self.window.pushButtonMeshSettings.setEnabled(True)

        self.window.lineEditMinX.setEnabled(True)
        self.window.lineEditMinY.setEnabled(True)
        self.window.lineEditMinZ.setEnabled(True)
        self.window.lineEditMaxX.setEnabled(True)
        self.window.lineEditMaxY.setEnabled(True)
        self.window.lineEditMaxZ.setEnabled(True)
        self.window.lineEdit_nX.setEnabled(True)
        self.window.lineEdit_nY.setEnabled(True)
        self.window.lineEdit_nZ.setEnabled(True)

    def load_ui(self):
        loader = QUiLoader()
        ui_path = os.path.join(src, "SplashCaseCreatorInputForm.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        self.setCentralWidget(self.window)
        # Increased the window height
        self.setGeometry(100, 100, 1400, 930)
        self.setWindowTitle("Splash Case Creator")
        
        # Add timer label programmatically
        self.timerLabel = self.window.findChild(QtWidgets.QLabel, "timerLabel")
        if not self.timerLabel:
            print("Error: 'timerLabel' not found in the UI.")
            return
        
        # Set up VTK widget
        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.window.widget)
        self.vl.addWidget(self.vtkWidget)
        self.ren = vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        
        # Initialize VTKManager
        self.vtk_manager = VTKManager(self.ren, self.vtkWidget)

        # Change Steady/Transient button into toggle button
        self.window.checkBoxSteadyTransient.setCheckable(True)
        
        # Launch Splash v0.2 when prompted
        self.window.launchSplash.clicked.connect(self.launch_splash)
        
        # Prepare sub-windows and event connections
        self.prepare_subWindows()
        self.prepare_events()
        
        # Configure VTK Background ComboBox -  with error handling
        self.vtkBackground = self.window.findChild(QtWidgets.QComboBox, "vtkBackground")
        if not self.vtkBackground:
            raise ValueError("UI element 'vtkBackground' not found in the loaded UI.")

        # Populate and bind the ComboBox
        self.vtkBackground.addItems([
            "Cyan-Gray Gradient",
            "White-Black Gradient",
            "Black-White Gradient",
            "Blue Gradient",
            "Solid White",
            "Solid Black",
        ])
        self.vtkBackground.currentIndexChanged.connect(
            lambda index: self.vtk_manager.update_vtk_background(index)
        )
        
        # Connect theme toggle
        self.window.themeToggle.stateChanged.connect(self.toggle_theme)
        
        
    def launch_splash(self):
        """Launch Splash.py in a separate thread."""
        self.splash_thread = SplashLauncherThread()
        self.splash_thread.error_signal.connect(lambda msg: SplashCaseCreatorIO.printMessage(msg, GUIMode=True, window=self))
        self.splash_thread.start()    

    def apply_default_theme(self):
        """
        Apply the default theme (dark) at application startup.
        """
        dark_mode = self.window.themeToggle.isChecked()
        apply_theme(self.window, self.vtk_manager, dark_mode)

    def toggle_theme(self):
        """
        Toggles between light and dark themes, applying the appropriate stylesheet
        and updating the VTK background via VTKManager.
        """
        #global global_darkmode
        dark_mode = self.window.themeToggle.isChecked()
        #global_darkmode = dark_mode
        set_global_darkmode(dark_mode)
        #print(f"Dark Mode: {dark_mode}")
        #print(f"Global Dark Mode: {global_darkmode}")
        apply_theme(self.window, self.vtk_manager, dark_mode)
        
        # Update color for property table
        if dark_mode:
            print("Dark mode selected")
            self.window.tableViewProperties.horizontalHeader().setStyleSheet("color: black")
        else:
            print("Light mode selected")
            self.window.tableViewProperties.horizontalHeader().setStyleSheet("color: black")
        
    # FLAG! For that purpose is this?    
    # def __del__(self):
    #     pass

    # This is not used at all. So, commented out.
    # def openCADDialog(self):
    #     fname,ftype = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
    #     'c:\\',"CAD files (*.brep *.igs *.iges)")
    #     if(fname==""):
    #         return -1 # CAD file not loaded
    #     else:
    #         #print("Current CAD File: ",fname)
    #         return fname
                       
    # manage sub windows
    def prepare_subWindows(self):
        self.createCaseWindow = None
    
    def update_list(self):
        self.window.listWidgetObjList.clear()
        for idx, stl in enumerate(self.project.stl_files):
            #print(f"Adding to list: {stl['name']}")
            self.window.listWidgetObjList.addItem(stl['name'])
        for idx, geometry in enumerate(self.project.geometries):
            print(f"Adding to list: {geometry['name']}")
            self.window.listWidgetObjList.addItem(geometry['name'])

    # ----------------------------------------------
    #  Highlighing the clicked STL file in the list
    # ---------------------------------------------
    def listClicked(self):
        """
        Handles the event when an item is clicked in the listWidgetObjList.
        Highlights the selected STL in the VTK viewer and updates the property box.
        """
        #try:
        # Find the selected item in the list
        item = self.window.listWidgetObjList.currentItem()
        if not item:
            print("No item selected.")
            return
        
        idx = self.window.listWidgetObjList.row(item)
        self.current_obj = item.text()

        # Check if the selected object is a boundary or an STL file
        is_STL = False
        is_STL = self.project.check_stl_file(self.current_obj)
        
        
        # Highlight the STL file in the VTK viewer
        self.vtk_manager.highlight_actor(
            self.current_obj,
            [s['name'] for s in self.project.stl_files],
            vtkNamedColors()
        )

        # Retrieve STL properties
        if is_STL:
            stl_properties = self.project.get_stl_properties(self.current_obj)
        else:
            stl_properties = None
        
        # For external flows, the selected object is probably a boundary.
        # In this case, we need to retrieve the boundary properties instead.
        if self.project.internalFlow==False:
            #patch_names = [s['name'] for s in self.project.meshSettings['patches']]
            self.vtk_manager.highlight_boundary(
                self.current_obj,
                [s['name'] for s in self.project.meshSettings['patches']],
                vtkNamedColors())
            boundary_properties = self.project.get_boundary(self.current_obj)
            #print(f"Boundary Properties: {boundary_properties}")
            #return
        
        if stl_properties==None and boundary_properties==None:
            print(f"No properties found for {self.current_obj}")
            return

        if is_STL:
            # Unpack STL properties
            purpose, refMin, refMax, featureEdges, featureLevel, nLayers, property, bounds = stl_properties
            
            self.window.tableViewProperties.clearContents()
            self.window.tableViewProperties.setRowCount(5)
            self.window.tableViewProperties.setColumnCount(2)

            # Setting headers (if not already set elsewhere)
            self.window.tableViewProperties.setHorizontalHeaderLabels(["Property", "Value"])
            
            self.window.tableViewProperties.setItem(0, 0, QtWidgets.QTableWidgetItem("Refinement Min"))
            self.window.tableViewProperties.setItem(0, 1, QtWidgets.QTableWidgetItem(str(refMin)))
            self.window.tableViewProperties.setItem(1, 0, QtWidgets.QTableWidgetItem("Refinement Max"))
            self.window.tableViewProperties.setItem(1, 1, QtWidgets.QTableWidgetItem(str(refMax)))
            self.window.tableViewProperties.setItem(2, 0, QtWidgets.QTableWidgetItem("Feature Edges"))
            self.window.tableViewProperties.setItem(2, 1, QtWidgets.QTableWidgetItem(str(featureEdges)))
            self.window.tableViewProperties.setItem(3, 0, QtWidgets.QTableWidgetItem("Feature Level"))
            self.window.tableViewProperties.setItem(3, 1, QtWidgets.QTableWidgetItem(str(featureLevel)))
            self.window.tableViewProperties.setItem(4, 0, QtWidgets.QTableWidgetItem("Purpose"))
            self.window.tableViewProperties.setItem(4, 1, QtWidgets.QTableWidgetItem(str(purpose)))
            
            # Additional rows for other properties
            additional_row = 5
            self.window.tableViewProperties.setRowCount(additional_row + 8)
            self.window.tableViewProperties.setItem(additional_row, 0, QtWidgets.QTableWidgetItem("nLayers"))
            self.window.tableViewProperties.setItem(additional_row, 1, QtWidgets.QTableWidgetItem(str(nLayers)))
            self.window.tableViewProperties.setItem(additional_row + 1, 0, QtWidgets.QTableWidgetItem("Min X"))
            self.window.tableViewProperties.setItem(additional_row + 1, 1, QtWidgets.QTableWidgetItem(f"{bounds[0]:.2f}"))
            self.window.tableViewProperties.setItem(additional_row + 2, 0, QtWidgets.QTableWidgetItem("Max X"))
            self.window.tableViewProperties.setItem(additional_row + 2, 1, QtWidgets.QTableWidgetItem(f"{bounds[1]:.2f}"))
            self.window.tableViewProperties.setItem(additional_row + 3, 0, QtWidgets.QTableWidgetItem("Min Y")) 
            self.window.tableViewProperties.setItem(additional_row + 3, 1, QtWidgets.QTableWidgetItem(f"{bounds[2]:.2f}")) 
            self.window.tableViewProperties.setItem(additional_row + 4, 0, QtWidgets.QTableWidgetItem("Max Y")) 
            self.window.tableViewProperties.setItem(additional_row + 4, 1, QtWidgets.QTableWidgetItem(f"{bounds[3]:.2f}")) 
            self.window.tableViewProperties.setItem(additional_row + 5, 0, QtWidgets.QTableWidgetItem("Min Z")) 
            self.window.tableViewProperties.setItem(additional_row + 5, 1, QtWidgets.QTableWidgetItem(f"{bounds[4]:.2f}"))
            self.window.tableViewProperties.setItem(additional_row + 6, 0, QtWidgets.QTableWidgetItem("Max Z")) 
            self.window.tableViewProperties.setItem(additional_row + 6, 1, QtWidgets.QTableWidgetItem(f"{bounds[5]:.2f}"))
            
        else:
            # Unpack boundary properties
            #print(f"Boundary Properties: {boundary_properties}")
            patchType = boundary_properties['type']

            #->>>
            patchProperty = boundary_properties.get('property', None)
            if patchProperty is None:
                #print(f"Warning: 'property' key not found in boundary_properties. Using default value (0,0,0).")
                patchProperty = (0.0, 0.0, 0.0)  # Default fallback

            #<<<- patchProperty = boundary_properties['property']

            patchPurpose = boundary_properties['purpose']

            self.window.tableViewProperties.clearContents()
            self.window.tableViewProperties.setRowCount(3)
            self.window.tableViewProperties.setColumnCount(2)

            # Setting headers (if not already set elsewhere)
            self.window.tableViewProperties.setHorizontalHeaderLabels(["Property", "Value"])
            
            self.window.tableViewProperties.setItem(0, 0, QtWidgets.QTableWidgetItem("Type"))
            self.window.tableViewProperties.setItem(0, 1, QtWidgets.QTableWidgetItem(patchType))
            self.window.tableViewProperties.setItem(1, 0, QtWidgets.QTableWidgetItem("Property"))
            self.window.tableViewProperties.setItem(1, 1, QtWidgets.QTableWidgetItem(str(patchProperty)))
            self.window.tableViewProperties.setItem(2, 0, QtWidgets.QTableWidgetItem("Purpose"))
            self.window.tableViewProperties.setItem(2, 1, QtWidgets.QTableWidgetItem(str(patchPurpose)))
            
            

        #except Exception as e:
        #    print(f"Error in listClicked: {e}")
    # ------------------------------------------------------
    #  End of: Highlighing the clicked STL file in the list
    # ------------------------------------------------------        

    def updateTerminal(self, *messages):
        """
        Updates the terminal output in the GUI with one or more messages.
        :param messages: Any number of strings to display in the terminal.
        """
        for message in messages:
            self.window.plainTextTerminal.insertPlainText(f"{message}\n")
        # Ensure the terminal scrolls to the most recent message
        self.window.plainTextTerminal.verticalScrollBar().setValue(
            self.window.plainTextTerminal.verticalScrollBar().maximum()
        )

    def updateStatusBar(self, message="Go!"):
        """
        Updates the status bar in the GUI.
        :param message: The message to display in the status bar.
        """
        self.window.statusbar.showMessage(message)
        self.window.plainTextTerminal.insertPlainText(f"{message}\n")

    def readyStatusBar(self):
        """
        Updates the status bar to 'Ready' after a short pause.
        """
        sleep(0.001)
        self.window.statusbar.showMessage("Ready")
    
# FLAG! Why is this line is written this way?   
# Thaw: This is the wrong way and already corrected.      
#self.window.plainTextTerminal.verticalScrollBar().setValue(self.window.plainTextTerminal.verticalScrollBar().maximum())
        
    #----------------- Event Handlers -----------------#    
    def prepare_events(self):
        # Saving screenshots and connecting relevant events
        save_screenshot_action = QAction("Save Screenshot", self)
        save_screenshot_action.triggered.connect(self.saveScreenshotOptions)

        # Add the "Save Screenshot" action before the "Exit" action
        self.window.menuFile.insertAction(self.window.actionExit, save_screenshot_action)  # Insert above "Exit"

        # Connect other menubar actions
        self.window.actionNew_Case.triggered.connect(self.createCase)
        self.window.actionOpen_Case.triggered.connect(self.openCase)
        self.window.actionSave_Case.triggered.connect(self.saveCase)
        self.window.actionExit.triggered.connect(self.close)

        # Additional button connections
        self.window.pushButtonSTLImport.clicked.connect(self.importSTL)
        self.window.pushButtonSphere.clicked.connect(self.createSphere)
        self.window.pushButtonBox.clicked.connect(self.createBox)
        self.window.pushButtonCylinder.clicked.connect(self.createCyliner)
        self.window.pushButtonCreate.clicked.connect(self.createCase)
        # Now in the menubar -> self.window.pushButtonOpen.clicked.connect(self.openCase)
        self.window.pushButtonGenerate.clicked.connect(self.generateCase)
        self.window.pushButtonPostProc.clicked.connect(self.postProcessDialog)
        self.window.radioButtonInternal.clicked.connect(self.chooseInternalFlow)
        self.window.radioButtonExternal.clicked.connect(self.chooseExternalFlow)
        self.window.listWidgetObjList.itemClicked.connect(self.listClicked)
        self.window.pushButtonDomainAuto.clicked.connect(self.autoDomainDriver)
        self.window.pushButtonDomainManual.clicked.connect(self.manualDomain)
        self.window.pushButtonSTLProperties.clicked.connect(self.stlPropertiesDialog)
        self.window.pushButtonMeshSettings.clicked.connect(self.advancedMeshDialog)
        self.window.pushButtonPhysicalProperties.clicked.connect(self.physicalPropertiesDialog)
        self.window.pushButtonBoundaryCondition.clicked.connect(self.boundaryConditionDialog)
        self.window.pushButtonNumerics.clicked.connect(self.numericsDialog)
        self.window.pushButtonControls.clicked.connect(self.controlsDialog)
        self.window.checkBoxSteadyTransient.clicked.connect(self.toggleSteadyTransient)
        self.window.pushButtonSummarize.clicked.connect(self.summarizeProject)
        self.window.pushButtonAddSTL.clicked.connect(self.importSTL)
        self.window.pushButtonRemoveSTL.clicked.connect(self.removeSTL)
        self.window.pushButtonMeshPoint.clicked.connect(self.setMeshPoint)

        # Toggle axes on the main render window
        self.window.axesCheckBox.stateChanged.connect(self.toggle_axes_with_vtk_manager) 

        ## (Beta) STEP import button connection --->
        ##self.window.pushButtonSTEPImport.clicked.connect(self.importSTEP)
        ## Create the STEP import action if not already defined
        #try:
        #    # Try to access the action (if created in the UI)
        #    action_step_import = self.window.actionSTEPImport
        #except AttributeError:
        #    # Otherwise, create it programmatically
        #    action_step_import = QAction("Import STEP", self)
        #    # Insert it into the File menu before the "Exit" action
        #    self.window.menuFile.insertAction(self.window.actionExit, action_step_import)
        #    # Optionally, you can assign it to the window for later use:
        #    self.window.actionSTEPImport = action_step_import
    
        ## Connect the STEP import action to the handler
        #action_step_import.triggered.connect(self.importSTEP)
    
        # Manual generation event
        download_manual_action = QAction("Download Manual", self)
        download_manual_action.triggered.connect(self.download_manual)
        self.window.menuHelp.addAction(download_manual_action)

        # VTK view changes
        self.window.pushButtonFitAll.clicked.connect(self.vtkFitAll)
        self.window.pushButtonPlusX.clicked.connect(self.vtkPlusX)
        self.window.pushButtonPlusY.clicked.connect(self.vtkPlusY)
        self.window.pushButtonPlusZ.clicked.connect(self.vtkPlusZ)
        self.window.pushButtonMinusX.clicked.connect(self.vtkMinusX)
        self.window.pushButtonMinusY.clicked.connect(self.vtkMinusY)
        self.window.pushButtonMinusZ.clicked.connect(self.vtkMinusZ)
        self.window.pushButtonShowWire.clicked.connect(self.vtkShowWire)
        self.window.pushButtonShowSurface.clicked.connect(self.vtkShowSurface)
        self.window.pushButtonShowEdges.clicked.connect(self.vtkShowEdges)
    #----------------- Event Handlers -----------------#
    
    def download_manual(self):
        """
        Generates the documentation for the application in both HTML and PDF formats.
        """
        try:
            from documentation_generator import DocumentationGenerator

            source_file = os.path.abspath(__file__)  # Path to the current script
            output_dir = os.path.join(os.getcwd(), "docs")
            DocumentationGenerator.generate_manual(source_file, output_dir)

            self.updateStatusBar("Manual downloaded successfully.")
        except Exception as e:
            self.updateStatusBar(f"Error generating manual: {e}")
            print(f"Error: {e}")
        
    #-------------------    
    # Screenshot saving
    #-------------------     
    def saveScreenshotOptions(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Screenshot Options")

        layout = QtWidgets.QVBoxLayout(dialog)

        # Resolution input
        resolution_label = QtWidgets.QLabel("Resolution (width x height):")
        layout.addWidget(resolution_label)
        resolution_input = QtWidgets.QLineEdit()
        resolution_input.setPlaceholderText("1920x1080")
        layout.addWidget(resolution_input)

        # Transparency checkbox
        transparency_checkbox = QtWidgets.QCheckBox("Transparent Background")
        layout.addWidget(transparency_checkbox)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Save")
        cancel_button = QtWidgets.QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Button actions
        def save_action():
            resolution = resolution_input.text().strip()
            transparent = transparency_checkbox.isChecked()
            dialog.accept()
            self.saveScreenshot(resolution, transparent)

        save_button.clicked.connect(save_action)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()
    
    def saveScreenshot(self, resolution="1920x1080", transparent=False):
        # Open a file dialog to get the save location and file name
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "",
            "Image Files (*.png *.jpg *.bmp *.tiff)",
            options=options
        )

        if not file_path:
            print("Save operation canceled.")
            return

        # Parse resolution
        try:
            width, height = map(int, resolution.split("x"))
        except ValueError:
            print("Invalid resolution format. Using default resolution.")
            width, height = 1920, 1080

        # Set up the VTK filter to capture the rendering window
        render_window = self.vtkWidget.GetRenderWindow()
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(render_window)

        # Configure transparency
        if transparent:
            window_to_image_filter.SetInputBufferTypeToRGBA()
            render_window.SetAlphaBitPlanes(1)  # Enable alpha channel for the render window
            self.ren.SetBackground(1.0, 1.0, 1.0)  # Set background color (white)
            self.ren.GetRenderWindow().SetMultiSamples(0)  # Disable multisampling for transparency
        else:
            window_to_image_filter.SetInputBufferTypeToRGB()
            self.ren.SetBackground(0.0, 0.0, 0.0)  # Set background color (black)

        # Set resolution
        render_window.SetSize(width, height)
        render_window.Render()  # Update the render window

        window_to_image_filter.Update()

        # Save the image
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(file_path)
        writer.SetInputConnection(window_to_image_filter.GetOutputPort())
        writer.Write()

        print(f"Screenshot saved to: {file_path}")
        self.updateStatusBar(f"Screenshot saved to: {file_path}")
        #--------------------------    
        # End of screenshot saving
        #-------------------------- 
    
    def importSTL(self):
        #print("Importing STL...")
        stl_path = SplashCaseCreatorPrimitives.ask_for_file([("STL Geometry", "*.stl"), ("OBJ Geometry", "*.obj")],qt=True)
        stl_status = self.project.add_stl_file(stl_path)
        #print(f"STL files:",self.project.stl_files)
        #print(f"STL Status: {stl_status}")
        if stl_status == -1:
            self.updateStatusBar("Failed to load STL file.")
            return
        #self.project.add_stl_to_project()
        #print(f"Project STL Files: {self.project.stl_files}")
        self.vtk_manager.render_stl(self.project.current_stl_file)
        self.update_list()
        self.updateStatusBar("STL imported successfully.")
        return 
        # try:
        #     #print("Importing STL...")
        #     stl_path = SplashCaseCreatorPrimitives.ask_for_file([("STL Geometry", "*.stl"), ("OBJ Geometry", "*.obj")],qt=True)
        #     stl_status = self.project.add_stl_file(stl_path)
        #     #print(f"STL files:",self.project.stl_files)
        #     #print(f"STL Status: {stl_status}")
        #     if stl_status == -1:
        #         self.updateStatusBar("Failed to load STL file.")
        #         return
        #     #self.project.add_stl_to_project()
        #     #print(f"Project STL Files: {self.project.stl_files}")
        #     self.vtk_manager.render_stl(self.project.current_stl_file)
        #     self.update_list()
        #     self.updateStatusBar("STL imported successfully.")
        # except Exception as e:
        #     self.updateStatusBar(f"Error importing STL: {e}")
        #     print(f"Error: {e}")

    def importMultipleSTL(self):
        # show the file dialog
        filters = "STL files (*.stl)"
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        stlList = fileDialog.getOpenFileNames(self,"Open STL files",r"C:\Users\mrtha\Desktop\GitHub\foamAutoGUI\src",filters)
        print(stlList[0])
        if(len(stlList[0])==0):
            return
        for stl in stlList[0]:
            status = self.project.add_one_stl_file(stl)
            if status==-1:
                SplashCaseCreatorIO.printError(f"STL file {stl} not loaded",GUIMode=True,window=self)
                #return
            self.project.add_stl_to_project()
            self.vtk_manager.showSTL(stlFile=stl)
        self.update_list()
        self.readyStatusBar()

    def removeSTL(self):
        item = self.window.listWidgetObjList.currentItem()
        if item==None or item.text()=="":
            return
        idx = self.window.listWidgetObjList.row(item)
        stl = item.text()
        self.project.remove_stl_file_by_name(stl)
        self.vtk_manager.remove_stl(stl)
        self.update_list()
        self.readyStatusBar()

    def check_list_for_duplicates(self, obj_name):
        objNames = [self.window.listWidgetObjList.item(i).text() for i in range(self.window.listWidgetObjList.count())]
        if obj_name in objNames:
            return True
        return False

    def createSphere(self):
        SplashCaseCreatorIO.printMessage("Creating Sphere",GUIMode=True,window=self)
        # create a sphere dialog
        sphereData = sphereDialogDriver()
        if sphereData == None:
            pass # Do nothing
            #SplashCaseCreatorIO.printError("Sphere Dialog Box Closed",GUIMode=True)
        else:
            name,x,y,z,r = sphereData
            obj_properties = {"name":name,"x":x,"y":y,"z":z,"radius":r,"refineMin":0,"refineMax":0,'property':None}
            # Check if there is already a cylinder with the same name
            if self.check_list_for_duplicates(name):
                SplashCaseCreatorIO.printError("Object with the same name already exists. Please choose a different name.",GUIMode=True)
                return
            # First, add to the project 
            self.project.add_vtk_object_to_project(obj_name=name,obj_type="sphere",obj_properties=obj_properties)
            # Then, add to the VTK viewer
            self.vtk_manager.add_sphere_to_VTK(center=(x,y,z),radius=r,objectName=name)
            # Add to the list
            self.window.listWidgetObjList.addItem(name)
            print("Center: ",x,y,z)
            print("Radius: ",r)
        self.readyStatusBar()

    def createCyliner(self):
        SplashCaseCreatorIO.printMessage("Creating Cylinder",GUIMode=True,window=self)
        # create a cylinder dialog
        cylinderData = cylinderDialogDriver()
        if cylinderData == None:
            pass # Do nothing
            #SplashCaseCreatorIO.printError("Cylinder Dialog Box Closed",GUIMode=True)
        else:
            name,x,y,z,r,h = cylinderData
            obj_properties = {"name":name,"x":x,"y":y,"z":z,"radius":r,"height":h,"refineMin":0,"refineMax":0,'property':None}
            # Check if there is already a cylinder with the same name
            if self.check_list_for_duplicates(name):
                SplashCaseCreatorIO.printError("Object with the same name already exists. Please choose a different name.",GUIMode=True)
                return
            # First, add to the project
            self.project.add_vtk_object_to_project(obj_name=name,obj_type="cylinder",obj_properties=obj_properties)
            # Then, add to the VTK viewer
            self.vtk_manager.add_cylinder_to_VTK(center=(x,y,z),radius=r,height=h,objectName=name)
            # Add to the list
            self.window.listWidgetObjList.addItem(name)
            print("Center: ",x,y,z)
            print("Radius: ",r)
            print("Height: ",h)

    def createBox(self):
        SplashCaseCreatorIO.printMessage("Creating Box",GUIMode=True,window=self)
        # create a box dialog
        boxData = boxDialogDriver()
        if boxData == None:
            pass   
        else:
            name,minx,miny,minz,maxx,maxy,maxz = boxData
            obj_properties = {"name":name,"minx":minx,"miny":miny,"minz":minz,"maxx":maxx,"maxy":maxy,"maxz":maxz,"refineMin":0,"refineMax":0,'property':None}
            # Check if there is already a cylinder with the same name
            if self.check_list_for_duplicates(name):
                SplashCaseCreatorIO.printError("Object with the same name already exists. Please choose a different name.",GUIMode=True)
                return
            # First, add to the project
            self.project.add_vtk_object_to_project(obj_name=name,obj_type="box",obj_properties=obj_properties)
            # Then, add to the VTK viewer
            self.vtk_manager.add_box_to_VTK(minx,miny,minz,maxx,maxy,maxz,objectName=name)
            # Add to the list
            self.window.listWidgetObjList.addItem(name)
            print("Min: ",minx,miny,minz)
            print("Max: ",maxx,maxy,maxz)

        self.readyStatusBar()

    def resizeEvent(self, event):
        """
        Dynamically resize widgets when the main window is resized.
        """
        TERMINAL_HEIGHT = 300  # Adjust as needed
        PROGRESS_BAR_HEIGHT = 20  # To adjust the progress bar and terminal positions
        TABLE_WIDTH = 200  # Width of the properties table
        TABLE_HEIGHT_FREE_SPACE = 410  # Window height - table height 
        WINDOW_HEIGHT = self.window.height()
        WINDOW_WIDTH = self.window.width()
        table_height = WINDOW_HEIGHT - TABLE_HEIGHT_FREE_SPACE - 50
        frame3_height = WINDOW_HEIGHT - 40 # height of the frame3 which contains the properties table
        vtkWidgetHeight = WINDOW_HEIGHT - TERMINAL_HEIGHT - PROGRESS_BAR_HEIGHT - 20
        vtkWidgetWidth = WINDOW_WIDTH - 560

        terminalX = self.window.widget.pos().x()
        terminalY = self.window.widget.pos().y() + vtkWidgetHeight + 5

        self.window.widget.resize(vtkWidgetWidth, vtkWidgetHeight)
        self.vtkWidget.resize(vtkWidgetWidth, vtkWidgetHeight)
        self.vtkWidget.GetRenderWindow().Render()

        # Resize the terminal, progress bar and properties table

        self.window.plainTextTerminal.move(terminalX, terminalY)
        self.window.plainTextTerminal.resize(vtkWidgetWidth, TERMINAL_HEIGHT - 70)
        self.window.plainTextTerminal.update()
        self.window.plainTextTerminal.repaint()
        self.window.progressBar.move(terminalX, terminalY+TERMINAL_HEIGHT-65)
        self.window.progressBar.resize(vtkWidgetWidth, PROGRESS_BAR_HEIGHT)
        self.window.progressBar.update()
        self.window.progressBar.repaint()

        #self.window.tableViewProperties.move(terminalX, terminalY + TERMINAL_HEIGHT + PROGRESS_BAR_HEIGHT + 2)
        
        #print(f"Table Height: {table_height}")
        self.window.frame_3.resize(self.window.frame_3.width(), frame3_height)
        self.window.tableViewProperties.resize(TABLE_WIDTH, table_height)
        self.readyStatusBar()

    def closeEventTriggered(self, event):
        self.close()

    def toggleSteadyTransient(self):
        buttonText = self.window.checkBoxSteadyTransient.text()
        if buttonText=="Steady-State":
            self.window.checkBoxSteadyTransient.setText("Transient")
            SplashCaseCreatorIO.printMessage("Transient Flow Selected",GUIMode=True,window=self)
            self.project.transient = True
            # this is to ensure that the ddtSchemes is set to Euler if the current value is steadyState
            if self.project.numericalSettings['ddtSchemes']['default'] == "steadyState":
                self.project.numericalSettings['ddtSchemes']['default'] = "Euler"
        else:
            self.window.checkBoxSteadyTransient.setText("Steady-State")
            SplashCaseCreatorIO.printMessage("Steady-State Flow Selected",GUIMode=True,window=self)
            self.project.transient = False
            # this is to ensure that the ddtSchemes is set to steadyState if the current value is not steadyState
            if self.project.numericalSettings['ddtSchemes']['default'] != "steadyState":
                self.project.numericalSettings['ddtSchemes']['default'] = "steadyState"
        self.project.set_transient_settings()
        self.readyStatusBar()

    def addExternalBoundaries(self):
        # add inlet, outlet, front, back, top, bottom to the list object
        items = ["inlet","outlet","front","back","top","bottom"]
        currentItems = [self.window.listWidgetObjList.item(i).text() for i in range(self.window.listWidgetObjList.count())]
        #print("Current Items: ",currentItems)
        for item in items:
            if item not in currentItems:
                self.window.listWidgetObjList.addItem(item)
        
    def removeExternalBoundaries(self):
        # remove inlet, outlet, front, back, top, bottom from the list object
        #self.updateStatusBar("Removing External Boundaries")
        # for all the items in the list, remove these if inlet, outlet, front, back, top, bottom
        boundaryPatches = ["inlet","outlet","front","back","top","bottom"]
        for j in range(self.window.listWidgetObjList.count()):
            for i in range(self.window.listWidgetObjList.count()):
                if self.window.listWidgetObjList.item(i)==None:
                    continue
                else:
                    if self.window.listWidgetObjList.item(i).text() in boundaryPatches:
                        self.window.listWidgetObjList.takeItem(i)
        #self.window.listWidgetObjList.takeItem(self.window.listWidgetObjList.row(0))
        #self.window.listWidgetObjList.takeItem(self.window.listWidgetObjList.row(0))
        #self.window.listWidgetObjList.takeItem(self.window.listWidgetObjList.row(0))
        #self.window.listWidgetObjList.takeItem(self.window.listWidgetObjList.row(0))
        #self.window.listWidgetObjList.takeItem(self.window.listWidgetObjList.row(0))
        #self.window.listWidgetObjList.takeItem(self.window.listWidgetObjList.row(0))
    
    def addBoundaryGrids(self):
        # add boundary grids to the vtk renderer
        domain_size = self.project.get_domain_size()
        self.vtk_manager.add_left_grid(domain_size)
        self.vtk_manager.add_right_grid(domain_size)
        self.vtk_manager.add_top_grid(domain_size)
        self.vtk_manager.add_bottom_grid(domain_size)
        self.vtk_manager.add_front_grid(domain_size)
        self.vtk_manager.add_back_grid(domain_size)
        self.readyStatusBar()
    
    def addOrRemoveExternalBoundaries(self):
        if self.project.internalFlow:
            # if internal flow, remove external boundaries if any
            self.removeExternalBoundaries()
        else:
            self.addExternalBoundaries()
            #VTKManager.add_x_grid(self.ren,self.project.meshSettings['minX'],self.project.meshSettings['maxX'],self.project.meshSettings['nX'])
            self.addBoundaryGrids()
            #self.readyStatusBar()
        
    def chooseInternalFlow(self):
        self.project.internalFlow = True
        self.project.meshSettings['internalFlow'] = True
        self.project.onGround = False
        self.window.checkBoxOnGround.setEnabled(False)
        self.window.radioButtonInternal.setChecked(True)
        self.addOrRemoveExternalBoundaries()
        self.updateStatusBar("Choosing Internal Flow")
        #sleep(0.001)
        self.readyStatusBar()

    def chooseExternalFlow(self):
        self.project.internalFlow = False
        self.project.meshSettings['internalFlow'] = False
        self.window.checkBoxOnGround.setEnabled(True)
        self.project.meshSettings['onGround'] = self.window.checkBoxOnGround.isChecked()
        self.project.onGround = self.window.checkBoxOnGround.isChecked()
        self.addOrRemoveExternalBoundaries()
        #self.vtk_manager.add_boundary_grid()
        self.updateStatusBar("Choosing External Flow")
        #sleep(0.001)
        self.readyStatusBar()

    def resetGUI(self):
        self.window.listWidgetObjList.clear()
        self.window.tableViewProperties.clearContents()
        self.window.lineEditMinX.clear()
        self.window.lineEditMinY.clear()
        self.window.lineEditMinZ.clear()
        self.window.lineEditMaxX.clear()
        self.window.lineEditMaxY.clear()
        self.window.lineEditMaxZ.clear()
        self.window.lineEdit_nX.clear()
        self.window.lineEdit_nY.clear()
        self.window.lineEdit_nZ.clear()
        self.window.radioButtonInternal.setChecked(False)
        self.window.radioButtonExternal.setChecked(True)
        self.window.checkBoxOnGround.setChecked(False)
        self.window.checkBoxSteadyTransient.setText("Steady-State")
        #self.project = None
        #self.project_opened = False
        ##self.disableButtons()
        self.ren.RemoveAllViewProps()
        self.updateStatusBar("GUI Reset")
        self.readyStatusBar()

    def createCase(self):
        if self.project_opened:
            # ask yes or no or cancel
            yNC = yesNoCancelDialogDriver("Save changes to current case files before creating a New Case","Save Changes")
            if yNC==1: # if yes
                # save the project
                #self.project.add_stl_to_project()
                SplashCaseCreatorIO.printMessage("Saving the current case...", GUIMode=True, window=self)
                self.project.write_settings()
                self.disableButtons()
                self.ren.RemoveAllViewProps()
            elif yNC==-1: # if no
                # close the project
                self.project = None
                self.project_opened = False
                self.disableButtons()
                self.ren.RemoveAllViewProps()
            else: # if cancel
                return
            
        self.updateStatusBar("Creating New Case")
        # clear terminal
        self.window.plainTextTerminal.clear()
        # clear vtk renderer
        self.ren.RemoveAllViewProps()
        
        # Also clear the object list and property table
        self.resetGUI()
        self.project = None # clear the project
        self.project = SplashCaseCreatorProject(GUIMode=True,window=self)
        
        self.project.set_project_directory(SplashCaseCreatorPrimitives.ask_for_directory(qt=True))
        if self.project.project_directory_path == None:
            SplashCaseCreatorIO.printMessage("No project directory selected.",GUIMode=True,window=self)
            self.updateTerminal("Canceled creating new case")
            self.readyStatusBar()
            return
        project_name = SplashCaseCreatorIO.get_input("Enter the project name: ",GUIMode=True)
        if project_name == None:
            SplashCaseCreatorIO.printError("Project Name not entered",GUIMode=True)
            self.updateTerminal("Canceled creating new case")
            self.readyStatusBar()
            return
        self.project.set_project_name(project_name)
        
        self.project.create_project_path()
        SplashCaseCreatorIO.printMessage("Creating the project",GUIMode=True,window=self)
        SplashCaseCreatorIO.printMessage(f"Project path: {self.project.project_path}",GUIMode=True,window=self)
        self.project.create_project()
        self.project.create_settings()
        
        self.project.set_global_refinement_level()
        
        # Now enable the buttons
        self.enableButtons()
        self.readyStatusBar()
        self.project_opened = True
        SplashCaseCreatorIO.printMessage(f"Project {project_name} created",GUIMode=True,window=self)
        
        # change window title
        self.setWindowTitle(f"Splash Case Creator: {project_name}")
        self.readyStatusBar()
        

    def openCase(self):
        """
        Opens an existing OpenFOAM case and loads its associated settings and STL files.
        
        This method handles the following:
        1. Prompts the user to save changes to the currently open project if applicable.
        2. Clears the terminal, renderer, and GUI elements to prepare for the new case.
        3. Loads the project directory selected by the user.
        4. Reads project settings, checks the case structure, and validates the directory.
        5. Renders all STL files in the case and updates the object list.
        6. Restores the camera to its previous state (if saved) or sets a default view.
        7. Updates the GUI elements based on the loaded project settings.
        8. Displays success or error messages in the terminal and status bar.

        GUI Elements Updated:
        - The object list is populated with STL file names.
        - Buttons are enabled or disabled based on the project state.
        - Camera view is adjusted to fit the loaded geometry.

        Error Handling:
        - If no project directory is selected or the directory is invalid, appropriate warnings are displayed.

        Raises:
            None
        """
        if self.project_opened:
            # Ask user to save changes, discard, or cancel
            yNC = yesNoCancelDialogDriver(
                "Save changes to current case files before creating a New Case", "Save Changes"
            )
            if yNC == 1:  # Yes
                SplashCaseCreatorIO.printMessage("Saving the current case...", GUIMode=True, window=self)
                #self.project.add_stl_to_project()
                self.project.write_settings()
                self.disableButtons()
                self.ren.RemoveAllViewProps()
            elif yNC == -1:  # No
                self.project = None
                self.project_opened = False
                self.disableButtons()
                self.ren.RemoveAllViewProps()
            else:  # Cancel
                self.readyStatusBar()
                return

        self.updateStatusBar("Opening Case")
        # Clear terminal and VTK renderer
        self.window.plainTextTerminal.clear()
        self.ren.RemoveAllViewProps()
        # Also clear the object list and property table
        self.resetGUI()

        # Reset the project
        self.project = None
        self.project = SplashCaseCreatorProject(GUIMode=True, window=self)
        self.window.listWidgetObjList.clear()  # Clear the object list

        project_found = self.project.set_project_path(SplashCaseCreatorPrimitives.ask_for_directory(qt=True))
        if project_found == -1:
            SplashCaseCreatorIO.printWarning("No project found. Failed to open case directory.", GUIMode=True)
            self.updateTerminal("No project found. Failed to open case directory.")
            self.readyStatusBar()
            # reset the background by adding initial grid
            self.vtk_manager.add_initial_grid()
            return -1

        SplashCaseCreatorIO.printMessage(f"Project path: {self.project.project_path}", GUIMode=True, window=self)
        SplashCaseCreatorIO.printMessage("Loading the project", GUIMode=True, window=self)

        # Load settings and validate the case structure
        self.project.go_inside_directory()
        self.project.load_settings()
        #print(f"Internal Flow: {self.project.internalFlow}")
        #print(f"On Ground: {self.project.onGround}")
        #print(f"Transient: {self.project.transient}")
        self.project.check_0_directory()
        SplashCaseCreatorIO.printMessage("Project loaded successfully", GUIMode=True, window=self)

        # Render all STL files in the case
        stl_file_paths = self.project.list_stl_paths()
        for stl_file in stl_file_paths:
            self.vtk_manager.render_stl(stl_file)

        # Update the object list panel
        self.update_list()

        # Restore camera state or set a default view
        self.vtk_manager.restore_camera_state()
        self.vtk_manager.set_default_camera()

        # Update GUI elements based on project settings
        self.enableButtons()
        
        # This autoDomain caused a lot of problems. So, replaced with prepareDomainView
        #self.autoDomain(analyze=False)
        self.prepareDomainView()
        #print(f"On Ground: {self.project.onGround}")
        if self.project.internalFlow:
            self.chooseInternalFlow()
            #self.window.radioButtonInternal.setChecked(True)
            #self.window.checkBoxOnGround.setEnabled(False)
        else:
            #self.window.radioButtonExternal.setChecked(True)
            self.window.checkBoxOnGround.setChecked(self.project.onGround)
            self.chooseExternalFlow()

        # Update window title and status
        self.project_opened = True
        self.setWindowTitle(f"Case Creator: {self.project.project_name}")
        SplashCaseCreatorIO.printMessage(f"Project {self.project.project_name} opened", GUIMode=True, window=self)
        self.readyStatusBar()
    
    # Generate a case of the current config. 
    def generateCase(self):
        self.updateStatusBar("Analyzing Case")
        #if(len(self.project.stl_files)>0):
        #    self.project.analyze_stl_file()
        self.updateStatusBar("Creating Project Files")
        self.project.useFOs = True
        self.project.set_post_process_settings()
        #project.list_stl_files()
        self.project.summarize_project()
        #project.analyze_stl_file()
        self.project.write_settings()
        self.project.create_project_files()
        self.updateTerminal("--------------------")
        self.updateTerminal("   Case generated!  ")
        self.updateTerminal("--------------------")
        self.readyStatusBar()
    
    def saveCase(self):
        self.updateStatusBar("Analyzing case before saving")
        #if(len(self.project.stl_files)>0):
        #    self.project.analyze_stl_file()
        self.updateStatusBar("Saving Case")
        self.updateTerminal("Saving Case")
        self.project.useFOs = True
        self.project.set_post_process_settings()
        self.project.write_settings()
        self.updateTerminal("--------------------")
        self.updateTerminal("     Case saved!    ")
        self.updateTerminal("--------------------")
        self.readyStatusBar()

    def autoDomainDriver(self):
        self.analyze = True
        self.autoDomain(self.analyze)
        # if internal flow, remove external boundaries if any
        self.addOrRemoveExternalBoundaries()
    
    def autoDomain(self,analyze=True):
       
        if self.project.internalFlow==True:
            onGround = False
        else:
            onGround = self.window.checkBoxOnGround.isChecked()
        self.project.meshSettings['onGround'] = onGround
        self.project.onGround = onGround

        # If object is on the ground, the bottom boundary condition is wall
        if onGround:
            self.project.set_external_boundary_condition(patch_name="bottom",boundary_condition="wall")
            self.project.set_boundary_type(patch_name="bottom",boundary_type="wall")
        if len(self.project.stl_files)==0:
            self.updateTerminal("No STL files loaded")
            self.readyStatusBar()
            return
        if analyze:
            self.project.analyze_stl_file()
        self.prepareDomainView()
        self.readyStatusBar()
    
    # This prepare the VTK renderer and sets the camera view.
    # Separated from autoDomain and manualDomain to only update the view when necessary.
    def prepareDomainView(self):
        minx = self.project.meshSettings['domain']['minx']
        miny = self.project.meshSettings['domain']['miny']
        minz = self.project.meshSettings['domain']['minz']
        maxx = self.project.meshSettings['domain']['maxx']
        maxy = self.project.meshSettings['domain']['maxy']
        maxz = self.project.meshSettings['domain']['maxz']
        nx = self.project.meshSettings['domain']['nx']
        ny = self.project.meshSettings['domain']['ny']
        nz = self.project.meshSettings['domain']['nz']
       
        self.window.lineEditMinX.setText(f"{minx:.2f}")
        self.window.lineEditMinY.setText(f"{miny:.2f}")
        self.window.lineEditMinZ.setText(f"{minz:.2f}")
        self.window.lineEditMaxX.setText(f"{maxx:.2f}")
        self.window.lineEditMaxY.setText(f"{maxy:.2f}")
        self.window.lineEditMaxZ.setText(f"{maxz:.2f}")
        self.window.lineEdit_nX.setText(str(nx))
        self.window.lineEdit_nY.setText(str(ny))
        self.window.lineEdit_nZ.setText(str(nz))
        #self.add_box_to_VTK(minX=minx,minY=miny,minZ=minz,maxX=maxx,maxY=maxy,maxZ=maxz)
        self.vtk_manager.add_box_to_VTK(minX=minx, minY=miny, minZ=minz, maxX=maxx, maxY=maxy, maxZ=maxz, objectName="Domain")
        self.addBoundaryGrids()
        self.vtkDrawMeshPoint()
        self.vtkRefreshView()
        
    def manualDomain(self):
        minx = float(self.window.lineEditMinX.text())
        miny = float(self.window.lineEditMinY.text())
        minz = float(self.window.lineEditMinZ.text())
        maxx = float(self.window.lineEditMaxX.text())
        maxy = float(self.window.lineEditMaxY.text())
        maxz = float(self.window.lineEditMaxZ.text())
        nx = int(self.window.lineEdit_nX.text())
        ny = int(self.window.lineEdit_nY.text())
        nz = int(self.window.lineEdit_nZ.text())
        #print(f"minx: {minx}, miny: {miny}, minz: {minz}")
        #print(f"maxx: {maxx}, maxy: {maxy}, maxz: {maxz}")
        if(nx<=0 or ny<=0 or nz<=0):
            SplashCaseCreatorIO.printError("Invalid Domain Size",GUIMode=True)
            self.readyStatusBar()
            return
        if(minx>maxx or miny>maxy or minz>maxz):
            SplashCaseCreatorIO.printError("Invalid Domain Size",GUIMode=True)
            self.readyStatusBar()
            return
        domain_size = [minx,maxx,miny,maxy,minz,maxz]
        self.project.set_max_domain_size(domain_size,nx,ny,nz)
        self.prepareDomainView()
        self.readyStatusBar()
       
    # Although the name is stlPropertiesDialog, this is applicable for all objects  
    def stlPropertiesDialog(self):
        stl = self.current_obj
        stl_status = self.project.check_stl_file(stl)
        if stl==None:
            return
        if stl_status==True:
            currentProperties = self.project.get_stl_properties(stl)
        else:
            currentProperties = self.project.get_boundary_properties(stl)
        if currentProperties==None:
            return
        
        # open STL properties dialog
        stlProperties = STLDialogDriver(stl,stlProperties=currentProperties)
        
        # The properties are:
        if stlProperties==None:
            return
        
        # update the properties
        if stl_status==True:
            status = self.project.set_stl_properties(stl,stlProperties)
        else:
            status = self.project.set_boundary_properties(stl,stlProperties)
        if status==-1:
            SplashCaseCreatorIO.printError("Patch Properties not updated",GUIMode=True)   
        else:
            #self.updateStatusBar(f"{stl}: Properties Updated")
            self.updateTerminal(f"{stl} Properties Updated")
            self.readyStatusBar()
        # To refresh the property table
        self.listClicked()

    def physicalPropertiesDialog(self):
        # assign initial values from read data
        rho = self.project.physicalProperties['rho']
        nu = self.project.physicalProperties['nu']
        cp = self.project.physicalProperties['Cp']
        turbulence_model = self.project.physicalProperties['turbulenceModel']
        fluid = self.project.physicalProperties['fluid']
        initialProperties = (fluid,rho,nu,cp)
        
        physicalProperties = physicalModelsDialogDriver(initialProperties)
        if physicalProperties==None:
            return 
        fluid,rho,nu,cp = physicalProperties
        # update the project physical properties
        SplashCaseCreatorIO.printMessage("Updating Physical Properties",GUIMode=True)
        SplashCaseCreatorIO.printMessage(f"Updated Properties: {physicalProperties}",GUIMode=True,window=self)
        self.project.physicalProperties['fluid'] = fluid
        self.project.physicalProperties['rho'] = rho
        self.project.physicalProperties['nu'] = nu
        self.project.physicalProperties['Cp'] = cp
        #self.project.physicalProperties['turbulenceModel'] = turbulence_model

    def boundaryConditionDialog(self):
        stl = self.project.get_stl(self.current_obj)
        patch_names = [patch['name'] for patch in self.project.meshSettings['patches']]
        if stl==None:
            # May be this is a predefined external boundary
            if self.current_obj in patch_names:
                boundary = None 
                for patch in self.project.meshSettings['patches']:
                    if patch['name']==self.current_obj:
                        boundary = patch
                        break
                #boundary['name'] = self.current_obj
                boundaryConditions = boundaryConditionDialogDriver(boundary,external_boundary=True)
                self.project.set_external_boundary_condition(self.current_obj,boundaryConditions)
                self.listClicked()
                self.updateTerminal(f"{self.current_obj} Boundary Conditions Updated")
                self.readyStatusBar()
                return
            else:
                SplashCaseCreatorIO.printError("Patch not found",GUIMode=True)
                return
        
        boundaryConditions = boundaryConditionDialogDriver(stl)
        if boundaryConditions==None:
            return
        # update the boundary conditions
        self.project.set_boundary_condition(self.current_obj,boundaryConditions)
        self.listClicked()
        self.updateTerminal(f"{self.current_obj} Boundary Conditions Updated")
        self.readyStatusBar()


    def numericsDialog(self):
        self.current_mode,self.project.numericalSettings,turbulence_model = numericsDialogDriver(self.current_mode,self.project.numericalSettings,
                                                                                                 self.project.physicalProperties['turbulenceModel'],
                                                                                                 transient=self.project.transient)  
        self.project.physicalProperties['turbulenceModel'] = turbulence_model

    def controlsDialog(self):
        self.project.simulationSettings,self.project.parallelSettings = controlsDialogDriver(self.project.simulationSettings,self.project.parallelSettings,self.project.transient)

    def advancedMeshDialog(self):
        meshSize = self.project.meshSettings['maxCellSize']
        self.project.meshSettings = advancedMeshDialogDriver(self.project.meshSettings)
        if meshSize!=self.project.meshSettings['maxCellSize']:
            self.project.update_mesh_size(self.project.meshSettings['maxCellSize'])
            self.prepareDomainView()
        if self.project.meshSettings['halfModel']:
            self.project.halfModel = True

    
    def postProcessDialog(self):
        postProcessDialogDriver()

    def summarizeProject(self):
        self.project.summarize_project()
        self.readyStatusBar()

    # Defining a point inside the domain 
    def setMeshPoint(self):
        """
        Opens the mesh point dialog, updates the VTK sphere visualization, and saves the new location.
        """
        # Open the mesh point dialog
        meshPoint = meshPointDialogDriver(self.project.get_location_in_mesh())

        if meshPoint is None:
            return

        # Find the QSpinBox widget safely | FLAG BUG here! the value is not read here 
        sphere_radius_widget = self.findChild(QtWidgets.QDoubleSpinBox, "sphereRadiusLocationInMesh")  # Changed to QDoubleSpinBox

        if sphere_radius_widget is None:
            print("Error: sphereRadiusLocationInMesh not found. Using default radius.")
            sphere_radius_value = 0.25  # Default radius
        else:
            # Get the user-defined radius (keeps user input)
            sphere_radius_value = sphere_radius_widget.value()

            # Only set default value if the user hasn't changed it
            if sphere_radius_value == sphere_radius_widget.minimum():  
                minX, minY, minZ, maxX, maxY, maxZ = (
                    self.project.meshSettings['domain']['minx'],
                    self.project.meshSettings['domain']['miny'],
                    self.project.meshSettings['domain']['minz'],
                    self.project.meshSettings['domain']['maxx'],
                    self.project.meshSettings['domain']['maxy'],
                    self.project.meshSettings['domain']['maxz']
                )
                auto_radius = max(maxX - minX, maxY - minY, maxZ - minZ) * 0.0025  # Auto-calculated size
                sphere_radius_widget.setValue(auto_radius)  # Set only if user input was not changed

        # Save only the mesh point coordinates
        self.project.set_location_in_mesh(meshPoint)

        # Pass the user-defined radius to VTK
        self.vtkDrawMeshPoint(sphere_radius_value)

#----------------- VTK Event Handlers -----------------#
    def vtkFitAll(self):
        """Reset the camera to fit all actors in view."""
        bounds = self.ren.ComputeVisiblePropBounds()
        print(f"Visible bounds: {bounds}")  # Debugging output
        self.vtk_manager.reset_camera()

    def vtkPlusX(self):
        """Set camera view to +X direction."""
        self.vtk_manager.set_camera_orientation(position=(1, 0, 0))

    def vtkPlusY(self):
        """Set camera view to +Y direction."""
        self.vtk_manager.set_camera_orientation(position=(0, 1, 0))

    def vtkPlusZ(self):
        """Set camera view to +Z direction."""
        self.vtk_manager.set_camera_orientation(position=(0, 0, 1), view_up=(0, 1, 0))

    def vtkMinusX(self):
        """Set camera view to -X direction."""
        self.vtk_manager.set_camera_orientation(position=(-1, 0, 0))

    def vtkMinusY(self):
        """Set camera view to -Y direction."""
        self.vtk_manager.set_camera_orientation(position=(0, -1, 0))

    def vtkMinusZ(self):
        """Set camera view to -Z direction."""
        self.vtk_manager.set_camera_orientation(position=(0, 0, -1), view_up=(0, 1, 0))

    def vtkShowWire(self):
        """Display all actors as wireframes."""
        self.vtk_manager.toggle_actor_representation(representation_mode="Wireframe")
        self.vtk_mode = vtkMode.VTK_WIREFRAME
        # in wireframe mode, boundary grid lines are shown
        self.vtk_manager.show_boundary_grids()

    def vtkShowSurface(self):
        """Display all actors as solid surfaces without edges."""
        self.vtk_manager.toggle_actor_representation(representation_mode="Surface")
        self.vtk_mode = vtkMode.VTK_SURFACE
        # in surface mode, boundary grid lines are hidden
        self.vtk_manager.hide_boundary_grids()

    def vtkShowEdges(self):
        """Display all actors as solid surfaces with visible edges."""
        self.vtk_manager.toggle_actor_representation(representation_mode="Surface", edge_visibility=True)
        self.vtk_mode = vtkMode.VTK_EDGES

    def vtkHilightSTL(self, stlFile):
        """Highlight the specified STL actor."""
        self.vtk_manager.highlight_actor(
            stl_file=stlFile,
            stl_names=[stl['name'] for stl in self.project.stl_files],
            colors=vtk.vtkNamedColors()
        )

    def vtkUpdateAxes(self):
        """Draw axes with a dynamic size based on project dimensions."""
        char_len = max(self.project.lenX, self.project.lenY, self.project.lenZ, 0.001) * 0.2
        print(char_len)
        self.vtk_manager.draw_axes(char_len)

    # def vtkDrawMeshPoint(self, sphere_radius=None):
    #     """
    #     Draw the mesh point using the VTKManager.
    #     """
    #     # Read the latest saved mesh point from project file
    #     location = self.project.get_location_in_mesh()

    #     if not location:
    #         print("No location found for the mesh point.")
    #         return

    #     domain_bounds = (
    #         self.project.meshSettings['domain']['minx'],
    #         self.project.meshSettings['domain']['miny'],
    #         self.project.meshSettings['domain']['minz'],
    #         self.project.meshSettings['domain']['maxx'],
    #         self.project.meshSettings['domain']['maxy'],
    #         self.project.meshSettings['domain']['maxz']
    #     )

    #     # If no sphere_radius provided, use an auto-scaled value
    #     if sphere_radius is None:
    #         minX, minY, minZ, maxX, maxY, maxZ = domain_bounds
    #         max_extent = max(maxX - minX, maxY - minY, maxZ - minZ)
    #         sphere_radius = max_extent * 0.0025  # Default scaling
    #         print(f"Auto-calculated radius: {sphere_radius}")

    #     # Ensure a minimum sphere size for visibility
    #     sphere_radius = max(sphere_radius, 1e-3)

    #     # Ensure the correct location is passed to the visualization function
    #     self.vtk_manager.draw_mesh_point(location, domain_bounds=domain_bounds, size_factor=sphere_radius, remove_previous=True)
    
    def vtkDrawMeshPoint(self, sphere_radius=None):
        """
        Draw the mesh point in the VTK renderer with a specified radius.
        """
        location = self.project.get_location_in_mesh()

        if not location:    
            print("No location found for the mesh point.")
            return

        domain_bounds = (
            self.project.meshSettings['domain']['minx'],
            self.project.meshSettings['domain']['miny'],
            self.project.meshSettings['domain']['minz'],
            self.project.meshSettings['domain']['maxx'],
            self.project.meshSettings['domain']['maxy'],
            self.project.meshSettings['domain']['maxz']
        )

        # If no sphere_radius provided, use an auto-scaled value
        if sphere_radius is None:
            minX, minY, minZ, maxX, maxY, maxZ = domain_bounds
            max_extent = max(maxX - minX, maxY - minY, maxZ - minZ)
            sphere_radius = max_extent * 0.0025  # Default scaling
            print(f"Auto-calculated radius: {sphere_radius}")

        # Ensure a minimum sphere size for visibility
        sphere_radius = max(sphere_radius, 1e-3)

        # Now, explicitly set the sphere radius for VTK
        self.vtk_manager.draw_mesh_point(location, domain_bounds=domain_bounds, size_factor=sphere_radius, remove_previous=True)

    # After every operation, VTK view will be refreshed to show the changes
    def vtkRefreshView(self):
        """Refresh the VTK view."""
        if self.vtk_mode == vtkMode.VTK_WIREFRAME:
            self.vtkShowWire()
        elif self.vtk_mode == vtkMode.VTK_SURFACE:
            self.vtkShowSurface()
        elif self.vtk_mode == vtkMode.VTK_EDGES:
            self.vtkShowEdges()
        else:
            self.vtkShowSurface()

    def toggle_axes_with_vtk_manager(self, state):
        """
        Calls the toggle_axes_with_checkbox function inside VTKManager
        when the checkbox is checked/unchecked.
        """
        if hasattr(self, "vtk_manager"):
            self.vtk_manager.toggle_axes_with_checkbox(state)
            
    #def importSTEP(self):
    #    # Open a file dialog to select a STEP file
    #    step_file, _ = QFileDialog.getOpenFileName(self, "Import STEP File", "", "STEP Files (*.step *.stp)")
    #    if step_file:
    #        try:
    #            self.updateTerminal("Importing STEP file: " + step_file)
    #            # Assuming your VTKManager instance is stored in self.vtk_manager:
    #            self.vtk_manager.render_step(step_file)
    #            self.updateTerminal("STEP file imported successfully.")
    #        except Exception as e:
    #            self.updateTerminal("Error importing STEP file: " + str(e))
            

#----------------- End of VTK Event Handlers -----------------#

def main():
    app = QApplication(sys.argv)
    w = mainWindow()
    w.show()
    app.exec()

if __name__ == "__main__":
    main()
