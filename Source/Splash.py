# Standard library imports 
import os
import re
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

class Splash:  
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

        # Load the icon
        if os.path.exists(icon_path):  # Check if the file exists before loading
            icon_image = tk.PhotoImage(file=icon_path)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon_image)
        else:
            print(f"Error: Icon file not found at {icon_path}")
    
        # Set the window icon using a PhotoImage
        #icon_path = "../Resources/Logos/simulitica_icon_logo.png"  # Replace with the actual path to your icon file
        icon_image = tk.PhotoImage(file=icon_path)
        self.root.tk.call('wm', 'iconphoto', self.root._w, icon_image)
        
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
        self.license_start_date_file = "license_start_date.txt"  # File to store the start date
        self.license_duration = 1 * 365 * 24 * 3600  # 1 year in seconds
        #self.license_duration = 14 * 24 * 3600  # 14 days in seconds
        self.notice_period_before_end = 15 * 24 * 3600  # Notify 15 days before the license expires
        self.elapsed_time_file = ".elapsed_time.txt"  # Making the file name start with a dot to "hide" it in Unix/Linux
        
        # Create a label for the "Elapsed Time" text
        self.elapsed_time_label = tk.Label(root, text="Elapsed Time", font=("Helvetica", 24), bg="white", fg="darkblue")
        self.elapsed_time_label.grid(row=0, column=7, sticky="nsew")  # Updated to sticky="nsew" for dynamic resizing
        
        # Create a label for the timer
        self.timer_label = tk.Label(root, text="00:00:00.0", font=("Helvetica", 35, "bold"), bg="white", fg="darkblue")
        self.timer_label.grid(row=1, column=7, sticky="nsew")  # Updated to sticky="nsew" for dynamic resizing
        
        # Start updating the timer
        self.update_timer()
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
        # Define the path for the new file
        new_file_path = os.path.join(os.getcwd(), "new_file.txt")

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
            

    def open_replace_properties_popup(self, old_values_mixture, old_values_thermo_type):
        selected_file = self.selected_file_path
        if selected_file:
            # Open a popup to replace the properties for the mixture and thermoType blocks
            ReplacePropertiesPopup(self, self.thermo_type_params, self.mixture_params, old_values_thermo_type, old_values_mixture)

        else:
            tk.messagebox.showerror("Error", "Please select a valid file first.")
            
    def detect_current_fuel(self):
        # Assuming the path is in the format '.../OpenFOAM-<version>/cases/<case_name>/constant/physicalProperties'
        parts = os.path.abspath(self.selected_file_path).split('.')   #split(os.sep)
        #partsi = os.path.abspath(self.selected_file_path).split('constant')   #split(os.sep)
        try:
            #index = parts.index('constant') 
            current_fuel = parts[1] # 0 + 1
            #print(current_fuel)
            return current_fuel
        except ValueError:
            return None
                  
    def on_fuel_selected(self, event):
        selected_fuel = self.fuel_options_menu.get().lower()
        if selected_fuel and selected_fuel != "Fuel Options":
            current_fuel = self.detect_current_fuel()
            if current_fuel:
                self.status_label.config(text=f"Current fuel: {current_fuel}")
                self.replace_fuel(selected_fuel, current_fuel)

    def replace_fuel(self, selected_fuel, current_fuel):
        # Assuming the 'constant' directory is inside the case directory
        case_directory = os.path.dirname(os.path.dirname(self.selected_file_path))
            
        
        # Use find and exec to run sed on all files under the 'constant' directory
        sed_command = f"find {case_directory}/constant -type f -exec sed -i 's/{current_fuel}/{selected_fuel}/g' {{}} +"
        
        # Execute the sed command
        subprocess.run(sed_command, shell=True)
        
        # --------------------- Renaming files inside constant/ after the selected fuel ----------------------->
        # Rename the file associated with the current fuel
        current_file_path = os.path.join(case_directory, 'constant', f'physicalProperties.{current_fuel.lower()}')
        new_file_path = os.path.join(case_directory, 'constant', f'physicalProperties.{selected_fuel.lower()}')
        try:
            os.rename(current_file_path, new_file_path)
            tk.messagebox.showinfo("Fuel option", f"Fuel has been updated to {selected_fuel}!")
        except FileNotFoundError:
            # Handle the case where the file does not exist
            pass
            
        # Update the status label
        self.status_label.config(text=f"Fuel replaced. Selected fuel: {selected_fuel}")
        # -----------------------------------------------------------------------------------------------------<

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
        
    # -------------- Welcome Message -------------------------- 
     
    # -------------- Splash background image(s) -------------------------->  

