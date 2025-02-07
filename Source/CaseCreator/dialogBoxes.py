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
        self.window.setWindowTitle(f"Mesh Refimenent: {self.stl_name}")
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
            self.window.lineEditReflevel.setEnabled(False)
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
    def __init__(self,boundary=None):
        super().__init__()
        self.boundary = boundary
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
        self.temporal_schemes = {"Steady State":"steadyState","Euler":"Euler","Backward Euler (2nd Order)":"backward","Crank-Nicolson (Blended 2nd Order)":"crankNicolson 0.5","Crank-Nicolson (2nd Order)":"crankNicolson 1.0"}
        self.grad_schemes = grad_schemes
        self.div_schemes = div_schemes
        self.laplacian_schemes = laplacian_schemes
        self.current_mode = current_mode
        
        self.OK_clicked = False
        
        # default values for numerical settings. 
        self.numericalSettings = numericalSettings
        if numericalSettings!=None:
            if "basicMode" in numericalSettings.keys():
                self.basicMode = numericalSettings["basicMode"]
            else:
                self.basicMode = True
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
        self.window.comboBoxMode.currentIndexChanged.connect(self.changeMode)
        self.window.comboBoxTurbulenceModels.currentIndexChanged.connect(self.changeTurbulenceModel)
        
        # These correspond to the changes in advanced mode
        self.window.comboBoxTemporal.currentIndexChanged.connect(self.setAdvancedMode)
        self.window.comboBoxGradScheme.currentIndexChanged.connect(self.setAdvancedMode)
        self.window.comboBoxDivScheme.currentIndexChanged.connect(self.setAdvancedMode)
        self.window.comboBoxDivTurb.currentIndexChanged.connect(self.setAdvancedMode)
        self.window.comboBoxLaplacian.currentIndexChanged.connect(self.setAdvancedMode)
  

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
        #self.window.comboBoxGradScheme.addItem("Gauss linear")
        #self.window.comboBoxGradScheme.addItem("Gauss Linear (Cell Limited)")
        #self.window.comboBoxGradScheme.addItem("Gauss Linear (Cell MD Limited)")
        #self.window.comboBoxGradScheme.addItem("Gauss Linear (Face Limited)")
        #self.window.comboBoxGradScheme.addItem("Gauss Linear (Face MD Limited)")
        #self.window.comboBoxGradScheme.addItem("Least Squares")

        for scheme in self.div_schemes.keys():
            self.window.comboBoxDivScheme.addItem(scheme)

        #self.window.comboBoxDivScheme.addItem("Gauss Linear")
        #self.window.comboBoxDivScheme.addItem("Gauss Linear Upwind")
        #self.window.comboBoxDivScheme.addItem("Gauss Upwind")  
        #self.window.comboBoxDivScheme.addItem("Gauss LUST")      
        #self.window.comboBoxDivScheme.addItem("Gauss Linear Limited")
        #self.window.comboBoxDivScheme.addItem("Gauss Linear LimitedV")

        #self.window.comboBoxGradScheme.addItem("grad(U)")

        self.window.comboBoxDivTurb.addItem("Gauss Upwind") 
        self.window.comboBoxDivTurb.addItem("Gauss Limited Linear")

        for scheme in self.laplacian_schemes.keys():
            self.window.comboBoxLaplacian.addItem(scheme)
        #self.window.comboBoxLaplacian.addItem("corrected")
        
        #self.window.comboBoxLaplacian.addItem("limited 0.333")
        #self.window.comboBoxLaplacian.addItem("limited 0.666")
        #self.window.comboBoxLaplacian.addItem("limited 1.0")
        print("Transient",self.transient)
        if self.transient==False:
            self.window.comboBoxTemporal.addItem("Steady State")
        else:
            self.window.comboBoxTemporal.addItem("Euler")
            self.window.comboBoxTemporal.addItem("Backward Euler (2nd Order)")
            self.window.comboBoxTemporal.addItem("Crank-Nicolson (Blended 2nd Order)")
            self.window.comboBoxTemporal.addItem("Crank-Nicolson (2nd Order)")
        if self.current_mode==0 or self.current_mode==1 or self.current_mode==2:
            self.setBasicMode()
            self.window.frame.setVisible(False)
        else:
            self.setAdvancedMode()
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
        self.window.comboBoxMode.currentIndexChanged.connect(self.changeMode)

    def on_pushButtonOK_clicked(self):
        #print("Push Button OK Clicked")
        self.on_pushButtonApply_clicked()
        self.window.close()

    def on_pushButtonCancel_clicked(self):
        self.window.close()

    def on_pushButtonDefault_clicked(self):
        #self.window.close()
        #print("Default Settings Choosen")
        self.window.comboBoxMode.setCurrentText("Balanced (Blended 2nd Order schemes)")
        self.window.comboBoxTurbulenceModels.setCurrentText("kOmegaSST")
        self.setBasicMode()


    def on_pushButtonApply_clicked(self):
        self.OK_clicked = True
        self.current_mode = self.window.comboBoxMode.currentIndex()
        self.turbulence_model = self.window.comboBoxTurbulenceModels.currentText()
        # if advanced mode is selected, then we need to set the numerical schemes
        if self.current_mode==3:
            #print("Advanced Mode Settings Used")
            self.setAdvancedMode()
        #self.print_numerical_settings()
    
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
    """
    def setBasicMode(self):
        self.basicMode = True
        self.numericalSettings['basicMode'] = True
        if(self.window.comboBoxMode.currentText()=="Balanced (Blended 2nd Order schemes)"):
            #print("Balanced Mode")
            #self.print_numerical_settings()
            self.numericalSettings['ddtSchemes']['default'] = "Euler"
            self.numericalSettings['gradSchemes']['default'] = "cellLimited Gauss linear 1"
            self.numericalSettings['gradSchemes']['grad(U)'] = "cellLimited Gauss linear 1"
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
            self.numericalSettings['ddtSchemes']['default'] = "CrankNicolson 0.5"
            self.numericalSettings['gradSchemes']['default'] = "Gauss linear"
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
            self.numericalSettings['ddtSchemes']['default'] = "Euler"
            self.numericalSettings['gradSchemes']['default'] = "cellLimited Gauss linear 1"
            self.numericalSettings['gradSchemes']['grad(U)'] = "cellLimited Gauss linear 1"
            self.numericalSettings['divSchemes']['default'] = "Gauss upwind"
            self.numericalSettings['divSchemes']['div(phi,U)'] = "Gauss upwind"
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
            self.setAdvancedMode()
            #print("Advanced Mode")

    """
    Advanced Mode will allow the user to select the numerical schemes manually.
    This function will set the initial numerical schemes.
    """
    def initAdvancedMode(self):
        self.window.comboBoxTemporal.setCurrentText(value_to_key(self.temporal_schemes,self.numericalSettings['ddtSchemes']['default']))
        self.window.comboBoxGradScheme.setCurrentText(value_to_key(self.grad_schemes,self.numericalSettings['gradSchemes']['default']))
        self.window.comboBoxDivScheme.setCurrentText(value_to_key(self.div_schemes,self.numericalSettings['divSchemes']['default']))
        self.window.comboBoxLaplacian.setCurrentText(value_to_key(self.laplacian_schemes,self.numericalSettings['laplacianSchemes']['default']))
        if(self.numericalSettings['divSchemes']['div(phi,k)']=="Gauss Linear Limited"):
            self.window.comboBoxDivTurb.setCurrentText("Gauss Linear Limited")
        else:
            self.window.comboBoxDivTurb.setCurrentText("Gauss Upwind")
        #self.window.comboBoxDivTurb.setCurrentText("Gauss upwind")
        
    def setAdvancedMode(self):

        self.basicMode = False
        self.numericalSettings['basicMode'] = False
        #self.initAdvancedMode() # show current numerical schemes
        self.numericalSettings['ddtSchemes']['default'] = self.temporal_schemes[self.window.comboBoxTemporal.currentText()]
        grad_sch = self.window.comboBoxGradScheme.currentText()
        div_sch = self.window.comboBoxDivScheme.currentText()
        lap_sch = self.window.comboBoxLaplacian.currentText()
        div_turb = self.window.comboBoxDivTurb.currentText()
        #print("Current Mode: ",self.window.comboBoxMode.currentText())
        #print(grad_sch,div_sch,lap_sch,div_turb)
        # check whether the selected scheme is available in the grad_schemes dictionary
        """
        if grad_sch in self.grad_schemes.keys():
            self.numericalSettings['gradSchemes']['default'] = self.grad_schemes[grad_sch]
            self.numericalSettings['gradSchemes']['grad(U)'] = self.grad_schemes[grad_sch]
        else:
            self.numericalSettings['gradSchemes']['default'] = "Gauss linear"
            self.numericalSettings['gradSchemes']['grad(U)'] = "cellLimited Gauss linear 1"
       
        if div_sch in self.div_schemes.keys():
            self.numericalSettings['divSchemes']['default'] = self.div_schemes[div_sch]
        else:
            self.numericalSettings['divSchemes']['default'] = "Gauss linear"
        """
        self.numericalSettings['gradSchemes']['default'] = self.grad_schemes[grad_sch]
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
        self.numericalSettings['snGradSchemes']['default'] = self.window.comboBoxLaplacian.currentText()
        #self.print_numerical_settings()
    
    def changeMode(self):
        if(self.window.comboBoxMode.currentText()=="Advanced Mode"):
            self.window.frame.setVisible(True)
            self.initAdvancedMode()
            self.setAdvancedMode()
        else:
            self.window.frame.setVisible(False) 
            self.setBasicMode()

    def assign_changes(self):
        pass

    def __del__(self):
        pass

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
    if(dialog.created==False):
        #print("Sphere Dialog Box Closed")
        return None
    return (x,y,z,r)

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

def boundaryConditionDialogDriver(boundary=None):
    #print(boundary)
    dialog = boundaryConditionDialog(boundary)
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
    meshPoint = vectorInputDialogDriver(prompt="Enter mesh point",input_type="float",initial_values=locationInMesh)
    if(meshPoint==None):
        return None
    x,y,z = meshPoint
    return [x,y,z]

def postProcessDialogDriver():
    dialog = postProcessDialog()
    dialog.window.exec()
    dialog.window.show()

def main():
    pass

if __name__ == "__main__":
    main()
