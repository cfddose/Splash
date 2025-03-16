import sys
import math
import os
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


# Utility functions for writing STL files
def write_box_stl(file_path, width, length, height):
    vertices = [
        (0, 0, 0), (width, 0, 0), (width, length, 0), (0, length, 0),
        (0, 0, height), (width, 0, height), (width, length, height), (0, length, height)
    ]
    faces = [
        (0, 1, 2), (0, 2, 3),  # Bottom face
        (4, 5, 6), (4, 6, 7),  # Top face
        (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)  # Sides
    ]

    with open(file_path, 'w') as file:
        file.write("solid box\n")
        for face in faces:
            v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            file.write(f"  facet normal 0 0 0\n")
            file.write("    outer loop\n")
            file.write(f"      vertex {v1[0]} {v1[1]} {v1[2]}\n")
            file.write(f"      vertex {v2[0]} {v2[1]} {v2[2]}\n")
            file.write(f"      vertex {v3[0]} {v3[1]} {v3[2]}\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")
        file.write("endsolid box\n")
        
        
def write_cylinder_stl(file_path, radius, height, segments):
    """Writes an STL file for a cylinder."""
    with open(file_path, 'w') as file:
        file.write("solid cylinder\n")
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * (i + 1) / segments
            x1, y1 = radius * math.cos(angle1), radius * math.sin(angle1)
            x2, y2 = radius * math.cos(angle2), radius * math.sin(angle2)

            # Bottom face
            file.write("  facet normal 0 0 -1\n")
            file.write("    outer loop\n")
            file.write(f"      vertex 0 0 0\n")
            file.write(f"      vertex {x1} {y1} 0\n")
            file.write(f"      vertex {x2} {y2} 0\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")

            # Top face
            file.write("  facet normal 0 0 1\n")
            file.write("    outer loop\n")
            file.write(f"      vertex 0 0 {height}\n")
            file.write(f"      vertex {x2} {y2} {height}\n")
            file.write(f"      vertex {x1} {y1} {height}\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")

            # Side face
            file.write("  facet normal 0 0 0\n")
            file.write("    outer loop\n")
            file.write(f"      vertex {x1} {y1} 0\n")
            file.write(f"      vertex {x2} {y2} 0\n")
            file.write(f"      vertex {x1} {y1} {height}\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")

            file.write("  facet normal 0 0 0\n")
            file.write("    outer loop\n")
            file.write(f"      vertex {x2} {y2} 0\n")
            file.write(f"      vertex {x2} {y2} {height}\n")
            file.write(f"      vertex {x1} {y1} {height}\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")
        file.write("endsolid cylinder\n")


def write_sphere_stl(file_path, radius, segments):
    """Writes an STL file for a sphere."""
    with open(file_path, 'w') as file:
        file.write("solid sphere\n")
        for i in range(segments):
            theta1 = math.pi * i / segments
            theta2 = math.pi * (i + 1) / segments

            for j in range(segments * 2):
                phi1 = 2 * math.pi * j / (segments * 2)
                phi2 = 2 * math.pi * (j + 1) / (segments * 2)

                # Four vertices of the current quad
                x1, y1, z1 = (radius * math.sin(theta1) * math.cos(phi1),
                              radius * math.sin(theta1) * math.sin(phi1),
                              radius * math.cos(theta1))
                x2, y2, z2 = (radius * math.sin(theta1) * math.cos(phi2),
                              radius * math.sin(theta1) * math.sin(phi2),
                              radius * math.cos(theta1))
                x3, y3, z3 = (radius * math.sin(theta2) * math.cos(phi1),
                              radius * math.sin(theta2) * math.sin(phi1),
                              radius * math.cos(theta2))
                x4, y4, z4 = (radius * math.sin(theta2) * math.cos(phi2),
                              radius * math.sin(theta2) * math.sin(phi2),
                              radius * math.cos(theta2))

                # Two triangles per quad
                file.write("  facet normal 0 0 0\n")
                file.write("    outer loop\n")
                file.write(f"      vertex {x1} {y1} {z1}\n")
                file.write(f"      vertex {x2} {y2} {z2}\n")
                file.write(f"      vertex {x3} {y3} {z3}\n")
                file.write("    endloop\n")
                file.write("  endfacet\n")

                file.write("  facet normal 0 0 0\n")
                file.write("    outer loop\n")
                file.write(f"      vertex {x2} {y2} {z2}\n")
                file.write(f"      vertex {x4} {y4} {z4}\n")
                file.write(f"      vertex {x3} {y3} {z3}\n")
                file.write("    endloop\n")
                file.write("  endfacet\n")
        file.write("endsolid sphere\n")


