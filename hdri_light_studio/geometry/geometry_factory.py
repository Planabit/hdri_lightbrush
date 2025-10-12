import bpy
import bmesh
import math
from mathutils import Vector



def create_closed_hemisphere(name="Closed_Hemisphere", radius=10.0, location=(0, 0, 0)):
    """Create a closed hemisphere with rounded bottom edge"""
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    # Create bmesh instance
    bm = bmesh.new()
    
    # Create UV sphere and select upper hemisphere
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius)
    
    # Remove lower hemisphere vertices but keep some for rounded edge
    round_radius = radius * 0.1  # 1/10th of main radius for rounding
    verts_to_remove = [v for v in bm.verts if v.co.z < -round_radius]
    bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')
    
    # Create rounded transition between sphere and bottom
    # Move vertices near the bottom to create rounded edge
    for vert in bm.verts:
        if -round_radius <= vert.co.z <= 0:
            # Calculate distance from edge
            distance_from_center = (vert.co.x**2 + vert.co.y**2)**0.5
            
            # Create rounded profile
            if distance_from_center > radius - round_radius:
                # Vertices on the outer edge - create rounded corner
                angle_factor = (distance_from_center - (radius - round_radius)) / round_radius
                angle_factor = min(angle_factor, 1.0)
                
                # Calculate rounded position
                angle = angle_factor * 1.5708  # 90 degrees in radians
                new_z = -round_radius + round_radius * (1 - math.cos(angle))
                scale_factor = (radius - round_radius + round_radius * math.sin(angle)) / distance_from_center
                
                vert.co.x *= scale_factor
                vert.co.y *= scale_factor
                vert.co.z = new_z
    
    # Fill the bottom hole to create a closed hemisphere
    bottom_edges = [e for e in bm.edges if e.is_boundary]
    if bottom_edges:
        bmesh.ops.holes_fill(bm, edges=bottom_edges)
    
    # Add subdivision and smoothing for better rounded edge
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
    
    # Flip normals to face inward
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    
    # Apply smooth shading
    for face in bm.faces:
        face.smooth = True
    
    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location
    obj.location = location
    
    return obj


def create_sphere(name="Sphere", radius=10.0, location=(0, 0, 0)):
    """Create a full sphere"""
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    # Create bmesh instance
    bm = bmesh.new()
    
    # Create UV sphere
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius)
    
    # Flip normals to face inward
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    
    # Apply smooth shading
    for face in bm.faces:
        face.smooth = True
    
    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location
    obj.location = location
    
    return obj


# Geometry type registry
GEOMETRY_TYPES = {
    'CLOSED_HEMISPHERE': {
        'name': 'Closed Hemisphere', 
        'description': 'Hemisphere with rounded bottom edge',
        'create_func': create_closed_hemisphere
    },
    'SPHERE': {
        'name': 'Full Sphere',
        'description': 'Complete sphere for 360° HDRI',
        'create_func': create_sphere
    }
}


def create_geometry(geometry_type, name, radius=10.0, location=(0, 0, 0)):
    """Factory function to create geometry based on type"""
    
    if geometry_type in GEOMETRY_TYPES:
        create_func = GEOMETRY_TYPES[geometry_type]['create_func']
        return create_func(name, radius, location)
    else:
        # Default to closed hemisphere
        return create_closed_hemisphere(name, radius, location)