"""
ULTIMATE INSTALLER - Guaranteed to work
Direct file copy with verification
"""
import os
import shutil
import subprocess
import time
from pathlib import Path

# Paths
SOURCE = Path(r"e:\Projects\HDRI_editor\hdri_light_studio")
TARGET = Path(r"C:\Users\plana\AppData\Roaming\Blender Foundation\Blender\4.2\scripts\addons\hdri_light_studio")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

print("="*70)
print("ULTIMATE INSTALLER - HDRI Light Studio")
print("="*70)

# Step 1: Kill Blender
print("\n[1/6] Closing Blender...")
try:
    result = subprocess.run(["taskkill", "/F", "/IM", "blender.exe"], 
                          capture_output=True, text=True)
    if "SUCCESS" in result.stdout:
        print("      ✅ Blender closed")
        time.sleep(2)
    else:
        print("      ℹ️  Blender not running")
except:
    print("      ℹ️  Could not close Blender")

# Step 2: Remove old addon
print("\n[2/6] Removing old addon...")
if TARGET.exists():
    try:
        shutil.rmtree(TARGET)
        print(f"      ✅ Removed: {TARGET}")
        time.sleep(1)
    except Exception as e:
        print(f"      ❌ Error removing: {e}")
        print(f"      Try closing Blender manually and run again")
        input("Press Enter to continue anyway...")
else:
    print("      ℹ️  No old addon found")

# Step 3: Copy files
print("\n[3/6] Copying files...")
try:
    # Copy without __pycache__
    def ignore_patterns(directory, files):
        return [f for f in files if f == '__pycache__' or f.endswith('.pyc')]
    
    shutil.copytree(SOURCE, TARGET, ignore=ignore_patterns)
    print(f"      ✅ Copied to: {TARGET}")
except Exception as e:
    print(f"      ❌ Copy failed: {e}")
    exit(1)

# Step 4: Verify files
print("\n[4/6] Verifying files...")
critical_files = {
    "__init__.py": "Main addon file",
    "ui.py": "User interface",
    "debug_paint_tracker.py": "Debug tools",
    "viewport_paint_operator.py": "Paint operator",
    "hemisphere_tools.py": "Hemisphere tools"
}

all_ok = True
for filename, description in critical_files.items():
    filepath = TARGET / filename
    if filepath.exists():
        size = filepath.stat().st_size
        print(f"      ✅ {filename:30s} {size:>8,} bytes - {description}")
    else:
        print(f"      ❌ {filename:30s} MISSING! - {description}")
        all_ok = False

# Step 5: Special check for debug section in ui.py
print("\n[5/6] Checking debug section in ui.py...")
ui_file = TARGET / "ui.py"
if ui_file.exists():
    content = ui_file.read_text(encoding='utf-8')
    
    debug_markers = [
        ("draw_debug_points", "Draw Test Points operator"),
        ("start_debug_tracking", "Start Tracking operator"),
        ("stop_debug_tracking", "Stop & Analyze operator"),
        ("Debug UV Tracking", "Debug section label")
    ]
    
    debug_ok = True
    for marker, desc in debug_markers:
        if marker in content:
            print(f"      ✅ Found: {marker:25s} - {desc}")
        else:
            print(f"      ❌ MISSING: {marker:25s} - {desc}")
            debug_ok = False
    
    if debug_ok:
        print(f"\n      🎉 DEBUG SECTION FULLY PRESENT IN UI.PY!")
    else:
        print(f"\n      ⚠️  DEBUG SECTION INCOMPLETE!")
        all_ok = False
else:
    print(f"      ❌ ui.py not found!")
    all_ok = False

# Step 6: Start Blender
print("\n[6/6] Starting Blender...")
if all_ok:
    print("      ✅ All checks passed!")
    print("      🚀 Starting Blender...")
    subprocess.Popen([BLENDER])
    time.sleep(3)
    print("\n" + "="*70)
    print("INSTALLATION COMPLETE!")
    print("="*70)
    print("\n📋 NEXT STEPS:")
    print("   1. In Blender: Edit → Preferences → Add-ons")
    print("   2. Search: 'HDRI'")
    print("   3. ✅ Enable 'HDRI Light Studio'")
    print("   4. Press N → 'HDRI Studio' tab")
    print("   5. Create Canvas → Add Hemisphere")
    print("   6. 🔍 Look for 'Debug UV Tracking' section!")
    print("="*70)
else:
    print("\n" + "="*70)
    print("⚠️  INSTALLATION COMPLETED WITH WARNINGS")
    print("="*70)
    print("\nSome files may be missing or incomplete.")
    print("Starting Blender anyway...")
    subprocess.Popen([BLENDER])

print("\nPress Enter to exit...")
input()
