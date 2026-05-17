"""License countdown / elapsed-timer mixin for the Splash main window.

Splits the recurring `update_timer` loop, license expiration popup, and
on-disk timer persistence out of `Splash.py`. The mixin reads/writes:
    self.start_time, self.timer_label, self.license_start_date_file,
    self.license_duration, self.notice_period_before_end,
    self.elapsed_time_file, self.root
which `Splash.__init__` is responsible for setting up before
`update_timer()` is called.
"""

import os
import time
import tkinter as tk
import webbrowser
from tkinter import ttk


class LicenseMixin:
    def update_timer(self):
        current_time = time.time()

        # Calculate elapsed time since the app was opened
        app_elapsed_time = current_time - self.start_time
        hours, remainder = divmod(int(app_elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        tenths_of_second = int((app_elapsed_time - int(app_elapsed_time)) * 10)

        # Update the elapsed time label
        self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}.{tenths_of_second}")

        # Load or set the license start date. If the file is missing, empty, or
        # corrupt, treat *now* as the start date and rewrite it — better than crashing.
        license_start_date = None
        if os.path.exists(self.license_start_date_file):
            try:
                with open(self.license_start_date_file, "r") as file:
                    license_start_date = float(file.read().strip())
            except (ValueError, OSError):
                license_start_date = None
        if license_start_date is None:
            license_start_date = current_time
            try:
                with open(self.license_start_date_file, "w") as file:
                    file.write(str(current_time))
            except OSError as e:
                print(f"Warning: could not write license file: {e}")

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
            welcome_image_path = os.path.join(base_path, "../Resources/Logos/simulitica_icon_logo.png")
            if os.path.exists(welcome_image_path):
                try:
                    welcome_image = tk.PhotoImage(file=welcome_image_path)
                    welcome_image = welcome_image.subsample(4, 4)
                    license_message_label.config(image=welcome_image, compound="top")
                    license_message_label.image = welcome_image  # Keep a reference
                except tk.TclError as e:
                    print(f"Warning: could not load license popup image: {e}")

            # OSS edition: point users at the public repo rather than the commercial
            # Splash-CFD product page, so this build is independent of the paid SKU.
            renew_button = ttk.Button(popup, text="Get the latest Splash", command=lambda: webbrowser.open_new_tab("https://github.com/cfddose/Splash"))
            renew_button.pack(pady=20)

    def load_last_recorded_time(self):
        if os.path.exists(self.elapsed_time_file):
            try:
                with open(self.elapsed_time_file, "r") as file:
                    last_time = float(file.read().strip())
                    return time.time() - last_time
            except (ValueError, OSError):
                return time.time()
        return time.time()

    def save_elapsed_time(self):
        try:
            with open(self.elapsed_time_file, "w") as file:
                elapsed_time = time.time() - self.start_time
                file.write(str(elapsed_time))
        except OSError as e:
            print(f"Warning: could not save elapsed time: {e}")
            return

        # Make the file hidden on Windows via the safe Win32 API (avoids shell-injection
        # risk and quoting issues from the old os.system('attrib +h ...') call).
        if os.name == 'nt':
            try:
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                ctypes.windll.kernel32.SetFileAttributesW(self.elapsed_time_file, FILE_ATTRIBUTE_HIDDEN)
            except Exception as e:
                print(f"Warning: could not hide elapsed time file: {e}")

    # Saving elapsed time on closing the app (now ignored!)
    def on_closing(self):
        self.save_elapsed_time()
        self.root.destroy()
