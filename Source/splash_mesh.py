"""Meshing mixin for the Splash main window.

Owns the "Create Mesh" flow: copying Allmesh* scripts into the case directory,
the mesh-type chooser, running the mesh script with live output capture, and
showing the checkMesh log.

Depends on the host class for: self.geometry_loaded, self.geometry_dest_path,
self.selected_file_path, self.mesh_type_var, self.mesh_params, self.text_box,
self.status_label, self.progress_bar_canvas_flag, self.separateMeshLogFile,
self.root, plus the helper methods generate_mesh_visual and start_progress_bar
(which live on the main class).
"""

import glob
import os
import re
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

from ReplaceMeshParameters import ReplaceMeshParameters

from splash_utils import make_executable


class MeshMixin:
    def create_mesh(self):
        # Check if geometry is loaded
        if not self.geometry_loaded:
            messagebox.showinfo("Geometry Not Loaded", "Please load a geometry before creating the mesh.")
            return

        # Ask the user for mesh type using clickable buttons
        self.mesh_type = self.ask_mesh_type()

        if self.mesh_type is not None:

            # Define the source directory for Allmesh* files and "system" directory.
            # Anchored to this file's location, not cwd — so it works no matter where
            # the user launched Splash from.
            source_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            meshing_directory = os.path.join(source_root, "Meshing")


            # Check if the destination path is the same as the meshing directory
            if os.path.normpath(self.geometry_dest_path) != os.path.normpath(meshing_directory):
                all_mesh_files = glob.glob(os.path.join(meshing_directory, "Allmesh*"))

                for file_path in all_mesh_files:
                    try:
                        # Copy each Allmesh* file to the geometry destination path
                        shutil.copy(file_path, self.geometry_dest_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to copy {file_path}: {e}")

                # Define the source and destination paths for the "system" directory
                source_system_directory = os.path.join(meshing_directory, "system")
                dest_system_directory = os.path.join(self.geometry_dest_path, "system")

                # Remove the existing "system" directory in the destination if it exists
                if os.path.exists(dest_system_directory):
                    shutil.rmtree(dest_system_directory)

                try:
                    # Copy the "system" directory to the geometry destination path
                    shutil.copytree(source_system_directory, dest_system_directory)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy 'system' directory: {e}")

            # Read the content of the "meshDict" file
            self.mesh_dict_file_path = os.path.join(self.geometry_dest_path, "system", "meshDict")

            try:
                with open(self.mesh_dict_file_path, "r") as mesh_dict_file:
                    file_content = mesh_dict_file.read()
                    self.selected_mesh_file_content = file_content

                old_values_mesh = {param: match.group(1) for param in self.mesh_params
                                   for match in re.finditer(f'{param}\s+(\S+)(;|;//.*)', file_content)}

                # Open a popup to replace mesh parameters
                self.open_replace_mesh_parameters_popup(old_values_mesh)

            except FileNotFoundError:
                tk.messagebox.showerror("Error", f"File not found - {self.mesh_dict_file_path}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error reading mesh parameters: {e}")

    def open_replace_mesh_parameters_popup(self, old_values_mesh):
        if old_values_mesh:
            # Open a popup to replace mesh parameters
            ReplaceMeshParameters(self, self.mesh_params, old_values_mesh)
        else:
            tk.messagebox.showerror("Error", "No mesh parameters found in the 'meshDict' file!")

    def start_meshing(self):

        # Choosing the right script based on the selected mesh type
        if self.mesh_type == "Cartesian":
            script_name = "AllmeshCartesian"
        elif self.mesh_type == "Polyhedral":
            script_name = "AllmeshPolyhedral"
        elif self.mesh_type == "Tetrahedral":
            script_name = "AllmeshTetrahedral"
        else:
            tk.messagebox.showerror("Error", f"Unsupported mesh type: {self.mesh_type_var}")
            return

        # Create the full path to the meshing script
        cartMesh_script = os.path.join(self.geometry_dest_path, script_name)

        # Initiate the text_box with a nice mesh representation!
        self.generate_mesh_visual()

        # Running mesh script
        if os.path.exists(cartMesh_script):
            make_executable(cartMesh_script)

            try:
                # Activating the progress bar "again" - to be on the safe side
                self.progress_bar_canvas_flag = True
                self.start_progress_bar()

                # Clear previous content from the text box
                ##self.text_box.delete(1.0, "end")

                # Use Popen to capture real-time output
                command = [f"./{os.path.basename(cartMesh_script)}"]
                process = subprocess.Popen(command, cwd=self.geometry_dest_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                # Continuously read and insert output into the Text widget
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.text_box.insert("end", line)
                    self.text_box.see("end")  # Scroll to the end to show real-time updates
                    self.text_box.update_idletasks()  # Update the widget

                # Wait for the process to complete
                process.communicate()

                # Enable the load_meshChecked function
                self.separateMeshLogFile = True

                # Update the status label
                self.status_label.config(text="Meshing process is finished!")

                # Check the return code and display appropriate messages
                if process.returncode == 0:
                    #pass
                    tk.messagebox.showinfo("Mesh is ready", "Mesh is generated successfully!") # DEBUGGING
                else:
                    tk.messagebox.showerror("Meshing Error", "There was an error during meshing. Check the console output.")

            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error running AllmeshCartesian script: {e.stderr}")
            finally:
                self.progress_bar_canvas_flag = False
        else:
            tk.messagebox.showerror("Error", "AllmeshCartesian script not found!")

    # ______Craft your own mesh with the desired type _______

    def ask_mesh_type(self):
        # Create a popup to ask the user for mesh type
        popup = tk.Toplevel(self.root)
        popup.geometry("250x130")

        # Add clickable buttons for mesh type
        ttk.Radiobutton(popup, text="Cartesian", variable=self.mesh_type_var, value="Cartesian").pack()
        ttk.Radiobutton(popup, text="Polyhedral", variable=self.mesh_type_var, value="Polyhedral").pack()
        ttk.Radiobutton(popup, text="Tetrahedral", variable=self.mesh_type_var, value="Tetrahedral").pack()

        # Add a button to confirm the selection
        ttk.Button(popup, text="OK", command=popup.destroy).pack()

        # Wait for the popup to be closed
        self.root.wait_window(popup)

        # Return the selected mesh type
        return self.mesh_type_var.get()

    # Decoration function for meshing process
    def generate_mesh_visual(self):
        mesh_representation = self.create_mesh_visual()
        self.text_box.delete(1.0, tk.END)  # Clear existing content
        self.text_box.insert(tk.END, mesh_representation)

    def create_mesh_visual(self):
        mesh = ""
        mesh += "+---+---+---+\n"
        mesh += f"| 1 | 2 | 3 |\n"
        mesh += "+---+---+---+\n"
        mesh += f"| 6 | 5 | 4 |\n"
        mesh += "+---+---+---+\n"
        mesh += f"| 7 | 8 | 9 |\n"
        mesh += "+---+---+---+\n"

         # Add the decorative pattern below the mesh
        pattern = """
 ____        _           _       __  __           _
/ ___| _ __ | | __ _ ___| |__   |  \\/  | ___  ___| |__   ___ _ __
\\___ \\| '_ \\| |/ _` / __| '_ \\  | |\\/| |/ _ \\/ __| '_ \\ / _ \\ '__|
 ___) | |_) | | (_| \\__ \\ | | | | |  | |  __/\\__ \\ | | |  __/ |
|____/| .__/|_|\\__,_|___/_| |_| |_|  |_|\\___||___/_| |_|\\___|_|
      |_|
__________________________________________________________________
\n"""
        return pattern + mesh

    def load_meshChecked(self): # Important, implement an error handling mechanism where the it spits useful info in case no mesh was created yet!

        # Check if the file exists
        if self.geometry_dest_path and os.path.exists(self.geometry_dest_path):  # If mesh was created stand alone
            # Specify the path to the "AllmeshCartesian" file
            allmesh_cartesian_path1 = os.path.join(self.geometry_dest_path, "log.checkMesh")  # Meshing dir.

            # Read the content of the file
            with open(allmesh_cartesian_path1, "r") as file:
                content = file.read()

            # Insert the content into the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", content)
        elif self.selected_file_path and os.path.exists(self.selected_file_path):  # If mesh was created stand alone
            # Specify the path to the "Allrun" file
            allmesh_cartesian_path2 = os.path.join(self.selected_file_path, "log.checkMesh")  # Case dir.

            # Read the content of the file
            with open(allmesh_cartesian_path2, "r") as file:
                content = file.read()

            # Insert the content into the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", content)
        else:
            # If the file doesn't exist, display a message in the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", "log.checkMesh file not found.")
            messagebox.showinfo("No Mesh Log-File Found!", "Please make sure a mesh is generated first then load its log file.")
