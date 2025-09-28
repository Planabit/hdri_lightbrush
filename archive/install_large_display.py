import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def find_blender_exe():
    """Find Blender executable in common installation locations"""
    possible_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

# CONFIGURATION
BLENDER_EXE = find_blender_exe()
ADDON_FILE = Path(__file__).parent.parent / "hdri_editor_large_display.py"

print(f"Installing Large Display HDRI addon from: {ADDON_FILE}")

if not BLENDER_EXE:
    print("Error: Could not find Blender executable!")
    sys.exit(1)

# Install script
script = f"""
import bpy
import sys

print("Installing HDRI Editor - Large Display addon...")

try:
    # Remove old version if exists
    if "hdri_editor_large_display" in bpy.context.preferences.addons.keys():
        bpy.ops.preferences.addon_remove(module="hdri_editor_large_display")

    # Install from file
    bpy.ops.preferences.addon_install(filepath=r"{ADDON_FILE}")
    print("Large display addon installed")
    
    # Enable addon
    bpy.ops.preferences.addon_enable(module="hdri_editor_large_display") 
    print("Large display addon enabled")
    
    # Test operators
    if hasattr(bpy.ops, 'hdri') and hasattr(bpy.ops.hdri, 'load_large'):
        print("✅ Large display HDRI operators available")
    else:
        print("❌ Large display HDRI operators not found")
    
    bpy.ops.wm.save_userpref()
    print("Large display addon ready!")
    
except Exception as e:
    print(f"Error: {{str(e)}}")
"""

print("Installing large display addon...")
result = subprocess.run([BLENDER_EXE, "--background", "--python-expr", script],
                       capture_output=True, text=True)

print("\nBlender Output:")
if result.stdout:
    print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Start Blender
print("Starting Blender...")
subprocess.Popen([BLENDER_EXE])
print("Test the 'HDRI Editor - Large Display' panel with different display methods!")