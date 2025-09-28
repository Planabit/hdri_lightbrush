"""
HDRI Light Studio Installer
Automated installation script for Blender addon
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def find_blender_addons_path():
    """Find Blender addons directory"""
    possible_paths = [
        # Windows
        Path.home() / "AppData/Roaming/Blender Foundation/Blender",
        # Linux  
        Path.home() / ".config/blender",
        # macOS
        Path.home() / "Library/Application Support/Blender"
    ]
    
    for base_path in possible_paths:
        if base_path.exists():
            # Look for version directories
            for version_dir in base_path.glob("*"):
                if version_dir.is_dir() and version_dir.name.replace(".", "").isdigit():
                    addons_path = version_dir / "scripts/addons"
                    if addons_path.exists():
                        return addons_path
    
    return None

def install_addon():
    """Install HDRI Light Studio addon"""
    print("🚀 HDRI Light Studio Installer")
    print("="*40)
    
    # Get source addon directory
    source_dir = Path(__file__).parent
    addon_name = "hdri_light_studio"
    
    # Find Blender addons directory
    print("📁 Searching for Blender addons directory...")
    addons_dir = find_blender_addons_path()
    
    if not addons_dir:
        print("❌ Could not find Blender addons directory")
        print("\n📋 Manual installation required:")
        print("1. Open Blender")
        print("2. Edit → Preferences → Add-ons → Install from Disk")
        print(f"3. Select: {source_dir}")
        return False
    
    print(f"✅ Found Blender addons: {addons_dir}")
    
    # Target installation path
    target_dir = addons_dir / addon_name
    
    # Check if addon already exists
    if target_dir.exists():
        print(f"⚠️  Addon already exists: {target_dir}")
        response = input("Overwrite existing installation? (y/n): ").lower()
        if response != 'y':
            print("❌ Installation cancelled")
            return False
        
        # Remove existing installation
        print("🗑️  Removing existing installation...")
        shutil.rmtree(target_dir)
    
    # Copy addon files
    print(f"📦 Installing addon to: {target_dir}")
    try:
        shutil.copytree(source_dir, target_dir, ignore=shutil.ignore_patterns(
            "test_addon.py", "install.py", "__pycache__", "*.pyc", ".git*"
        ))
        
        print("✅ Addon installed successfully!")
        print("\n🎯 Next steps:")
        print("1. Open/Restart Blender")
        print("2. Edit → Preferences → Add-ons")
        print("3. Search for 'HDRI Light Studio'")
        print("4. Enable the addon")
        print("5. Access via 3D Viewport → Sidebar → HDRI Studio tab")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print("\n🔍 Checking dependencies...")
    
    try:
        import numpy
        print("✅ NumPy available")
    except ImportError:
        print("⚠️  NumPy not found - install in Blender Python environment")
        print("   Blender usually includes NumPy by default")
    
    print("ℹ️  Blender dependencies (bpy, gpu, bgl) will be available in Blender environment")

def main():
    """Main installer function"""
    try:
        # Check dependencies
        check_dependencies()
        
        # Install addon
        success = install_addon()
        
        if success:
            print("\n🎉 Installation completed successfully!")
        else:
            print("\n❌ Installation failed - try manual installation")
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()