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

def find_all_blender_exes():
    """Find all Blender executables in common installation locations"""
    base_dir = r"C:\Program Files\Blender Foundation"
    found = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower() == "blender.exe":
                found.append(os.path.join(root, file))
    return found

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
                        os.path.join(version_path, "scripts", "addons", "hdri_lightbrush"),
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
    addon_src = Path(__file__).parent.parent / "hdri_lightbrush"
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
BLENDER_EXES = find_all_blender_exes()
ADDON_SRC = Path(__file__).parent.parent / "hdri_lightbrush"
ADDON_ZIP = ADDON_SRC.parent / "hdri_lightbrush.zip"

# A separate distributable zip that will NOT be deleted (for manual install / sharing)
DIST_DIR = ADDON_SRC.parent / "dist"
ADDON_VERSION = get_addon_version(ADDON_SRC / "__init__.py")
DIST_ZIP = make_versioned_path(DIST_DIR / f"hdri_lightbrush_{ADDON_VERSION}.zip")

print("🚀 HDRI LightBrush - Automatic Installer")
print("=" * 50)
print(f"📁 Source: {ADDON_SRC}")
print(f"📦 Target: {ADDON_ZIP}")
print(f"📦 Share Zip: {DIST_ZIP}")

if not BLENDER_EXES:
    print("❌ Error: Could not find any Blender executables!")
    print("   Please install Blender or modify the script with the correct path.")
    sys.exit(1)

for BLENDER_EXE in BLENDER_EXES:
    # Create a temporary directory for correct zip structure
    temp_dir = os.path.join(os.path.dirname(ADDON_ZIP), f"temp_build_{os.path.basename(BLENDER_EXE)}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # Copy addon files to temp directory with correct structure
    temp_addon_dir = os.path.join(temp_dir, "hdri_lightbrush")
    print(f"   Creating temporary structure in {temp_dir}...")
    shutil.copytree(ADDON_SRC, temp_addon_dir)
    print(f"✅ Using Blender from: {BLENDER_EXE}")
    print("🔧 Installing addon...")
    script = f"""
import bpy
import sys
import os

print("🧹 Deep cleaning Blender addon cache...")

# Remove old addon if exists
addon_name = "hdri_lightbrush"
addon_path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "addons", addon_name)

if os.path.exists(addon_path):
    import shutil
    try:
        shutil.rmtree(addon_path)
        print(f"  Removed old addon: {{addon_path}}")
    except Exception as e:
        print(f"  Warning: Could not remove old addon: {{e}}")

# Disable addon if enabled
try:
    bpy.ops.preferences.addon_disable(module=addon_name)
    print(f"  Disabled existing addon: {{addon_name}}")
except:
    pass

# Install addon from zip
zip_path = r"{ADDON_ZIP}"
print(f"  Installing from: {{zip_path}}")

try:
    bpy.ops.preferences.addon_install(filepath=zip_path, overwrite=True)
    print("  ✅ Addon installed successfully")
except Exception as e:
    print(f"  ❌ Installation failed: {{e}}")
    sys.exit(1)

# Enable the addon
print("  Enabling addon...")
try:
    bpy.ops.preferences.addon_enable(module=addon_name)
    print("  ✅ Addon enabled successfully")
except Exception as e:
    print(f"  ❌ Failed to enable addon: {{e}}")
    sys.exit(1)

# Verify addon is enabled
if addon_name in bpy.context.preferences.addons:
    print(f"  ✅ Verified: {{addon_name}} is enabled")
else:
    print(f"  ❌ Addon {{addon_name}} not found in enabled addons!")
    sys.exit(1)

# Save user preferences to persist the enabled state
try:
    bpy.ops.wm.save_userpref()
    print("  ✅ User preferences saved")
except Exception as e:
    print(f"  ⚠️ Could not save preferences: {{e}}")

print('')
print('🎉 Installation complete!')
print('')
print('📍 To use HDRI LightBrush:')
print('   1. Open 3D Viewport')
print("   2. Press 'N' to show sidebar")
print("   3. Find 'HDRI LightBrush' tab")
print('   4. Start creating and painting HDRIs!')
"""

# Exclude unnecessary files from zip (do this in the main script, not in the Blender script string)
exclude_patterns = ['__pycache__', '.pyc', '.git', '.gitignore', 'test_*']
for root, dirs, files in os.walk(temp_addon_dir):
    dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
    for filename in files[:]:
        if any(pattern in filename for pattern in exclude_patterns):
            os.remove(os.path.join(root, filename))
            print(f"   Excluded: {filename}")

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
close_blender()

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
else:
    print("✅ Installation successful!")

# After all installations complete, start all Blender versions
print("\n" + "=" * 50)
print("🚀 Launching all Blender versions...")
print("=" * 50)

launched_blenders = []
for blender_exe_path in BLENDER_EXES:
    try:
        subprocess.Popen([blender_exe_path])
        launched_blenders.append(blender_exe_path)
        print(f"  ✅ Started: {blender_exe_path}")
        time.sleep(1)  # Small delay between launches
    except Exception as e:
        print(f"  ❌ Failed to start {blender_exe_path}: {e}")

print(f"\n🎉 Launched {len(launched_blenders)} Blender instance(s)")

print(f"\n🎉 Launched {len(launched_blenders)} Blender instance(s)")
