"""Simulation-runner mixin for the Splash main window.

Owns case loading, initialization (Allclean), simulation setup popups,
controlDict editing, run/stop, log viewing, and the simulation monitor
that streams residuals into gnuplot.

Depends on the host class for: self.selected_directory, self.selected_file_path,
self.selected_openfoam_path, self.text_box, self.status_label, self.entry,
self.root, self.simulation_running, self.simulation_thread,
self.run_simulation_button, self.initialize_simulation_button,
self.configure_simulation_button, self.stop_simulation_button,
self.progress_bar_canvas, self.progress_bar_canvas_flag,
self.control_dict_params, self.monitor_simulation_var,
self.monitor_simulationLog_var, self.caseMeshLogFile, self.solverLogFile.
"""

import os
import re
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from ReplaceControlDictParameters import ReplaceControlDictParameters
from ReplaceSimulationSetupParameters import ReplaceSimulationSetupParameters

from splash_utils import make_executable


class RunnerMixin:
    def load_case(self):
        self.selected_directory = filedialog.askdirectory()

        if self.selected_directory:
            # Check if the selected directory contains the necessary OpenFOAM folders
            base_folders = ["constant", "system"]
            time_folders = ["0", "0.orig"]  # Check for either '0' or '0.orig'

            # Validate OpenFOAM case structure
            base_folders_exist = all(os.path.isdir(os.path.join(self.selected_directory, d)) for d in base_folders)
            time_folder_exists = any(os.path.isdir(os.path.join(self.selected_directory, t)) for t in time_folders)

            if base_folders_exist and time_folder_exists:
                self.selected_file_path = self.selected_directory
                self.status_label.config(text=f"Case directory identified: {self.selected_directory}", foreground="darkblue")
                self.run_simulation_button["state"] = tk.NORMAL
                self.initialize_simulation_button["state"] = tk.NORMAL
                self.configure_simulation_button["state"] = tk.NORMAL
                self.stop_simulation_button["state"] = tk.NORMAL

                # Check for 'mesh' or 'Allmesh' files and execute them
                mesh_script_path = None
                for script_name in ["mesh", "Allmesh"]:
                    script_path = os.path.join(self.selected_directory, script_name)
                    if os.path.isfile(script_path) and os.access(script_path, os.X_OK):  # Ensure it's executable
                        mesh_script_path = script_path
                        break  # Stop searching after the first match

                if mesh_script_path:
                    # Run the meshing script
                    self.status_label.config(text="Executing meshing script, please wait...", foreground="orange")
                    self.text_box.update_idletasks()  # Update_idletasks()

                    try:
                        subprocess.run([mesh_script_path], check=True, cwd=self.selected_directory)
                        self.status_label.config(text="Meshing completed successfully!", foreground="green")
                    except subprocess.CalledProcessError as e:
                        self.status_label.config(text=f"Error executing meshing script: {e}", foreground="red")
                        return  # Stop execution if meshing fails

                # Create a dummy 'splash.foam' file
                try:
                    dummy_file_path = os.path.join(self.selected_directory, "splash.foam")
                    with open(dummy_file_path, 'w') as dummy_file:
                        dummy_file.write('')  # Create an empty file
                except Exception as e:
                    self.status_label.config(text=f"Error creating 'splash.foam': {e}", foreground="red")
                    return

                # Check for existing mesh
                polyMesh_path = os.path.join(self.selected_directory, "constant", "polyMesh")
                if os.path.isdir(polyMesh_path):
                    response = messagebox.askyesno("Mesh Confirmation", "This case has a mesh. Do you want to visualize it in ParaView?")
                    if response:
                        self.launch_paraview_with_case()  # Open ParaView with the case file

            else:
                messagebox.showerror("Invalid OpenFOAM Case", "The selected folder does not represent a valid OpenFOAM case.")
                self.status_label.config(text="Invalid OpenFOAM case selected!", foreground="red")
                self.run_simulation_button["state"] = tk.DISABLED
                self.initialize_simulation_button["state"] = tk.DISABLED
                self.configure_simulation_button["state"] = tk.DISABLED
                self.stop_simulation_button["state"] = tk.DISABLED
        else:
            self.status_label.config(text="No case directory selected!", foreground="darkblue")
            self.run_simulation_button["state"] = tk.DISABLED
            self.initialize_simulation_button["state"] = tk.DISABLED
            self.configure_simulation_button["state"] = tk.DISABLED
            self.stop_simulation_button["state"] = tk.DISABLED

    # Function to launch ParaView with splash.foam
    def launch_paraview_with_case(self):
        splash_foam_path = os.path.join(self.selected_directory, "splash.foam")

        if os.path.exists(splash_foam_path):
            self.status_label.config(text="Launching ParaView...", foreground="blue")
            try:
                subprocess.Popen(["paraview", splash_foam_path], cwd=self.selected_directory)
            except Exception as e:
                self.status_label.config(text=f"Error launching ParaView: {e}", foreground="red")
        else:
            messagebox.showerror("File Not Found", "The splash.foam file could not be found.")

    def initialize_simulation(self):
        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was identified. Please make sure your case is loaded properly.")
            return

        allclean_script = os.path.join(self.selected_file_path, "Allclean")
        if os.path.exists(allclean_script):
            make_executable(allclean_script)

            try:
                self.start_progress_bar()

                # Use Popen to capture real-time output
                process = subprocess.Popen(["./Allclean"], cwd=self.selected_file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                # Clear previous content from the text box
                self.text_box.delete(1.0, "end")

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

                # Check the return code and display appropriate messages
                if process.returncode == 0:
                    tk.messagebox.showinfo("Simulation Initialized", "Simulation directory has been reset to default!")

                else:
                    pass # FLAG! must check what openfoam "returns" in case of a successful operation
                    #tk.messagebox.showerror("Simulation Error", "There was an error during simulation. Check the console output.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error running Allclean script: {e.stderr}")
            finally:
                self.stop_progress_bar()
        else:
        # tk.messagebox.showerror("Error", "Allclean script not found!")
            # Allclean script not found, creating a temporary script to clean the case
            temp_clean_script_path = os.path.join(self.selected_file_path, "temp_clean.sh")
            try:
                with open(temp_clean_script_path, 'w') as temp_script:
                    temp_script.write("#!/bin/bash\n")
                    if hasattr(self, 'selected_openfoam_path') and self.selected_openfoam_path:
                        temp_script.write(f". {self.selected_openfoam_path}\n")  # Source the selected version
                    else:
                        raise Exception("OpenFOAM path is not set. Please select an OpenFOAM version first.")
                    temp_script.write("cd ${0%/*} || exit 1\n")  # Go to the directory
                    temp_script.write(". ${WM_PROJECT_DIR:?}/bin/tools/CleanFunctions\n")  # Tutorial clean functions

                    if 'openfoam' in self.selected_openfoam_path:
                        if '/opt/openfoam' in self.selected_openfoam_path:
                            temp_script.write("foamCleanCase\n")  # Foundation version command
                        elif '/usr/lib/openfoam' in self.selected_openfoam_path:
                            temp_script.write("foamCleanTutorials\n")  # ESI version command
                    else:
                        raise Exception("Unknown OpenFOAM path, no cleaning command executed.")

                make_executable(temp_clean_script_path)
                self.text_box.delete(1.0, tk.END)  # Clear existing content

                self.start_progress_bar()
                # Use Popen to capture real-time output and run the temporary clean script
                process = subprocess.Popen(["./temp_clean.sh"], cwd=self.selected_file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.text_box.insert("end", line)
                    self.text_box.see("end")  # Scroll to the end to show real-time updates
                    self.text_box.update_idletasks()  # Update the widget

                process.communicate()

                if process.returncode == 0:
                    tk.messagebox.showinfo("Simulation Initialized", "Simulation directory has been reset to default!")
                else:
                    raise Exception("Temporary clean script failed to run successfully.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to initialize simulation: {e}")
            finally:
                self.stop_progress_bar()
                if os.path.exists(temp_clean_script_path):
                    os.remove(temp_clean_script_path)

    #+++++++++++++++++++++++++++++++++ Sim Setup ++++++++++++++++++++++++++++++++++++++++
    # Define this method to read existing parameter values
    def read_simulation_setup_existing_values(self, directory, file_name, param_list):
        file_path = os.path.join(self.selected_file_path, directory, file_name)
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                existing_values = {
                    param: match.group(1).strip() for param in param_list
                    for match in re.finditer(f'{param}[ \\t]+([^;]+?)(;|[ \\t]*//.*)', file_content)
                }

            return existing_values
        except FileNotFoundError:
            #tk.messagebox.showerror("Error", f"File not found - {file_path}")
            self.simulation_running = False  # Let the user try again
            return {}
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading {directory} parameters: {e}")
            return {}

    # Modify open_simulation_setup_popup
    def open_simulation_setup_popup(self):

        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was identified. Please make sure your case is loaded properly.")
            return

        # Specify the list of parameters for each file
        constant_params = {
            "transportProperties": ["transportModel", "nu"],
            "thermophysicalProperties": ["equationOfState", "molWeight", "Cp", "Hf", "mu", "Pr"],
            "turbulenceProperties": ["simulationType", "RASModel", "printCoeffs"]
            # more files can be added in a similar fashion
        }
        system_params = {
            #"fvSchemes": ["div(phi,U)", "div(phi,k)", "div(phi,epsilon)", "div(phi,omega)", "turbulence", "energy", "method"],
            "fvSchemes": ["turbulence", "energy", "method"],
            "fvSolution": ["nOuterCorrectors", "nCorrectors", "nNonOrthogonalCorrectors", "pMinFactor", "pMaxFactor"],
            "snappyHexMeshDict": ["castellatedMesh", "snap", "addLayers", "maxLocalCells", "maxGlobalCells", "minRefinementCells", "maxLoadUnbalance", "nCellsBetweenLevels", "nSmoothPatch", "tolerance", "nSolveIter", "nRelaxIter", "nFeatureSnapIter", "implicitFeatureSnap", "explicitFeatureSnap", "multiRegionFeatureSnap"]
        }

        # Read existing values for constant parameters
        existing_values_constant = {}
        for file_name, param_list in constant_params.items():
            existing_values_constant.update(self.read_simulation_setup_existing_values("constant", file_name, param_list))

        # Read existing values for system parameters
        existing_values_system = {}
        for file_name, param_list in system_params.items():
            existing_values_system.update(self.read_simulation_setup_existing_values("system", file_name, param_list))

        # Combine existing values for both constant and system parameters
        existing_values = {**existing_values_constant, **existing_values_system}

        # Open a popup to replace simulation setup parameters
        ReplaceSimulationSetupParameters(self, constant_params, system_params, existing_values)
    # ++++++++++++++++++++++++++++++++ Sim Setup ++++++++++++++++++++++++++++++++++++++++

    def update_control_dict_parameters(self):
        # Read the content of the "controlDict" file
        self.control_dict_file_path = os.path.join(self.selected_file_path, "system", "controlDict")

        try:
            with open(self.control_dict_file_path, "r") as control_dict_file:
                file_content = control_dict_file.read()
                self.selected_control_file_content = file_content
                existing_values_control_dict = {
                    param: match.group(1) for param in self.control_dict_params
                    for match in re.finditer(f'{param}\\s+([^;]+)(;|;//.*)', file_content)
                }

            # Open a popup to replace controlDict parameters
            self.open_replace_control_dict_parameters_popup(existing_values_control_dict)

        except FileNotFoundError:
            tk.messagebox.showerror("Error", f"File not found - {self.control_dict_file_path}")
            self.simulation_running = False # Let the user try again
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading controlDict parameters: {e}")

    def open_replace_control_dict_parameters_popup(self, existing_values):
        if existing_values:
            # Open a popup to replace controlDict parameters
            ReplaceControlDictParameters(self, self.control_dict_params, existing_values)
        else:
            tk.messagebox.showerror("Error", "No controlDict parameters found in the 'controlDict' file!")

    # --------------------------- Running the simulation --------------------------------->
    def run_simulation(self):

        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was identified. Please make sure your case is loaded properly.")
            return

        # FLAG! In case the controlDict still has more than 1 instance of "writeNow"
        control_dict_path = os.path.join(self.selected_file_path, "system", "controlDict")
        self.replace_write_now_with_end_time(control_dict_path)

        if not self.simulation_running:
            #self.simulation_thread = threading.Thread(target=self.run_openfoam_simulation)
            self.simulation_thread = threading.Thread(target=self.update_control_dict_parameters)
            self.simulation_thread.start()
            self.simulation_running = True
            self.stop_simulation_button["state"] = tk.NORMAL
        else:
            tk.messagebox.showinfo("Simulation Running", "Simulation is already running.")

    def run_openfoam_simulation(self):
        allrun_script = os.path.join(self.selected_file_path, "Allrun")
        if os.path.exists(allrun_script):

            #_____________________________________________________________________________
            # Important FLAG! to run an existing script we need 2 things;
            # 1- header must be bin/bash
            # 2- sourcing the openfoam version chosen by the user

            # Read the current content of the Allrun script
            print(f"Selected OpenFOAM path: {self.selected_openfoam_path}")  # Debug print
            with open(allrun_script, "r") as file:
                lines = file.readlines()

            # Ensure the first line is '#!/bin/bash'
            if not lines[0].startswith("#!/bin/bash"):
                lines[0] = "#!/bin/bash\n"

            source_command = f". {self.selected_openfoam_path}\n" if self.selected_openfoam_path else ""

            # Insert or replace source command after the first line
            if len(lines) > 1 and lines[1].strip().startswith('. '):
                lines[1] = source_command  # Replace the existing source command
            else:
                lines.insert(1, source_command)  # Insert a new source command after the shebang line

            # Write the modified content back to the Allrun script
            with open(allrun_script, "w") as file:
                file.writelines(lines)
            #_____________________________________________________________________________

            make_executable(allrun_script)

            try:
                self.start_progress_bar()

                # Initiate the text_box with a nice mesh representation!
                self.generate_run_visual()

                # Use Popen to capture real-time output
                process = subprocess.Popen(["./Allrun"], cwd=self.selected_file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

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

                # Enable the load_meshChecked function (to allow checking the mesh stats; also while sim is running)
                self.caseMeshLogFile = True

                # Enable the load_log_file function (even if the simulation was not terminated gracefully!)
                self.solverLogFile = True

                # Check the return code and display appropriate messages
                if process.returncode == 0:
                    tk.messagebox.showinfo("Simulation Finished", "Simulation completed successfully.")

                    # Giving the user the possibility to re-run the simulation
                    self.simulation_running = False
                else:
                    pass # FLAG! must check what openfoam "returns" in case of a successful operation
                    #tk.messagebox.showerror("Simulation Error", "There was an error during simulation. Check the console output.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error running Allrun script: {e.stderr}")
            finally:
                self.stop_progress_bar()
                self.stop_simulation_button["state"] = tk.DISABLED
        else:
            tk.messagebox.showerror("Error", "Allrun script not found!")

    # --------------------------- Running the simulation ---------------------------------<

    def stop_simulation(self): # FLAG! at the moment, the controlDict file needs to be open and saved and closed, for the function to work :/
        if not self.simulation_running:
            tk.messagebox.showinfo("Nothing to Stop", "There's no simulation currently running to stop.")
            return

        control_dict_path = os.path.join(self.selected_file_path, "system", "controlDict")  # FLAG! Duplication..
        if os.path.exists(control_dict_path):
            try:
                subprocess.run(["sed", "-i", '0,/endTime/s//writeNow/', control_dict_path], check=True)
                print(control_dict_path) # FLAG! DEBUGGING
                tk.messagebox.showinfo("Stop Simulation", "Simulation stopped successfully.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error stopping simulation: {e.stderr}")
        else:
            tk.messagebox.showerror("Error", "controlDict file not found!")

        self.stop_simulation_button["state"] = tk.DISABLED  # FLAG - is that really needed?!

        # Enable the user to user "run simulation" button again
        self.simulation_running = False

        # Disable the button until a new sim is launched
        self.stop_simulation_button["state"] = tk.DISABLED


    def replace_write_now_with_end_time(self, control_dict_path):
        subprocess.run(["sed", "-i", 's/writeNow/endTime/g', control_dict_path], check=True)

    def start_progress_bar(self):
        self.root.after(100, self.update_progress)

    def update_progress(self):
        # Update the progress bar value
        self.progress_bar_canvas.step(5)

        # Check if the flag is activated to stop the progress bar
        if not self.progress_bar_canvas_flag:
            self.stop_progress_bar()
            return  # Exit the method to prevent further updates

        # Schedule the update_progress method to be called after 100 milliseconds
        self.root.after(100, self.update_progress)

    def stop_progress_bar(self):
        # Stop the progress bar
        self.progress_bar_canvas.stop()

        # Set the mode to 'determinate' to reset the progress bar
        self.progress_bar_canvas.configure(mode="determinate")
        self.progress_bar_canvas["value"] = 0

    def load_log_file(self):

        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was found to be tracked. Please make sure your case is loaded/run properly.")
            return

        # List of identifiable "solver" names
        solver_names = ["simpleFoam", "pimpleFoam", "icoFoam", "sonicFoam", "compressibleInterFoam", "foamRun"]  # Add more solver names...

        # Check each solver log file
        for solver_name in solver_names:
            log_file_path = os.path.join(self.selected_file_path, f"log.{solver_name}")

            # Check if the file exists
            if os.path.exists(log_file_path):
                # Read the content of the file
                with open(log_file_path, "r") as file:
                    content = file.read()

                # Insert the content into the Text widget
                self.text_box.delete(1.0, "end")  # Clear previous content
                self.text_box.insert("end", content)

                # Break the loop once a log file is found
                break
        else:
            # If none of the log files exist, display a message in the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", "No log file found.")

    # -------------------------------- Plot results ------------------------------
    # Function to plot results using xmgrace
    def plot_results_xmgrace(self):

        xmgrace_sample_file = os.path.join(os.path.pardir, "Resources", "Sample_Results", "stresses.agr")
        try:
            # Check if xmgrace is installed
            subprocess.run(["xmgrace", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Run xmgrace in the same terminal window
            subprocess.run(["xmgrace", xmgrace_sample_file])
        except subprocess.CalledProcessError:
            tk.messagebox.showerror("Error", "xmgrace is not installed or not in the system's PATH.")
    # -------------------------------- Plot results ------------------------------

    def toggle_monitor_simulation(self):
        if self.monitor_simulation_var.get():
            # Call your monitor_simulation function here
            self.monitor_simulation()
        else:
            # Handle the case when the Checkbutton is unchecked (if needed)
            pass

    def toggle_simulation_results(self):
        if self.monitor_simulationLog_var.get():
            # Call your simulation_results function here [showing the log file - no more.]
            self.load_log_file()
        else:
            # Handle the case when the Checkbutton is unchecked (if needed)
            pass

    def monitor_simulation(self):

        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was found to be monitored. Please make sure your case is loaded properly.")
            return

        # Get the path to solverInfo.dat
        solver_info_file = os.path.join(self.selected_file_path, "postProcessing", "residuals", "0", "solverInfo.dat")
        #solver_info_file = os.path.join(self.selected_file_path, "postProcessing", "residuals", "0", "residuals.dat")

        # Check if the solverInfo file exists
        if not os.path.exists(solver_info_file):
            messagebox.showerror("Error", "SolverInfo file not found!")
            return

        # Get the absolute path to the SplashMonitor binary
        splash_monitor_path = os.path.abspath("../Resources/Utilities/SplashMonitor")

        # Construct the SplashMonitor command with the given arguments
        splash_monitor_command = [splash_monitor_path, "-l", "-i", "2", "-r", "1", solver_info_file]

        # Run SplashMonitor in a subprocess, capturing the standard output
        process = subprocess.Popen(splash_monitor_command, stdout=subprocess.PIPE, universal_newlines=True)

        # Check if Gnuplot is installed
        try:
            subprocess.run(["gnuplot", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Gnuplot is not installed. Please install Gnuplot.")
            return

        # Run Gnuplot with the output stream
        gnuplot_command = ["gnuplot", "-persist"]
        gnuplot_process = subprocess.Popen(gnuplot_command, stdin=subprocess.PIPE, universal_newlines=True)

        # Pass the data to Gnuplot
        for line in process.stdout:
            gnuplot_process.stdin.write(line)

        # Close the stdin of the Gnuplot process
        gnuplot_process.stdin.close()

        # Wait for Gnuplot to finish
        gnuplot_process.wait()

    # Decoration function for Simulation Run
    def generate_run_visual(self):
        cad_representation = self.create_run_visual()
        self.text_box.delete(1.0, tk.END)  # Clear existing content
        self.text_box.insert(tk.END, cad_representation)

    def create_run_visual(self):
        run = ""
        run += "+-----------+\n"
        run += f"|           |\n"
        run += "+           +\n"
        run += f"|           |\n"
        run += "+           +\n"
        run += f"|           |\n"
        run += "+-----------+\n"

         # Add the decorative pattern below the mesh
        pattern = """
 ____        _           _       ____  _   _ _   _
/ ___| _ __ | | __ _ ___| |__   |  _ \\| | | | \\ | |
\\___ \\| '_ \\| |/ _` / __| '_ \\  | |_) | | | |  \\| |
 ___) | |_) | | (_| \\__ \\ | | | |  _ <| |_| | |\\  |
|____/| .__/|_|\\__,_|___/_| |_| |_| \\_\\\\____/|_| \\_|
      |_|
_____________________________________________________
\n"""
        return pattern + run
