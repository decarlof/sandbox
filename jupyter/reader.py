import os
import tkinter as tk
from tkinter import filedialog

def get_last_directory():
    """Retrieve the last used directory from a file."""
    try:
        with open("last_dir.txt", "r") as f:
            last_dir = f.read().strip()
            if os.path.exists(last_dir):
                return last_dir
    except FileNotFoundError:
        pass
    return os.getcwd()  # Default to current working directory

def save_last_directory(directory):
    """Save the last used directory to a file."""
    with open("last_dir.txt", "w") as f:
        f.write(directory)

def select_file_and_list_similar():
    # Initialize Tkinter (hide main window)
    root = tk.Tk()
    root.withdraw()  

    initial_dir = get_last_directory()
    # Ask the user to select a file
    file_path = filedialog.askopenfilename(title="Select a file")
    
    if not file_path:
        print("No file selected.")
        return []

    directory, filename = os.path.split(file_path)
    save_last_directory(directory)  # Save directory for future selections

    # Extract folder and prefix
    folder, filename = os.path.split(file_path)
    prefix = os.path.splitext(filename)[0][:-5]  # Remove extension and _XXXX

    # Find all files with the same prefix
    # matching_files = [f for f in os.listdir(folder) if f.startswith(prefix)]
    matching_files = [
        os.path.join(directory, f) for f in os.listdir(directory) if f.startswith(prefix)
    ]
        
    return matching_files

# Run the function and display the results
files_with_same_prefix = select_file_and_list_similar()
print("Matching files:", files_with_same_prefix)
