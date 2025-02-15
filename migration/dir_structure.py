# migration/dir_structure.py
from config import *
import shutil

def create_folders(paths):
    """Create the specified folders if they do not already exist."""
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")

def create_files(files):
    """Create files if they do not already exist."""
    for file in files.values():
        os.makedirs(os.path.dirname(file), exist_ok=True)  # First create the folder
        if not os.path.exists(file):  # Only if it does not already exist
            with open(file, "w", encoding="utf-8") as f:
                f.write("# Auto-generated file\n")
            print(f"Created file: {file}")

def copy_static_files(copy_config):
    """Copies the files read from the INI file."""
    for key, path in copy_config.items():
        try:
            src, dst = map(str.strip, path.split(","))  # Separation by comma
            os.makedirs(os.path.dirname(dst), exist_ok=True)  # Create a target folder
            #if not os.path.exists(dst):  # Only if it's not there yet
            shutil.copy2(src, dst)
            print(f"Copied: {src} -> {dst}")
        except Exception as e:
            print(f"Error copying {key}: {e}")

