# Standard library imports
import os
import re
import tempfile
import vtk
import signal
import time
import datetime
import glob
import shutil # For file copying
import threading # For running a process in a separate thread
import tkinter as tk
import webbrowser
import matplotlib
import subprocess
import tkinter.simpledialog

# Importing third-party libs
from tkinter import ttk, filedialog, font, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk
from tkinter import scrolledtext
from tkinter import Listbox
from collections import defaultdict # Import defaultdict | for mesh parameters
from tkinter.colorchooser import askcolor
from tkinter.font import Font
from STLProcessor import STLProcessor

# Importing local classes
from SearchWidget import SearchWidget  # Import the SearchWidget class from the other file
from ReplaceProperties import ReplacePropertiesPopup
from ReplaceMeshParameters import ReplaceMeshParameters
from ReplaceControlDictParameters import ReplaceControlDictParameters
from ReplaceSimulationSetupParameters import ReplaceSimulationSetupParameters

# Splash main-window concerns are split across mixin modules to keep this file
# focused on layout/widgets and overall composition. Each mixin reads/writes
# attributes that Splash.__init__ sets up below.
from splash_license import LicenseMixin
from splash_properties import PropertiesMixin
from splash_mesh import MeshMixin
from splash_runner import RunnerMixin


# Define menu functions
def edit_undo():
    print("In the works")

def show_help():
    print("Show Help")

def view_status_bar():
    print("Status Bar View")

def view_toolbar():
    print("Toolbar View")
#______________
#
# TERMINAL APP
#______________

