#!/usr/bin/env python3
"""
HDRI Light Studio - Clean Installer
Completely removes old installation and installs fresh version
"""

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
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe", 
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

def force_kill_blender():
    """Force kill all Blender processes"""
    print("🔄 Stopping all Blender processes...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'blender.exe'], 
                      capture_output=True, check=False)
        print("✅ Blender processes stopped")
    except:
        print("ℹ️  No Blender processes running")
    time.sleep(2)

def clean_addon_installation():
    """Remove all traces of the addon"""
    print("🧹 Cleaning old installation...")
    
    addon_dir = Path(os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\hdri_light_studio"))
    if addon_dir.exists():
        shutil.rmtree(addon_dir)
        print("   Removed old addon directory")
    
    # Clean config cache
    config_dir = Path(os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\4.2\config"))
    if config_dir.exists():
        startup_file = config_dir / "startup.blend" 
        userpref_file = config_dir / "userpref.blend"
        for f in [startup_file, userpref_file]:
            if f.exists():
                f.unlink()
                print(f"   Cleared {f.name}")
    
    print("✅ Cleanup complete")

def main():
    print("🚀 HDRI Light Studio - Clean Installer")
    print("=" * 50)
    
    # Configuration
    BLENDER_EXE = find_blender_exe()
    ADDON_SRC = Path(__file__).parent.parent / "hdri_light_studio"
    ADDON_ZIP = ADDON_SRC.parent / "hdri_light_studio_clean.zip"
    
    if not BLENDER_EXE:
        print("❌ Error: Could not find Blender executable!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not ADDON_SRC.exists():
        print(f"❌ Error: Addon source directory not found: {ADDON_SRC}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"📁 Source: {ADDON_SRC}")
    print(f"🎯 Blender: {BLENDER_EXE}")
    
    # Step 1: Force close Blender
    force_kill_blender()
    
    # Step 2: Clean old installation  
    clean_addon_installation()
    
    # Step 3: Create fresh zip
    print("📦 Creating fresh addon package...")
    if ADDON_ZIP.exists():
        ADDON_ZIP.unlink()
    
    temp_dir = ADDON_SRC.parent / "temp_clean_build"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    temp_addon_dir = temp_dir / "hdri_light_studio"
    shutil.copytree(ADDON_SRC, temp_addon_dir)
    
    # Remove cache files
    for root, dirs, files in os.walk(temp_addon_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files[:]:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    # Create zip
    zip_base = str(ADDON_ZIP).replace(".zip", "")
    shutil.make_archive(zip_base, "zip", temp_dir)
    shutil.rmtree(temp_dir)
    print(f"✅ Fresh package created: {ADDON_ZIP}")
    
    # Step 4: Install via Blender
    print("🔧 Installing addon...")
    
    install_script = f'''
import bpy
import addon_utils

print("🔧 Installing HDRI Light Studio...")

# Install addon
try:
    bpy.ops.preferences.addon_install(filepath=r"{ADDON_ZIP}")
    print("✅ Package installed")
except Exception as e:
    print(f"❌ Install failed: {{e}}")
    import sys
    sys.exit(1)

# Enable addon
try:
    bpy.ops.preferences.addon_enable(module="hdri_light_studio")
    print("✅ Addon enabled")
except Exception as e:
    print(f"❌ Enable failed: {{e}}")

# Save preferences
try:
    bpy.ops.wm.save_userpref()
    print("✅ Preferences saved")
except Exception as e:
    print(f"⚠️  Preferences save failed: {{e}}")

# Verify installation
print("🔍 Verifying installation...")
if hasattr(bpy.ops, 'hdrils'):
    print("✅ Operators registered")
    if hasattr(bpy.ops.hdrils, 'create_2k_canvas'):
        print("✅ 2K Canvas operator found")
    if hasattr(bpy.ops.hdrils, 'create_4k_canvas'):
        print("✅ 4K Canvas operator found")
else:
    print("❌ Operators not found")

print("🎉 Installation complete!")
'''
    
    result = subprocess.run([BLENDER_EXE, "--background", "--python-expr", install_script],
                           capture_output=True, text=True)
    
    print("\n📋 Installation Output:")
    print("-" * 30)
    if result.stdout:
        print(result.stdout)
    if result.stderr and "warning" not in result.stderr.lower():
        print("Errors:")
        print(result.stderr)
    
    if result.returncode != 0:
        print("❌ Installation failed!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Step 5: Clean up and restart Blender
    print("\n🚀 Starting Blender...")
    try:
        ADDON_ZIP.unlink()
        print("✅ Cleanup complete")
    except:
        pass
    
    subprocess.Popen([BLENDER_EXE])
    time.sleep(3)
    
    print("✅ HDRI Light Studio installed and ready!")
    print("=" * 50)
    print("📍 To use the addon:")
    print("   1. Open 3D Viewport")  
    print("   2. Press 'N' to show sidebar")
    print("   3. Find 'HDRI Light Studio' tab")
    print("   4. Click '2K' or '4K' to create canvas")
    print("\n🎨 Happy HDRI editing!")

if __name__ == "__main__":
    main()