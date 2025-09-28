#!/usr/bin/env python3
"""
HDRI Light Studio v2 - Clean Installer
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def find_blender_exe():
    """Find Blender executable"""
    possible_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def main():
    print("🚀 HDRI Light Studio v2 - Clean Installer")
    print("=" * 50)
    
    BLENDER_EXE = find_blender_exe()
    ADDON_SRC = Path(__file__).parent.parent / "hdri_light_studio_v2"
    ADDON_ZIP = ADDON_SRC.parent / "hdri_light_studio_v2.zip"
    
    if not BLENDER_EXE:
        print("❌ Error: Could not find Blender!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not ADDON_SRC.exists():
        print(f"❌ Error: Addon source not found: {ADDON_SRC}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"📁 Source: {ADDON_SRC}")
    print(f"🎯 Blender: {BLENDER_EXE}")
    
    # Force close Blender
    print("🔄 Stopping Blender...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'blender.exe'], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Remove old installations
    print("🧹 Cleaning old installations...")
    old_dirs = [
        Path(os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\hdri_light_studio")),
        Path(os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\hdri_light_studio_v2"))
    ]
    
    for old_dir in old_dirs:
        if old_dir.exists():
            shutil.rmtree(old_dir)
            print(f"   Removed: {old_dir.name}")
    
    # Create zip
    print("📦 Creating package...")
    if ADDON_ZIP.exists():
        ADDON_ZIP.unlink()
    
    temp_dir = ADDON_SRC.parent / "temp_v2_build"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    temp_addon_dir = temp_dir / "hdri_light_studio_v2"
    shutil.copytree(ADDON_SRC, temp_addon_dir)
    
    # Create zip
    zip_base = str(ADDON_ZIP).replace(".zip", "")
    shutil.make_archive(zip_base, "zip", temp_dir)
    shutil.rmtree(temp_dir)
    print(f"✅ Package created: {ADDON_ZIP}")
    
    # Install
    print("🔧 Installing addon...")
    install_script = f'''
import bpy

print("Installing HDRI Light Studio v2...")

try:
    bpy.ops.preferences.addon_install(filepath=r"{ADDON_ZIP}")
    print("✅ Package installed")
    
    bpy.ops.preferences.addon_enable(module="hdri_light_studio_v2")
    print("✅ Addon enabled")
    
    bpy.ops.wm.save_userpref()
    print("✅ Preferences saved")
    
    # Verify
    if hasattr(bpy.ops, 'hdrils'):
        print("✅ Operators available")
        if hasattr(bpy.ops.hdrils, 'create_2k_canvas'):
            print("✅ 2K Canvas button ready!")
        if hasattr(bpy.ops.hdrils, 'create_4k_canvas'):
            print("✅ 4K Canvas button ready!")
    else:
        print("❌ Operators not found")
        
except Exception as e:
    print(f"❌ Error: {{e}}")
    import sys
    sys.exit(1)

print("🎉 HDRI Light Studio v2 ready!")
'''
    
    result = subprocess.run([BLENDER_EXE, "--background", "--python-expr", install_script],
                           capture_output=True, text=True)
    
    print("\n📋 Installation Result:")
    print("-" * 30)
    if result.stdout:
        print(result.stdout)
    if result.stderr and "warning" not in result.stderr.lower():
        print("Errors:")
        print(result.stderr)
    
    # Clean up and launch
    try:
        ADDON_ZIP.unlink()
    except:
        pass
    
    if result.returncode == 0:
        print("\n🚀 Starting Blender...")
        subprocess.Popen([BLENDER_EXE])
        time.sleep(3)
        
        print("✅ SUCCESS! HDRI Light Studio v2 installed!")
        print("=" * 50)
        print("📍 To find your Canvas buttons:")
        print("   1. Open 3D Viewport")
        print("   2. Press 'N' key")
        print("   3. Look for 'HDRI Light Studio' tab")
        print("   4. Click 'Create 2K Canvas' or 'Create 4K Canvas'")
    else:
        print("❌ Installation failed!")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()