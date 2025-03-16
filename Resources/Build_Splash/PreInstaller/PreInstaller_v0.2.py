import os
import subprocess
import sys
import time
#from PySide6.QtWidgets import (QApplication, QVBoxLayout, QCheckBox, QPushButton, QLabel, QDialog, QMessageBox, QProgressBar, QTextEdit, QHBoxLayout, QLineEdit, QScrollArea, QWidget, QFrame)
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QMovie
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QScrollArea, QWidget  
from PySide6.QtCore import Qt, QThread, Signal, QSize
    
# Global definition for OpenFOAM packages
OPENFOAM_PACKAGES = [
    ("OF_Foundation_v11", "OpenFOAM Foundation v11 (Required)"),
    ("OF_ESI_openfoam2306-default", "OpenFOAM ESI v2306 (Required)"),
    ("OF_Foundation_v8", "OpenFOAM Foundation v8"),
    ("OF_Foundation_v9", "OpenFOAM Foundation v9"),
    ("OF_Foundation_v10", "OpenFOAM Foundation v10"),
    ("OF_Foundation_v12", "OpenFOAM Foundation v12"),
    ("OF_ESI_openfoam2206-default", "OpenFOAM ESI v2206"),
    ("OF_ESI_openfoam2312-default", "OpenFOAM ESI v2312"),
    ("OF_ESI_openfoam2406-default", "OpenFOAM ESI v2406 (Required)"),
]