# Main Application Class
class ShapeSTLApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("3D Shape STL Generator")
        self.setGeometry(100, 100, 500, 400)

        # Main Layout
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Header
        header = QLabel("3D Shape STL Generator")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(header)

        # Shape Selection
        shape_section = QHBoxLayout()
        shape_label = QLabel("Shape:")
        shape_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.shape_selector = QComboBox()
        self.shape_selector.addItems(["Box", "Cylinder", "Sphere"])
        self.shape_selector.currentTextChanged.connect(self.update_inputs)
        shape_section.addWidget(shape_label)
        shape_section.addWidget(self.shape_selector)
        layout.addLayout(shape_section)

        # Resolution Selection
        resolution_section = QHBoxLayout()
        resolution_label = QLabel("Resolution:")
        resolution_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.resolution_selector = QComboBox()
        self.resolution_selector.addItems(["Low", "Medium", "High"])
        resolution_section.addWidget(resolution_label)
        resolution_section.addWidget(self.resolution_selector)
        layout.addLayout(resolution_section)

        # Input Fields
        self.inputs_layout = QFormLayout()
        self.update_inputs()
        layout.addLayout(self.inputs_layout)

        # Buttons
        self.generate_button = QPushButton("Generate STL")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """)
        self.generate_button.clicked.connect(self.generate_stl)
        layout.addWidget(self.generate_button)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: green;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def update_inputs(self):
        # Clear existing inputs
        while self.inputs_layout.rowCount() > 0:
            self.inputs_layout.removeRow(0)

        # Add input fields based on shape
        shape = self.shape_selector.currentText()
        if shape == "Box":
            self.width_input = QLineEdit()
            self.length_input = QLineEdit()
            self.height_input = QLineEdit()
            self.inputs_layout.addRow("Width (m):", self.width_input)
            self.inputs_layout.addRow("Length (m):", self.length_input)
            self.inputs_layout.addRow("Height (m):", self.height_input)
        elif shape == "Cylinder":
            self.radius_input = QLineEdit()
            self.height_input = QLineEdit()
            self.inputs_layout.addRow("Radius (m):", self.radius_input)
            self.inputs_layout.addRow("Height (m):", self.height_input)
        elif shape == "Sphere":
            self.radius_input = QLineEdit()
            self.inputs_layout.addRow("Radius (m):", self.radius_input)

    def generate_stl(self):
        shape = self.shape_selector.currentText()
        resolution = self.resolution_selector.currentText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save STL File", "", "STL Files (*.stl)")

        if not file_path:
            QMessageBox.warning(self, "File Error", "No file selected for saving.")
            return

        if not file_path.endswith(".stl"):
            file_path += ".stl"

        segments = {"Low": 12, "Medium": 36, "High": 72}[resolution]

        try:
            if shape == "Box":
                # Retrieve input values for Box
                width = float(self.width_input.text())
                length = float(self.length_input.text())
                height = float(self.height_input.text())
                write_box_stl(file_path, width, length, height)
            elif shape == "Cylinder":
                # Retrieve input values for Cylinder
                radius = float(self.radius_input.text())
                height = float(self.height_input.text())
                write_cylinder_stl(file_path, radius, height, segments)
            elif shape == "Sphere":
                # Retrieve input values for Sphere
                radius = float(self.radius_input.text())
                write_sphere_stl(file_path, radius, segments)
            else:
                QMessageBox.critical(self, "Shape Error", "Unknown shape selected.")
                return

            # Confirm file save
            if os.path.exists(file_path):
                self.status_label.setText(f"STL file successfully saved at {file_path}")
            else:
                QMessageBox.critical(self, "File Error", "Failed to save the STL file. Please try again.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")


# Run the Application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = ShapeSTLApp()
    main_window.show()
    sys.exit(app.exec())
