#!/usr/bin/env python3
"""
Test and install HDRI Light Studio addon
Run this script to install and test the addon functionality
"""

import sys
import os
import shutil
import subprocess

def get_blender_addon_path():
    """Get Blender addon installation path"""
    
    # Try different common Blender addon paths
    addon_paths = [
        os.path.expanduser("~/AppData/Roaming/Blender Foundation/Blender/4.2/scripts/addons"),
        os.path.expanduser("~/AppData/Roaming/Blender Foundation/Blender/4.1/scripts/addons"), 
        os.path.expanduser("~/AppData/Roaming/Blender Foundation/Blender/4.0/scripts/addons"),
        "C:/Program Files/Blender Foundation/Blender 4.2/4.2/scripts/addons",
        "C:/Program Files/Blender Foundation/Blender 4.1/4.1/scripts/addons"
    ]
    
    for path in addon_paths:
        if os.path.exists(path):
            return path
    
    print("❌ No Blender addon directory found!")
    print("Please install Blender 4.0+ or manually specify addon path")
    return None

def install_addon():
    """Install HDRI Light Studio addon to Blender"""
    
    print("🔧 Installing HDRI Light Studio addon...")
    
    # Get current directory (where this script is)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Addon source is in parent directory
    parent_dir = os.path.dirname(script_dir)
    addon_source = os.path.join(parent_dir, "hdri_light_studio")
    
    if not os.path.exists(addon_source):
        print(f"❌ Addon source not found: {addon_source}")
        return False
    
    # Get Blender addon path
    addon_path = get_blender_addon_path()
    if not addon_path:
        return False
    
    addon_dest = os.path.join(addon_path, "hdri_light_studio")
    
    try:
        # Remove existing addon if present
        if os.path.exists(addon_dest):
            print(f"🗑️  Removing existing addon: {addon_dest}")
            shutil.rmtree(addon_dest)
        
        # Copy addon to Blender
        print(f"📁 Copying addon to: {addon_dest}")
        shutil.copytree(addon_source, addon_dest)
        
        print("✅ Addon installed successfully!")
        print(f"📍 Location: {addon_dest}")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def create_test_script():
    """Create Blender test script for addon verification"""
    
    test_script = '''
import bpy
import sys

def test_hdri_light_studio():
    """Test HDRI Light Studio addon functionality"""
    
    print("\\n=== HDRI Light Studio Test ===")
    
    try:
        # Check if addon is available
        import hdri_light_studio
        print("✅ Addon import successful")
        
        # Check if properties are registered
        scene = bpy.context.scene
        if hasattr(scene, 'hdri_studio'):
            props = scene.hdri_studio
            print("✅ Properties registered")
            
            # Test property access
            print(f"📏 Default canvas size: {props.canvas_size}")
            print(f"🎨 Default tool: {props.current_tool}")
            print(f"🌡️  Default temperature: {props.color_temperature}K")
            
        else:
            print("❌ Properties not registered")
            return False
        
        # Check if operators are available
        operators_to_check = [
            "hdri_studio.create_canvas",
            "hdri_studio.clear_canvas", 
            "hdri_studio.paint_canvas",
            "hdri_studio.add_light",
            "hdri_studio.interactive_light"
        ]
        
        for op_id in operators_to_check:
            if hasattr(bpy.ops, op_id.split('.')[0]) and hasattr(getattr(bpy.ops, op_id.split('.')[0]), op_id.split('.')[1]):
                print(f"✅ Operator available: {op_id}")
            else:
                print(f"❌ Operator missing: {op_id}")
                return False
        
        # Check utils functions
        from hdri_light_studio.utils import kelvin_to_rgb, create_light_shape
        
        # Test Kelvin conversion
        test_rgb = kelvin_to_rgb(6500)
        print(f"🌡️  6500K → RGB: {test_rgb}")
        
        # Test light shape creation
        coords_x, coords_y, values = create_light_shape('CIRCLE', 50, 100, 100, 1.0, (1.0, 0.8, 0.6))
        print(f"💡 Light shape created: {len(coords_x)} pixels")
        
        print("\\n🎉 All tests passed! HDRI Light Studio is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hdri_light_studio()
    sys.exit(0 if success else 1)
'''
    
    script_path = os.path.join(os.path.dirname(__file__), "test_hdri_light_studio.py")
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"📝 Test script created: {script_path}")
    return script_path

def main():
    """Main installation and test function"""
    
    print("🚀 HDRI Light Studio - Installation & Test")
    print("=" * 50)
    
    # Install addon
    if not install_addon():
        return False
    
    # Create test script
    test_script_path = create_test_script()
    
    print("\\n📋 Next Steps:")
    print("1. Start Blender")
    print("2. Go to Edit > Preferences > Add-ons")
    print("3. Search for 'HDRI Light Studio'")
    print("4. Enable the addon")
    print("5. Go to 3D Viewport > Sidebar (N) > HDRI Studio tab")
    print("6. Click 'Create Canvas' to start!")
    
    print("\\n🧪 To test addon functionality:")
    print(f"   Run this script in Blender: {test_script_path}")
    
    print("\\n✨ Real-time Features:")
    print("   • Paint in Image Editor → see changes in 3D viewport World")
    print("   • Use temperature control (1000K-40000K)")
    print("   • Interactive light placement with shapes")
    print("   • Automatic viewport splitting")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\\n🎊 Installation completed successfully!")
    else:
        print("\\n💥 Installation failed!")
        sys.exit(1)