##    # Clickable background image (process STL file)
##    #______________________________________________
##    def add_bgImage(self):
##        # Specify the image path
##        image_path = "../Resources/Images/racing-car.png"

##        # Create a tk.PhotoImage object directly from the file
##        self.splash_bgImage = tk.PhotoImage(file=image_path)

##        # Adjust the subsample as needed
##        self.splash_bgImage = self.splash_bgImage.subsample(6, 6)

##        # Create a button with the image, and bind it to the process_stl function
##        self.splash_bgImage_button = tk.Button(
##            self.root, 
##            image=self.splash_bgImage, 
##            bg="white",  # Set background color to white
##            activebackground="white",  # Set active background to white to prevent color change on click
##            bd=0,  # Remove border
##            command=self.process_stl_click,  # Attach the function directly
##            cursor="hand2",  # Set cursor to hand on hover
##            relief="flat"  # Flat border style
##        )

##        # Use grid() for layout
##        self.splash_bgImage_button.grid(row=2, column=7, pady=5, padx=10, sticky="nsew", rowspan=6)


         # Clickable background image (website link)
         #______________________________________________
#        # Create a label to display the image, initially without the frame effect [FLAG: Do we need this at all?!]
#        self.splash_bgImage_label = tk.Label(self.root, image=self.splash_bgImage, bg="white", cursor="hand2")
#        self.splash_bgImage_label.grid(row=2, column=7, pady=1, padx=10, sticky="nsew", rowspan=4)

#        # Bind the hover effect
#        self.splash_bgImage_label.bind("<Enter>", self.on_hover)
#        self.splash_bgImage_label.bind("<Leave>", self.off_hover)

#        # Make the image clickable
#        #self.splash_bgImage_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.buymeacoffee.com/simulitica/membership"))
#        #self.splash_bgImage_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.skool.com/cfd-dose-5227/about"))
#        self.splash_bgImage_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.cfddose.substack.com"))

#    def on_hover(self, event):
#        # Change the label appearance to simulate a frame around it on hover
#        event.widget.config(bg="white", bd=1, relief="groove")

#    def off_hover(self, event):
#        # Revert the label appearance when not hovering over it
#        event.widget.config(bg="white", bd=0, relief="flat")

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

