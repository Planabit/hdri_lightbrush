import os
import shutil
import subprocess
import sys
import time

# CONFIGURATION
BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"  # Update this path if needed
ADDON_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '../hdri_editor'))
ADDON_ZIP = os.path.abspath(os.path.join(os.path.dirname(__file__), '../hdri_editor.zip'))

# 1. Zip the addon
if os.path.exists(ADDON_ZIP):
    os.remove(ADDON_ZIP)

# Create a temporary directory for correct zip structure
temp_dir = os.path.join(os.path.dirname(ADDON_ZIP), 'temp_build')
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Copy addon files to temp directory with correct structure
temp_addon_dir = os.path.join(temp_dir, 'hdri_editor')
shutil.copytree(ADDON_SRC, temp_addon_dir)

# Create zip from temp directory
shutil.make_archive(ADDON_ZIP.replace('.zip', ''), 'zip', temp_dir)
print(f"Addon zipped: {ADDON_ZIP}")

# Clean up temp directory
shutil.rmtree(temp_dir)

# 2. Close Blender (Windows only, closes all Blender instances)
os.system('taskkill /IM blender.exe /F')
time.sleep(2)

# 3. Install the addon using Blender's CLI
install_script = f'''
import bpy
bpy.ops.preferences.addon_install(filepath=r"{ADDON_ZIP}", overwrite=True)
bpy.ops.preferences.addon_enable(module="hdri_editor")
bpy.ops.wm.save_userpref()
'''

subprocess.run([
    BLENDER_EXE,
    "--background",
    "--python-expr",
    install_script
], check=True)
print("Addon installed and enabled.")

# 4. Restart Blender
detached = subprocess.Popen([BLENDER_EXE])
print("Blender restarted.")
