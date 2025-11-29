"""
Create a pre-configured sphere with perfect equirectangular UV mapping.
Run this in Blender to generate the sphere_equirect.blend asset file.
"""

import bpy
import bmesh
import math
from mathutils import Vector

def create_equirectangular_sphere(name="Sphere_Equirect", radius=1.0, segments=64):
    """Create a sphere with perfect equirectangular UV mapping."""
    
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create sphere geometry with bmesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=segments//2, radius=radius)
    
    # Remove the automatic UV layer (it's cylindrical)
    if bm.loops.layers.uv:
        uv_layer = bm.loops.layers.uv.active
        if uv_layer:
            bm.loops.layers.uv.remove(uv_layer)
    
    # Write bmesh to mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # NOW create proper equirectangular UV mapping
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    
    uv_layer = mesh.uv_layers.active.data
    
    # Apply equirectangular projection
    # Formula: U = atan2(y, x) / (2π) + 0.5
    #          V = asin(z/r) / π + 0.5
    
    vertex_uvs = {}
    for vertex in mesh.vertices:
        co = vertex.co
        x, y, z = co.x, co.y, co.z
        
        # Equirectangular projection
        u = (math.atan2(y, x) / (2 * math.pi)) + 0.5
        v = (math.asin(max(-1.0, min(1.0, z / radius))) / math.pi) + 0.5
        
        vertex_uvs[vertex.index] = (u, v)
    
    # Apply UVs to loops
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            loop = mesh.loops[loop_index]
            vertex_index = loop.vertex_index
            uv_layer[loop_index].uv = vertex_uvs[vertex_index]
    
    # Update mesh
    mesh.update()
    
    # Set object properties
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    # Select the object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    print(f"✅ Created sphere '{name}' with equirectangular UV mapping")
    print(f"   Vertices: {len(mesh.vertices)}")
    print(f"   Polygons: {len(mesh.polygons)}")
    print(f"   UV Layers: {len(mesh.uv_layers)}")
    
    return obj


def create_half_sphere(name="HalfSphere_Equirect", radius=1.0, segments=64):
    """Create a half-sphere with perfect equirectangular UV mapping."""
    
    # First create a full sphere
    obj = create_equirectangular_sphere(f"{name}_temp", radius, segments)
    mesh = obj.data
    
    # Enter edit mode and select lower hemisphere vertices
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Select vertices with z < threshold
    threshold = -0.1 * radius  # Keep some vertices for rounded edge
    for vertex in mesh.vertices:
        if vertex.co.z < threshold:
            vertex.select = True
    
    # Delete selected vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Rename object
    obj.name = name
    mesh.name = name
    
    print(f"✅ Created half-sphere '{name}' with equirectangular UV mapping")
    print(f"   Vertices: {len(mesh.vertices)}")
    print(f"   Polygons: {len(mesh.polygons)}")
    
    return obj


if __name__ == "__main__":
    # Create full sphere
    sphere = create_equirectangular_sphere("Sphere_Equirect", radius=1.0, segments=64)
    
    # Save the blend file
    import os
    script_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
    assets_dir = os.path.join(os.path.dirname(script_dir), "hdri_light_studio", "assets")
    
    # Create assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)
    
    blend_file = os.path.join(assets_dir, "sphere_equirect.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    
    print(f"\n✅ Saved sphere asset to: {blend_file}")
    print("\nNow you can load this sphere in the addon using:")
    print("  bpy.ops.wm.append(filename='Sphere_Equirect', directory=blend_file)")
