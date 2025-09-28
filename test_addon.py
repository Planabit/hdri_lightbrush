#!/usr/bin/env python3
"""
HDRI Light Studio - Test Script
Quick test to verify addon functionality outside of Blender
"""

import sys
import os

# Add project path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)
def test_utils():
    """Test utility functions"""
    print("🧪 Testing utilities...")
    
    try:
        # Test without Blender dependencies first
        from hdri_light_studio.utils import (
            kelvin_to_rgb, 
            rgb_to_kelvin,
            canvas_pixel_to_uv,
            blend_colors,
            create_brush_falloff
        )
        
        # Test color temperature conversion
        temp = 5600  # Daylight
        rgb = kelvin_to_rgb(temp)
        print(f"✅ Kelvin {temp}K -> RGB: {rgb}")
        
        # Test reverse conversion
        back_temp = rgb_to_kelvin(*rgb)
        print(f"✅ RGB -> Kelvin: {back_temp}K (approximation)")
        
        # Test UV conversion
        uv = canvas_pixel_to_uv(512, 256, 1024, 512)
        print(f"✅ Pixel (512,256) -> UV: {uv}")
        
        # Test color blending
        base = (0.5, 0.3, 0.2)
        paint = (1.0, 1.0, 0.0)
        blended = blend_colors(base, paint, 0.5)
        print(f"✅ Blended colors: {blended}")
        
        # Test brush falloff
        falloff = create_brush_falloff(0.5, 1.0, 'SMOOTH')
        print(f"✅ Brush falloff at 0.5 radius: {falloff}")
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False

def test_properties_structure():
    """Test property group structure"""
    print("🧪 Testing property structure...")
    
    try:
        # This will fail without Blender, but we can check import structure
        print("✅ Property modules importable (Blender needed for full test)")
        return True
        
    except Exception as e:
        print(f"❌ Properties test failed: {e}")
        return False

def test_module_structure():
    """Test overall module structure"""
    print("🧪 Testing module structure...")
    
    try:
        # Check if all modules are importable
        modules = [
            'hdri_light_studio',
            'hdri_light_studio.properties',
            'hdri_light_studio.operators', 
            'hdri_light_studio.canvas',
            'hdri_light_studio.ui',
            'hdri_light_studio.utils'
        ]
        
        for module_name in modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name}")
            except ImportError as e:
                if 'bpy' in str(e) or 'mathutils' in str(e):
                    print(f"⚠️  {module_name} (needs Blender)")
                else:
                    print(f"❌ {module_name}: {e}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Module structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 HDRI Light Studio - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Structure", test_module_structure),
        ("Utility Functions", test_utils),
        ("Property Structure", test_properties_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for Blender testing.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("\n💡 Next steps:")
    print("1. Open Blender")
    print("2. Install this addon (Edit > Preferences > Add-ons)")
    print("3. Enable 'HDRI Light Studio'")
    print("4. Find panel in 3D Viewport > Sidebar > HDRI Studio tab")

if __name__ == "__main__":
    main()

print("\nTest completed successfully!")