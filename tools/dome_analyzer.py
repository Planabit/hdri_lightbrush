import bpy
import sys
import os

# Add the script directory to the path
script_dir = r"e:\Projects\HDRI_editor\tools"
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Load the dome.blend file
dome_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\addon_resources\blendfiles\domes\dome.blend"
bpy.ops.wm.open_mainfile(filepath=dome_path)

print("\n" + "="*60)
print("DOME GEOMETRY ANALYSIS")
print("="*60)

for obj in bpy.data.objects:
    print(f"\nObject: {obj.name}")
    print(f"  Type: {obj.type}")
    
    if obj.type == 'MESH':
        mesh = obj.data
        print(f"  Vertices: {len(mesh.vertices)}")
        print(f"  Faces: {len(mesh.polygons)}")
        print(f"  Location: {obj.location}")
        print(f"  Scale: {obj.scale}")
        
        # Check bounds
        if mesh.vertices:
            vertices = [v.co for v in mesh.vertices]
            min_x = min(v.x for v in vertices)
            max_x = max(v.x for v in vertices)
            min_y = min(v.y for v in vertices)
            max_y = max(v.y for v in vertices)
            min_z = min(v.z for v in vertices)
            max_z = max(v.z for v in vertices)
            
            print(f"  Bounds:")
            print(f"    X: {min_x:.3f} to {max_x:.3f}")
            print(f"    Y: {min_y:.3f} to {max_y:.3f}")
            print(f"    Z: {min_z:.3f} to {max_z:.3f}")
            
            # Count vertices by region
            center_verts = len([v for v in vertices if abs(v.z) < 0.1])
            bottom_verts = len([v for v in vertices if v.z < -0.1])
            top_verts = len([v for v in vertices if v.z > 0.1])
            
            print(f"  Vertex distribution:")
            print(f"    Center (Z ~0): {center_verts}")
            print(f"    Bottom (Z < -0.1): {bottom_verts}")
            print(f"    Top (Z > 0.1): {top_verts}")
        
        # Check modifiers
        if obj.modifiers:
            print(f"  Modifiers:")
            for mod in obj.modifiers:
                print(f"    - {mod.name} ({mod.type})")

print("\nAnalysis complete!")