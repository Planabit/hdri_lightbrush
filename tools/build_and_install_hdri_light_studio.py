import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import re

# Try to import psutil, but don't fail if it's not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Note: psutil not available, using basic process management")

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

def is_blender_running():
    """Check if Blender is currently running"""
    if HAS_PSUTIL:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                if proc.info['name'] and 'blender' in proc.info['name'].lower():
                    return True, proc.info['pid']
            return False, None
        except:
            pass
    
    # Fallback method
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq blender.exe'], 
                           capture_output=True, text=True, shell=True)
    return 'blender.exe' in result.stdout.lower(), None

def close_blender():
    """Force close running Blender instances"""
    print("🔄 Force closing Blender instances...")
    try:
        # Force kill all blender processes
        result = subprocess.run(['taskkill', '/F', '/IM', 'blender.exe'], 
                               capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("  ✅ Blender processes terminated")
        else:
            print("  ℹ️  No Blender processes found")
        time.sleep(3)  # Wait for cleanup
        return True
    except Exception as e:
        print(f"  ⚠️  Error closing Blender: {e}")
        return False

def clean_blender_cache():
    """Remove all Blender addon cache and config files"""
    print("🧹 Deep cleaning Blender cache and config...")
    
    # Find all Blender versions and clean them
    blender_base_paths = [
        os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender"),
        os.path.expandvars(r"%LOCALAPPDATA%\Blender Foundation\Blender")
    ]
    
    cache_paths = []
    
    for base_path in blender_base_paths:
        if os.path.exists(base_path):
            # Add paths for all Blender versions found
            for version_dir in os.listdir(base_path):
                version_path = os.path.join(base_path, version_dir)
                if os.path.isdir(version_path):
                    cache_paths.extend([
                        os.path.join(version_path, "scripts", "addons", "hdri_light_studio"),
                        os.path.join(version_path, "scripts", "addons", "hdri_light_studio_v2"),
                        os.path.join(version_path, "config", "startup.blend"),
                        os.path.join(version_path, "config", "userpref.blend"),
                        os.path.join(version_path, "config", "bookmarks.txt"),
                        os.path.join(version_path, "config", "recent-files.txt"),
                        os.path.join(version_path, "cache"),
                        os.path.join(version_path, "python")
                    ])
    
    for path in cache_paths:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"  🗑️  Removed directory: {path}")
                else:
                    os.remove(path)
                    print(f"  🗑️  Removed file: {path}")
        except Exception as e:
            print(f"  ⚠️  Could not remove {path}: {e}")
    
    # Clean source Python cache
    addon_src = Path(__file__).parent.parent / "hdri_light_studio"
    if addon_src.exists():
        print("🧹 Cleaning source Python cache...")
        for pycache_dir in addon_src.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache_dir)
                print(f"  🗑️  Removed: {pycache_dir.relative_to(addon_src)}")
            except Exception as e:
                print(f"  ⚠️  Could not remove {pycache_dir}: {e}")
        
        for pyc_file in addon_src.rglob("*.pyc"):
            try:
                os.remove(pyc_file)
                print(f"  🗑️  Removed: {pyc_file.relative_to(addon_src)}")
            except Exception as e:
                print(f"  ⚠️  Could not remove {pyc_file}: {e}")
    
    print("  ✅ Cache cleanup complete")

def wait_for_blender_startup():
    """Wait for Blender to fully start"""
    print("⏳ Waiting for Blender to start...")
    time.sleep(5)  # Wait for Blender to fully initialize


def get_addon_version(addon_init_py: Path) -> str:
    """Best-effort read of bl_info['version'] from addon __init__.py.

    Returns a string like "1.0.0". Falls back to "0.0.0" if not found.
    """
    try:
        text = addon_init_py.read_text(encoding="utf-8", errors="ignore")
        # Match: "version": (1, 0, 0)
        match = re.search(r"\"version\"\s*:\s*\((\s*\d+\s*),\s*(\d+)\s*,\s*(\d+)\s*\)", text)
        if match:
            major, minor, patch = match.group(1).strip(), match.group(2), match.group(3)
            return f"{major}.{minor}.{patch}"
    except Exception:
        pass
    return "0.0.0"


def make_versioned_path(path: Path) -> Path:
    """Return versioned path - overwrites same version until version bump."""
    return path