class InstallationWorker(QThread):
    progress = Signal(int)  # Signal to update progress
    log_message = Signal(str)  # Signal to update the log terminal
    error = Signal(str)  # Signal to report errors
    finished = Signal()  # Signal when installation is complete

    def __init__(self, packages, openfoam_versions, sudo_password):
        super().__init__()
        self.packages = packages
        self.openfoam_versions = openfoam_versions
        self.sudo_password = sudo_password
        self.start_time = None
        self.errors = []  # Track errors
        
    def run(self):
        self.start_time = time.time()
        total_steps = len(self.packages) + len(self.openfoam_versions) + 2  # +2 for repositories and APT update
        step = 0

        try:
            self.log_message.emit("Adding required PPAs and repositories...")
            self.add_repositories()
            step += 1
            self.progress.emit(step)
            
            self.log_message.emit("PPAs and repositories added successfully.")

            self.log_message.emit("Updating APT package list...")
            self.run_with_sudo(["apt-get", "update"], shell=False)
            step += 1
            self.progress.emit(step)

            self.log_message.emit("APT package list updated successfully.")

            for version in self.openfoam_versions:
                self.log_message.emit(f"Installing OpenFOAM version: {version}...")
                self.install_openfoam(version)
                step += 1
                self.progress.emit(step)

            for package in self.packages:
                self.log_message.emit(f"Installing package: {package}...")
                self.install_package(package)
                step += 1
                self.progress.emit(step)

        except Exception as e:
            self.log_message.emit(str(e))
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def install_package(self, package):
        try:
            # Define known alternatives for missing packages
            alternatives = {
                "libxcb-cursor0": "libxcb-cursor-dev",
                "libx11-xcb-dev": "libx11-dev",
                "libxcb-render0-dev": "libxcb-render0",
                "grace": "grace",  # Direct installation
                "x11-apps": "x11-utils",
                "meld": "meld"  # Direct installation
            }

            # Special handling for Python packages
            if package in ["scipy", "PyQt5"]:
                self.log_message.emit(f"Installing {package} with pip as fallback...")
                try:
                    # Try installing with pip
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        text=True
                    )
                except subprocess.CalledProcessError:
                    # Fallback installation for scipy using apt
                    if package == "scipy":
                        self.log_message.emit("Trying fallback method for scipy...")
                        self.run_with_sudo(["apt-get", "install", "-y", "python3-pip"])
                        subprocess.run(
                            [sys.executable, "-m", "pip", "install", "numpy", "scipy"],
                            check=True,
                            text=True
                        )
                    elif package == "PyQt5":
                        self.log_message.emit("Trying fallback method for PyQt5...")
                        self.run_with_sudo(["apt-get", "install", "-y", "python3-pyqt5"])
                self.log_message.emit(f"{package} installed successfully.")
                return  # Skip to avoid using alternatives for these packages

            if package in alternatives:
                self.log_message.emit(f"Installing {package} or its alternative: {alternatives[package]}...")
                self.run_with_sudo(["apt-get", "install", "-y", alternatives[package]])
            else:
                self.run_with_sudo(["apt-get", "install", "-y", package])
            self.log_message.emit(f"{package} (or alternative) installed successfully.")
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Failed to install {package}: {str(e)}")
            raise Exception(f"Error installing {package}: {str(e)}")
        
    def add_repositories(self):
        total_repos = len(self.openfoam_versions) + len(self.packages)
        progress_increment = 100 / total_repos

        repositories = [
            {
                "name": "Kitware",
                "repo": "deb [arch=amd64 signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ focal main",
                "gpg_key_url": "https://apt.kitware.com/keys/kitware-archive-latest.asc",
                "list_file": "/etc/apt/sources.list.d/kitware.list",
                "keyring_file": "/usr/share/keyrings/kitware-archive-keyring.gpg"
            },
            {
                "name": "OpenFOAM Foundation",
                "commands": [
                    'sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc"',
                    "sudo add-apt-repository -y http://dl.openfoam.org/ubuntu"
                ]
            },
            {
                "name": "OpenFOAM ESI",
                "commands": [
                    "wget -q -O - https://dl.openfoam.com/add-debian-repo.sh | sudo bash"
                ]
            },
        ]

        for index, repo_info in enumerate(repositories, start=1):
            try:
                self.log_message.emit(f"Configuring repository: {repo_info['name']}...")
                # Handle repositories with GPG key and repo URL
                if "gpg_key_url" in repo_info:
                    if not os.path.exists(repo_info["keyring_file"]):
                        self.log_message.emit(f"Adding GPG key for {repo_info['name']}...")
                        subprocess.run(
                            f"wget -qO - {repo_info['gpg_key_url']} | sudo gpg --dearmor -o {repo_info['keyring_file']}",
                            shell=True, check=True
                        )
                    else:
                        self.log_message.emit(f"GPG key for {repo_info['name']} already exists.")

                    if not os.path.exists(repo_info["list_file"]):
                        self.log_message.emit(f"Adding repository for {repo_info['name']}...")
                        subprocess.run(
                            f'echo "{repo_info["repo"]}" | sudo tee {repo_info["list_file"]}',
                            shell=True, check=True
                        )
                elif "commands" in repo_info:
                    for cmd in repo_info["commands"]:
                        self.log_message.emit(f"Executing command for {repo_info['name']}: {cmd}")
                        subprocess.run(cmd, shell=True, check=True)

                self.progress.emit(int(progress_increment * index))
                self.log_message.emit(f"Repository added: {repo_info['name']}")
                self.progress.emit(index)  # Increment progress for each repository
            except subprocess.CalledProcessError as e:
                self.log_message.emit(f"Failed to configure repository: {repo_info['name']}. Error: {e}")
                self.errors.append(f"Failed to configure repository: {repo_info['name']}")
            
    def install_openfoam(self, version):
        total_foam_versions = len(self.openfoam_versions)
        progress_increment = 100 / total_foam_versions

        try:
            self.log_message.emit("Setting up OpenFOAM repository...")
            repo_setup_cmd = "curl -s https://dl.openfoam.com/add-debian-repo.sh | sudo bash"
            self.run_with_sudo(repo_setup_cmd, shell=True)

            self.log_message.emit("Updating package lists...")
            self.run_with_sudo(["apt-get", "update"])

            package_name = version.split("_")[-1]
            if "Foundation" in version:
                package_name = package_name.replace("v", "")
                package_name = f"openfoam{package_name}"
            elif "ESI" in version:
                package_name = package_name
            else:
                raise ValueError(f"Unrecognized OpenFOAM version format: {version}")

            self.log_message.emit(f"Installing OpenFOAM package: {package_name}")
            self.run_with_sudo(["apt-get", "install", "-y", package_name])
            self.progress.emit(int(progress_increment * (self.openfoam_versions.index(version) + 1)))
        except subprocess.CalledProcessError as e:
            self.log_message.emit(f"Error configuring OpenFOAM: {e}")
            self.errors.append(f"Failed to configure OpenFOAM version: {version}")
            raise Exception(f"Failed to configure OpenFOAM version {version}.")

    def run_with_sudo(self, command, shell=False, **kwargs):
        try:
            # Ensure command is correctly formatted based on shell usage
            if shell and isinstance(command, list):
                command = ' '.join(command)
            
            # Log the command being run
            self.log_message.emit(f"Running command: {command if isinstance(command, str) else ' '.join(command)}")

            # Prefix the command with sudo and set the environment variable
            full_command = f"DEBIAN_FRONTEND=noninteractive {command if isinstance(command, str) else ' '.join(command)}"
            
            process = subprocess.run(
                ["sudo"] + full_command.split() if not shell else f"sudo {full_command}",
                shell=shell,  # Use shell only if necessary
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **kwargs
            )
            self.log_message.emit(process.stdout)  # Log the output
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {e.stderr.strip()}"
            self.log_message.emit(error_msg)
            raise Exception(error_msg)
        
    def get_total_time(self):
        return time.time() - self.start_time if self.start_time else 0

