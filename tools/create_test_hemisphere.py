import bpy
import mathutils
import bmesh

def create_exact_sample_hemisphere():
    """Create hemisphere exactly like in sample dome.blend"""
    
    # Clear existing mesh
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create UV Sphere first
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=5.0,
        enter_editmode=False,
        location=(0, 0, 0)
    )
    
    sphere = bpy.context.active_object
    sphere.name = "Test_Hemisphere"
    
    # Enter edit mode and modify to hemisphere
    bpy.context.view_layer.objects.active = sphere
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select all
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Deselect all first
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Switch to vertex select mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)
    
    # Get mesh data
    mesh = bmesh.from_edit_mesh(sphere.data)
    mesh.verts.ensure_lookup_table()
    
    # Select vertices below z = 0 (bottom hemisphere)
    verts_to_remove = []
    for vert in mesh.verts:
        if vert.co.z < 0:
            vert.select = True
            verts_to_remove.append(vert)
    
    # Delete selected vertices
    bmesh.ops.delete(mesh, geom=verts_to_remove, context='VERTS')
    
    # Update mesh
    bmesh.update_edit_mesh(sphere.data)
    
    # Flip normals to face inward
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    
    # Enable smooth shading
    bpy.ops.mesh.faces_shade_smooth()
    
    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add subdivision surface modifier
    subdiv = sphere.modifiers.new(name="Subdivision", type='SUBSURF')
    subdiv.levels = 2
    subdiv.render_levels = 3
    
    # Add corrective smooth modifier
    smooth = sphere.modifiers.new(name="CorrectiveSmooth", type='CORRECTIVE_SMOOTH')
    smooth.iterations = 2
    smooth.smooth_type = 'SIMPLE'
    
    print(f"Created hemisphere: {sphere.name}")
    print(f"Vertices: {len(sphere.data.vertices)}")
    print(f"Faces: {len(sphere.data.polygons)}")
    
    return sphere

if __name__ == "__main__":
    hemisphere = create_exact_sample_hemisphere()
    bpy.ops.wm.save_mainfile(filepath=r"e:\Projects\HDRI_editor\tools\test_hemisphere.blend")