
import bpy

print("=== HDRI Light Studio Operator Check ===")

# Check if addon is loaded
if hasattr(bpy.ops, 'hdrils'):
    print("✅ hdrils operators namespace exists")
    
    # Check specific operators
    if hasattr(bpy.ops.hdrils, 'create_2k_canvas'):
        print("✅ create_2k_canvas operator found")
    else:
        print("❌ create_2k_canvas operator NOT found")
        
    if hasattr(bpy.ops.hdrils, 'create_4k_canvas'):
        print("✅ create_4k_canvas operator found")
    else:
        print("❌ create_4k_canvas operator NOT found")
        
    if hasattr(bpy.ops.hdrils, 'create_canvas'):
        print("✅ create_canvas operator found")
    else:
        print("❌ create_canvas operator NOT found")
        
    # List all available hdrils operators
    print("\nAll hdrils operators:")
    for attr in dir(bpy.ops.hdrils):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
else:
    print("❌ hdrils operators namespace NOT found")
    print("Available operator namespaces:")
    for attr in dir(bpy.ops):
        if not attr.startswith('_'):
            print(f"  - {attr}")

# Check panel registration
print("\n=== Panel Check ===")
panel_found = False
for cls in bpy.types.Panel.__subclasses__():
    if hasattr(cls, 'bl_idname') and 'HDRILS' in cls.bl_idname:
        print(f"✅ Found panel: {cls.bl_idname} - {cls.bl_label}")
        panel_found = True

if not panel_found:
    print("❌ No HDRILS panels found")

# Check addon status
print("\n=== Addon Status ===")
import addon_utils
addon_info = addon_utils.check("hdri_light_studio")
if addon_info:
    print(f"✅ Addon found: {addon_info[1]}")
    print(f"   Enabled: {addon_info[0]}")
    print(f"   Module: {addon_info[2]}")
else:
    print("❌ Addon not found in addon_utils")
