# Importing necessary libraries and modules
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import asyncio
import os
import time
import getpath
import urlinfo
import urlreq

# Color constants for the application interface
BASE_COLOR = "#FAFAFA"
FRAME_COLOR = "#D4D4D8"
LOADING_BG = "#E4E4E7"
LOADING_FG = "#22C55E"
ENTRY_BG = "#E4E4E7"
BORDER_COLOR = "#A1A1AA"
BUTTON_BG = "#38BDF8"
BUTTON_HOVER = "#0EA5E9"
BUTTON_TEXT = "#FAFAFA"
HEADING_BG = "#E4E4E7"
TABLE_COLOR = "#A1A1AA"
TEXT_COLOR = "#09090B"
FADED_TEXT = "#71717A"

# Initialize global variables for status label
URL = "None"
STATUS = "None"
SIZE = "NaN"
CURSIZE = "NaN"
SPEED = "NaN"
TIMELEFT = "NaN"

# Initial values for global variables
ROW = 0
UPDATE = True
SIZE_CHANGE = 0
TEMP_SIZE = 0

if __name__ == "__main__":
    # Create an instance of CTk window
    root = ctk.CTk()
    geometry = "680x480"
    
    # Function to center the window on the screen
    def center_win(root, geometry):
        root.update_idletasks()
        
        scr_width = root.winfo_screenwidth()
        scr_height = root.winfo_screenheight()
        
        size = tuple(int(_) for _ in geometry.split("+")[0].split("x"))
        
        x = (scr_width // 2) - (size[0] // 2)
        y = (scr_height // 2) - (size[1] // 2)
        
        root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")
    
    # Configure the main window
    root.geometry(geometry)
    root.configure(bg_color = BASE_COLOR)
    root.title("Photon Download Manager 1.0.0-alpha")
    root.iconbitmap(getpath.base("public/icon.ico"))
    root.resizable(False, False)
    
    # Center the window on the screen
    center_win(root, geometry)
    
    # Create the main frame
    main_frame = ctk.CTkFrame(root, corner_radius = 4, fg_color = FRAME_COLOR)
    main_frame.grid(row = 0, column = 0, padx = 16, pady = (16, 0), sticky = "nsew")    
    main_frame.grid_columnconfigure(0, weight = 1)
    main_frame.grid_rowconfigure(0, weight = 1)
    
    root.grid_columnconfigure(0, weight = 1)
    root.grid_rowconfigure(1, weight = 1)
    
    # Initialize URL input variable
    url_var = tk.StringVar()
    url_var.set("Enter URL")
    
    # Function to reset global variables
    def reset_vars():
        global URL, STATUS, SIZE, CURSIZE, SPEED, TIMELEFT
        global ROW, SIZE_CHANGE, TEMP_SIZE
        
        root.title("Photon Download Manager 1.0.0-alpha")
        
        URL = "None"
        STATUS = "None"
        SIZE = "NaN"
        CURSIZE = "NaN"
        SPEED = "NaN"
        TIMELEFT = "NaN"
        
        ROW = 0
        SIZE_CHANGE = 0
        TEMP_SIZE = 0
    
    # Event handler for entry click
    def on_entry_click(event):
        if url_var.get() == "Enter URL":
            url_entry.configure(text_color = TEXT_COLOR)
            url_var.set("")
    
    # Event handler for focus out        
    def on_focus_out(event):
        if url_var.get() == "":
            url_entry.configure(text_color = FADED_TEXT)
            url_var.set("Enter URL")
    
    # Function to remove focus from the entry    
    def leave_entry(event):
        root.focus()
    
    # Function to get the current status as a formatted string
    def get_status():
        status = f"""
        URL\t\t\t: {URL}
        Status\t\t: {STATUS}
        
        File size\t\t: {SIZE}
        Downloaded\t\t: {CURSIZE}
        Transfer rate\t\t: {SPEED}
        Time left\t\t: {TIMELEFT}
        """
        
        return status
    
    # Function to truncate the URL if it is too long
    def cut_url(url):
        if len(url) >= 74:
            url = url[:74]
            url = f"{url}..."
        
        return url
    
    # Function to handle the download process 
    def download():
        global URL, STATUS, SIZE, CURSIZE, SPEED, TIMELEFT
        global ROW, UPDATE, TEMP_SIZE

        url = url_var.get()

        URL = cut_url(url)
        STATUS = "Preparing..."
        UPDATE = True
        
        # Delete the entire contents of the info_table
        for item in info_table.get_children():
            info_table.delete(item)
        
        update_status()  # Update the status
        
        if URL and URL != "Enter URL":
            url_entry.configure(text_color = FADED_TEXT)
            url_var.set("Enter URL")
            
            leave_entry(None)
            
            info = urlinfo.MimeType(url)
            ext, size = info(True)
            
            STATUS = "Collecting data..."
            SIZE = f"{(size / (1024 ** 2)):.2f} Mb"
            
            update_status()  # Update the status
            
            req = urlreq.URLReq(url, size, ext)
            
            # Starts the file download process
            thread = threading.Thread(target = req.get_file)
            thread.start()
            
            # Function to run internet speed test function
            def speedtest():
                global SPEED
                
                SPEED = f"{(asyncio.run(req.get_speed()) / (1024 * 8)):.2f} Mbps"
            
            # Function to perform periodic update
            def periodic_update():
                global ROW, SIZE_CHANGE
                
                if UPDATE:
                    if (TEMP_SIZE != CURSIZE):
                        SIZE_CHANGE = TEMP_SIZE
                        ROW += 1

                        update_table()
                        
                        # Function to mark successful download task
                        def success():
                            update_table("Success")
                        
                            root.after(1000, periodic_update)
                            
                        root.after(1000, success)
                    else:
                        root.after(1000, periodic_update)
            
            # Function to stop periodic update
            def stop_update():
                global UPDATE
                
                UPDATE = False
            
            first_index = True
            sec_index = False
            
            # Updates the status on the label every 0.1 seconds
            while not req.DONE:
                cursize, percentage, timeleft = req.get_cursize()
                
                speed_thread = threading.Thread(target = speedtest)
                speed_thread.start()
                
                CURSIZE = f"{cursize / (1024 ** 2):.2f} Mb ({percentage:.2f}%)"
                TIMELEFT = f"{timeleft:.2f} sec"
                TEMP_SIZE = cursize
                
                root.title(f"({percentage:.2f}%) Photon Download Manager 1.0.0-alpha")
                
                # Executes the periodic_update function on the second index
                if sec_index:
                    update_thread = threading.Thread(target = periodic_update)
                    update_thread.start()
                    
                    sec_index = False
                elif first_index:                    
                    first_index = False
                    sec_index = True
                else:
                    update_status()
                
                    download_bar.set(percentage / 100)
                    
                time.sleep(0.1)
            
            CURSIZE = f"{(size / (1024 ** 2)):.2f} Mb ({100.00}%)"
            
            download_bar.set(1)
            root.title(f"({100.00}%) Photon Download Manager 1.0.0-alpha")
            
            update_status()
        
        # Function to reset all processes
        def reset_all():
            download_bar.set(0)
            
            stop_update()  # Stop the update
            reset_vars()  # Reset the variables
            update_status()  # Update the status
        
        root.after(2000, reset_all)
        
    def update_status():
        # Update the status label with the current status
        status_label.configure(text = get_status())
        status_label.update_idletasks()  # Refresh the label to reflect the change
        
    def update_table(status = "Collecting data..."):
        # Update the status of the last row when the download is success
        if status == "Success":
            iid = info_table.get_children()[ROW - 1]
            info_table.set(iid, "Status", status)
        else:
            # Insert a new row with the current status during the download process
            info_table.insert("", ROW - 1, text = f"{ROW}", values = (ROW, CURSIZE, status))
        
        info_table.update_idletasks()  # Refresh the table to reflect the change
        
    def start_download():
        # Start the download process in a separate thread
        thread = threading.Thread(target = download)
        thread.start()
    
    # Create a frame for the URL entry and download button
    url_frame = ctk.CTkFrame(main_frame, corner_radius = 4, fg_color = FRAME_COLOR)
    url_frame.grid(row = 0, column = 0, padx = 12, pady = (12, 8), sticky = "nsew")
    url_frame.grid_columnconfigure(0, weight = 1)
    url_frame.grid_rowconfigure(0, weight = 1)
    
    # Create an entry widget for the URL input
    url_entry = ctk.CTkEntry(url_frame, textvariable = url_var, corner_radius = 4, fg_color = ENTRY_BG, height = 24, border_width = 1, 
                             border_color = BORDER_COLOR, text_color = FADED_TEXT, font = ("Arial", 12, "normal"))
    url_entry.grid(row = 0, column = 0, padx = (0, 8), pady = 0, sticky = "ew")
    
    url_entry.bind("<FocusIn>", on_entry_click)  # Bind event handler for focus in
    url_entry.bind("<FocusOut>", on_focus_out)  # Bind event handler for focus out
    url_entry.bind("<Return>", leave_entry)  # Bind event handler for return key
    
    # Create a button to start the download process
    download_button = ctk.CTkButton(url_frame, text = "Download", height = 24, width = 86, corner_radius = 4, fg_color = BUTTON_BG, 
                                    hover_color = BUTTON_HOVER, text_color = BUTTON_TEXT, font = ("Arial", 12, "normal"), 
                                    command = start_download)
    download_button.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "ew")
    
    # Create a label to display the current status
    status_label = ctk.CTkLabel(main_frame, text = get_status(), text_color = TEXT_COLOR, font = ("Arial", 12, "normal"), justify = "left")
    status_label.grid(row = 1, column = 0, padx = 12, pady = 0, sticky = "w")
    
    # Create a progress bar to show the download progress
    download_bar = ctk.CTkProgressBar(main_frame, height = 24, corner_radius = 2, mode = "determinate", indeterminate_speed = 1,
                                     fg_color = LOADING_BG, progress_color = LOADING_FG, border_width = 1, border_color = BORDER_COLOR)
    download_bar.grid(row = 2, column = 0, padx = 12, pady = (8, 12), sticky = "nsew")
    download_bar.set(0)
    
    # Create a frame for the information table
    info_frame = ctk.CTkFrame(root, corner_radius = 4, fg_color = FRAME_COLOR)
    info_frame.grid(row = 1, column = 0, padx = 16, pady = 16, sticky = "nsew")
    info_frame.grid_columnconfigure(0, weight = 1)
    info_frame.grid_rowconfigure(0, weight = 1)
    
    # Define the columns for the information table
    columns = ("No", "Downloaded", "Status")
    
    # Configure the style for the Treeview widget
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview", font = ("Arial", 12, "normal"), rowheight = 32, background = TABLE_COLOR, foreground = TEXT_COLOR)
    style.configure("Treeview.Heading", font = ("Arial", 12, "bold"), rowheight = 32, background = HEADING_BG, foreground = TEXT_COLOR)
    
    # Create the Treeview widget for displaying information
    info_table = ttk.Treeview(info_frame, columns = columns, show = "headings")
    info_table.grid(row = 0, column = 0, padx = 20, pady = 20, sticky = "nsew")
    
    # Define the headings for each column
    info_table.heading(columns[0], text = columns[0])
    info_table.heading(columns[1], text = columns[1])
    info_table.heading(columns[2], text = columns[2])
    
    # Set the column widths for the table
    info_table.column(columns[0], width = 24)
    info_table.column(columns[1], width = 280)
    info_table.column(columns[2], width = 480)
    
    root.grid_rowconfigure(1, weight = 1)
    
    # Start the main event loop of the application
    root.mainloop()
    