class Splash(LicenseMixin, MeshMixin, PropertiesMixin, RunnerMixin):
    def __init__(self, root):
        self.root = root
        self.root.config(background="white")
        self.root.title("Splash - v0.2")

        # Get the absolute path of the script directory
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Convert relative path to absolute path
        icon_path = os.path.join(base_path, "../Resources/Logos/simulitica_icon_logo.png")

        # Ensure the path is absolute
        icon_path = os.path.abspath(icon_path)

        # Load the icon. Keep a reference on self so Tk doesn't GC the PhotoImage,
        # and skip the second (unconditional) load that would crash if the file is missing.
        if os.path.exists(icon_path):
            try:
                self._window_icon = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, self._window_icon)
            except tk.TclError as e:
                print(f"Warning: could not set window icon: {e}")
        else:
            print(f"Warning: icon file not found at {icon_path}")

        # ======================= Create a menubar ----------------------------->
        menubar = tk.Menu(root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New File", command=self.file_new)
        file_menu.add_command(label="Create Case", command=self.case_creator)
        file_menu.add_command(label="Analyze STL file", command=self.process_stl)
        file_menu.add_command(label="Profile theme", command=self.change_theme)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=edit_undo)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Status Bar", command=view_status_bar)
        toolbar_submenu = tk.Menu(view_menu, tearoff=0)
        toolbar_submenu.add_command(label="Show Toolbar", command=view_toolbar)
        toolbar_submenu.add_command(label="Hide Toolbar", command=lambda: print("Hide Toolbar"))
        view_menu.add_cascade(label="Toolbar", menu=toolbar_submenu)
        view_menu.add_command(label="Results Panel", command=self.toggle_results_panel)
        menubar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_message)
        help_menu.add_command(label="Manual", command=self.splash_online_manual, background="black", foreground="cyan")
        help_menu.add_command(label="Splash-GPT", command=self.splash_GPT_page, background="black", foreground="pink")
        help_menu.add_command(label="Report an issue", command=self.open_contact_page, background="black", foreground="red")
        help_menu.add_command(label="Support Splash", command=self.support_Splash, background="black", foreground="lightgreen")
        help_menu.add_command(label="Cloud HPC", command=self.cloud_HPC, background="black", foreground="white")
        menubar.add_cascade(label="Help", menu=help_menu)

        # Display the menu bar
        root.config(menu=menubar)
        # ======================= Create a menubar -----------------------------<

        # ============= Time Recorder =============>
        # License parameters
        self.start_time = time.time()
        # Per-user config dir, namespaced to avoid colliding with commercial Splash-CFD
        config_dir = os.path.join(os.path.expanduser("~"), ".splash-oss")
        try:
            os.makedirs(config_dir, exist_ok=True)
        except OSError as e:
            print(f"Warning: could not create config dir {config_dir}: {e}")
            config_dir = os.path.dirname(os.path.abspath(__file__))
        self.license_start_date_file = os.path.join(config_dir, "license_start_date.txt")
        self.license_duration = 1 * 365 * 24 * 3600  # 1 year in seconds
        #self.license_duration = 14 * 24 * 3600  # 14 days in seconds
        self.notice_period_before_end = 15 * 24 * 3600  # Notify 15 days before the license expires
        self.elapsed_time_file = os.path.join(config_dir, "elapsed_time.txt")

        # Create a label for the "Elapsed Time" text
        self.elapsed_time_label = tk.Label(root, text="Elapsed Time", font=("Helvetica", 24), bg="white", fg="darkblue")
        self.elapsed_time_label.grid(row=0, column=7, sticky="nsew")  # Updated to sticky="nsew" for dynamic resizing

        # Create a label for the timer
        self.timer_label = tk.Label(root, text="00:00:00.0", font=("Helvetica", 35, "bold"), bg="white", fg="darkblue")
        self.timer_label.grid(row=1, column=7, sticky="nsew")  # Updated to sticky="nsew" for dynamic resizing
        # ============= Time Recorder =============<

        # Display the main text box widget
        self.setup_ui()

        # Variable to track visibility state of the action bar
        self.show_first_column = True

        # Add a background image
        self.add_bgImage()

        # Initialize the bg color of the 3D STL CAD
        self.bg_color_counter = 1

        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the recurring timer only after the UI is fully constructed —
        # otherwise an exception in setup_ui leaves update_timer scheduled to fire
        # on widgets that don't exist yet.
        self.update_timer()

        # Display a welcome message
        self.show_welcome_message()

        # Ensure that the column and row have weight to resize dynamically
        self.root.grid_columnconfigure(10, weight=1)  # Ensures that the column with index 10 resizes dynamically
        self.root.grid_rowconfigure(2, weight=1)  # Ensures that the row with index 2 (Elapsed Time label) resizes
        self.root.grid_rowconfigure(3, weight=1)  # Ensures that the row with index 3 (Timer label) resizes

        # Add logos
        self.add_logos()

        # ----------------------
        # Style of Action Panel
        # ----------------------
        # Create a ttk.Style to configure buttons
        style = ttk.Style()
        style.configure(
            "TButton",
            padding=5,
            relief="flat",
            background="lightblue",
            foreground="black",
            font=("Arial", 12, "bold")
        )

        # Initialize the STLProcessor
        self.stl_processor = STLProcessor(self)

        # Create a button to import a geometry file
        self.import_button = ttk.Button(self.root, text="Import Geometry", command=self.import_geometry)
        self.import_button.grid(row=0, column=0, pady=1, padx=10, sticky="nsew")

        # Create a mesh type variable (set it so "Cartesian" as a default)
        self.mesh_type_var = tk.StringVar(value="Cartesian")
        self.mesh_type = None

        # Create a button to create the mesh
        self.create_mesh_button = ttk.Button(self.root, text="Create Mesh", command=self.create_mesh)
        self.create_mesh_button.grid(row=1, column=0, pady=1, padx=10, sticky="nsew")

        # Create a button to load the case directory
        self.load_case_button = ttk.Button(self.root, text="Load Case", command=self.load_case)
        self.load_case_button.grid(row=2, column=0, pady=1, padx=10, sticky="nsew")

        # Create a button to initialize the command execution
        self.initialize_simulation_button = ttk.Button(self.root, text="Initialize Simulation", command=self.initialize_simulation)
        self.initialize_simulation_button.grid(row=3, column=0, pady=1, padx=10, sticky="nsew")

        # Create a button to configure the simulation settings before run
        self.configure_simulation_button = ttk.Button(self.root, text="Configure Simulation", command=self.open_simulation_setup_popup)
        self.configure_simulation_button.grid(row=4, column=0, pady=1, padx=10, sticky="nsew")

        # Create a button to run simulation
        self.run_simulation_button = ttk.Button(self.root, text="Run Simulation", command=self.run_simulation)
        self.run_simulation_button.grid(row=5, column=0, pady=1, padx=10, sticky="nsew")

        # Stop Simulation Button
        self.stop_simulation_button = ttk.Button(self.root, text="Stop Simulation", command=self.stop_simulation)
        self.stop_simulation_button.grid(row=6, column=0, pady=1, padx=10, sticky="nsew")

        # Create a button to plot results using xmgrace (2D Plotting)
        self.plot_results_xmgrace_button = ttk.Button(self.root, text="2D Plotting", command=self.plot_results_xmgrace)
        self.plot_results_xmgrace_button.grid(row=7, column=0, pady=1, padx=10, sticky="nsew")  # Changed sticky to "nsew" for dynamic resizing
        self.add_tooltip(self.plot_results_xmgrace_button, "Click to plot simulation results using xmgrace")

        # Configure the row where the 2D Plotting button is located to allow resizing
        self.root.grid_rowconfigure(7, weight=1)  # Ensure row 7 resizes

        # Create a button for post-processing
        self.paraview_button = ttk.Button(self.root, text="Post-processing", command=self.paraview_application)
        self.paraview_button.grid(row=8, column=0, pady=1, padx=10, sticky="nsew")

        # Configuring row and column weights to make window responsive
        no_global_columns = 5
        no_global_rows = 13

        for i in range(no_global_rows):
            self.root.rowconfigure(i, weight=1, uniform="rows")

        for i in range(no_global_columns):
            self.root.columnconfigure(i, weight=1, uniform="columns")

        # Set the initial size of the window to fit a small monitor
        self.root.geometry("1400x800")  # Example size for small monitor # 1400x1000

        # Centering the window on the screen:
        self.root.update_idletasks()  # Ensure window has been drawn
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Create a button to execute commands to the terminal kernel
        self.execute_button = tk.Button(self.root, text="CLI", command=self.execute_command)
        self.execute_button.configure(relief="flat", background="lightblue", foreground="black", font=("Arial", 12, "bold"))
        self.execute_button.grid(row=10, column=1, pady=3, padx=1, sticky="new")  # Changed row to 14 and column to 0 (below the text box on the left)
        self.add_tooltip(self.execute_button, "Click to run a terminal command")

        # Configure a smaller style for the button
        style = ttk.Style()
        style.configure("Small.TButton", font=("TkDefaultFont", 10), padding=3, background="lightblue")

        # Configure a custom style for the Entry widget
        style.configure('Professional.TEntry',
                        foreground='lightblue',
                        font=('Helvetica', 11, 'bold'),
                        borderwidth=2,
                        relief='flat',
                        padding=10)

        # Create an entry field for entering the commands by the user
        default_sentence = "top"  # Or "htop"
        self.entry = ttk.Entry(self.root, style='Professional.TEntry', width=18, foreground="lightblue", font=("Arial", 12, "bold"))
        self.entry.grid(row=9, column=1, pady=3, padx=1, sticky="sew")  # Changed row to 15 and column to 0 (below the execute button)
        self.entry.insert(0, default_sentence)

        # Ensure the button and entry field can resize
        self.root.grid_rowconfigure(13, weight=1)  # Ensures the row for the execute button resizes dynamically
        self.root.grid_rowconfigure(14, weight=1)  # Ensures the row for the entry field resizes dynamically

