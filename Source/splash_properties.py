"""Fuel / properties mixin for the Splash main window.

Wraps the "Replace Properties" popup and the fuel-substitution flow that
rewrites every file under a case's `constant/` directory.

Depends on the host class for: self.selected_file_path, self.thermo_type_params,
self.mixture_params, self.fuel_options_menu, self.status_label.
"""

import os
import tkinter as tk

from ReplaceProperties import ReplacePropertiesPopup


class PropertiesMixin:
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

        # Replace fuel name in every file under constant/. Done in pure Python rather
        # than shelling out to find/sed so fuel names containing shell metacharacters
        # or sed delimiters can't be injected.
        constant_dir = os.path.join(case_directory, "constant")
        if os.path.isdir(constant_dir):
            for dirpath, _dirnames, filenames in os.walk(constant_dir):
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            contents = f.read()
                    except OSError:
                        continue
                    if current_fuel in contents:
                        try:
                            with open(fpath, "w", encoding="utf-8") as f:
                                f.write(contents.replace(current_fuel, selected_fuel))
                        except OSError as e:
                            print(f"Warning: could not rewrite {fpath}: {e}")

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
