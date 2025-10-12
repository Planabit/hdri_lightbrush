import bpy

def load_and_analyze_dome():
    """Load and analyze the sample dome objects"""
    
    # Clear current scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Load dome.blend file
    dome_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\addon_resources\blendfiles\domes\dome.blend"
    
    # Import all objects from dome.blend
    with bpy.data.libraries.load(dome_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    # Link objects to scene
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
    
    print("\n" + "="*60)
    print("LOADED DOME OBJECTS ANALYSIS")
    print("="*60)
    
    for obj in bpy.context.collection.objects:
        print(f"\nObject: {obj.name}")
        print(f"  Type: {obj.type}")
        
        if obj.type == 'MESH':
            mesh = obj.data
            print(f"  Vertices: {len(mesh.vertices)}")
            print(f"  Faces: {len(mesh.polygons)}")
            
            # Analyze bounds
            if mesh.vertices:
                vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
                min_x = min(v.x for v in vertices)
                max_x = max(v.x for v in vertices)
                min_y = min(v.y for v in vertices)
                max_y = max(v.y for v in vertices)
                min_z = min(v.z for v in vertices)
                max_z = max(v.z for v in vertices)
                
                print(f"  Bounds (world space):")
                print(f"    X: {min_x:.3f} to {max_x:.3f} (size: {max_x-min_x:.3f})")
                print(f"    Y: {min_y:.3f} to {max_y:.3f} (size: {max_y-min_y:.3f})")
                print(f"    Z: {min_z:.3f} to {max_z:.3f} (size: {max_z-min_z:.3f})")
                
                # Check shape characteristics
                vertices_local = [v.co for v in mesh.vertices]
                center_verts = len([v for v in vertices_local if abs(v.z) < 0.1])
                bottom_verts = len([v for v in vertices_local if v.z < -0.1])
                top_verts = len([v for v in vertices_local if v.z > 0.1])
                
                print(f"  Shape analysis:")
                print(f"    Center vertices (Z ~0): {center_verts}")
                print(f"    Bottom vertices (Z < -0.1): {bottom_verts}")
                print(f"    Top vertices (Z > 0.1): {top_verts}")
                
                # Radius analysis
                max_radius = max(((v.x**2 + v.y**2)**0.5) for v in vertices_local)
                print(f"    Max radius: {max_radius:.3f}")
            
            # Check modifiers
            if obj.modifiers:
                print(f"  Modifiers:")
                for mod in obj.modifiers:
                    print(f"    - {mod.name} ({mod.type})")
                    if mod.type == 'SUBSURF':
                        print(f"      Levels: {mod.levels}")
                    elif mod.type == 'CORRECTIVE_SMOOTH':
                        print(f"      Iterations: {mod.iterations}")
                        print(f"      Smooth Type: {mod.smooth_type}")

if __name__ == "__main__":
    load_and_analyze_dome()
    bpy.ops.wm.save_mainfile(filepath=r"e:\Projects\HDRI_editor\tools\dome_analysis.blend")