# CONFIGURATION
BLENDER_EXE = find_blender_exe()
ADDON_SRC = Path(__file__).parent.parent / "hdri_light_studio"
ADDON_ZIP = ADDON_SRC.parent / "hdri_paint_studio.zip"

# A separate distributable zip that will NOT be deleted (for manual install / sharing)
DIST_DIR = ADDON_SRC.parent / "dist"
ADDON_VERSION = get_addon_version(ADDON_SRC / "__init__.py")
DIST_ZIP = make_versioned_path(DIST_DIR / f"hdri_light_studio_{ADDON_VERSION}.zip")

print("🚀 HDRI Paint Studio - Automatic Installer")
print("=" * 50)
print(f"📁 Source: {ADDON_SRC}")
print(f"📦 Target: {ADDON_ZIP}")
print(f"📦 Share Zip: {DIST_ZIP}")

# Check if source exists
if not ADDON_SRC.exists():
    print(f"❌ Error: Addon source directory not found: {ADDON_SRC}")
    sys.exit(1)

# Zip the addon
print("📦 Creating addon zip...")
if ADDON_ZIP.exists():
    ADDON_ZIP.unlink()
    print("   Removed existing zip file")

# Create a temporary directory for correct zip structure
temp_dir = os.path.join(os.path.dirname(ADDON_ZIP), "temp_build")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# Copy addon files to temp directory with correct structure
temp_addon_dir = os.path.join(temp_dir, "hdri_light_studio")
print(f"   Creating temporary structure in {temp_dir}...")
shutil.copytree(ADDON_SRC, temp_addon_dir)

# Exclude unnecessary files from zip
exclude_patterns = ['__pycache__', '.pyc', '.git', '.gitignore', 'test_*']
for root, dirs, files in os.walk(temp_addon_dir):
    # Remove __pycache__ directories
    dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
    # Remove .pyc files
    for file in files[:]:
        if any(pattern in file for pattern in exclude_patterns):
            os.remove(os.path.join(root, file))
            print(f"   Excluded: {file}")

# Create zip from temp directory
zip_base = str(ADDON_ZIP).replace(".zip", "")
print("   Creating zip file...")
shutil.make_archive(zip_base, "zip", temp_dir)
print(f"✅ Addon zipped successfully to: {ADDON_ZIP}")

# Also persist a copy for manual installation / sharing
try:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ADDON_ZIP, DIST_ZIP)
    print(f"✅ Shareable addon zip created: {DIST_ZIP}")
except Exception as e:
    print(f"⚠️  Could not create shareable zip copy: {e}")

# Clean up temp directory
shutil.rmtree(temp_dir)
print("   Cleaned up temporary files.")

# Step 1: Force close Blender and clean cache
print("🔄 Preparing clean installation environment...")
close_blender()
clean_blender_cache()
print("✅ Environment prepared")

# Check if Blender was found
if not BLENDER_EXE:
    print("❌ Error: Could not find Blender executable!")
    print("   Please install Blender or modify the script with the correct path.")
    print("   Expected locations:")
    possible_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe", 
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
    ]
    for path in possible_paths:
        print(f"   - {path}")
    input("Press Enter to exit...")
    sys.exit(1)

print(f"✅ Using Blender from: {BLENDER_EXE}")

