# Importing necessary libraries
import sys
import os

# Function to generate the base path for a given file or directory path
def base(path):
    try:
        # Get the base path 
        base = sys._MEIPASS
    except Exception:
        # Use the absolute path of the current directory
        base = os.path.abspath(".")

    base = os.path.join(base, path)
    base = base.replace("\\", "/")
    
    return base