# ----------------------
# Splash Installer Class
# ---------------------- 
class SplashInstaller(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Splash Pre-Installer v0.2")
        self.setGeometry(100, 100, 800, 1200) # last 2 entries to resize

        self.include_openfoam = True
        self.sudo_password = ""
        self.setup_ui()
        
    def setup_ui(self):
        # Create a scrollable area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)  # Enable resizing

        # Create a central widget for the scroll area
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("../Logos/simulitica_icon_logo.png") # FLAG: Path
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(200, 100, Qt.KeepAspectRatio))
        else:
            logo_label.setText("Splash Logo Placeholder")
            logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Title Label 
        title_label = QLabel("Splash Pre-requisite List")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(14)  
        title_label.setFont(title_font)
        # Set the label text color to green
        title_label.setStyleSheet("color: grey;")
        layout.addWidget(title_label)

        # Password Field with Show/Hide Button
        password_layout = QHBoxLayout()
        self.password_label = QLabel("Enter your sudo password:")
        layout.addWidget(self.password_label)

        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_field)

        self.show_password_button = QPushButton("Show")
        self.show_password_button.setCheckable(True)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_button)
        layout.addLayout(password_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        layout.addWidget(separator)

        # Required Packages Label 
        required_label = QLabel("Required Packages")
        required_label.setAlignment(Qt.AlignLeft)
        foam_font = required_label.font()
        foam_font.setBold(True)
        foam_font.setPointSize(12) 
        required_label.setFont(foam_font)
        required_label.setStyleSheet("color: black;")
        layout.addWidget(required_label)

        # Required Packages
        self.required_packages = [
            ("paraview", "Scientific data analysis and visualization"),
            ("freecad", "3D CAD modeler"),
            ("gmsh", "3D finite element grid generator"),
            ("curl", "Command-line tool for data transfer"),
            ("git", "Version control system"),
            ("python3-tk", "Python Tkinter library"),
            ("python3-pip", "Python package installer"),
            ("python3-matplotlib", "Python plotting library"),
            ("libxcb-cursor0", "Qt xcb dependencies"),
            ("libx11-xcb-dev", "X11 to XCB library"),
            ("libxcb-render0-dev", "XCB rendering library"),
            ("grace", "2D plotting software"),
            ("x11-apps", "X11 applications for GUI"),

        ]

        self.required_checkboxes = []
        for pkg, desc in self.required_packages:
            checkbox = QCheckBox(f"{pkg}: {desc}")
            checkbox.setChecked(True)
            checkbox.setEnabled(False)
            self.required_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        layout.addWidget(separator)

        # Optional Packages Label 
        optional_label = QLabel("Optional Packages")
        optional_label.setAlignment(Qt.AlignLeft)
        foam_font = optional_label.font()
        foam_font.setBold(True)
        foam_font.setPointSize(12) 
        optional_label.setFont(foam_font)
        optional_label.setStyleSheet("color: blue;")
        layout.addWidget(optional_label)
        
        # Optional Packages
        self.optional_packages = [
            ("vim", "Text editor"),
            ("numpy-stl", "Python library for STL files"),
            ("scipy", "Scientific computing library"),
            ("PyQt5", "Python bindings for Qt"),
            ("cloc", "Counts lines of code in a project"),
            ("shellcheck", "Shell script analysis tool"),
            ("htop", "Interactive process viewer for Unix systems"),
            ("ffmpeg", "Multimedia framework for audio and video processing"),
            ("vlc", "Media player"),
            ("meld", "Visual diff and merge tool"),
        ]

        self.optional_checkboxes = []
        for pkg, desc in self.optional_packages:
            checkbox = QCheckBox(f"{pkg}: {desc}")
            self.optional_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        layout.addWidget(separator)

        # OpenFOAM Packages Label 
        foam_label = QLabel("OpenFOAM Packages")
        foam_label.setAlignment(Qt.AlignLeft)
        foam_font = foam_label.font()
        foam_font.setBold(True)
        foam_font.setPointSize(12)  
        foam_label.setFont(foam_font)
        foam_label.setStyleSheet("color: green;")
        layout.addWidget(foam_label)

        self.openfoam_checkboxes = []
        for pkg, desc in OPENFOAM_PACKAGES:
            checkbox = QCheckBox(f"{pkg}: {desc}")
            if "Required" in desc:
                checkbox.setChecked(True)
                checkbox.setEnabled(False)
            self.openfoam_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # OpenFOAM Toggle
        self.openfoam_toggle = QCheckBox("Include OpenFOAM Installation")
        self.openfoam_toggle.setChecked(True)
        self.openfoam_toggle.toggled.connect(self.toggle_openfoam)
        layout.addWidget(self.openfoam_toggle)

        # Loading Animation
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_animation = QMovie("../GIF/spin5.gif") 

        # Resize the GIF
        self.loading_animation.setScaledSize(QSize(140, 100))  # 240, 180 for spin7 
        self.loading_label.setMovie(self.loading_animation)
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
          
        # Install Button
        install_button = QPushButton("Install Selected Packages")
        install_button.clicked.connect(self.run_installation)
        layout.addWidget(install_button)

        # Toggle Button for Terminal
        toggle_button = QPushButton("More Info")
        toggle_button.setCheckable(True)
        toggle_button.toggled.connect(self.toggle_terminal_visibility)
        layout.addWidget(toggle_button)

        # Log Terminal
        self.log_terminal = QTextEdit()
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setStyleSheet("color: green;")
        self.log_terminal.setVisible(False)
        layout.addWidget(self.log_terminal)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        # Set layout for the central widget and add it to the scroll area
        central_widget.setLayout(layout)
        scroll_area.setWidget(central_widget)

        # Set the scroll area as the main layout of the dialog
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    
    def toggle_password_visibility(self):
            if self.show_password_button.isChecked():
                self.password_field.setEchoMode(QLineEdit.Normal)
                self.show_password_button.setText("Hide")
            else:
                self.password_field.setEchoMode(QLineEdit.Password)
                self.show_password_button.setText("Show")
                
    def toggle_openfoam(self):
        for checkbox in self.openfoam_checkboxes:
            checkbox.setChecked(self.openfoam_toggle.isChecked())

    def toggle_terminal_visibility(self, checked):
        self.log_terminal.setVisible(checked)
        sender = self.sender()
        if sender:
            sender.setText("Less Info" if checked else "More Info")

    def run_installation(self):
        self.sudo_password = self.password_field.text()
        if not self.sudo_password:
            QMessageBox.warning(self, "Password Required", "Please enter your sudo password to proceed.")
            return

        selected_packages = [pkg for i, (pkg, _) in enumerate(self.optional_packages) if self.optional_checkboxes[i].isChecked()]
        required_packages = [pkg for pkg, _ in self.required_packages]
        foam_packages = [pkg for i, (pkg, _) in enumerate(OPENFOAM_PACKAGES) if self.openfoam_checkboxes[i].isChecked()]  # OpenFOAM versions

        all_packages = required_packages + selected_packages

        self.progress_bar.setMaximum(len(all_packages) + len(foam_packages) + 2)  # +2 for APT update and repositories

        self.loading_label.setVisible(True)
        self.loading_animation.start()

        # Pass foam_packages to the InstallationWorker
        self.worker = InstallationWorker(all_packages, foam_packages, self.sudo_password)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.log_message.connect(self.log)
        self.worker.error.connect(self.handle_error)

        self.worker.finished.connect(self.finish_installation)
        self.worker.start()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)
        if value == 1:  # After APT update
            self.log("APT update complete. Continuing with package installation...")

    def log(self, message):
        self.log_terminal.append(message)
        with open("Pre-installer.log", "a") as log_file:
            log_file.write(message + "\n")

    def handle_error(self, error_message):
        self.loading_animation.stop()
        self.loading_label.setVisible(False)
        QMessageBox.critical(self, "Error", f"Installation failed: {error_message}")

    def finish_installation(self):
        self.loading_animation.stop()
        self.loading_label.setVisible(False)

        # Display failed packages
        failed_packages = self.worker.errors
        if failed_packages:
            failed_list = "\n".join(failed_packages)
            QMessageBox.critical(self, "Installation Incomplete", f"The following packages failed to install:\n\n{failed_list}\n\nCheck the logs for details.")
            self.log_terminal.append(f"\nInstallation completed with errors for packages: {failed_list}")
        else:
            total_time = self.worker.get_total_time()
            msg = f"All selected packages were installed successfully in {total_time:.2f} seconds!\n\nWelcome to Splash!"
            QMessageBox.information(self, "Installation Complete", msg)
            self.log_terminal.append(f"\nInstallation completed in {total_time:.2f} seconds!")
            self.accept()  # Close the GUI

def main():
    app = QApplication(sys.argv)
    installer = SplashInstaller()
    installer.exec()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
