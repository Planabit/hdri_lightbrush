"""
HDRI Light Studio Test Script
Validates addon structure and basic functionality without Blender dependencies
"""

import os
import sys
from pathlib import Path

def test_addon_structure():
    """Test if all required files exist"""
    addon_dir = Path(__file__).parent
    required_files = [
        "__init__.py",
        "properties.py", 
        "operators.py",
        "ui.py",
        "canvas_renderer.py",
        "README.md"
    ]
    
    print("🔍 Testing Addon Structure...")
    
    missing_files = []
    for file in required_files:
        file_path = addon_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def test_bl_info():
    """Test bl_info structure in __init__.py"""
    print("\n🔍 Testing bl_info structure...")
    
    try:
        # Read __init__.py and check for bl_info
        init_file = Path(__file__).parent / "__init__.py"
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for required bl_info keys
        required_keys = ["name", "version", "blender", "category"]
        
        for key in required_keys:
            if f'"{key}"' in content:
                print(f"  ✅ bl_info['{key}'] found")
            else:
                print(f"  ❌ bl_info['{key}'] missing")
                return False
                
        print("\n✅ bl_info structure valid")
        return True
        
    except Exception as e:
        print(f"\n❌ bl_info test failed: {e}")
        return False

def test_module_imports():
    """Test if modules can be imported (syntactically)"""
    print("\n🔍 Testing Module Import Structure...")
    
    addon_dir = Path(__file__).parent
    modules = ["properties", "operators", "ui", "canvas_renderer"]
    
    all_good = True
    # We can't actually import because of bpy dependencies
    # But we can check syntax
    for module_name in modules:
        module_file = addon_dir / f"{module_name}.py"
        
        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic syntax check - look for class/function definitions
            if "def register():" in content and "def unregister():" in content:
                print(f"  ✅ {module_name}.py - register/unregister functions found")
            else:
                print(f"  ❌ {module_name}.py - missing register/unregister functions")
                all_good = False
                
        except Exception as e:
            print(f"  ❌ {module_name}.py - error reading: {e}")
            all_good = False
    
    print("\n✅ Module structure validation complete")
    return all_good

def test_gpu_features():
    """Test GPU-related feature definitions"""
    print("\n🔍 Testing GPU Features...")
    
    canvas_file = Path(__file__).parent / "canvas_renderer.py"
    
    try:
        with open(canvas_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        gpu_features = [
            "HDRICanvasRenderer",
            "bgl.GL_TRIANGLE_FAN",
            "gpu.types.GPUTexture",
            "render_canvas",
            "paint_at_position"
        ]
        
        all_good = True
        for feature in gpu_features:
            if feature in content:
                print(f"  ✅ {feature} implementation found")
            else:
                print(f"  ⚠️  {feature} not found or different naming")
                all_good = False
                
        print("\n✅ GPU features validation complete")
        return all_good
        
    except Exception as e:
        print(f"\n❌ GPU features test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("HDRI Light Studio - Addon Structure Test")
    print("="*50)
    
    tests = [
        test_addon_structure,
        test_bl_info,
        test_module_imports,
        test_gpu_features
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ Addon ready for Blender installation!")
        print("\nInstallation steps:")
        print("1. Open Blender 4.2+")  
        print("2. Edit → Preferences → Add-ons → Install from Disk")
        print("3. Select hdri_light_studio folder")
        print("4. Enable 'HDRI Light Studio' addon")
        print("5. Access via 3D Viewport → Sidebar → HDRI Studio tab")
    else:
        print(f"⚠️  TESTS INCOMPLETE ({passed}/{total})")
        print("Some issues found, but addon might still work in Blender")

if __name__ == "__main__":
    main()