import bpy
import bmesh
import mathutils

def analyze_dome_objects():
    """Analyze dome objects in the current blend file"""
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
            print(f"  Rotation: {obj.rotation_euler}")
            
            # Check modifiers
            if obj.modifiers:
                print(f"  Modifiers:")
                for mod in obj.modifiers:
                    print(f"    - {mod.name} ({mod.type})")
                    if mod.type == 'SUBSURF':
                        print(f"      Levels: {mod.levels}")
                        print(f"      Render Levels: {mod.render_levels}")
                    elif mod.type == 'CORRECTIVE_SMOOTH':
                        print(f"      Iterations: {mod.iterations}")
                        print(f"      Smooth Type: {mod.smooth_type}")
            
            # Analyze mesh geometry
            print(f"  Mesh Analysis:")
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.faces.ensure_lookup_table()
            bm.verts.ensure_lookup_table()
            
            # Check vertex positions to understand the shape
            min_z = min(v.co.z for v in bm.verts)
            max_z = max(v.co.z for v in bm.verts)
            center_verts = [v for v in bm.verts if abs(v.co.z) < 0.1]
            bottom_verts = [v for v in bm.verts if v.co.z < -0.5]
            top_verts = [v for v in bm.verts if v.co.z > 0.5]
            
            print(f"    Min Z: {min_z:.3f}, Max Z: {max_z:.3f}")
            print(f"    Center vertices (Z ~0): {len(center_verts)}")
            print(f"    Bottom vertices (Z < -0.5): {len(bottom_verts)}")
            print(f"    Top vertices (Z > 0.5): {len(top_verts)}")
            
            # Check if normals are flipped
            face_normals = [f.normal.z for f in bm.faces if len(f.verts) > 2]
            if face_normals:
                avg_normal_z = sum(face_normals) / len(face_normals)
                print(f"    Average face normal Z: {avg_normal_z:.3f}")
                print(f"    Normals pointing {'inward' if avg_normal_z < 0 else 'outward'}")
            
            bm.free()
        
        elif obj.type == 'EMPTY':
            print(f"  Empty display type: {obj.empty_display_type}")
            print(f"  Empty display size: {obj.empty_display_size}")

if __name__ == "__main__":
    analyze_dome_objects()