# Install addon
print("🔧 Installing addon...")
script = f"""
import bpy
import sys

print("🧹 Deep cleaning Blender addon cache...")

# Force clear module cache
modules_to_clear = [name for name in sys.modules.keys() if 'hdri_light_studio' in name]
for module_name in modules_to_clear:
    del sys.modules[module_name]
    print(f"   Cleared module: {{module_name}}")

# Remove old addon installations
try:
    import addon_utils
    addon_utils.disable("hdri_light_studio", default_set=True)
    addon_utils.disable("hdri_light_studio_v2", default_set=True)
    print("   Disabled old versions")
except:
    pass

print("📦 Installing fresh addon version...")
try:
    bpy.ops.preferences.addon_install(filepath=r"{ADDON_ZIP}", overwrite=True)
    print("✅ Addon installed successfully")
except Exception as e:
    print(f"❌ Installation failed: {{str(e)}}")
    # Manual installation fallback
    try:
        import zipfile
        import os
        addon_path = bpy.utils.user_resource('SCRIPTS', "addons")
        with zipfile.ZipFile(r"{ADDON_ZIP}", 'r') as zip_ref:
            zip_ref.extractall(addon_path)
        print("✅ Manual installation successful")
    except Exception as e2:
        print(f"❌ Manual installation failed: {{str(e2)}}")
        sys.exit(1)

print("🔌 Enabling addon with module refresh...")
try:
    # Force refresh modules before enabling
    import importlib
    import sys
    
    # Try to import and reload the addon module
    try:
        if 'hdri_light_studio' in sys.modules:
            importlib.reload(sys.modules['hdri_light_studio'])
    except:
        pass
    
    # Enable the addon (using zip filename as module name)
    bpy.ops.preferences.addon_enable(module="hdri_light_studio")
    print("✅ Addon enabled successfully")
except Exception as e:
    print(f"⚠️  Error enabling addon: {{str(e)}}")
    # Try manual registration as fallback
    try:
        import hdri_light_studio
        hdri_light_studio.register()
        print("✅ Addon manually registered")
    except Exception as e2:
        print(f"❌ Manual registration failed: {{str(e2)}}")
        print("   Installation may still be successful - check manually")

print("🔍 Verifying installation...")
try:
    # Check if the addon classes are registered
    if hasattr(bpy.ops, 'hdrils'):
        print("✅ HDRI Light Studio operators are available")
        
        # Check specific operators
        if hasattr(bpy.ops.hdrils, 'create_canvas'):
            print("✅ Canvas creation operator found")
        if hasattr(bpy.ops.hdrils, 'paint_modal'):
            print("✅ Paint modal operator found")
        if hasattr(bpy.ops.hdrils, 'place_light_shape'):
            print("✅ Light shape operator found")
    else:
        print("⚠️  HDRI Light Studio operators not found")
        
    # Check properties
    if hasattr(bpy.context.scene, 'hdrils_props'):
        print("✅ Scene properties registered")
    else:
        print("⚠️  Scene properties not found")
        
    # Check UI panels
    panel_found = False
    for cls in bpy.types.Panel.__subclasses__():
        if hasattr(cls, 'bl_idname') and 'HDRI_PT' in cls.bl_idname:
            panel_found = True
            break
    
    if panel_found:
        print("✅ UI panels registered")
    else:
        print("⚠️  UI panels not found")
        
except Exception as e:
    print(f"⚠️  Verification error: {{str(e)}}")

print("💾 Saving user preferences...")
try:
    bpy.ops.wm.save_userpref()
    print("✅ Preferences saved")
except Exception as e:
    print(f"⚠️  Warning: Could not save preferences: {{str(e)}}")

print("🎉 Installation complete!")
print("")
print("📍 To use HDRI Light Studio:")
print("   1. Open 3D Viewport")
print("   2. Press 'N' to show sidebar")
print("   3. Find 'HDRI Studio' tab")
print("   4. Start creating and painting HDRIs!")
"""

print("   Running Blender installation script...")
result = subprocess.run([BLENDER_EXE, "--background", "--python-expr", script],
                       capture_output=True, text=True)

print("\n📋 Blender Output:")
print("-" * 30)
if result.stdout:
    print(result.stdout)
if result.stderr:
    print("⚠️  Errors:")
    print(result.stderr)

if result.returncode != 0:
    print("❌ Installation failed!")
    print(f"   Return code: {result.returncode}")
    sys.exit(1)
else:
    print("✅ Installation successful!")

# Step 2: Automatic restart of Blender 
print("\n� Restarting Blender automatically...")

# Clean up zip file automatically
try:
    ADDON_ZIP.unlink()
    print("✅ Installation files cleaned up")
except Exception as e:
    print(f"⚠️  Could not delete zip: {e}")

# Start Blender automatically
print("� Starting Blender with addon ready...")
subprocess.Popen([BLENDER_EXE])

# Wait for Blender to start
wait_for_blender_startup()

print("✅ Blender restarted successfully!")
print("\n🎨 HDRI Light Studio is ready!")
print("=" * 50)
print("📍 To use the addon:")
print("   1. Open 3D Viewport")
print("   2. Press 'N' to show sidebar")  
print("   3. Find 'HDRI Studio' tab")
print("   4. Click 'Create 2K Canvas' or 'Create 4K Canvas'")
print("   5. Start painting your HDRI!")
print("\n� Happy HDRI editing!")