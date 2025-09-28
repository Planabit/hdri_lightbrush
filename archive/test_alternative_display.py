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
ADDON_FILE = Path(__file__).parent.parent / "hdri_editor_alternative.py"

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

# Install and test alternative addon
script = f"""
import bpy
import sys
import os

# Add current directory to path
sys.path.insert(0, r"{ADDON_FILE.parent}")

print("Testing alternative HDRI display methods...")

try:
    # Remove old version if exists
    if "hdri_editor_alternative" in bpy.context.preferences.addons.keys():
        bpy.ops.preferences.addon_remove(module="hdri_editor_alternative")

    # Install from file
    bpy.ops.preferences.addon_install(filepath=r"{ADDON_FILE}")
    print("Alternative addon installed")
    
    # Enable addon
    bpy.ops.preferences.addon_enable(module="hdri_editor_alternative") 
    print("Alternative addon enabled")
    
    # Test different display methods
    print("Testing display methods...")
    
    # Check if operators are available
    if hasattr(bpy.ops, 'hdri') and hasattr(bpy.ops.hdri, 'load_alt'):
        print("✅ Alternative HDRI operators available")
    else:
        print("❌ Alternative HDRI operators not found")
    
    print("Alternative addon ready for testing!")
    
except Exception as e:
    print(f"Error with alternative addon: {{str(e)}}")

bpy.ops.wm.save_userpref()
print("Testing setup complete")
"""

print("Installing alternative HDRI addon for testing...")
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
    print("Alternative addon installation successful!")

# Start Blender for testing
print("Starting Blender for testing alternative display methods...")
subprocess.Popen([BLENDER_EXE])
print("Test different display methods in the HDRI Editor - Alternative Display panel!")