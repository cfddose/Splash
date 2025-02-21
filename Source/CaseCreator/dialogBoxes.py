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

from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox

#from primitives import SplashCaseCreatorPrimitives

import sys
from time import sleep
import os
from gui_text_to_foam_dict import grad_schemes,div_schemes,temporal_schemes,laplacian_schemes
from gui_text_to_foam_dict import value_to_key

# For resetting to default settings 
from constants import meshSettings

# to keep theme consistent
from theme_switcher import apply_theme_dialog_boxes
global_darkmode = True

loader = QUiLoader()

src = None

# set theme
def set_global_darkmode(darkmode):
    global global_darkmode
    global_darkmode = darkmode

# set the path of the src folder
def set_src(src_path):
    global src
    src = src_path
#---------------------------------------------------------
main_fluids = {"Air":{"density":1.225,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "Water":{"density":1000,"viscosity":1.002e-3,"specificHeat":4186,"thermalConductivity":0.606},
               "Nitrogen":{"density":1.165,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "Oxygen":{"density":1.429,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "Argon":{"density":1.784,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "CarbonDioxide":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "Steam":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "R134a":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "R22":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "R410a":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "R404a":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "R123":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "R245fa":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257},
               "R32":{"density":1.977,"viscosity":1.7894e-5,"specificHeat":1006.43,"thermalConductivity":0.0257}}

class sphereDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.surfaces = []
        self.centerX = 0.0
        self.centerY = 0.0
        self.centerZ = 0.0
        self.radius = 0.0
        self.created = False
    
    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\createSphereDialog.ui"
        ui_path = os.path.join(src, "createSphereDialog.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        #self.window.setWindowTitle("Sphere Dialog")
        self.prepare_events()
        # make text box for number only with floating points OK
        self.window.lineEditSphereX.setValidator(QDoubleValidator())
        self.window.lineEditSphereRadius.setValidator(QDoubleValidator(0.0,1e10,3))
        
    
    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
    
    def on_pushButtonOK_clicked(self):
        self.name = self.window.lineEditSphereName.text()
        self.centerX = float(self.window.lineEditSphereX.text())
        self.centerY = float(self.window.lineEditSphereY.text())
        self.centerZ = float(self.window.lineEditSphereZ.text())
        self.radius = float(self.window.lineEditSphereRadius.text())
        self.created = True
        
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        
        self.window.close()
        
    def __del__(self):
        pass

class cylinderDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.centerX = 0.0
        self.centerY = 0.0
        self.centerZ = 0.0
        self.radius = 0.0
        self.cyl_height = 0.0
        self.created = False
    
    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\createCylinderDialog.ui"
        ui_path = os.path.join(src, "createCylinderDialog.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        #self.window.setWindowTitle("Cylinder Dialog")
        self.prepare_events()
        # make text box for number only with floating points OK
        self.window.lineEditCylinderX.setValidator(QDoubleValidator())
        self.window.lineEditCylinderY.setValidator(QDoubleValidator())
        self.window.lineEditCylinderZ.setValidator(QDoubleValidator())
        self.window.lineEditCylinderRadius.setValidator(QDoubleValidator())
        self.window.lineEditCylinderHeight.setValidator(QDoubleValidator())
        
    
    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
    
    def on_pushButtonOK_clicked(self):
        self.name = self.window.lineEditCylinderName.text()
        self.centerX = float(self.window.lineEditCylinderX.text())
        self.centerY = float(self.window.lineEditCylinderY.text())
        self.centerZ = float(self.window.lineEditCylinderZ.text())
        self.radius = float(self.window.lineEditCylinderRadius.text())
        self.cyl_height = float(self.window.lineEditCylinderHeight.text())
        self.created = True
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        
        self.window.close()
        
    def __del__(self):
        pass

class boxDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.load_ui()
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.minX = 0.0
        self.maxX = 0.0
        self.minY = 0.0
        self.maxY = 0.0
        self.minZ = 0.0
        self.maxZ = 0.0
        self.created = False
    
    def load_ui(self):
        ui_path = os.path.join(src, "createBoxDialog.ui")
        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        #self.window.setWindowTitle("Box Dialog")
        self.prepare_events()
        # make text box for number only with floating points OK
        self.window.lineEditBoxMinX.setValidator(QDoubleValidator())
        self.window.lineEditBoxMaxX.setValidator(QDoubleValidator())
        self.window.lineEditBoxMinY.setValidator(QDoubleValidator())
        self.window.lineEditBoxMaxY.setValidator(QDoubleValidator())
        self.window.lineEditBoxMinZ.setValidator(QDoubleValidator())
        self.window.lineEditBoxMaxZ.setValidator(QDoubleValidator())
        
    
    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
    
    def on_pushButtonOK_clicked(self):
        self.name = self.window.lineEditBoxName.text()
        self.minX = float(self.window.lineEditBoxMinX.text())
        self.maxX = float(self.window.lineEditBoxMaxX.text())
        self.minY = float(self.window.lineEditBoxMinY.text())
        self.maxY = float(self.window.lineEditBoxMaxY.text())
        self.minZ = float(self.window.lineEditBoxMinZ.text())
        self.maxZ = float(self.window.lineEditBoxMaxZ.text())
        lx, ly, lz = self.maxX-self.minX, self.maxY-self.minY, self.maxZ-self.minZ
        # check if the box dimensions are positive
        if lx<=0 or ly<=0 or lz<=0:
            msg = QMessageBox()
            msg.setWindowTitle("Invalid Box Dimensions")
            msg.setText("Box dimensions must be positive")
            msg.exec()
            return
        self.created = True
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        
        self.window.close()
        
    def __del__(self):
        pass

class inputDialog(QDialog):
    def __init__(self, prompt="Enter Input",input_type="string"):
        super().__init__()
        
        self.input = None
        self.created = False
        self.prompt = prompt
        self.input_type = input_type
        self.load_ui()
        apply_theme_dialog_boxes(self.window, global_darkmode)

    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\inputDialog.ui"
        ui_path = os.path.join(src, "inputDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        self.window.setWindowTitle("Input Dialog")
        self.window.labelPrompt.setText(self.prompt)
        if(self.input_type=="int"):
            self.window.input.setValidator(QIntValidator())
        elif(self.input_type=="float"):
            self.window.input.setValidator(QDoubleValidator())
        else:
            pass
        self.prepare_events()
        

    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
    
    def on_pushButtonOK_clicked(self):
        
        self.input = self.window.input.text()
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        #print("Push Button Cancel Clicked")
        self.window.close()

class vectorInputDialog(QDialog):
    def __init__(self, prompt="Enter Input",input_type="float",initial_values=[0.0,0.0,0.0]):
        super().__init__()
        if initial_values != None:
            self.xx = initial_values[0]
            self.yy = initial_values[1]
            self.zz = initial_values[2]
        else:
            self.xx = 0
            self.yy = 0
            self.zz = 0
        self.OK_clicked = False
        
        self.created = False
        self.prompt = prompt
        self.input_type = input_type
        self.load_ui()
        apply_theme_dialog_boxes(self.window, global_darkmode)

    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\vectorInputDialog.ui"
        ui_path = os.path.join(src, "vectorInputDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
        self.window.setWindowTitle("Vector Input Dialog")
        self.window.labelPrompt.setText(self.prompt)
        if(self.input_type=="int"):
            self.window.lineEditX.setValidator(QIntValidator())
            self.window.lineEditY.setValidator(QIntValidator())
            self.window.lineEditZ.setValidator(QIntValidator())
            # show initial values
            self.window.lineEditX.setText(str(self.xx))
            self.window.lineEditY.setText(str(self.yy))
            self.window.lineEditZ.setText(str(self.zz))
        elif(self.input_type=="float"):
            self.window.lineEditX.setValidator(QDoubleValidator())
            self.window.lineEditY.setValidator(QDoubleValidator())
            self.window.lineEditZ.setValidator(QDoubleValidator())
            # show initial values
            self.window.lineEditX.setText(f"{self.xx:.3f}")
            self.window.lineEditY.setText(f"{self.yy:.3f}")
            self.window.lineEditZ.setText(f"{self.zz:.3f}")
        else:
            pass
        
        self.prepare_events()
        

    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
    
    def on_pushButtonOK_clicked(self):
        self.xx = float(self.window.lineEditX.text())
        self.yy = float(self.window.lineEditY.text())
        self.zz = float(self.window.lineEditZ.text())
        self.OK_clicked = True
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        #print("Push Button Cancel Clicked")
        self.window.close()

class STLDialog(QDialog):
    def __init__(self, stl_name="stl_file.stl",stlProperties=None):
        super().__init__()
        
        self.load_ui()
        global global_darkmode
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.stl_name = stl_name
        self.OK_clicked = False
        self.stl_properties = stlProperties
        self.set_initial_values()
        self.show_stl_properties()
        self.prepare_events()

    def show_stl_properties(self):
        purposeUsage = {"wall":"Wall","inlet":"Inlet","outlet":"Outlet","symmetry":"Symmetry",
                        "refinementSurface":"Refinement_Surface","refinementRegion":"Refinement_Region",
                        "cellZone":"Cell_Zone","baffles":"Baffle","interface":"Interface"}
        if self.stl_properties != None:
            purpose,refMin,refMax,featureEdges,featureLevel,nLayers,property,bounds = self.stl_properties
            usage = purposeUsage[purpose]

            
            if purpose in purposeUsage.keys():
                self.window.comboBoxUsage.setCurrentText(purposeUsage[purpose])
                self.changeUsage()
            else:
                self.window.comboBoxUsage.setCurrentText("Wall")
            if usage=="Inlet" or usage=="Outlet":
                self.window.lineEditRefMin.setText(str(refMin))
                self.window.lineEditRefMax.setText(str(refMax))
                self.window.lineEditRefLevel.setText("0")
                self.window.lineEditNLayers.setText("0")
            elif usage=="Refinement_Surface" or usage=="Refinement_Region":
                #self.window.lineEditRefMin.setText(str(refMin))
                #self.window.lineEditRefMax.setText(str(refMax))
                self.window.lineEditRefLevel.setText(str(property))
                #self.window.lineEditNLayers.setText("0")
            elif usage=="Cell_Zone":
                self.window.lineEditRefLevel.setText(str(property[0]))
                self.window.checkBoxAMI.setChecked(property[1])
            elif usage=="Symmetry":
                self.window.lineEditRefLevel.setText("0")
                self.window.lineEditNLayers.setText("0")
            else: 
                self.window.lineEditRefMin.setText(str(refMin))
                self.window.lineEditRefMax.setText(str(refMax))
                self.window.lineEditRefLevel.setText(str(refMax))
                self.window.lineEditNLayers.setText(str(nLayers))
                self.window.checkBoxEdgeRefine.setChecked(featureEdges)


    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\stlDialog.ui"
        ui_path = os.path.join(src, "stlDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()

    def set_initial_values(self):
        # change window title
        self.window.setWindowTitle(f"Patch Properties: {self.stl_name}")
        self.window.comboBoxUsage.addItem("Wall")
        self.window.comboBoxUsage.addItem("Inlet")
        self.window.comboBoxUsage.addItem("Outlet")
        self.window.comboBoxUsage.addItem("Symmetry")
        self.window.comboBoxUsage.addItem("Refinement_Surface")
        self.window.comboBoxUsage.addItem("Refinement_Region")
        self.window.comboBoxUsage.addItem("Cell_Zone")
        self.window.comboBoxUsage.addItem("Baffle")
        self.window.comboBoxUsage.addItem("Interface")
        self.window.lineEditRefMin.setText("1")
        self.window.lineEditRefMax.setText("1")
        self.window.lineEditRefMin.setValidator(QIntValidator())
        self.window.lineEditRefMax.setValidator(QIntValidator())
        self.window.lineEditRefLevel.setText("1")
        self.window.lineEditRefLevel.setValidator(QIntValidator())
        self.window.lineEditRefLevel.setEnabled(False)
        self.window.lineEditNLayers.setText("0")
        self.window.checkBoxAMI.setChecked(False)
        self.window.checkBoxAMI.setEnabled(False)
        # to store initial values
        # these will be used as default values if cancel is clicked
        self.refMin = int(self.window.lineEditRefMin.text())
        self.refMax = int(self.window.lineEditRefMax.text())
        self.refLevel = int(self.window.lineEditRefLevel.text())
        self.nLayers = int(self.window.lineEditNLayers.text())
        self.usage = self.window.comboBoxUsage.currentText()
        self.edgeRefine = self.window.checkBoxEdgeRefine.isChecked()
        self.ami = self.window.checkBoxAMI.isChecked()

    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
        self.window.comboBoxUsage.currentIndexChanged.connect(self.changeUsage)
        # when closed the dialog box
        #self.window.resizeEvent = self.show_closed
        #self.window.closeEvent = self.show_closed

    def show_closed(self):
        pass

    def on_pushButtonOK_clicked(self):
        #print("Push Button OK Clicked")
        self.refMin = int(self.window.lineEditRefMin.text())
        self.refMax = int(self.window.lineEditRefMax.text())
        self.refLevel = int(self.window.lineEditRefLevel.text())
        self.nLayers = int(self.window.lineEditNLayers.text())
        self.usage = self.window.comboBoxUsage.currentText()
        self.edgeRefine = self.window.checkBoxEdgeRefine.isChecked()
        self.ami = self.window.checkBoxAMI.isChecked()
        
        self.OK_clicked = True
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        self.OK_clicked = False
        self.window.close()

    def changeUsage(self):
        if(self.window.comboBoxUsage.currentText()=="Wall"):
            self.window.lineEditRefMin.setEnabled(True)
            self.window.lineEditRefMax.setEnabled(True)
            
            self.window.lineEditRefLevel.setEnabled(False)
            self.window.checkBoxAMI.setEnabled(False)
            self.window.checkBoxEdgeRefine.setEnabled(True)
        elif(self.window.comboBoxUsage.currentText()=="Baffle"):
            self.window.lineEditRefLevel.setEnabled(False)
            self.window.checkBoxAMI.setEnabled(False)
            self.window.checkBoxEdgeRefine.setEnabled(True)
        elif(self.window.comboBoxUsage.currentText()=="Inlet"):
            self.window.lineEditRefLevel.setEnabled(False)
            self.window.checkBoxAMI.setEnabled(False)
            self.window.checkBoxEdgeRefine.setEnabled(True)
            self.window.lineEditNLayers.setEnabled(False)
            self.window.lineEditNLayers.setText("0")
        elif(self.window.comboBoxUsage.currentText()=="Outlet"):
            self.window.lineEditRefLevel.setEnabled(False)
            self.window.checkBoxAMI.setEnabled(False)
            self.window.checkBoxEdgeRefine.setEnabled(True)
            self.window.lineEditNLayers.setEnabled(False)
            self.window.lineEditNLayers.setText("0")
        elif(self.window.comboBoxUsage.currentText()=="Symmetry"):
            self.window.lineEditRefLevel.setEnabled(False)
            self.window.checkBoxAMI.setEnabled(False)
            self.window.checkBoxEdgeRefine.setEnabled(False)
            self.window.lineEditRefMin.setEnabled(False)
            self.window.lineEditRefMax.setEnabled(False)
            self.window.lineEditNLayers.setEnabled(False)
            #self.window.lineEditReflevel.setEnabled(False)
        elif(self.window.comboBoxUsage.currentText()=="Refinement_Surface"):
            self.window.lineEditRefLevel.setEnabled(True)
            self.window.checkBoxAMI.setEnabled(False)
            self.window.checkBoxEdgeRefine.setEnabled(False)
            self.window.lineEditRefMin.setEnabled(False)
            self.window.lineEditRefMax.setEnabled(False)
        elif(self.window.comboBoxUsage.currentText()=="Refinement_Region"):
            self.window.lineEditRefLevel.setEnabled(True)
            self.window.checkBoxAMI.setEnabled(False)
            self.window.checkBoxEdgeRefine.setEnabled(False)
            self.window.lineEditNLayers.setEnabled(False)
            self.window.lineEditNLayers.setText("0")
            self.window.lineEditRefMin.setEnabled(False)
            self.window.lineEditRefMax.setEnabled(False)
        elif(self.window.comboBoxUsage.currentText()=="Cell_Zone"):
            self.window.lineEditRefLevel.setEnabled(True)
            self.window.checkBoxAMI.setEnabled(True)
            self.window.checkBoxEdgeRefine.setEnabled(True)
        else:
            self.window.lineEditRefLevel.setEnabled(False)
            self.window.checkBoxAMI.setEnabled(True)
            self.window.checkBoxEdgeRefine.setEnabled(True)
    
    def __del__(self):
        pass

class physicalModelsDialog(QDialog):
    def __init__(self,initialProperties=None):
        super().__init__()
        
        self.fluids = main_fluids
        self.fluid = "Air"
        self.rho = 1.225
        self.mu = 1.7894e-5
        self.cp = 1006.43
        self.nu = self.mu/self.rho
        
        self.initialProperties = None
        if initialProperties!=None:
            self.initialProperties = initialProperties
            self.fluid,self.rho,self.nu,self.cp = initialProperties
            self.mu = self.rho*self.nu
        self.load_ui()
        global global_darkmode
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.disable_advanced_physics()
        self.fill_fluid_types()
        
        self.prepare_events()
        self.OK_clicked = False
    

    def load_ui(self):
        ##ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\physicalPropertiesDialog.ui"
        ui_path = os.path.join(src, "physicalModelsDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()
    
    def disable_advanced_physics(self):
        self.window.checkBoxDynamicMesh.setEnabled(False)
        self.window.checkBoxMultiphase.setEnabled(False)
        self.window.checkBoxCompressibleFluid.setEnabled(False)
        self.window.checkBoxBoussinesqHeat.setEnabled(False)
        self.window.checkBoxCHT.setEnabled(False)

    def fill_fluid_types(self):
        fluid_names = list(self.fluids.keys())
        for fluid in fluid_names:
            self.window.comboBoxFluids.addItem(fluid)
        if self.initialProperties!=None:
            self.window.comboBoxFluids.addItem(self.fluid)
            self.window.comboBoxFluids.setCurrentText(self.fluid)
            self.window.lineEditRho.setText(str(self.rho))
            self.window.lineEditMu.setText(str(self.mu))
            self.window.lineEditCp.setText(str(self.cp))
        else:  
            self.window.comboBoxFluids.setCurrentText("Air")
            self.window.lineEditRho.setText(str(1.225))
            self.window.lineEditMu.setText(str(1.7894e-5))
            self.window.lineEditCp.setText(str(1006.43))
        

    def changeFluidProperties(self):
        fluid = self.window.comboBoxFluids.currentText()
        if fluid not in self.fluids.keys():
            # set default values for Air
            self.window.lineEditRho.setText(str(1.225))
            self.window.lineEditMu.setText(str(1.7894e-5))
            self.window.lineEditCp.setText(str(1006.43))
        self.window.lineEditRho.setText(str(self.fluids[fluid]["density"]))
        self.window.lineEditMu.setText(str(self.fluids[fluid]["viscosity"]))
        self.window.lineEditCp.setText(str(self.fluids[fluid]["specificHeat"]))
        
    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
        self.window.pushButtonApply.clicked.connect(self.on_pushButtonApply_clicked) 
        self.window.comboBoxFluids.currentIndexChanged.connect(self.changeFluidProperties)
       

    def on_pushButtonOK_clicked(self):
        #print("Push Button OK Clicked")
        self.on_pushButtonApply_clicked()
        self.OK_clicked = True
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        self.window.close()

    def on_pushButtonApply_clicked(self):
        
        self.rho = float(self.window.lineEditRho.text())
        self.mu = float(self.window.lineEditMu.text())
        self.cp = float(self.window.lineEditCp.text())
        self.nu = self.mu/self.rho
        #self.turbulenceOn = self.window.checkBoxTurbulenceOn.isChecked()
        #if self.turbulenceOn:
        #self.turbulence_model = self.window.comboBoxTurbulenceModels.currentText()
        #else:
        #    self.turbulence_model = "laminar"
        self.OK_clicked = True
        #self.window.close()

    def __del__(self):
        pass

class boundaryConditionDialog(QDialog):
    def __init__(self,boundary=None,external_boundary=False):
        super().__init__()
        self.boundary = boundary
        self.external_boundary = external_boundary # to check if the boundary is external
        # since external boundaries do not have names when parsed, we need to set the name
        # if external_boundary:
        #     self.boundary['name'] = bc_name
        self.purpose = boundary["purpose"]
        self.pressureType = "Gauge"
        self.velocityBC = None
        self.pressureBC = None
        self.turbulenceBC = None
        self.load_ui()
        global global_darkmode
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.setNameAndType()
        self.window.setWindowTitle(f"Boundary Condition: {self.boundary['name']} ({self.boundary['purpose']})")
        self.disable_unnecessary_fields()
        self.fill_input_types()
        self.OK_clicked = False
        self.window.lineEditU.setValidator(QDoubleValidator())
        self.window.lineEditV.setValidator(QDoubleValidator())
        self.window.lineEditW.setValidator(QDoubleValidator())
        self.window.lineEditPressure.setValidator(QDoubleValidator())
        self.window.lineEditK.setValidator(QDoubleValidator())
        self.window.lineEditEpsilon.setValidator(QDoubleValidator())
        self.window.lineEditOmega.setValidator(QDoubleValidator())
        self.prepare_events()

    def disable_unnecessary_fields(self):
        if(self.purpose=="wall"):
            self.window.lineEditU.setEnabled(False)
            self.window.lineEditV.setEnabled(False)
            self.window.lineEditW.setEnabled(False)
            self.window.lineEditVelMag.setEnabled(False)
            self.window.lineEditPressure.setEnabled(False)
            self.window.lineEditIntensity.setEnabled(False)
            self.window.lineEditLengthScale.setEnabled(False)
            self.window.lineEditViscosityRatio.setEnabled(False)
            self.window.lineEditHydraulicDia.setEnabled(False)
            self.window.lineEditK.setEnabled(False)
            self.window.lineEditEpsilon.setEnabled(False)
            self.window.lineEditOmega.setEnabled(False)
        elif(self.purpose=="symmetry" or self.purpose=="refinementRegion" or self.purpose=="refinementSurface"):
            self.window.lineEditU.setEnabled(False)
            self.window.lineEditV.setEnabled(False)
            self.window.lineEditW.setEnabled(False)
            self.window.lineEditVelMag.setEnabled(False)
            self.window.lineEditPressure.setEnabled(False)
            self.window.lineEditIntensity.setEnabled(False)
            self.window.lineEditLengthScale.setEnabled(False)
            self.window.lineEditViscosityRatio.setEnabled(False)
            self.window.lineEditHydraulicDia.setEnabled(False)
            self.window.lineEditK.setEnabled(False)
            self.window.lineEditEpsilon.setEnabled(False)
            self.window.lineEditOmega.setEnabled(False)
        elif(self.purpose=="outlet"):
            self.window.lineEditK.setEnabled(False)
            self.window.lineEditEpsilon.setEnabled(False)
            self.window.lineEditOmega.setEnabled(False)
        else:
            pass


    # to set the default values of the input fields based on the boundary type
    def fill_input_types(self):
        if(self.purpose=="wall"):
            self.fill_wall_bcs()
        elif(self.purpose=="inlet"):
            self.fill_inlet_bcs()
        elif(self.purpose=="outlet"):
            self.fill_outlet_bcs()
        else:
            pass

    def setNameAndType(self):
        self.window.labelBC.setText(f"{self.boundary['name']} ({self.boundary['purpose']})")

    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
        self.window.pushButtonApply.clicked.connect(self.on_pushButtonApply_clicked)
        self.window.comboBoxVelocityStyle.currentIndexChanged.connect(self.changeVelocityStyle)
        self.window.comboBoxPressure.currentIndexChanged.connect(self.changePressureType)

        
    def changeVelocityStyle(self):
        if(self.window.comboBoxVelocityStyle.currentText()=="Components"):
            self.window.lineEditVelMag.setEnabled(False)
            self.window.lineEditU.setEnabled(True)
            self.window.lineEditV.setEnabled(True)
            self.window.lineEditW.setEnabled(True)
        else:
            self.window.lineEditVelMag.setEnabled(True)  
            self.window.lineEditU.setEnabled(False)
            self.window.lineEditV.setEnabled(False)
            self.window.lineEditW.setEnabled(False) 

    def changePressureType(self):
        if(self.window.comboBoxPressure.currentText()=="Gauge Pressure"):
            self.pressureType = "Gauge"
        else:
            self.pressureType = "Total"

    def fill_wall_bcs(self):
        # clear all items
        self.window.comboBoxVelocityStyle.clear()
        self.window.comboBoxVelocityStyle.addItem("Non-slip")
        self.window.comboBoxVelocityStyle.addItem("Slip")
        self.window.comboBoxVelocityStyle.addItem("Moving Wall")
        self.window.comboBoxPressure.clear()
        self.window.comboBoxPressure.addItem("Zero Gradient")
        #self.window.comboBoxPressure.addItem("Fixed Flux Pressure")
        self.window.comboBoxTurbulence.clear()
        self.window.comboBoxTurbulence.addItem("Wall Functions")
        #self.window.comboBoxTurbulence.addItem("Resolve Wall (y+<1)")
        # disable unnecessary fields
        self.window.lineEditU.setEnabled(False)
        self.window.lineEditV.setEnabled(False)
        self.window.lineEditW.setEnabled(False)
        self.window.lineEditVelMag.setEnabled(False)
        self.window.lineEditPressure.setEnabled(False)
        self.window.lineEditIntensity.setEnabled(False)
        self.window.lineEditLengthScale.setEnabled(False)
        self.window.lineEditViscosityRatio.setEnabled(False)
        self.window.lineEditHydraulicDia.setEnabled(False)
        self.window.lineEditK.setEnabled(False)
        self.window.lineEditEpsilon.setEnabled(False)
        self.window.lineEditOmega.setEnabled(False)

    def fill_inlet_bcs(self):
        self.window.comboBoxVelocityStyle.clear()
        self.window.comboBoxVelocityStyle.addItem("Components")
        self.window.comboBoxVelocityStyle.addItem("Normal to boundary")
        #self.window.comboBoxVelocityStyle.addItem("Parabolic Profile")
        self.window.comboBoxPressure.clear()
        self.window.comboBoxPressure.addItem("Zero Gradient")
        self.window.comboBoxPressure.addItem("Fixed Flux Pressure")
        
        self.window.comboBoxTurbulence.clear()
        self.fill_turbulence_types()

        # disable unnecessary fields
        self.window.lineEditVelMag.setEnabled(False)
        u,v,w = self.boundary["property"][0],self.boundary["property"][1],self.boundary["property"][2]
        self.window.lineEditU.setText(str(u))
        self.window.lineEditV.setText(str(v))
        self.window.lineEditW.setText(str(w))
        self.window.lineEditPressure.setEnabled(False)


    def fill_outlet_bcs(self):
        self.window.comboBoxVelocityStyle.clear()
        self.window.comboBoxVelocityStyle.addItem("Zero Gradient")
        self.window.comboBoxVelocityStyle.addItem("Inlet Outlet")
        
        self.window.comboBoxPressure.clear()
        self.window.comboBoxPressure.addItem("Fixed Value")
        self.window.comboBoxPressure.addItem("Fixed Flux Pressure")
        self.window.comboBoxTurbulence.clear()
        self.window.comboBoxTurbulence.addItem("Zero Gradient")
        self.window.comboBoxTurbulence.addItem("Inlet Outlet")
        # disable unnecessary fields
        self.window.lineEditU.setEnabled(False)
        self.window.lineEditV.setEnabled(False)
        self.window.lineEditW.setEnabled(False)
        self.window.lineEditVelMag.setEnabled(False)
        self.window.lineEditK.setEnabled(False)
        self.window.lineEditEpsilon.setEnabled(False)
        self.window.lineEditOmega.setEnabled(False)

        # set default value for pressure
        self.window.lineEditPressure.setText("0")


    def fill_turbulence_types(self):
        self.window.comboBoxTurbulence.addItem("Intensity and Length Scale")
        self.window.comboBoxTurbulence.addItem("Intensity and Viscosity Ratio")
        self.window.comboBoxTurbulence.addItem("Intensity and Hydraulic Diameter")
        self.window.comboBoxTurbulence.addItem("Turbulent Kinetic Energy (k) and Specific Dissipation Rate (omega)")
        self.window.comboBoxTurbulence.addItem("Turbulent Kinetic Energy (k) and Dissipation Rate (epsilon)")
        # default values
        self.window.comboBoxTurbulence.setCurrentText("Intensity and Length Scale")
        self.window.lineEditIntensity.setEnabled(True)
        self.window.lineEditLengthScale.setEnabled(True)
        self.window.lineEditViscosityRatio.setEnabled(False)
        self.window.lineEditHydraulicDia.setEnabled(False)
        self.window.lineEditK.setEnabled(False)
        self.window.lineEditEpsilon.setEnabled(False)
        self.window.lineEditOmega.setEnabled(False)

    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\boundaryConditionDialog.ui"
        ui_path = os.path.join(src, "boundaryConditionDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()

    def on_pushButtonApply_clicked(self):
        #print("Push Button OK Clicked")
        self.OK_clicked = True
        velocity_style = self.window.comboBoxVelocityStyle.currentText()
        pressure_type = self.window.comboBoxPressure.currentText()
        if(velocity_style=="Components"):
            U = float(self.window.lineEditU.text())
            V = float(self.window.lineEditV.text())
            W = float(self.window.lineEditW.text())
            self.velocityBC = (U,V,W)
        if self.purpose=="inlet":
            if(velocity_style=="Components"):
                U = float(self.window.lineEditU.text())
                V = float(self.window.lineEditV.text())
                W = float(self.window.lineEditW.text())
                self.velocityBC = (U,V,W)
            else:
                self.velocityBC = (0,0,0)
            if(pressure_type=="Fixed Flux Pressure"):
                self.pressureBC = "fixedFluxPressure"
            else:
                self.pressureBC = "zeroGradientPressure"
        elif self.purpose=="outlet":
            if(velocity_style=="Zero Gradient"):
                self.velocityBC = "zeroGradient"
            else:
                self.velocityBC = "inletOutlet"
            self.pressureBC = self.window.lineEditPressure.text()
        elif self.purpose=="wall":
            if(velocity_style=="Non-slip"):
                self.velocityBC = "nonSlip"
            elif(velocity_style=="Slip"):
                self.velocityBC = "slip"
            else:
                self.velocityBC = "movingWall"
            self.pressureBC = "zeroGradient"
            self.turbulenceBC = "wallFunctions"
        #self.window.close()

    def on_pushButtonOK_clicked(self):
        self.on_pushButtonApply_clicked()
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        self.window.close()


    def __del__(self):
        pass

class numericalSettingsDialog(QDialog):
    def __init__(self,current_mode=0,numericalSettings=None,turbulenceModel="kOmegaSST",transient=False):
        super().__init__()
        self.turbulenceOn = True
        self.transient = transient
        self.turbulence_model = turbulenceModel
        self.modes = ["Balanced (Blended 2nd Order schemes)","Stablity Mode (1st Order schemes)","Accuracy Mode (2nd Order schemes)","Advanced Mode"]
        self.temporal_schemes = temporal_schemes #
        self.grad_schemes = grad_schemes
        self.div_schemes = div_schemes
        self.laplacian_schemes = laplacian_schemes
        
        
        self.OK_clicked = False
        
        # default values for numerical settings. 
        self.numericalSettings = numericalSettings
        self.current_mode = self.numericalSettings["mode"]
        
        self.load_ui()
        global global_darkmode
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.fill_comboBox_values()
        self.fill_turbulence_models()
        self.prepare_events()

    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
        self.window.pushButtonApply.clicked.connect(self.on_pushButtonApply_clicked)
        self.window.pushButtonDefault.clicked.connect(self.on_pushButtonDefault_clicked)
        self.window.comboBoxMode.currentIndexChanged.connect(self.readSettings)
        self.window.comboBoxTurbulenceModels.currentIndexChanged.connect(self.changeTurbulenceModel)
      
    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\numericDialog.ui"
        ui_path = os.path.join(src, "numericDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()

    def fill_comboBox_values(self):
        for mode in self.modes:
            self.window.comboBoxMode.addItem(mode)
        self.window.comboBoxMode.setCurrentIndex(self.current_mode)

        for scheme in self.grad_schemes.keys():
            self.window.comboBoxGradScheme.addItem(scheme)
        
        for scheme in self.div_schemes.keys():
            self.window.comboBoxDivScheme.addItem(scheme)

        self.window.comboBoxDivTurb.addItem("Gauss Upwind") 
        self.window.comboBoxDivTurb.addItem("Gauss Limited Linear")

        for scheme in self.laplacian_schemes.keys():
            self.window.comboBoxLaplacian.addItem(scheme)
       
        print("Transient",self.transient)
        if self.transient==False:
            self.window.comboBoxTemporal.addItem("Steady State")
        else:
            self.window.comboBoxTemporal.addItem("Euler")
            self.window.comboBoxTemporal.addItem("Backward Euler (2nd Order)")
            self.window.comboBoxTemporal.addItem("Crank-Nicolson (Blended 2nd Order)")
            self.window.comboBoxTemporal.addItem("Crank-Nicolson (2nd Order)")
        if self.current_mode==0 or self.current_mode==1 or self.current_mode==2:
            self.window.frame.setVisible(False)
        else:
            self.initAdvancedMode()
            self.window.frame.setVisible(True)
        
    def fill_turbulence_models(self):
        turbulence_models = ["laminar","kEpsilon","kOmegaSST","SpalartAllmaras","RNGkEpsilon"
                             ,"realizableKE",]
        for model in turbulence_models:
            self.window.comboBoxTurbulenceModels.addItem(model)
        if self.turbulence_model!=None:
            self.window.comboBoxTurbulenceModels.setCurrentText(self.turbulence_model)
        else:
            self.window.comboBoxTurbulenceModels.setCurrentIndex(2)

    def changeTurbulenceModel(self):
        self.turbulence_model = self.window.comboBoxTurbulenceModels.currentText()


    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
        self.window.pushButtonApply.clicked.connect(self.on_pushButtonApply_clicked)
        self.window.pushButtonDefault.clicked.connect(self.on_pushButtonDefault_clicked)
        self.window.comboBoxMode.currentIndexChanged.connect(self.readSettings)

    def on_pushButtonOK_clicked(self):
        #print("Push Button OK Clicked")
        self.on_pushButtonApply_clicked()
        self.print_numerical_settings()
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        self.window.close()

    def on_pushButtonDefault_clicked(self):
        #self.window.close()
        #print("Default Settings Choosen")
        self.window.comboBoxMode.setCurrentText("Balanced (Blended 2nd Order schemes)")
        self.current_mode = 0
        
        self.window.comboBoxTurbulenceModels.setCurrentText("kOmegaSST")
        self.readSettings()


    def on_pushButtonApply_clicked(self):
        self.OK_clicked = True
        #self.current_mode = self.window.comboBoxMode.currentIndex()
        self.turbulence_model = self.window.comboBoxTurbulenceModels.currentText()
        self.readSettings()
    
    def print_numerical_settings(self):
        print("\n----------------------Numerical Settings----------------------")
        print("ddtScheme",self.numericalSettings['ddtSchemes']['default'])
        print("grad",self.numericalSettings['gradSchemes']['default'])
        print("gradU",self.numericalSettings['gradSchemes']['grad(U)'])
        print("div",self.numericalSettings['divSchemes']['default'])
        print("div, convection",self.numericalSettings['divSchemes']['div(phi,U)'])
        print("div, k",self.numericalSettings['divSchemes']['div(phi,k)'])
        print("laplacian",self.numericalSettings['laplacianSchemes']['default'])
        print("snGrad",self.numericalSettings['snGradSchemes']['default'])
        print("----------------------------------------------------------------")
    """
    We have 3 basic modes: Balanced, Stability, Accuracy.
    This function will set the numerical schemes based on the mode selected.
    It will read the mode and set the numerical settings accordingly.
    """
    def readSettings(self):
        if(self.window.comboBoxMode.currentText()=="Balanced (Blended 2nd Order schemes)"):
            # First, hide the advanced settings
            self.window.frame.setVisible(False) 
            self.current_mode = 0
            self.numericalSettings['ddtSchemes']['default'] = "Euler"
            self.numericalSettings['gradSchemes']['default'] = "cellLimited Gauss linear 0.5"
            self.numericalSettings['gradSchemes']['grad(U)'] = "cellLimited Gauss linear 0.5"
            self.numericalSettings['divSchemes']['default'] = "Gauss linear"
            self.numericalSettings['divSchemes']['div(phi,U)'] = "Gauss linearUpwind grad(U)"
            self.numericalSettings['divSchemes']['div(phi,k)'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,epsilon)'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,omega)'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,nuTilda)'] = "Gauss upwind"

            self.numericalSettings['laplacianSchemes']['default'] = "Gauss linear limited corrected 0.5"
            self.numericalSettings['snGradSchemes']['default'] = "limited corrected 0.5"
            if self.transient==False:
                self.numericalSettings['ddtSchemes']['default'] = "steadyState"
                self.numericalSettings['divSchemes']['div(phi,U)'] = "bounded Gauss linearUpwind grad(U)"
                self.numericalSettings['divSchemes']['div(phi,k)'] = "bounded Gauss upwind"
                self.numericalSettings['divSchemes']['div(phi,epsilon)'] = "bounded Gauss upwind"
                self.numericalSettings['divSchemes']['div(phi,omega)'] = "bounded Gauss upwind"
                self.numericalSettings['divSchemes']['div(phi,nuTilda)'] = "bounded Gauss upwind"
        elif(self.window.comboBoxMode.currentText()=="Accuracy Mode (2nd Order schemes)"):
            self.window.frame.setVisible(False) 
            self.current_mode = 2
            self.numericalSettings['ddtSchemes']['default'] = "CrankNicolson 0.5"
            self.numericalSettings['gradSchemes']['default'] = "Gauss linear"
            self.numericalSettings['gradSchemes']['grad(U)'] = "Gauss linear"
            self.numericalSettings['divSchemes']['default'] = "Gauss linear"
            self.numericalSettings['divSchemes']['div(phi,U)'] = "Gauss linear"
            self.numericalSettings['divSchemes']['div(phi,k)'] = "Gauss limitedLinear 1"
            self.numericalSettings['divSchemes']['div(phi,epsilon)'] = "Gauss limitedLinear 1"
            self.numericalSettings['divSchemes']['div(phi,omega)'] = "Gauss limitedLinear 1"
            self.numericalSettings['divSchemes']['div(phi,nuTilda)'] = "Gauss limitedLinear 1"

            self.numericalSettings['laplacianSchemes']['default'] = "Gauss linear corrected"
            self.numericalSettings['snGradSchemes']['default'] = "corrected"
            if self.transient==False:
                self.numericalSettings['ddtSchemes']['default'] = "steadyState"
             
        elif(self.window.comboBoxMode.currentText()=="Stablity Mode (1st Order schemes)"):
            self.window.frame.setVisible(False) 
            self.current_mode = 1
            self.numericalSettings['ddtSchemes']['default'] = "Euler"
            self.numericalSettings['gradSchemes']['default'] = "cellLimited Gauss linear 1"
            self.numericalSettings['gradSchemes']['grad(U)'] = "cellLimited Gauss linear 1"
            self.numericalSettings['divSchemes']['default'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,U)'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,k)'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,epsilon)'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,omega)'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,nuTilda)'] = "Gauss upwind"
            self.numericalSettings['laplacianSchemes']['default'] = "Gauss linear limited corrected 0.333"
            self.numericalSettings['snGradSchemes']['default'] = "limited corrected 0.333"
            if self.transient==False:
                self.numericalSettings['ddtSchemes']['default'] = "steadyState"
                self.numericalSettings['divSchemes']['div(phi,U)'] = "bounded Gauss upwind"
                self.numericalSettings['divSchemes']['div(phi,k)'] = "bounded Gauss upwind"
                self.numericalSettings['divSchemes']['div(phi,epsilon)'] = "bounded Gauss upwind"
                self.numericalSettings['divSchemes']['div(phi,omega)'] = "bounded Gauss upwind"
                self.numericalSettings['divSchemes']['div(phi,nuTilda)'] = "bounded Gauss upwind"

        else:
            self.current_mode = 3
            # read the saved settings
            #self.initAdvancedMode()
            # Now show the advanced settings
            self.window.frame.setVisible(True)
            
            self.readAdvancedModeSettings()
        # finally, save the mode
        self.numericalSettings["mode"] = self.current_mode

    """
    Advanced Mode will allow the user to select the numerical schemes manually.
    This function will set the initial numerical schemes.
    """
    def initAdvancedMode(self):
        temporal_sheme = value_to_key(self.temporal_schemes,self.numericalSettings['ddtSchemes']['default'])
        grad_scheme = value_to_key(self.grad_schemes,self.numericalSettings['gradSchemes']['default'])
        div_scheme = value_to_key(self.div_schemes,self.numericalSettings['divSchemes']['default'])
        div_turb = value_to_key(self.div_schemes,self.numericalSettings['divSchemes']['div(phi,k)'])
        lap_scheme = value_to_key(self.laplacian_schemes,self.numericalSettings['laplacianSchemes']['default'])

        # grad_scheme = self.temporal_schemes[self.numericalSettings['ddtSchemes']['default']]
        # div_scheme = self.grad_schemes[self.numericalSettings['gradSchemes']['default']]
        # div_turb = self.div_schemes[self.numericalSettings['divSchemes']['div(phi,k)']]
        # lap_scheme = self.laplacian_schemes[self.numericalSettings['laplacianSchemes']['default']]
        self.window.comboBoxTemporal.setCurrentText(temporal_sheme)
        self.window.comboBoxGradScheme.setCurrentText(grad_scheme)
        self.window.comboBoxDivScheme.setCurrentText(div_scheme)
        self.window.comboBoxDivTurb.setCurrentText(div_turb)
        self.window.comboBoxLaplacian.setCurrentText(lap_scheme)

        # self.window.comboBoxDivScheme.setCurrentText(value_to_key(self.div_schemes,self.numericalSettings['divSchemes']['default']))
        # self.window.comboBoxDivTurb.setCurrentText(value_to_key(self.div_schemes,self.numericalSettings['divSchemes']['div(phi,k)']))
        # self.window.comboBoxLaplacian.setCurrentText(value_to_key(self.laplacian_schemes,self.numericalSettings['laplacianSchemes']['default']))
        # #self.window.comboBoxSnGrad.setCurrentText(value_to_key(self.numericalSettings['snGradSchemes']['default']))

    # In this mode, all the numerical settings are read from comboBoxes  
    def readAdvancedModeSettings(self):
        temp_sch = self.window.comboBoxTemporal.currentText()
        grad_sch = self.window.comboBoxGradScheme.currentText()
        div_sch = self.window.comboBoxDivScheme.currentText()
        lap_sch = self.window.comboBoxLaplacian.currentText()
        div_turb = self.window.comboBoxDivTurb.currentText()
       
        # check whether the selected scheme is available in the grad_schemes dictionary
        self.numericalSettings['ddtSchemes']['default'] = self.temporal_schemes[temp_sch]
        self.numericalSettings['gradSchemes']['default'] = self.grad_schemes[grad_sch]
        self.numericalSettings['gradSchemes']['grad(U)'] = self.grad_schemes[grad_sch]
        self.numericalSettings['divSchemes']['default'] = self.div_schemes[div_sch]
        if div_sch == "Gauss Linear" or div_sch == "Gauss Upwind":
            self.numericalSettings['divSchemes']['div(phi,U)'] = self.div_schemes[div_sch]
        else:
            self.numericalSettings['divSchemes']['div(phi,U)'] = self.div_schemes[div_sch]+" grad(U)"
        #self.numericalSettings['divSchemes']['div(phi,U)'] = self.div_schemes[div_sch]
        self.numericalSettings['divSchemes']['div(phi,k)'] = self.div_schemes[div_turb]
        self.numericalSettings['divSchemes']['div(phi,epsilon)'] = self.div_schemes[div_turb]
        self.numericalSettings['divSchemes']['div(phi,omega)'] = self.div_schemes[div_turb]
        self.numericalSettings['divSchemes']['div(phi,nuTilda)'] = self.div_schemes[div_turb]
        self.numericalSettings['laplacianSchemes']['default'] = self.laplacian_schemes[lap_sch] #"Gauss linear "+ self.window.comboBoxLaplacian.currentText()
        #self.numericalSettings['snGradSchemes']['default'] = self.window.comboBoxLaplacian.currentText()
        self.print_numerical_settings()
    

class controlsDialog(QDialog):
    def __init__(self,simulationSettings=None,parallelSettings=None,transient=False):
        super().__init__()
        self.OK_clicked = False
        self.transient = transient
        self.simulationSettings = simulationSettings
        self.parallelSettings = parallelSettings
        #print(self.simulationSettings)
        #print(self.parallelSettings)
        self.load_ui()
        self.set_input_types()
        self.fill_initial_values()
        self.fill_parallel_settings()
        global global_darkmode
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.prepare_events()

    def set_input_types(self):
        self.window.lineEditStartTime.setValidator(QDoubleValidator())
        self.window.lineEditEndTime.setValidator(QDoubleValidator())
        self.window.lineEditTimeStep.setValidator(QDoubleValidator())
        self.window.lineEditOutputInterval.setValidator(QDoubleValidator())
        self.window.lineEditWritePrecision.setValidator(QIntValidator())
        self.window.lineEdit_nProcs.setValidator(QIntValidator())
        self.window.lineEditX.setValidator(QIntValidator())
        self.window.lineEditY.setValidator(QIntValidator())
        self.window.lineEditZ.setValidator(QIntValidator())


    def change_parallel_settings(self):
        if(self.window.checkBoxParallel.isChecked()):
            self.window.lineEdit_nProcs.setEnabled(True)
            self.window.comboBoxDecompositionMethod.setEnabled(True)
            if(self.window.comboBoxDecompositionMethod.currentText()=="simple"):
                self.window.lineEditX.setEnabled(True)
                self.window.lineEditY.setEnabled(True)
                self.window.lineEditZ.setEnabled(True)
            else:
                self.window.lineEditX.setEnabled(False)
                self.window.lineEditY.setEnabled(False)
                self.window.lineEditZ.setEnabled(False)
        else:
            self.window.lineEdit_nProcs.setEnabled(False)
            self.window.comboBoxDecompositionMethod.setEnabled(False)
            self.window.lineEditX.setEnabled(False)
            self.window.lineEditY.setEnabled(False)
            self.window.lineEditZ.setEnabled(False)

    def fill_initial_values(self):
        self.window.comboBoxStartFrom.addItem("startTime")
        self.window.comboBoxStartFrom.addItem("latestTime")
        self.window.comboBoxStartFrom.addItem("firstTime")
        self.window.lineEditStartTime.setText(str(self.simulationSettings["startTime"]))
        self.window.lineEditEndTime.setText(str(self.simulationSettings["endTime"]))
        self.window.lineEditTimeStep.setText(str(self.simulationSettings["deltaT"]))
        self.window.lineEditOutputInterval.setText(str(self.simulationSettings["writeInterval"]))
        self.window.comboBoxWriteControl.addItem("timeStep")
        self.window.comboBoxWriteControl.addItem("runTime")
        self.window.comboBoxWriteControl.addItem("adjustableRunTime")
        self.window.comboBoxWriteControl.addItem("cpuTime")
        self.window.comboBoxWriteFormat.addItem("binary")
        self.window.comboBoxWriteFormat.addItem("ascii")
        self.window.comboBoxWriteControl.setCurrentText(self.simulationSettings["writeControl"])
        self.window.comboBoxWriteFormat.setCurrentText(self.simulationSettings["writeFormat"])
        self.window.lineEditWritePrecision.setText(str(self.simulationSettings["writePrecision"]))

    def fill_parallel_settings(self):
        if self.parallelSettings['parallel']==True:
            self.window.checkBoxParallel.setChecked(True)
        else:
            self.window.checkBoxParallel.setChecked(False)
        self.window.lineEdit_nProcs.setText(str(self.parallelSettings['numberOfSubdomains']))
        self.window.comboBoxDecompositionMethod.addItem("simple")
        self.window.comboBoxDecompositionMethod.addItem("hierarchical")
        self.window.comboBoxDecompositionMethod.addItem("scotch")

        if(self.parallelSettings['parallel']==False):
            self.window.lineEdit_nProcs.setEnabled(False)
            self.window.comboBoxDecompositionMethod.setEnabled(False)
            self.window.lineEditX.setEnabled(False)
            self.window.lineEditY.setEnabled(False)
            self.window.lineEditZ.setEnabled(False)
        else:
            self.window.lineEdit_nProcs.setEnabled(True)
            self.window.comboBoxDecompositionMethod.setEnabled(True)
            self.window.comboBoxDecompositionMethod.setCurrentText(self.parallelSettings['method'])
        
        if(self.parallelSettings['method']=="simple"):
            self.window.lineEditX.setEnabled(True)
            self.window.lineEditY.setEnabled(True)
            self.window.lineEditZ.setEnabled(True)
        else:
            self.window.lineEditX.setEnabled(False)
            self.window.lineEditY.setEnabled(False)
            self.window.lineEditZ.setEnabled(False)

    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\controlsDialog.ui"
        ui_path = os.path.join(src, "controlsDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()

    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
        self.window.pushButtonApply.clicked.connect(self.on_pushButtonApply_clicked)
        self.window.pushButtonDefault.clicked.connect(self.on_pushButtonDefault_clicked)
        self.window.checkBoxParallel.stateChanged.connect(self.change_parallel_settings)
        self.window.comboBoxDecompositionMethod.currentIndexChanged.connect(self.change_parallel_settings)
    
    def on_pushButtonOK_clicked(self):
        self.on_pushButtonApply_clicked()
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        self.window.close()

    def on_pushButtonApply_clicked(self):
        self.OK_clicked = True
        self.simulationSettings["startTime"] = self.window.lineEditStartTime.text()
        self.simulationSettings["endTime"] = self.window.lineEditEndTime.text()
        self.simulationSettings["deltaT"] = self.window.lineEditTimeStep.text()
        self.simulationSettings["writeInterval"] = self.window.lineEditOutputInterval.text()
        self.simulationSettings["writeControl"] = self.window.comboBoxWriteControl.currentText()
        self.simulationSettings["writePrecision"] = self.window.lineEditWritePrecision.text()
        self.simulationSettings["writeFormat"] = self.window.comboBoxWriteFormat.currentText()
        self.parallelSettings["parallel"] = self.window.checkBoxParallel.isChecked()
        self.parallelSettings["numberOfSubdomains"] = int(self.window.lineEdit_nProcs.text())
        self.parallelSettings["method"] = self.window.comboBoxDecompositionMethod.currentText()
        x = self.window.lineEditX.text()
        y = self.window.lineEditY.text()
        z = self.window.lineEditZ.text()
        
        
        if(self.parallelSettings["method"]=="simple"):
            x = int(x)
            y = int(y)
            z = int(z)
            if x*y*z!=self.parallelSettings["numberOfSubdomains"]:
                # show a warning message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Number of subdomains should be equal to x*y*z")
                msg.setWindowTitle("Warning")
                msg.exec_()
            
                return
            self.parallelSettings["x"] = x
            self.parallelSettings["y"] = y
            self.parallelSettings["z"] = z
        else:
            # Just dummy values. 
            self.parallelSettings["x"] = 1
            self.parallelSettings["y"] = 1
            self.parallelSettings["z"] = 1
        
        #self.window.close()

    def on_pushButtonDefault_clicked(self):
        self.set_to_default()

    def set_to_default(self):
        self.window.comboBoxWriteControl.setCurrentText("runTime")
        self.window.comboBoxWriteFormat.setCurrentText("binary")
        self.window.lineEditWritePrecision.setText("8")
        self.window.lineEditStartTime.setText("0")
        if self.transient==False:
            self.window.lineEditEndTime.setText("1000")
        
            self.window.lineEditTimeStep.setText("1")
            self.window.lineEditOutputInterval.setText("100")
        else:
            self.window.lineEditEndTime.setText("10")
            self.window.lineEditTimeStep.setText("0.005")
            self.window.lineEditOutputInterval.setText("0.1")
        self.window.checkBoxParallel.setChecked(True)
        self.window.lineEdit_nProcs.setText("4")
        self.window.comboBoxDecompositionMethod.setCurrentText("scotch")
        self.window.lineEditX.setText("2")
        self.window.lineEditY.setText("2")
        self.window.lineEditZ.setText("1")

    def __del__(self):
        pass

class postProcessDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.OK_clicked = False
        
        self.load_ui()
        self.fill_initial_values()
        global global_darkmode
        apply_theme_dialog_boxes(self.window, global_darkmode)

    def load_ui(self):
        #ui_path = r"C:\Users\Ridwa\Desktop\CFD\01_CFD_Software_Development\SplashCaseCreatorCFD\src\controlsDialog.ui"
        ui_path = os.path.join(src, "postProcessDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()

    def fill_initial_values(self):
        self.window.comboBoxFOType.addItem("Forces")
        self.window.comboBoxFOType.addItem("Force Coefficients")
        self.window.comboBoxFOType.addItem("Mass Flow")
        self.window.comboBoxFOType.addItem("Probes")

class advancedMeshDialog(QDialog):
    def __init__(self,meshSettings=None):
        super().__init__()
        self.OK_clicked = False
        self.meshSettings = meshSettings
        self.load_ui()
        global global_darkmode
        apply_theme_dialog_boxes(self.window, global_darkmode)
        self.prepare_events()
        self.set_input_types()
        self.initialize_values()


    def load_ui(self):
        ui_path = os.path.join(src, "advancedMeshSettingsDialog.ui")
        ui_file = QFile(ui_path)
        #ui_file = QFile("inputDialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file, None)
        ui_file.close()

    def set_input_types(self):
        # castellated mesh controls
        self.window.lineEditMaxLocalCells.setValidator(QIntValidator())
        self.window.lineEditMaxGlobalCells.setValidator(QIntValidator())
        self.window.lineEditCellsBetweenLevels.setValidator(QIntValidator())
        self.window.lineEditResolveFeatureAngle.setValidator(QDoubleValidator())
        # snapping controls
        self.window.lineEditTolerance.setValidator(QDoubleValidator())
        self.window.lineEditSolverIter.setValidator(QIntValidator())
        self.window.lineEditRelaxIter.setValidator(QIntValidator())
        self.window.lineEditFeatureIter.setValidator(QIntValidator())
        # layer controls
        self.window.lineEditExpansionRatio.setValidator(QDoubleValidator())
        self.window.lineEditFinalLayer.setValidator(QDoubleValidator())
        self.window.lineEditLayerFeatureAngle.setValidator(QDoubleValidator())
        self.window.lineEditLayerIter.setValidator(QIntValidator())
        self.window.lineEditLayerOuterIter.setValidator(QIntValidator())
        # mesh quality metrics
        self.window.lineEditMaxNonOrtho.setValidator(QDoubleValidator())
        self.window.lineEditBoundarySkewness.setValidator(QDoubleValidator())
        self.window.lineEditInternalSkewness.setValidator(QDoubleValidator())
        self.window.lineEditConcave.setValidator(QDoubleValidator())
        self.window.lineEditDeterminant.setValidator(QDoubleValidator())

    def read_values(self):
        self.meshSettings['castellatedMeshControls']["maxLocalCells"] = int(self.window.lineEditMaxLocalCells.text())
        self.meshSettings['castellatedMeshControls']["maxGlobalCells"] = int(self.window.lineEditMaxGlobalCells.text())
        self.meshSettings['castellatedMeshControls']["nCellsBetweenLevels"] = int(self.window.lineEditCellsBetweenLevels.text())
        self.meshSettings['castellatedMeshControls']["resolveFeatureAngle"] = float(self.window.lineEditResolveFeatureAngle.text())

        self.meshSettings['snapControls']["tolerance"] = float(self.window.lineEditTolerance.text())
        self.meshSettings['snapControls']["nSolveIter"] = int(self.window.lineEditSolverIter.text())
        self.meshSettings['snapControls']["nRelaxIter"] = int(self.window.lineEditRelaxIter.text())
        self.meshSettings['snapControls']["nFeatureSnapIter"] = int(self.window.lineEditFeatureIter.text())

        self.meshSettings['addLayersControls']["expansionRatio"] = float(self.window.lineEditExpansionRatio.text())
        self.meshSettings['addLayersControls']["finalLayerThickness"] = float(self.window.lineEditFinalLayer.text())
        self.meshSettings['addLayersControls']["featureAngle"] = float(self.window.lineEditLayerFeatureAngle.text())
        self.meshSettings['addLayersControls']["nLayerIter"] = int(self.window.lineEditLayerIter.text())
        self.meshSettings['addLayersControls']["nOuterIter"] = int(self.window.lineEditLayerOuterIter.text())

        self.meshSettings['meshQualityControls']["maxNonOrtho"] = float(self.window.lineEditMaxNonOrtho.text())
        self.meshSettings['meshQualityControls']["maxBoundarySkewness"] = float(self.window.lineEditBoundarySkewness.text())
        self.meshSettings['meshQualityControls']["maxInternalSkewness"] = float(self.window.lineEditInternalSkewness.text())
        self.meshSettings['meshQualityControls']["maxConcave"] = float(self.window.lineEditConcave.text())
        self.meshSettings['meshQualityControls']["minDeterminant"] = float(self.window.lineEditDeterminant.text())

        self.meshSettings['snappyHexSteps']['castellatedMesh'] = self.window.checkBoxCastellated.isChecked()
        self.meshSettings['snappyHexSteps']['snap'] = self.window.checkBoxSnap.isChecked()
        self.meshSettings['snappyHexSteps']['addLayers'] = self.window.checkBoxAddLayers.isChecked()

        if self.window.radioButtonImplicitSnap.isChecked():
            self.meshSettings['snapControls']["explicitFeatureSnap"] = False
            self.meshSettings['snapControls']["implicitFeatureSnap"] = True
        else:
            self.meshSettings['snapControls']["explicitFeatureSnap"] = True
            self.meshSettings['snapControls']["implicitFeatureSnap"] = False
        self.meshSettings['addLayersControls']["relativeSizes"] = self.window.checkBoxRelativeSizes.isChecked()

        # general mesh settings
        self.meshSettings['maxCellSize'] = float(self.window.lineEditMeshSize.text())


    def assign_values(self,meshSettings):
        # to avoid unncessary changes to the original meshSettings dictionary, we will create a copy of it.
        meshSettings['snappyHexSteps']['castellatedMesh'] = self.meshSettings['snappyHexSteps']['castellatedMesh']
        meshSettings['snappyHexSteps']['snap'] = self.meshSettings['snappyHexSteps']['snap']
        meshSettings['snappyHexSteps']['addLayers'] = self.meshSettings['snappyHexSteps']['addLayers']

        meshSettings['castellatedMeshControls']["maxLocalCells"] = self.meshSettings['castellatedMeshControls']["maxLocalCells"]
        meshSettings['castellatedMeshControls']["maxGlobalCells"] = self.meshSettings['castellatedMeshControls']["maxGlobalCells"]
        meshSettings['castellatedMeshControls']["nCellsBetweenLevels"] = self.meshSettings['castellatedMeshControls']["nCellsBetweenLevels"]
        meshSettings['castellatedMeshControls']["resolveFeatureAngle"] = self.meshSettings['castellatedMeshControls']["resolveFeatureAngle"]
        meshSettings['snapControls']["tolerance"] = self.meshSettings['snapControls']["tolerance"]
        meshSettings['snapControls']["nSolveIter"] = self.meshSettings['snapControls']["nSolveIter"]
        meshSettings['snapControls']["nRelaxIter"] = self.meshSettings['snapControls']["nRelaxIter"]
        meshSettings['snapControls']["nFeatureSnapIter"] = self.meshSettings['snapControls']["nFeatureSnapIter"]
        meshSettings['addLayersControls']["expansionRatio"] = self.meshSettings['addLayersControls']["expansionRatio"]
        meshSettings['addLayersControls']["finalLayerThickness"] = self.meshSettings['addLayersControls']["finalLayerThickness"]
        meshSettings['addLayersControls']["featureAngle"] = self.meshSettings['addLayersControls']["featureAngle"]
        meshSettings['addLayersControls']["nLayerIter"] = self.meshSettings['addLayersControls']["nLayerIter"]
        meshSettings['addLayersControls']["nOuterIter"] = self.meshSettings['addLayersControls']["nOuterIter"]
        meshSettings['meshQualityControls']["maxNonOrtho"] = self.meshSettings['meshQualityControls']["maxNonOrtho"]
        meshSettings['meshQualityControls']["maxBoundarySkewness"] = self.meshSettings['meshQualityControls']["maxBoundarySkewness"]
        meshSettings['meshQualityControls']["maxInternalSkewness"] = self.meshSettings['meshQualityControls']["maxInternalSkewness"]
        meshSettings['meshQualityControls']["maxConcave"] = self.meshSettings['meshQualityControls']["maxConcave"]
        meshSettings['meshQualityControls']["minDeterminant"] = self.meshSettings['meshQualityControls']["minDeterminant"]
        return meshSettings
    
    # this is to set default values for the mesh settings
    def assign_default_values(self):    
        global meshSettings
        self.meshSettings['snappyHexSteps']['castellatedMesh'] = meshSettings['snappyHexSteps']['castellatedMesh']
        self.meshSettings['snappyHexSteps']['snap'] = meshSettings['snappyHexSteps']['snap']
        self.meshSettings['snappyHexSteps']['addLayers'] = meshSettings['snappyHexSteps']['addLayers']
        self.meshSettings['castellatedMeshControls']["maxLocalCells"] = meshSettings['castellatedMeshControls']["maxLocalCells"]
        self.meshSettings['castellatedMeshControls']["maxGlobalCells"] = meshSettings['castellatedMeshControls']["maxGlobalCells"]
        self.meshSettings['castellatedMeshControls']["nCellsBetweenLevels"] = meshSettings['castellatedMeshControls']["nCellsBetweenLevels"]
        self.meshSettings['castellatedMeshControls']["resolveFeatureAngle"] = meshSettings['castellatedMeshControls']["resolveFeatureAngle"]
        self.meshSettings['snapControls']["tolerance"] = meshSettings['snapControls']["tolerance"]
        self.meshSettings['snapControls']["nSolveIter"] = meshSettings['snapControls']["nSolveIter"]
        self.meshSettings['snapControls']["nRelaxIter"] = meshSettings['snapControls']["nRelaxIter"]
        self.meshSettings['snapControls']["nFeatureSnapIter"] = meshSettings['snapControls']["nFeatureSnapIter"]
        self.meshSettings['addLayersControls']["expansionRatio"] = meshSettings['addLayersControls']["expansionRatio"]
        self.meshSettings['addLayersControls']["finalLayerThickness"] = meshSettings['addLayersControls']["finalLayerThickness"]
        self.meshSettings['addLayersControls']["featureAngle"] = meshSettings['addLayersControls']["featureAngle"]
        self.meshSettings['addLayersControls']["nLayerIter"] = meshSettings['addLayersControls']["nLayerIter"]
        self.meshSettings['addLayersControls']["nOuterIter"] = meshSettings['addLayersControls']["nOuterIter"]
        self.meshSettings['meshQualityControls']["maxNonOrtho"] = meshSettings['meshQualityControls']["maxNonOrtho"]
        self.meshSettings['meshQualityControls']["maxBoundarySkewness"] = meshSettings['meshQualityControls']["maxBoundarySkewness"]
        self.meshSettings['meshQualityControls']["maxInternalSkewness"] = meshSettings['meshQualityControls']["maxInternalSkewness"]
        self.meshSettings['meshQualityControls']["maxConcave"] = meshSettings['meshQualityControls']["maxConcave"]
        self.meshSettings['meshQualityControls']["minDeterminant"] = meshSettings['meshQualityControls']["minDeterminant"]
        
    def prepare_events(self):
        self.window.pushButtonOK.clicked.connect(self.on_pushButtonOK_clicked)
        self.window.pushButtonCancel.clicked.connect(self.on_pushButtonCancel_clicked)
        self.window.pushButtonDefault.clicked.connect(self.on_pushButtonDefault_clicked)
        self.window.pushButtonApply.clicked.connect(self.on_pushButtonApply_clicked)

    def on_pushButtonOK_clicked(self):
        self.OK_clicked = True
        self.on_pushButtonApply_clicked()
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        self.window.close()

    def on_pushButtonDefault_clicked(self):
        self.OK_clicked = False
        # load default values
        self.assign_default_values()
        self.initialize_values()
        #self.window.close()

    def on_pushButtonApply_clicked(self):   
        self.OK_clicked = True
        self.read_values()

    
    def initialize_values(self):
        self.window.checkBoxCastellated.setChecked(self.meshSettings['snappyHexSteps']['castellatedMesh'])
        self.window.checkBoxSnap.setChecked(self.meshSettings['snappyHexSteps']['snap'])
        self.window.checkBoxAddLayers.setChecked(self.meshSettings['snappyHexSteps']['addLayers'])

        self.window.lineEditMaxLocalCells.setText(str(self.meshSettings['castellatedMeshControls']["maxLocalCells"]))
        self.window.lineEditMaxGlobalCells.setText(str(self.meshSettings['castellatedMeshControls']["maxGlobalCells"]))
        self.window.lineEditCellsBetweenLevels.setText(str(self.meshSettings['castellatedMeshControls']["nCellsBetweenLevels"]))
        self.window.lineEditResolveFeatureAngle.setText(str(self.meshSettings['castellatedMeshControls']["resolveFeatureAngle"]))

        self.window.lineEditTolerance.setText(str(self.meshSettings['snapControls']["tolerance"]))
        self.window.lineEditSolverIter.setText(str(self.meshSettings['snapControls']["nSolveIter"]))
        self.window.lineEditRelaxIter.setText(str(self.meshSettings['snapControls']["nRelaxIter"]))
        self.window.lineEditFeatureIter.setText(str(self.meshSettings['snapControls']["nFeatureSnapIter"]))

        self.window.lineEditExpansionRatio.setText(str(self.meshSettings['addLayersControls']["expansionRatio"]))
        self.window.lineEditFinalLayer.setText(str(self.meshSettings['addLayersControls']["finalLayerThickness"]))
        self.window.lineEditLayerFeatureAngle.setText(str(self.meshSettings['addLayersControls']["featureAngle"]))
        self.window.lineEditLayerIter.setText(str(self.meshSettings['addLayersControls']["nLayerIter"]))
        self.window.lineEditLayerOuterIter.setText(str(self.meshSettings['addLayersControls']["nOuterIter"]))

        self.window.lineEditMaxNonOrtho.setText(str(self.meshSettings['meshQualityControls']["maxNonOrtho"]))
        self.window.lineEditBoundarySkewness.setText(str(self.meshSettings['meshQualityControls']["maxBoundarySkewness"]))
        self.window.lineEditInternalSkewness.setText(str(self.meshSettings['meshQualityControls']["maxInternalSkewness"]))
        self.window.lineEditConcave.setText(str(self.meshSettings['meshQualityControls']["maxConcave"]))
        self.window.lineEditDeterminant.setText(str(self.meshSettings['meshQualityControls']["minDeterminant"]))

        # general settings
        self.window.lineEditMeshSize.setText(str(self.meshSettings['maxCellSize']))
        self.window.checkBoxHalfDomain.setChecked(self.meshSettings['halfModel'])

        if self.meshSettings['snapControls']["implicitFeatureSnap"]:
            self.window.radioButtonImplicitSnap.setChecked(True)
        else:
            self.window.radioButtonExplicitSnap.setChecked(True)

        self.window.checkBoxRelativeSizes.setChecked(self.meshSettings['addLayersControls']["relativeSizes"])

        
    def __del__(self):
        pass
#---------------------------------------------------------
# Driver function for different dialog boxes
#---------------------------------------------------------

def yesNoDialogDriver(prompt="Save changes to current case files",title="Save Changes"):
    msg = QMessageBox().question(None, title, prompt, QMessageBox.Yes | QMessageBox.No)
    #msg.exec_()
    if(msg==QMessageBox.Yes):
        return True
    else:
        return False
    
def yesNoCancelDialogDriver(prompt="Save changes to current case files",title="Save Changes"):
    msg = QMessageBox().question(None, title, prompt, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
    #msg.exec_()
    if(msg==QMessageBox.Yes):
        return 1
    elif(msg==QMessageBox.No):
        return -1
    else:
        return 0

def sphereDialogDriver():
    dialog = sphereDialog()
    dialog.window.exec()
    dialog.window.show()
    x,y,z = dialog.centerX,dialog.centerY,dialog.centerZ
    r = dialog.radius
    name = dialog.name
    if(dialog.created==False):
        #print("Sphere Dialog Box Closed")
        return None
    return (name,x,y,z,r)

def cylinderDialogDriver():
    dialog = cylinderDialog()
    dialog.window.exec()
    dialog.window.show()
    x,y,z = dialog.centerX,dialog.centerY,dialog.centerZ
    r = dialog.radius
    h = dialog.cyl_height
    name = dialog.name
    if(dialog.created==False):
        return None
    return (name,x,y,z,r,h)

def boxDialogDriver():
    dialog = boxDialog()
    dialog.window.exec()
    dialog.window.show()
    minx,miny,minz = dialog.minX,dialog.minY,dialog.minZ
    maxx,maxy,maxz = dialog.maxX,dialog.maxY,dialog.maxZ
    name = dialog.name
    if(dialog.created==False):
        return None
    return (name,minx,miny,minz,maxx,maxy,maxz)

def inputDialogDriver(prompt="Enter Input",input_type="string"):
    dialog = inputDialog(prompt=prompt,input_type=input_type)
    dialog.window.exec()
    dialog.window.show()
    input = dialog.input
    if(input==None):
        return None
    return input

def vectorInputDialogDriver(prompt="Enter Input",input_type="float",initial_values=[0.0,0.0,0.0]):
    dialog = vectorInputDialog(prompt=prompt,input_type=input_type,initial_values=initial_values)
    dialog.window.exec()
    dialog.window.show()
    xx,yy,zz = dialog.xx,dialog.yy,dialog.zz
    if dialog.OK_clicked==False:
        return None
    return (xx,yy,zz)
    

def STLDialogDriver(stl_name="stl_file.stl",stlProperties=None):
    dialog = STLDialog(stl_name=stl_name,stlProperties=stlProperties)
    dialog.window.exec()
    dialog.window.show()
    OK_clicked = dialog.OK_clicked
    if(OK_clicked==False):
        return None

    refMin = dialog.refMin
    refMax = dialog.refMax
    refLevel = dialog.refLevel
    nLayers = dialog.nLayers
    usage = dialog.usage
    edgeRefine = dialog.edgeRefine
    ami = dialog.ami
    if(dialog.usage=="Inlet"):
        # just give a temporary value. 
        # The actual value will be changed in Boundary Condition Dialog
        U = (1,0,0)
        return (refMin,refMax,refLevel,nLayers,usage,edgeRefine,ami,U)
    return (refMin,refMax,refLevel,nLayers,usage,edgeRefine,ami,None)

def physicalModelsDialogDriver(initialProperties=None):
    dialog = physicalModelsDialog(initialProperties)
    dialog.window.exec()
    dialog.window.show()
    OK_clicked = dialog.OK_clicked
    if(OK_clicked==False):
        return None
    rho = dialog.rho
    mu = dialog.mu
    cp = dialog.cp
    nu = dialog.nu
    fluid = dialog.window.comboBoxFluids.currentText()
    
    return (fluid,rho,nu,cp,)

def boundaryConditionDialogDriver(boundary=None,external_boundary=False):
    #print(boundary)
    dialog = boundaryConditionDialog(boundary,external_boundary)
    dialog.window.exec()
    dialog.window.show()
    OK_clicked = dialog.OK_clicked
    if(OK_clicked==False):
        return None
    velocityBC = dialog.velocityBC
    pressureBC = dialog.pressureBC
    turbulenceBC = dialog.turbulenceBC
    return (velocityBC,pressureBC,turbulenceBC)

def numericsDialogDriver(current_mode=0,numericalSettings=None,turbulenceModel=None,transient=False):
    #print("Turbulence Model",turbulenceModel)
    dialog = numericalSettingsDialog(current_mode=current_mode,numericalSettings=numericalSettings,turbulenceModel=turbulenceModel,transient=transient)
    dialog.window.exec()
    dialog.window.show()
    #turbulence_models = {"laminar":"laminar","k-epsilon":"kEpsilon","kOmegaSST":"kOmegaSST","SpalartAllmaras":"SpalartAllmaras",
    #                     "RNG_kEpsilon":"RNGkEpsilon","realizableKE":"realizableKE"}
    
    return dialog.current_mode,dialog.numericalSettings,dialog.turbulence_model

def controlsDialogDriver(simulationSettings=None,parallelSettings=None,transient=False):
    dialog = controlsDialog(simulationSettings,parallelSettings,transient=transient)
    dialog.window.exec()
    dialog.window.show()
    return dialog.simulationSettings,dialog.parallelSettings

def meshPointDialogDriver(locationInMesh=None):
    meshPoint = vectorInputDialogDriver(prompt="Enter locationInMesh point",input_type="float",initial_values=locationInMesh)
    if(meshPoint==None):
        return None
    x,y,z = meshPoint
    return [x,y,z]

def postProcessDialogDriver():
    dialog = postProcessDialog()
    dialog.window.exec()
    dialog.window.show()

def advancedMeshDialogDriver(meshSettings=None):
    dialog = advancedMeshDialog(meshSettings=meshSettings)
    dialog.window.exec()
    dialog.window.show()
    return dialog.meshSettings

def main():
    pass

if __name__ == "__main__":
    main()