# --------------->
#  Check buttons
# <--------------
        # Set different weights for the rows to control how they resize
        self.root.grid_rowconfigure(14, weight=0)  # Reset Profile Theme button's row gets some priority
        self.root.grid_rowconfigure(15, weight=0)  # Give less weight to the rows below so they shrink first
        self.root.grid_rowconfigure(16, weight=0)
        self.root.grid_rowconfigure(17, weight=0)

        # Create a Checkbutton for resetting profile theme to default
        self.reset_var = tk.BooleanVar()
        reset_checkbutton_style = ttk.Style()
        reset_checkbutton_style.configure("Custom.TCheckbutton", foreground="black", background="white")

        reset_checkbutton = ttk.Checkbutton(root, text="Reset Profile Theme", variable=self.reset_var, style="Custom.TCheckbutton", command=self.toggle_reset)
        reset_checkbutton.grid(row=14, column=0, padx=7, pady=1, sticky="nw")  # Stick to the top-left corner

        # Create Checkbutton for monitoring simulation
        self.monitor_simulation_var = tk.BooleanVar()
        monitor_simulation_checkbutton = ttk.Checkbutton(root, text="Monitor Simulation", variable=self.monitor_simulation_var, command=self.toggle_monitor_simulation, style="Custom.TCheckbutton")
        monitor_simulation_checkbutton.grid(row=15, column=0, pady=1, padx=7, sticky="nsew")  # These buttons can resize freely

        # Create Checkbutton for monitoring simulation log
        self.monitor_simulationLog_var = tk.BooleanVar()
        monitor_simulationLog_checkbutton = ttk.Checkbutton(root, text="Simulation log", variable=self.monitor_simulationLog_var, command=self.toggle_simulation_results, style="Custom.TCheckbutton")
        monitor_simulationLog_checkbutton.grid(row=16, column=0, pady=1, padx=7, sticky="nsew")

        # Create a Checkbutton using the custom style for showing/hiding the results section
        self.results_panel_var = tk.BooleanVar(value=True)  # Set to False so it starts unchecked
        toggle_visibility_button = ttk.Checkbutton(
            root,
            text="Show Elapsed Time",
            variable=self.results_panel_var,
            command=self.toggle_results_panel,
            style="Custom.TCheckbutton"
        )
        toggle_visibility_button.grid(row=17, column=0, pady=1, padx=7, sticky="nsew")

        # Store initial profile theme values
        self.initial_font = self.text_box.cget("font")
        self.initial_foreground = self.text_box.cget("foreground")
        self.initial_background = self.text_box.cget("background")

        # Create a style for the progress bar
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="white", background="lightblue", thickness=10)

        # Create a progress bar with the custom style
        self.progress_bar_canvas = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=280,
            mode="indeterminate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar_canvas.grid(row=12, column=0, padx=10, pady=5, sticky="new")
        self.progress_bar_canvas_flag = True

        #----------Text Widget with Scrollbar-----------
        # Add the search widget to the main app
        self.search_widget = SearchWidget(root, self.text_box)

        # Initialize variables for simulation thread
        self.simulation_thread = None
        self.simulation_running = False

        # Initialize the available fuels to choose from
        self.fuels = ["Propane", "Gasoline", "Ethanol", "Hydrogen", "Methanol", "Ammonia", "Dodecane", "Heptane"]

        # Define the fuel options
        fuels = ["Methanol", "Ammonia", "Dodecane"]

        # Create a StringVar to store the selected fuel
        self.selected_fuel = tk.StringVar()

        # Set a default value for the dropdown
        default_value = "Available fuel options"
        self.selected_fuel.set(default_value)

        # Create a label for status messages
        self.status_label_title = ttk.Label(self.root, text="")
        status_title = "Splash v0.2"
        self.status_label_title.grid(row=14, column=1, columnspan=1, pady=1, padx=10, sticky="nsew")  # Changed to sticky="nsew" for dynamic resizing
        self.status_label_title.config(text=status_title, font=("Helvetica", 14, "bold"), background="white", foreground="grey")

        # Separate the status bar
        separator = tk.Frame(self.root, height=1, bg="darkred")
        separator.grid(row=15, column=1, columnspan=1, pady=(5, 1), padx=10, sticky="new")

        self.status_label = ttk.Label(self.root, text="")
        default_status = "Start by importing your geometry or configuring an existing OpenFOAM case!"
        self.status_label.grid(row=16, column=1, columnspan=8, pady=1, padx=10, sticky="new")  # Changed to sticky="nsew" for dynamic resizing
        self.status_label.config(text=default_status, font=("Helvetica", 12), background="white", foreground="darkblue")

        # Other parameter initializations
        self.selected_file_path = None
        self.selected_openfoam_path = None
        self.selected_file_content = None
        self.mesh_dict_file_path = None
        self.control_dict_file_path = None
        self.selected_mesh_file_content = None
        self.selected_control_file_content = None
        self.geometry_dest_path = None
        self.control_dict_path = None
        self.separateMeshLogFile = False
        self.openfoam_sourced = False
        self.caseMeshLogFile = False
        self.solverLogFile = False
        self.geometry_loaded = False

        # Mesh parameters
        self.mesh_params = ["minCellSize", "maxCellSize", "boundaryCellSize", "nLayers", "optimiseLayer", "untangleLayers", "thicknessRatio",
                            "maxFirstLayerThickness", "nSmoothNormals", "maxNumIterations", "featureSizeFactor", "reCalculateNormals",
                            "relThicknessTol", "restartFromLatestStep", "enforceGeometryConstraints"]

        self.control_dict_params = ["application", "startFrom", "startTime", "stopAt", "endTime", "deltaT", "writeControl", "writeInterval",
                                    "purgeWrite", "writeFormat", "writePrecision", "timePrecision", "runTimeModifiable", "maxCo"]

        # Add header
        self.header = """/*--------------------------------*- C++ -*----------------------------------*\\
          =========                 |
          \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
           \\\\    /   O peration     | Website:  https://openfoam.org
            \\\\  /    A nd           | Version:  Splash v0.2
             \\\\/     M anipulation  |
        \\*---------------------------------------------------------------------------*/\n"""

        self.thermo_type_params = ["type", "mixture", "transport", "thermo", "equationOfState", "specie", "energy"]
        self.mixture_params = ["molWeight", "rho", "rho0", "p0", "B", "gamma", "Cv", "Cp", "Hf", "mu", "Pr"]


    # Creating an empty text file
    def file_new(self):
        # Use the system temp dir rather than the cwd — the latter is whatever
        # directory the user launched the app from and may not be writable.
        new_file_path = os.path.join(tempfile.gettempdir(), "splash_new_file.txt")

        # Create a new empty text file
        with open(new_file_path, 'w') as new_file:
            new_file.write("")  # Writing an empty string (left for furture dev.)

        # Function to open the file in gedit in a separate thread
        def open_in_gedit():
            try:
                subprocess.run(["gedit", new_file_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to open gedit: {e}")

        # Start the open_in_gedit function in a new thread to avoid blocking the UI
        gedit_thread = threading.Thread(target=open_in_gedit)
        gedit_thread.start()

    def case_creator(self):
        """Launch the Case Creator GUI built with PySide."""
        # Script path for SplashCaseCreator
        script_path = os.path.abspath(os.path.join("CaseCreator", "SplashCaseCreator_gui.py"))

        try:
            print(f"Launching Case Creator at: {script_path}")
            # Set environment variable to force Qt to use X11
            env = os.environ.copy()
            env["QT_QPA_PLATFORM"] = "xcb"

            # Set the working directory to CaseCreator to ensure the .ui file can be accessed
            process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=os.path.abspath("CaseCreator")
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Error launching Case Creator: {stderr.decode().strip()}")
                messagebox.showerror("Error", f"Case Creator failed to launch. See console for details.")
            else:
                print(f"Case Creator launched successfully: {stdout.decode().strip()}")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Script not found: {script_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Case Creator: {e}")
    # -------------- Main logos -------------------------->
    def add_logos(self):

        # Create PhotoImage objects directly from image files
        base_path = os.path.dirname(os.path.abspath(__file__))

        self.logo_openfoam = tk.PhotoImage(file=os.path.abspath(os.path.join(base_path, "../Resources/Logos/openfoam_logo.png")))
        self.logo_simulitica = tk.PhotoImage(file=os.path.abspath(os.path.join(base_path, "../Resources/Logos/simulitica_logo.png")))

        #self.logo_openfoam = tk.PhotoImage(file="../Resources/Logos/openfoam_logo.png")
        #self.logo_simulitica = tk.PhotoImage(file="../Resources/Logos/simulitica_logo.png")

        # Resize images if needed
        self.logo_openfoam = self.logo_openfoam.subsample(3, 3)  # Adjust the subsample as needed
        self.logo_simulitica = self.logo_simulitica.subsample(8, 8)  # Adjust the subsample as needed



        # Create a style for the button to remove any hover effect or unwanted borders
        style = ttk.Style()
        style.configure('White.TButton', background='white', relief="flat", borderwidth=0)
        style.map('White.TButton', background=[('active', 'white')], relief=[('pressed', 'flat')])

        # Create the button for OpenFOAM version with the logo
        self.OF_version_button = ttk.Button(
            self.root,
            text="",
            command=self.select_openfoam_version,
            image=self.logo_openfoam,
            style='White.TButton',
            cursor="hand2"  # Make it clear it's clickable
        )
        self.OF_version_button.grid(row=9, column=0, pady=1, padx=5, sticky="nsew")  # Use nsew for proper resizing



        # Add the Simulitica logo
        self.simLabel = tk.Label(self.root, image=self.logo_simulitica)
        self.simLabel.grid(row=10, column=0, pady=1, padx=5, sticky="nsew")  # Changed sticky to "nsew" for dynamic resizing
        self.simLabel.configure(background="white")

        # Add copyright text
        self.copyright_label = ttk.Label(self.root, text="© 2023 Simulitica Ltd")
        self.copyright_label.grid(row=11, column=0, pady=1, padx=5, sticky="nsew")  # Changed sticky to "nsew" for dynamic resizing
        self.copyright_label.configure(background="white", font="bold")

        # Ensure that rows 9, 10, and 11 are configured for resizing
        self.root.grid_rowconfigure(9, weight=1)
        self.root.grid_rowconfigure(10, weight=1)
        self.root.grid_rowconfigure(11, weight=1)
    # -------------- Main logos --------------------------<

    def process_stl(self):
        # Open file dialog to select STL file
        self.selected_file_path = filedialog.askopenfilename(title="Select STL File", filetypes=[("STL files", "*.stl")])
        if self.selected_file_path:
            self.stl_processor.process_stl(self.selected_file_path)
            messagebox.showinfo("Processing Complete", "STL analysis completed. Check the generated report.")

    def paraview_application(self):
        # This function will be executed in a separate thread to avoid blocking the main GUI thread
        def run_paraview():
            try:
                # Launch ParaView in a non-blocking way using Popen
                subprocess.Popen(["paraview"])
            except Exception as e:
                # Handle errors if ParaView fails to launch
                print(f"Error running ParaView: {e}")

        # Create a new thread to run the ParaView process
        paraview_thread = threading.Thread(target=run_paraview)

        # Set daemon to True so the thread will not block the application from closing
        paraview_thread.daemon = True

        # Start the thread, which will run ParaView in the background without blocking the main UI
        paraview_thread.start()

    # Toggle function for action bar visibility
    def toggle_results_panel(self):
        self.show_first_column = self.results_panel_var.get()  # Check the state of the variable

        # Toggle the visibility of buttons in the first column
        if self.show_first_column:
            # Show elements
            self.elapsed_time_label.grid(row=0, column=7, sticky="nsew")
            self.timer_label.grid(row=1, column=7, sticky="nsew")
            self.splash_bgImage_label.grid(row=2, column=7, pady=5, padx=10, sticky="nsew", rowspan=6)
        else:
            # Hide elements
            self.elapsed_time_label.grid_remove()
            self.timer_label.grid_remove()
            self.splash_bgImage_label.grid_remove()

    def browse_directory(self):
        selected_file = filedialog.askopenfilename()

        if selected_file and os.path.basename(selected_file).startswith("physicalProperties"):
            self.selected_file_path = selected_file
            self.status_label.config(text=f"Selected file: {selected_file}")

            # Update the current fuel status label
            current_fuel = self.detect_current_fuel()
            if current_fuel:
                self.status_label.config(text=f"Current fuel: {current_fuel}")

                # Check if the detected current fuel matches any of the available fuels
                # If it does, set it as the selected fuel in the dropdown
                for fuel in self.fuels:
                    if fuel.lower() == current_fuel.lower():
                        self.selected_fuel.set(fuel)
                        break

            with open(selected_file, 'r') as file:
                file_content = file.read()
                self.selected_file_content = file_content
                old_values_mixture = {param: match.group(1) for param in self.mixture_params
                                      for match in re.finditer(f'{param}\s+(\S+)(;|;//.*)', file_content)}
                old_values_thermo_type = {param: match.group(1) for param in self.thermo_type_params
                                           for match in re.finditer(f'{param}\s+(\S+)(;|;//.*)', file_content)}
                self.open_replace_properties_popup(old_values_mixture, old_values_thermo_type)
        else:
            tk.messagebox.showerror("Error", "Selected file is not a physicalProperties file! Please look for the constant dir in your OF case!")

    # -------------- Welcome Message --------------------------
    def show_welcome_message(self):
        welcome_message = (
            "\n"
            "Welcome to Splash!\n\n"
            "Your interactive OpenFOAM simulation platform.\n"
            "_____________________________________________________________________________\n"
            "\n"
            "Copyright (C) Simulitica Ltd. - All Rights Reserved.\n"
            "This program is licensed under the GNU Lesser General Public License (LGPL) v3.0.\n"
            "You may redistribute and/or modify this software under the terms of the LGPL.\n"
            "For full license details, please refer to the LICENSE file provided with this software.\n"
            "Written by Mohamed Aly SAYED (mohamed.sayed@simulitica.com), November 2023.\n"
            "_____________________________________________________________________________"
        )

        # Create a Label to display the welcome message
        welcome_label = ttk.Label(self.root, text=welcome_message, font=("TkDefaultFont", 12), background="white", justify='center', relief='sol', borderwidth=1)
        welcome_label.grid(row=0, column=0, columnspan=5, rowspan=10, pady=1, padx=10, sticky="nsew")

        # Create a PhotoImage object and set it to the Label
        base_path = os.path.dirname(os.path.abspath(__file__))
        welcome_image = tk.PhotoImage(file=os.path.abspath(os.path.join(base_path, "../Resources/Images/racing-car.png")))
        #welcome_image = tk.PhotoImage(file="../Resources/Images/racing-car.png")
        welcome_image = welcome_image.subsample(9, 9)
        welcome_label.config(image=welcome_image, compound="top")

        # Update the main loop to display the image for 2 seconds
        self.root.update()
        time.sleep(2)  # wait for 3 seconds
        welcome_label.destroy()  # Destroy the Label to collapse the popup

    def show_about_message(self):
        about_message = (
            "\n"
            "Welcome to Splash!\n\n"
            "Your interactive OpenFOAM simulation platform.\n"
            "_____________________________________________________________________________\n"
            "\n"
            "Copyright (C) Simulitica Ltd. - All Rights Reserved.\n"
            "This program is licensed under the GNU Lesser General Public License (LGPL) v3.0.\n"
            "You may redistribute and/or modify this software under the terms of the LGPL.\n"
            "For full license details, please refer to the LICENSE file provided with this software.\n"
            "Written by Mohamed Aly SAYED (mohamed.sayed@simulitica.com), November 2023.\n"
            "_____________________________________________________________________________"
        )

        # Create a Toplevel window for the welcome message
        popup = tk.Toplevel(self.root)
        popup.title("Splash v0.2")
        popup.geometry("750x700")  # Adjust the size as needed

        # Create a Label in the Toplevel window to display the welcome message
        welcome_label = ttk.Label(popup, text=about_message, font=("TkDefaultFont", 12), justify='center')
        welcome_label.pack(padx=10, pady=10)

        # Create a PhotoImage object and set it to the Label
        base_path = os.path.dirname(os.path.abspath(__file__))
        welcome_image = tk.PhotoImage(file=os.path.join(base_path, "../Resources/Images/racing-car.png"))
        #welcome_image = tk.PhotoImage(file="../Resources/Images/racing-car.png")  # Adjust the path as needed
        welcome_image = welcome_image.subsample(4, 4)  # Adjust subsampling as needed
        welcome_label.config(image=welcome_image, compound="top")
        welcome_label.image = welcome_image  # Keep a reference

    # -------------- Splash background image(s) -------------------------->
    def add_bgImage(self):
        # Specify the image path

        #image_path = "../Resources/Images/racing-car.png"
        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.abspath(os.path.join(base_path, "../Resources/Images/racing-car.png"))

        # Create a tk.PhotoImage object directly from the file
        self.splash_bgImage = tk.PhotoImage(file=image_path)

        # Adjust the subsample as needed
        self.splash_bgImage = self.splash_bgImage.subsample(6, 6)

        # Create a label to display the image (not clickable)
        self.splash_bgImage_label = tk.Label(
            self.root,
            image=self.splash_bgImage,
            bg="white"  # Set background color to white to match the background
        )

        # Use grid for layout
        self.splash_bgImage_label.grid(row=2, column=7, pady=5, padx=10, sticky="new", rowspan=6)


    def process_stl_click(self, event=None):
        # Call the process_stl method when the image is clicked
        self.process_stl()

    # -------------- Splash background image(s) --------------------------<

    # ------------------------------------- Importing the geometry ------------------------------------->
    def import_geometry(self):
        file_path = filedialog.askopenfilename(
            title="Select Geometry File",
            filetypes=[("STL Files", "*.stl"), ("OBJ Files", "*.obj"), ("STEP Files", "*.stp"), ("All Files", "*.*")],
            initialdir=os.path.dirname(self.selected_file_path) if self.selected_file_path else None
        )

        if file_path:
            self.selected_file_path = file_path
            meshing_folder = os.path.join(os.path.dirname(self.selected_file_path), "Meshing")
            self.status_label.config(text="The geometry file is successfully imported!")
            # To enable meshing to start
            self.geometry_loaded = True

            # Create the Meshing folder if it doesn't exist
            if not os.path.exists(meshing_folder):
                os.makedirs(meshing_folder)

            # Initiate the text_box with a nice mesh representation!
            self.generate_cad_visual()

            # Copy and rename the geometry file
            geometry_filename = f"CAD.{file_path.split('.')[-1].lower()}"
            geometry_dest = os.path.join(meshing_folder, geometry_filename)
            self.geometry_dest_path = os.path.join(geometry_dest.split('CAD')[0])
            shutil.copyfile(self.selected_file_path, geometry_dest)

            # Find the path to the directory just before "Resources"
            current_path = os.getcwd()
            index = current_path.find("Source")
            base_path = current_path[:index] if index != -1 else current_path  # Fallback to current path if "Source" not found

            # CAD programs logo paths
            splash_logo_path = os.path.join(base_path, "Resources", "Logos", "simulitica_icon_logo.png")
            freecad_logo_path = os.path.join(base_path, "Resources", "Logos", "freecad_logo.png")
            gmsh_logo_path = os.path.join(base_path, "Resources", "Logos", "gmsh_logo.png")
            #blender_logo_path = os.path.join(base_path, "Resources", "Logos", "blender_logo.png")
            blender_logo_path = os.path.join(base_path, "Resources", "Logos", "blender-logo-2.png")
            paraview_logo_path = os.path.join(base_path, "Resources", "Logos", "paraview_logo.png")

            # Create a popup to ask the user whether to open the CAD file in FreeCAD, Gmsh, or ParaView
            popup = tk.Toplevel(self.root)
            popup.title("Choose CAD Viewer")
            popup.geometry("400x750")
            popup.configure(bg="white")

            # --------- Toggle for processing the imported CAD file ----------->
            # Add a toggle button at the bottom of the popup
            self.toggle_on = False  # Initialize the toggle state to off

            def toggle_frame_color():
                if not self.toggle_on:
                    frame_toggle_button.config(bg="lightblue")
                    # Process the STL file when toggle is on..
                    self.stl_processor.process_stl(self.selected_file_path)
                else:
                    frame_toggle_button.config(bg="white")
                self.toggle_on = not self.toggle_on

            def on_hover(event):
                frame_toggle_button.config(bg="lightblue", fg="black")

            def on_leave(event):
                if not self.toggle_on:
                    frame_toggle_button.config(bg="white", fg="black")

            frame_toggle_button = tk.Button(
                popup,
                text="Process STL File",
                command=toggle_frame_color,
                bg="black",
                fg="cyan",
                bd=1,
                relief="raised"
            )

            frame_toggle_button.bind("<Enter>", on_hover)
            frame_toggle_button.bind("<Leave>", on_leave)

            frame_toggle_button.pack(side=tk.BOTTOM, pady=5)
            # --------- Toggle for processing the imported CAD file -----------<

            def open_freecad():
                subprocess.run(["freecad", geometry_dest, "&"], check=True)
                # Zoom to fit
                try:
                    doc = FreeCAD.ActiveDocument
                    doc.getObject(geometry_filename).ViewObject.Proxy.fit()
                except Exception as e:
                    print(f"Error zooming to fit in FreeCAD: {e}")
                popup.destroy()

            def open_gmsh():
                subprocess.run(["gmsh", geometry_dest, "&"], check=True)
                popup.destroy()

            def open_blender():
                # Get the directory of the currently running script
                current_dir = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(current_dir, "import_stl_to_blender.py")

                try:
                    # Run Blender with the script and the path to the STL file
                    subprocess.run(["blender", "--python", script_path, "--", geometry_dest], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to open Blender: {e}")
                finally:
                    popup.destroy()

            def open_paraview():
                # This function runs ParaView in a separate thread to avoid blocking the main UI
                def run_paraview():
                    try:
                        # Launch ParaView without blocking the main UI
                        subprocess.Popen(["paraview", geometry_dest])
                    except Exception as e:
                        print(f"Error running ParaView: {e}")
                    finally:
                        popup.destroy()

                # Start ParaView in a new thread
                paraview_thread = threading.Thread(target=run_paraview)
                paraview_thread.daemon = True
                paraview_thread.start()

            # Load logos
            splash_logo = tk.PhotoImage(file=splash_logo_path).subsample(7, 7)
            freecad_logo = tk.PhotoImage(file=freecad_logo_path).subsample(4, 4)
            gmsh_logo = tk.PhotoImage(file=gmsh_logo_path).subsample(9, 9)
            blender_logo = tk.PhotoImage(file=blender_logo_path).subsample(6, 6)
            paraview_logo = tk.PhotoImage(file=paraview_logo_path).subsample(9, 9)

            # ---------------------------------------------
            # Create buttons with logos for the CAD viewers
            # ---------------------------------------------
            # Splash Visualizer button
            splash_button = tk.Button(
                popup,
                text="Open in Splash Viewer",
                command=self.open_splash_visualizer,
                image=splash_logo,
                compound="top",
                bg="white",
                highlightbackground="white",
                borderwidth=0,  # No border
                relief="flat"  # Flat appearance
            )
            splash_button.image = splash_logo
            splash_button.pack(side=tk.TOP, padx=30, pady=2)

            # Gmsh Visualizer button
            gmsh_button = tk.Button(
                popup,
                text="Open in Gmsh",
                command=open_gmsh,
                image=gmsh_logo,
                compound="top",
                bg="white",
                highlightbackground="white",
                borderwidth=0,  # No border
                relief="flat"  # Flat appearance
            )
            gmsh_button.image = gmsh_logo
            gmsh_button.pack(side=tk.TOP, padx=20, pady=2)

            # Blender Visualizer button
            blender_button = tk.Button(
                popup,
                text="Open in Blender",
                command=open_blender,
                image=blender_logo,
                compound="top",
                bg="white",
                highlightbackground="white",
                borderwidth=0,  # No border
                relief="flat"  # Flat appearance
            )
            blender_button.image = blender_logo
            blender_button.pack(side=tk.TOP, padx=20, pady=2)

            # FreeCAD Visualizer button
            freecad_button = tk.Button(
                popup,
                text="Open in FreeCAD",
                command=open_freecad,
                image=freecad_logo,
                compound="top",
                bg="white",
                highlightbackground="white",
                borderwidth=0,  # No border
                relief="flat"  # Flat appearance
            )
            freecad_button.image = freecad_logo
            freecad_button.pack(side=tk.TOP, padx=30, pady=2)

            # Paraview Visualizer button
            paraview_button = tk.Button(
                popup,
                text="Open in ParaView",
                command=open_paraview,
                image=paraview_logo,
                compound="top",
                bg="white",
                highlightbackground="white",
                borderwidth=0,  # No border
                relief="flat"  # Flat appearance
            )
            paraview_button.image = paraview_logo
            paraview_button.pack(side=tk.TOP, padx=30, pady=2)
#
            popup.mainloop()

        else:
            tk.messagebox.showerror("Error", "No file selected for import")
   # ------------------------------------- Importing the geometry -------------------------------------<

    def visualize_stl(self, file_path):
        # Read the STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_path)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Create a renderer, render window, and interactor
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        # Add the actor to the scene
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.1, 0.1)  # Background color

        # Render and interact
        render_window.Render()
        interactor.Start()

    def open_splash_visualizer(self):
        """
        Function to open the imported geometry in the Splash Visualizer.
        """
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            tk.messagebox.showerror("Error", "No geometry file selected for visualization.")
            return

        # Visualize the imported STL file using the existing functionality
        if self.selected_file_path.lower().endswith(".stl"):
            self.visualize_stl(self.selected_file_path)
        else:
            tk.messagebox.showerror("Error", "Splash Visualizer currently supports only STL files.")

    # Decoration function for CAD import
    def generate_cad_visual(self):
        cad_representation = self.create_cad_visual()
        self.text_box.delete(1.0, tk.END)  # Clear existing content
        self.text_box.insert(tk.END, cad_representation)

    def create_cad_visual(self):
        cad = ""
        cad += "+-----------+\n"
        cad += f"|           |\n"
        cad += "+           +\n"
        cad += f"|           |\n"
        cad += "+           +\n"
        cad += f"|           |\n"
        cad += "+-----------+"

         # Add the decorative pattern below the mesh
        pattern = """
 ____        _           _        ____    _    ____
/ ___| _ __ | | __ _ ___| |__    / ___|  / \\  |  _ \\
\\___ \\| '_ \\| |/ _` / __| '_ \\  | |     / _ \\ | | | |
 ___) | |_) | | (_| \\__ \\ | | | | |___ / ___ \\| |_| |
|____/| .__/|_|\\__,_|___/_| |_|  \\____/_/   \\_\\____/
      |_|
_____________________________________________________
\n"""
        return pattern + cad

    #=============================================================================
    def execute_command(self):
        #command = "source ~/.bashrc"; self.entry.get()
        command = self.entry.get()

        # Create a new terminal window and execute the command
        self.terminal_process = subprocess.Popen(
            #f"gnome-terminal -- bash -c 'source ~/.bashrc'",
            f"gnome-terminal -- bash -c '{command}; exec bash'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid,  # Create a new process group
        )

        # Disable the execute button
        self.execute_button.config(state=tk.DISABLED)

        # Monitor the terminal process and display the output
        self.monitor_terminal()

    def monitor_terminal(self):
        if self.terminal_process:
            try:
                # Read the standard output and standard error of the terminal
                output, _ = self.terminal_process.communicate(timeout=0.1)
                if output:
                    self.output_text.insert(tk.END, output)
                    self.output_text.see(tk.END)
            except subprocess.TimeoutExpired:
                # The terminal process is still running
                self.root.after(100, self.monitor_terminal)
            else:
                # The terminal process has completed
                self.execute_button.config(state=tk.NORMAL)
                self.status_label.config(text="Command executed successfully")
                #self.status_label.delete(0, END)

    # ===================Tool tip (hover over the button)=============================================
    def add_tooltip(self, widget, text):
        widget.bind("<Enter>", lambda event: self.show_tooltip_right(widget, text))
        widget.bind("<Leave>", lambda event: self.hide_tooltip())

    def show_tooltip_right(self, widget, text):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 150  # Adjust 25 as needed for the desired distance
        y += widget.winfo_rooty()
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=text, justify='left', background='#ffffe0', relief='solid', borderwidth=1)
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            del self.tooltip


    def setup_ui(self):
        # Create the Text widget
        self.text_box = tk.Text(self.root, wrap=tk.WORD, height=30, width=100)
        self.text_box.grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)  # Changed columnspan to 4 for better layout
        self.text_box.configure(foreground="lightblue", background="black", font=("courier", 10, "bold"))

        splash_welcome_msg = """






                       __        __   _                            _
                       \\ \\      / /__| | ___ ___  _ __ ___   ___  | |_ ___
                        \\ \\ /\\ / / _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\ | __/ _ \\
                         \\ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
                          \\_/\\_/ \\___|_|\\___\\___/|_| |_| |_|\\___|  \\__\\___/

                        ____        _           _     _____ ___    _    __  __
                       / ___| _ __ | | __ _ ___| |__ |  ___/ _ \\  / \\  |  \\/  |
                       \\___ \\| '_ \\| |/ _` / __| '_ \\| |_ | | | |/ _ \\ | |\\/| |
                        ___) | |_) | | (_| \\__ \\ | | |  _|| |_| / ___ \\| |  | |
                       |____/| .__/|_|\\__,_|___/_| |_|_|   \\___/_/   \\_\\_|  |_|
                             |_|


                                 Your gate to efficient CFD production!
                                 ______________________________________
        """
        self.text_box.insert(tk.END, splash_welcome_msg)

        # Make the Text widget read-only (for now it's "normal", can be "disabled" if needed)
        self.text_box.configure(state="normal")

        # Create a vertical scrollbar for the Text widget
        self.text_box_scrollbar = tk.Scrollbar(self.root, command=self.text_box.yview)
        self.text_box_scrollbar.grid(row=0, column=5, padx=1, pady=1, sticky='nsw', rowspan=9)  # Ensure it sticks to "nsw" for proper resizing
        self.text_box['yscrollcommand'] = self.text_box_scrollbar.set

        # Configure row and column weights for proper resizing
        self.root.grid_rowconfigure(0, weight=1)   # Ensures the row where the text box is resizable
        self.root.grid_rowconfigure(8, weight=1)   # Ensures the row for the scrollbar is resizable
        self.root.grid_columnconfigure(1, weight=1)  # Ensures the column where the text box is located resizes
        self.root.grid_columnconfigure(5, weight=0)  # Ensures the scrollbar column doesn't resize excessively

    def change_theme(self):
        # Ask for font
        current_font = self.text_box.cget("font")
        new_font = simpledialog.askstring("Font", "Enter font (e.g., Arial 12 bold)", initialvalue=current_font)
        if new_font:
            self.text_box.configure(font=new_font)

        # Ask for text color
        text_color = colorchooser.askcolor(color=self.text_box.cget("foreground"))[1]
        if text_color:
            self.text_box.configure(foreground=text_color)

        # Ask for background color
        bg_color = colorchooser.askcolor(color=self.text_box.cget("background"))[1]
        if bg_color:
            self.text_box.configure(background=bg_color)

        # Reset if the Reset checkbox is selected
        if self.reset_var.get():
            self.reset_theme()

    def toggle_reset(self):
        # Toggle between the Reset and user-chosen themes
        if self.reset_var.get():
            self.reset_theme()
        else:
            self.text_box.configure(font=self.initial_font)
            self.text_box.configure(foreground=self.initial_foreground)
            self.text_box.configure(background=self.initial_background)

    def reset_theme(self):
        # Reset to initial values
        self.text_box.configure(font=self.initial_font)
        self.text_box.configure(foreground=self.initial_foreground)
        self.text_box.configure(background=self.initial_background)

    #____________________________________________ sourcing OF __________________________________________________
    # Sourcing openfoam (version option)
    def source_openfoam(self, version, popup):
        paths = {
            "8": "/opt/openfoam8/etc/bashrc",
            "9": "/opt/openfoam9/etc/bashrc",
            "10": "/opt/openfoam10/etc/bashrc",
            "11": "/opt/openfoam11/etc/bashrc",
            "12": "/opt/openfoam12/etc/bashrc",
            "2212": "/usr/lib/openfoam/openfoam2212/etc/bashrc",
            "2306": "/usr/lib/openfoam/openfoam2306/etc/bashrc",
            "2312": "/usr/lib/openfoam/openfoam2312/etc/bashrc",
            "2406": "/usr/lib/openfoam/openfoam2406/etc/bashrc"
        }
        bashrc_path = paths.get(version)
        if not bashrc_path:
            messagebox.showerror("Error", "Unsupported OpenFOAM version specified.")
            popup.destroy()
            return

        command = f'source {bashrc_path}'
        #command = f'source {bashrc_path} && env'
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable="/bin/bash")
        output, errors = process.communicate()

        if errors:
            error_message = errors.decode()
            messagebox.showerror("Error Sourcing OpenFOAM", f"Failed to source OpenFOAM version {version}. Please make sure the chosen version is pre-installed on your system!")
            self.openfoam_sourced = False
            popup.destroy()
            return
        else:
            self.selected_openfoam_path = bashrc_path  # Update the path

        # Decode the output and split it into lines
        env_vars = output.decode().split('\n')

        # Set each environment variable in the current Python process
        for var in env_vars:
            parts = var.split('=', 1)
            if len(parts) == 2:
                os.environ[parts[0]] = parts[1]

        # If you reach this point, sourcing was successful
        print(f"Sourced OpenFOAM version {version}!")
        messagebox.showinfo("Success", f"Sourced OpenFOAM version {version} successfully!")
        self.openfoam_sourced = True
        return True
        popup.destroy()

    def select_openfoam_version(self):
        # Create a popup window
        popup = tk.Toplevel(self.root)
        popup.title("Select OpenFOAM Version")
        popup.geometry("350x450")
        selected_version = tk.StringVar(value="2306")  # Set the default version to v2306

        # Create a style object for custom styling
        style = ttk.Style()

        # Configure radiobutton padding
        style.configure("TRadiobutton", padding=5)

        # Custom style for section titles
        style.configure("Title.TLabel", font=("TkDefaultFont", 12, "bold"), foreground="darkblue")

        # OpenFOAM Foundation Versions
        foundation_frame = ttk.LabelFrame(popup, text="OpenFOAM Foundation", padding=(10, 5))
        foundation_frame.pack(side='top', padx=10, pady=10, fill='both', expand=True)

        # Foundation versions
        foundation_versions = [("v8", "8"), ("v9", "9"), ("v10", "10"), ("v11", "11"), ("v12", "12")]
        for text, version in foundation_versions:
            ttk.Radiobutton(foundation_frame, text=text, variable=selected_version, value=version, style="TRadiobutton").pack(anchor='w')

        # OpenFOAM ESI Versions
        extended_frame = ttk.LabelFrame(popup, text="OpenFOAM ESI", padding=(10, 5))
        extended_frame.pack(side='top', padx=10, pady=10, fill='both', expand=True)

        # ESI versions (default selected is v2306)
        extended_versions = [("v2212", "2212"), ("v2306", "2306"), ("v2312", "2312"), ("v2406", "2406")]
        for text, version in extended_versions:
            ttk.Radiobutton(extended_frame, text=text, variable=selected_version, value=version, style="TRadiobutton").pack(anchor='w')

        # Activate button
        def activate_and_close():
            version = selected_version.get()
            if version:
                self.source_openfoam(version, popup)
                popup.destroy()

        ttk.Button(popup, text="Activate", command=activate_and_close).pack(pady=10)

        # Ensure popup is modal
        popup.transient(self.root)
        popup.grab_set()
        self.root.wait_window(popup)

    #____________________________________________ sourcing OF __________________________________________________

    def open_contact_page(self, event=None):
        webbrowser.open_new("https://www.simulitica.com/contact")
    def support_Splash(self, event=None):
        webbrowser.open_new("https://www.buymeacoffee.com/simulitica")
    def splash_online_manual(self, event=None):
        webbrowser.open_new("https://github.com/mohamedalysayed/Splash/tree/main")
    def splash_GPT_page(self, event=None):
        webbrowser.open_new("https://chat.openai.com/g/g-RGYvE3TsL-splash-gpt")
    def cloud_HPC(self, event=None):
        webbrowser.open_new("https://cfddose.substack.com/p/cfd-free-from-complexity")


# ---------------------------------------------------------------------------<
# Hot links
# https://www.simulitica.com/splash-v10
# https://www.buymeacoffee.com/simulitica # poor simulitica :(
# https://www.udemy.com/course/t-flows-crash-course-cfd/ -> T-Flows on Udemy
# ---------------------------------------------------------------------------<


if __name__ == "__main__":
    try:
        root = tk.Tk()
    except tk.TclError as e:
        # No display available (e.g. headless SSH, missing $DISPLAY)
        print(f"Error: could not initialize a Tk display: {e}", file=__import__('sys').stderr)
        raise SystemExit(1)

    root.option_add('*tearOff', False)  # Disable menu tear-off
    root.title("Splash v0.2")
    root.wm_title("Splash v0.2")  # Window manager title

    try:
        app = Splash(root)
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Splash failed to start", f"{type(e).__name__}: {e}")
        except Exception:
            pass
        raise SystemExit(1)

    root.mainloop()