# -------------------------------- Mesh Construction ------------------------------>
    def create_mesh(self):
        # Check if geometry is loaded
        if not self.geometry_loaded:
            messagebox.showinfo("Geometry Not Loaded", "Please load a geometry before creating the mesh.")
            return

        # Ask the user for mesh type using clickable buttons
        self.mesh_type = self.ask_mesh_type()

        if self.mesh_type is not None:

            # Define the source directory for Allmesh* files and "system" directory
            meshing_directory = os.path.join(os.path.dirname(os.getcwd()), "Meshing")


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
            chmod_command = ["chmod", "+x", cartMesh_script]
            subprocess.run(chmod_command, check=True)

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
/ ___| _ __ | | __ _ ___| |__    / ___|  / \  |  _ \ 
\___ \| '_ \| |/ _` / __| '_ \  | |     / _ \ | | | |
 ___) | |_) | | (_| \__ \ | | | | |___ / ___ \| |_| |
|____/| .__/|_|\__,_|___/_| |_|  \____/_/   \_\____/ 
      |_|                                                                          
_____________________________________________________
\n"""
        return pattern + cad
            
        
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
/ ___| _ __ | | __ _ ___| |__   |  \/  | ___  ___| |__   ___ _ __ 
\___ \| '_ \| |/ _` / __| '_ \  | |\/| |/ _ \/ __| '_ \ / _ \ '__|
 ___) | |_) | | (_| \__ \ | | | | |  | |  __/\__ \ | | |  __/ |   
|____/| .__/|_|\__,_|___/_| |_| |_|  |_|\___||___/_| |_|\___|_|   
      |_|                                                         
__________________________________________________________________
\n"""
        return pattern + mesh

          
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
/ ___| _ __ | | __ _ ___| |__   |  _ \| | | | \ | |
\___ \| '_ \| |/ _` / __| '_ \  | |_) | | | |  \| |
 ___) | |_) | | (_| \__ \ | | | |  _ <| |_| | |\  |
|____/| .__/|_|\__,_|___/_| |_| |_| \_\\____/|_| \_|
      |_|                                            
_____________________________________________________
\n"""
        return pattern + run
        
    # # Loading an existing OpenFOAM case
    # def load_case(self):
    #     self.selected_directory = filedialog.askdirectory()
    #     if self.selected_directory:
    #         # Check if the selected directory contains the necessary OpenFOAM folders
    #         base_folders = ["constant", "system"]
    #         time_folders = ["0", "0.orig"]  # Check for either '0' or '0.orig'

    #         # Check if 'constant' and 'system' folders exist
    #         base_folders_exist = all(os.path.isdir(os.path.join(self.selected_directory, d)) for d in base_folders)
    #         # Check if either '0' or '0.orig' exists
    #         time_folder_exists = any(os.path.isdir(os.path.join(self.selected_directory, t)) for t in time_folders)

    #         if base_folders_exist and time_folder_exists:
    #             self.selected_file_path = self.selected_directory
    #             self.status_label.config(text=f"Case directory identified: {self.selected_directory}", foreground="darkblue")
    #             self.run_simulation_button["state"] = tk.NORMAL  # Enable the "Run Simulation" button
    #             self.initialize_simulation_button["state"] = tk.NORMAL  
    #             self.configure_simulation_button["state"] = tk.NORMAL  
    #             self.stop_simulation_button["state"] = tk.NORMAL 
                
    #             # Create a dummy 'splash.foam' file in the selected directory
    #             try:
    #                 dummy_file_path = os.path.join(self.selected_directory, "splash.foam")
    #                 with open(dummy_file_path, 'w') as dummy_file:
    #                     dummy_file.write('')  # Write an empty string to create an empty file
    #             except Exception as e:
    #                 self.status_label.config(text=f"Error creating 'splash.foam': {e}", foreground="red")
                    
    #             # Check for constant/polyMesh directory
    #             polyMesh_path = os.path.join(self.selected_directory, "constant", "polyMesh")
    #             if os.path.isdir(polyMesh_path):
    #                 # Prompt the user
    #                 response = messagebox.askyesno("Mesh Confirmation", "This case seems to have a mesh, do you want to load it?")
    #                 if response:
    #                     self.paraview_application()  # Call the function to load the mesh

    #             # Additional OpenFOAM-related checks can be added here
                
    #         else:
    #             messagebox.showerror("Invalid OpenFOAM Case", "The selected folder does not represent a valid OpenFOAM case. ")
    #             self.status_label.config(text="Invalid OpenFOAM case selected!", foreground="red")
    #             self.run_simulation_button["state"] = tk.DISABLED  # Disable the "Run Simulation" button
    #             self.initialize_simulation_button["state"] = tk.DISABLED  
    #             self.configure_simulation_button["state"] = tk.DISABLED  
    #             self.stop_simulation_button["state"] = tk.DISABLED  
    #     else:
    #         self.status_label.config(text="No case directory selected!", foreground="darkblue")
    #         self.run_simulation_button["state"] = tk.DISABLED  # Disable the "Run Simulation" button
    #         self.initialize_simulation_button["state"] = tk.DISABLED  
    #         self.configure_simulation_button["state"] = tk.DISABLED  
    #         self.stop_simulation_button["state"] = tk.DISABLED  

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
                        subprocess.run(mesh_script_path, shell=True, check=True, cwd=self.selected_directory)
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
            chmod_command = ["chmod", "+x", allclean_script]
            subprocess.run(chmod_command, check=True)

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

                chmod_command = ["chmod", "+x", temp_clean_script_path]
                self.text_box.delete(1.0, tk.END)  # Clear existing content
                subprocess.run(chmod_command, check=True)

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

            chmod_command = ["chmod", "+x", allrun_script]
            subprocess.run(chmod_command, check=True)

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
#______________________________________________________________________
    # FLAG: essentially intended to be dedicated for checkMesh script****
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
#__________________________________________________________________           
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
                       \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___     
                        \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \    
                         \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |   
                          \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/    
                                                                                 
                        ____        _           _     _____ ___    _    __  __ 
                       / ___| _ __ | | __ _ ___| |__ |  ___/ _ \  / \  |  \/  |
                       \___ \| '_ \| |/ _` / __| '_ \| |_ | | | |/ _ \ | |\/| |
                        ___) | |_) | | (_| \__ \ | | |  _|| |_| / ___ \| |  | |
                       |____/| .__/|_|\__,_|___/_| |_|_|   \___/_/   \_\_|  |_|
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

    # Splash Timer (license related)
    def update_timer(self):
        current_time = time.time()

        # Calculate elapsed time since the app was opened
        app_elapsed_time = current_time - self.start_time
        hours, remainder = divmod(int(app_elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        tenths_of_second = int((app_elapsed_time - int(app_elapsed_time)) * 10)

        # Update the elapsed time label
        self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}.{tenths_of_second}")
    
        # Load or set the license start date
        if not os.path.exists(self.license_start_date_file):
            with open(self.license_start_date_file, "w") as file:
                file.write(str(current_time))
            license_start_date = current_time
        else:
            with open(self.license_start_date_file, "r") as file:
                license_start_date = float(file.read())

        # Calculate remaining license duration
        elapsed_time_since_start = current_time - license_start_date
        remaining_time = self.license_duration - elapsed_time_since_start

        # Check if it's time to notify about the license expiration
        if 0 < remaining_time <= self.notice_period_before_end:
            self.notify_license_expiration(remaining_time, expiring_soon=True)
        elif remaining_time <= 0:
            self.notify_license_expiration(remaining_time, expiring_soon=False)

        # Schedule the next update if license has not expired
        if remaining_time > 0:
            self.root.after(100, self.update_timer)
        else:
            # Optionally delay closing to allow the user to read the message
            self.root.after(10000, self.root.destroy)  # Closes the app after 10 seconds

    def notify_license_expiration(self, remaining_time, expiring_soon=True):
        # Prevent multiple notifications
        if not hasattr(self, 'license_expiration_notified'):
            self.license_expiration_notified = True  # Set the flag immediately

            if expiring_soon:
                remaining_days = remaining_time / (3600 * 24)  # Convert remaining time in seconds to days
                if remaining_days < 1:
                    # For less than 1 day, show the remaining hours
                    remaining_hours = remaining_time / 3600
                    message = f"License Expiring Soon!\nYour license will expire in less than {remaining_hours:.0f} hours. Please save your work."
                else:
                    # For 1 day or more, show the remaining days
                    message = f"License Expiring Soon!\nYour license will expire in less than {remaining_days:.0f} days. Please save your work."
            else:
                message = "License Expired!\nYour license has already expired. Please renew your license to continue using Splash."

            license_message = (
                "\n"
                f"{message}\n\n"
                "_____________________________________________________________________________\n"
                "\n"
                "Copyright (C) Simulitica Ltd. [now CFD Dose] - All Rights Reserved.\n"
                "This program is licensed under the GNU Lesser General Public License (LGPL) 3.0.\n"
                "You may redistribute and/or modify this software under the terms of the LGPL.\n"
                "For full license details, please refer to the LICENSE file provided with this software.\n"
                "Written by Mohamed Aly SAYED (mohamed.sayed@simulitica.com), November 2023.\n"
                "_____________________________________________________________________________"
            )

            # Create a Toplevel window for the message
            popup = tk.Toplevel(self.root)
            popup.title("Splash v0.2")
            popup.geometry("800x600")  # Adjust the size as needed

            # Create a Label in the Toplevel window to display the message
            license_message_label = tk.Label(popup, text=license_message, font=("Helvetica", 14, "bold"), fg="darkblue", justify='center')
            license_message_label.pack(padx=10, pady=10)

            # Create a PhotoImage object and set it to the Label
            base_path = os.path.dirname(os.path.abspath(__file__))
            welcome_image = tk.PhotoImage(file=os.path.join(base_path, "../Resources/Logos/simulitica_icon_logo.png"))
            #welcome_image = tk.PhotoImage(file="../Resources/Logos/simulitica_icon_logo.png")  
            welcome_image = welcome_image.subsample(4, 4)  # Adjust subsampling as needed
            license_message_label.config(image=welcome_image, compound="top")
            license_message_label.image = welcome_image  # Keep a reference

            # Create a "Renew License Now" button inside the popup
            renew_button = ttk.Button(popup, text="Renew License Now", command=lambda: webbrowser.open_new_tab("https://www.simulitica.com/splash-v1"))
            renew_button.pack(pady=20)  # Adjust padding as needed

# ---------------------------------------------------------------------------<
# Hot links
# https://www.simulitica.com/splash-v10
# https://www.buymeacoffee.com/simulitica # poor simulitica :( 
# https://www.udemy.com/course/t-flows-crash-course-cfd/ -> T-Flows on Udemy
# ---------------------------------------------------------------------------<
    def load_last_recorded_time(self):
        if os.path.exists(self.elapsed_time_file):
            with open(self.elapsed_time_file, "r") as file:
                try:
                    last_time = float(file.read())
                    return time.time() - last_time
                except ValueError:   
                    return time.time()
        else:
            return time.time()

    def save_elapsed_time(self):
        with open(self.elapsed_time_file, "w") as file:
            elapsed_time = time.time() - self.start_time
            file.write(str(elapsed_time))

        # Make the file hidden on Windows
        if os.name == 'nt':  # Checking if the OS is Windows
            os.system(f'attrib +h {self.elapsed_time_file}')
     
    # Saving elapsed time on closing the app (now ignored!)
    def on_closing(self):
        self.save_elapsed_time()
        self.root.destroy()
        
if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*tearOff', False)  # Disable menu tear-off
    root.title("Splash v0.2")
    root.wm_title("Splash v0.2")  # Window manager title
    app = Splash(root)
    root.mainloop()
