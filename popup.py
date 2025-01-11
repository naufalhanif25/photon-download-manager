# Importing necessary libraries and modules
import tkinter as tk
from screeninfo import get_monitors
import threading
import player
import time as timelib
import main
import getpath

# Function to open a popup window
def open_popup(message, role = "message", count = True):
    # Creating a Toplevel window as a popup
    popup = tk.Tk()
    popup.withdraw()  # Hide the popup initially
    popup.configure(bg = main.BASE_COLOR)
    
    if role == "message":
        popup.title("Message")
        popup.iconbitmap(getpath.base("public/message.ico"))
        player.playsound(getpath.base("public/message.wav"))
    elif role == "warning":
        popup.title("Warning")
        popup.iconbitmap(getpath.base("public/warning.ico"))
        player.playsound(getpath.base("public/warning.wav"))
    else:
        return
    
    geometry = "480x120"
    
    # Function to place the popup window in the center of the screen
    def center_popup(popup, geometry):
        # Ensure all window settings are applied
        popup.update_idletasks()

        width = popup.winfo_width()
        height = popup.winfo_height()
        
        scr_width = get_monitors()[0].width
        scr_height = get_monitors()[0].height
        
        size = tuple(int(_) for _ in geometry.split("x"))
        
        # Calculate the x and y coordinates to center the popup
        x = (scr_width // 2) - (width // 2)
        y = (scr_height // 2) - (height // 2)
        
        # Set the geometry of the popup window with the calculated position
        popup.geometry(f"{size[0]}x{size[1]}+{x}+{y}")
    
    # Function to activate countdown 
    def countdown(time):        
        while time > 0:
            mins, secs = divmod(time, 60)
            clock = f"{mins:02d}:{secs:02d}"

            message_label.config(text = f"{message}\n[{clock}]")  
            timelib.sleep(1)
            
            time -= 1
            
        message_label.config(text = f"{message}\n[You can close this window]")
        
    # Set the initial size of the popup window
    popup.geometry(f"{geometry}")
    popup.resizable(False, False)
    
    # Configure the grid column and row to expand with weight
    popup.grid_columnconfigure(0, weight = 1)
    popup.grid_rowconfigure(0, weight = 1)
    
    # Create a label with the message and add it to the popup window
    message_label = tk.Label(popup, text = f"{message}", font = ("Arial", 10, "normal"), fg = main.TEXT_COLOR, bg = main.BASE_COLOR)
    message_label.grid(row = 0, column = 0, padx = 12, pady = 12, sticky = "nsew")
    
    # Function to enable closing of popup windows
    def enable_close():
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)
    
    if count:
        threading.Thread(target = countdown, args = (3,)).start()
        
        popup.protocol("WM_DELETE_WINDOW", True)
        popup.after(3000, enable_close)
    
    center_popup(popup, geometry)  # Center the popup window on the screen
    
    # Show the popup window
    popup.deiconify()
    popup.mainloop()
    