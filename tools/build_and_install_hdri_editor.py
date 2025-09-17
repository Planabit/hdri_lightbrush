import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def find_blender_exe():
    """Find Blender executable in common installation locations"""
    possible_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

# CONFIGURATION
BLENDER_EXE = find_blender_exe()
ADDON_SRC = Path(__file__).parent.parent / "hdri_editor"
ADDON_ZIP = ADDON_SRC.parent / "hdri_editor.zip"

# Zip the addon
print("Creating addon zip...")
if ADDON_ZIP.exists():
    ADDON_ZIP.unlink()

# Create a temporary directory for correct zip structure
temp_dir = os.path.join(os.path.dirname(ADDON_ZIP), "temp_build")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Copy addon files to temp directory with correct structure
temp_addon_dir = os.path.join(temp_dir, "hdri_editor")
print(f"Creating temporary structure in {temp_dir}...")
shutil.copytree(ADDON_SRC, temp_addon_dir)

# Create zip from temp directory
zip_base = str(ADDON_ZIP).replace(".zip", "")
print("Creating zip file...")
shutil.make_archive(zip_base, "zip", temp_dir)
print(f"Addon zipped successfully to: {ADDON_ZIP}")

# Clean up temp directory
shutil.rmtree(temp_dir)
print("Cleaned up temporary files.")

# Close Blender
print("Closing Blender...")
try:
    subprocess.run(["taskkill", "/IM", "blender.exe", "/F"], 
                  capture_output=True, text=True, check=True)
except subprocess.CalledProcessError:
    print("No Blender instances running.")
time.sleep(2)

# Check if Blender was found
if not BLENDER_EXE:
    print("Error: Could not find Blender executable!")
    print("Please install Blender or modify the script with the correct path.")
    sys.exit(1)

print(f"Using Blender from: {BLENDER_EXE}")

# Install addon
print("Installing addon...")
script = f"""
import bpy
import sys

print("Attempting to remove old version...")
try:
    bpy.ops.preferences.addon_remove(module="hdri_editor")
    print("Old version removed successfully")
except Exception as e:
    print(f"Note: Could not remove old version: {{str(e)}}")

print("Installing new version...")
try:
    bpy.ops.preferences.addon_install(filepath=r"{ADDON_ZIP}", overwrite=True)
    print("Addon installed")
except Exception as e:
    print(f"Error installing addon: {{str(e)}}")
    sys.exit(1)

print("Enabling addon...")
try:
    bpy.ops.preferences.addon_enable(module="hdri_editor")
    print("Addon enabled")
except Exception as e:
    print(f"Error enabling addon: {{str(e)}}")
    sys.exit(1)

print("Saving user preferences...")
bpy.ops.wm.save_userpref()
print("Installation complete")
"""

print("Running Blender installation script...")
result = subprocess.run([BLENDER_EXE, "--background", "--python-expr", script],
                       capture_output=True, text=True)

print("\nBlender Output:")
if result.stdout:
    print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

if result.returncode != 0:
    print("Installation failed!")
    sys.exit(1)
else:
    print("Installation successful!")

# Start Blender
print("Starting Blender...")
subprocess.Popen([BLENDER_EXE])
print("Done.")
