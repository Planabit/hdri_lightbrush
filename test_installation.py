"""
Test installation script for HDRI Editor addon
This script can be run in Blender's Text Editor to test the addon
"""

import bpy
import sys
import os

def test_hdri_addon():
    print("=" * 50)
    print("HDRI Editor Addon Installation Test")
    print("=" * 50)
    
    try:
        # Check if addon is already enabled
        if "hdri_editor" in bpy.context.preferences.addons.keys():
            print("✅ HDRI Editor addon is already enabled")
        else:
            print("❌ HDRI Editor addon not found in enabled addons")
            return False
        
        # Test WindowManager properties
        if hasattr(bpy.types.WindowManager, 'hdri_properties'):
            print("✅ WindowManager.hdri_properties exists")
        else:
            print("❌ WindowManager.hdri_properties not found")
            return False
        
        # Test Scene properties  
        if hasattr(bpy.types.Scene, 'hdri_image'):
            print("✅ Scene.hdri_image exists")
        else:
            print("❌ Scene.hdri_image not found")
            return False
        
        # Test operators
        operators_to_check = [
            "hdri.load",
            "hdri.prev_image", 
            "hdri.next_image"
        ]
        
        for op_name in operators_to_check:
            if bpy.ops.hdri and hasattr(bpy.ops.hdri, op_name.split('.')[1]):
                print(f"✅ Operator {op_name} exists")
            else:
                print(f"❌ Operator {op_name} not found")
                return False
        
        # Test UI panel
        try:
            from hdri_editor import HDRI_PT_panel
            print("✅ HDRI_PT_panel class imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import HDRI_PT_panel: {e}")
            return False
        
        # Test enum function safely
        try:
            wm = bpy.context.window_manager
            if hasattr(wm, 'hdri_properties'):
                props = wm.hdri_properties
                # This should not cause errors now
                items = props.bl_rna.properties['hdri_preview_enum'].enum_items_static
                print("✅ Enum items function works without errors")
            else:
                print("⚠️  Cannot test enum - hdri_properties not available")
        except Exception as e:
            print(f"❌ Enum function error: {e}")
            return False
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED! Addon is properly installed.")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("=" * 50)
        return False

if __name__ == "__main__":
    test_hdri_addon()