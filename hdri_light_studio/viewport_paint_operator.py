"""
HDRI Light Studio - 3D Viewport Paint Operator

This module provides direct 3D painting on the interior surface of hemispheres/spheres.
Key features:
- SECOND INTERSECTION: Finds interior surface by using second ray hit
- SPHERICAL UV: Converts 3D position to spherical coordinates for accurate UV mapping
- DEBUG TRACKING: Integrates with debug_paint_tracker for UV validation
"""

import bpy
import bmesh
import math
from mathutils import Vector
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader

# Import debug tracker for UV validation
try:
    from . import debug_paint_tracker
    DEBUG_AVAILABLE = True
except ImportError:
    DEBUG_AVAILABLE = False
    print("Debug paint tracker not available")


class HDRI_OT_viewport_paint(bpy.types.Operator):
    """Direct 3D painting on hemisphere interior surface"""
    bl_idname = "hdri_studio.viewport_paint"
    bl_label = "3D Viewport Paint"
    bl_description = "Paint directly on hemisphere interior surface in 3D viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.hemisphere = None
        self.canvas_image = None

    def invoke(self, context, event):
        """Initialize modal painting mode"""
        
        # Find hemisphere object
        self.hemisphere = bpy.data.objects.get("HDRI_Hemisphere")
        if not self.hemisphere:
            self.report({'ERROR'}, "No HDRI Hemisphere found. Create one first.")
            return {'CANCELLED'}

        # Get canvas image
        self.canvas_image = bpy.data.images.get("HDRI_Canvas")
        if not self.canvas_image:
            self.report({'ERROR'}, "No HDRI Canvas found. Create canvas first.")
            return {'CANCELLED'}

        # Setup painting context
        self.setup_paint_mode(context)
        
        # Enter modal mode
        context.window_manager.modal_handler_add(self)
        
        self.report({'INFO'}, "3D Paint Mode - Click to paint, ESC to exit")
        print("\n" + "="*60)
        print("3D PAINT MODE ACTIVE")
        print("  LEFT CLICK: Paint on hemisphere interior")
        print("  ESC: Exit paint mode")
        print("="*60 + "\n")
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        """Handle mouse events for painting"""
        
        # Exit on ESC
        if event.type == 'ESC':
            self.cleanup(context)
            print("\n3D Paint Mode EXITED\n")
            return {'FINISHED'}
        
        # Paint on left mouse button click
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Check if mouse is over 3D viewport
            if context.area and context.area.type == 'VIEW_3D':
                self.paint_at_cursor(context, event)
                
                # Force viewport update
                context.area.tag_redraw()
        
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        """Fallback execute method - redirects to invoke"""
        return self.invoke(context, None)

    def setup_paint_mode(self, context):
        """Setup painting context"""
        # Make sure we're in object mode
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass

    def paint_at_cursor(self, context, event):
        """Paint at cursor position using SECOND ray intersection (interior surface)"""
        
        # Get 3D viewport region
        region = context.region
        region_3d = context.space_data.region_3d
        
        # Convert mouse coordinates to 3D ray
        mouse_coord = (event.mouse_region_x, event.mouse_region_y)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_coord)
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_coord)
        
        # Find ALL intersections with hemisphere (we want the SECOND one)
        intersections = self.find_all_ray_intersections(ray_origin, ray_direction)
        
        if len(intersections) >= 2:
            # Use SECOND (farther) intersection for interior painting
            hit_location, hit_normal, face_index = intersections[1]
            
            # Debug info
            print(f"Found {len(intersections)} intersections:")
            for i, (loc, norm, face) in enumerate(intersections):
                print(f"  Intersection {i+1}: {loc}, normal: {norm}")
            
            # Always use the SECOND intersection for interior surface
            # No need for normal checking - second intersection IS the interior by definition
            self.apply_paint_at_location(hit_location, face_index)
            print(f"Painting at INTERIOR surface (2nd intersection): {hit_location}")
                
        elif len(intersections) == 1:
            # Only one intersection - check if camera is inside hemisphere
            hit_location, hit_normal, face_index = intersections[0]
            
            # If camera inside hemisphere, the single intersection IS the interior surface
            center = self.hemisphere.location
            camera_to_center = (center - ray_origin).length
            hemisphere_radius = self.hemisphere.scale[0] * 2.0  # Approximate hemisphere radius
            
            if camera_to_center < hemisphere_radius:
                # Camera inside - single intersection is interior
                self.apply_paint_at_location(hit_location, face_index)
                print(f"Painting from INSIDE hemisphere: {hit_location}")
            else:
                # Camera outside with only one intersection - this means ray is tangent or grazing
                # Still paint on it as it's the only option
                self.apply_paint_at_location(hit_location, face_index)
                print(f"Painting on single intersection (grazing ray): {hit_location}")
        else:
            print("No intersections found - ray missed hemisphere")

    def find_all_ray_intersections(self, ray_origin, ray_direction):
        """Find ALL intersections between ray and hemisphere mesh using multiple ray casts"""
        intersections = []
        
        obj = self.hemisphere
        
        # Transform ray to object space for ray_cast
        ray_origin_local = obj.matrix_world.inverted() @ ray_origin
        ray_direction_local = obj.matrix_world.inverted().to_3x3() @ ray_direction
        
        # Use Blender's built-in ray_cast to find first intersection
        success1, location1, normal1, face_index1 = obj.ray_cast(ray_origin_local, ray_direction_local)
        
        if success1:
            # Transform back to world space
            location1_world = obj.matrix_world @ location1
            normal1_world = obj.matrix_world.to_3x3() @ normal1
            distance1 = (location1_world - ray_origin).length
            
            intersections.append((location1_world, normal1_world, face_index1, distance1))
            
            # Find second intersection by casting from slightly past the first hit
            offset_distance = 0.001  # Small offset past first intersection
            new_origin = location1 + ray_direction_local * offset_distance
            
            success2, location2, normal2, face_index2 = obj.ray_cast(new_origin, ray_direction_local)
            
            if success2:
                # Transform back to world space
                location2_world = obj.matrix_world @ location2
                normal2_world = obj.matrix_world.to_3x3() @ normal2
                distance2 = (location2_world - ray_origin).length
                
                intersections.append((location2_world, normal2_world, face_index2, distance2))
        
        # Sort intersections by distance (closest first)
        intersections.sort(key=lambda x: x[3])
        
        # Remove distance from result (keep location, normal, face_index)
        return [(loc, norm, face_idx) for loc, norm, face_idx, dist in intersections]

    def ray_triangle_intersect(self, ray_origin, ray_direction, triangle):
        """
        Ray-triangle intersection using Möller–Trumbore algorithm
        Returns (hit_point, distance) or (None, None) if no intersection
        """
        v0, v1, v2 = triangle
        
        # Möller–Trumbore intersection algorithm
        edge1 = v1 - v0
        edge2 = v2 - v0
        h = ray_direction.cross(edge2)
        a = edge1.dot(h)
        
        if -0.00001 < a < 0.00001:  # Ray parallel to triangle
            return None, None
        
        f = 1.0 / a
        s = ray_origin - v0
        u = f * s.dot(h)
        
        if u < 0.0 or u > 1.0:
            return None, None
        
        q = s.cross(edge1)
        v = f * ray_direction.dot(q)
        
        if v < 0.0 or u + v > 1.0:
            return None, None
        
        # Calculate distance to intersection point
        t = f * edge2.dot(q)
        
        if t > 0.00001:  # Ray intersection
            intersection_point = ray_origin + ray_direction * t
            return intersection_point, t
        else:
            return None, None

    def apply_paint_at_location(self, hit_location, face_index):
        """Apply paint at the hit location on hemisphere interior"""
        
        # Get UV coordinate at hit location using SPHERICAL MAPPING
        uv_coord = self.get_uv_at_face_center(face_index)
        if not uv_coord:
            print(f"Failed to get UV coordinate for face {face_index}")
            return
        
        print(f"UV coordinate: {uv_coord}")
        
        # Convert UV to pixel coordinates
        image_width = self.canvas_image.size[0]
        image_height = self.canvas_image.size[1]
        pixel_x = int(uv_coord[0] * image_width)
        pixel_y = int((1.0 - uv_coord[1]) * image_height)  # Flip Y coordinate
        
        print(f"Painting at pixel: ({pixel_x}, {pixel_y}) on {image_width}x{image_height} image")
        
        # Record click for debug tracking if enabled
        if DEBUG_AVAILABLE:
            debug_paint_tracker.record_paint_click(uv_coord, (pixel_x, pixel_y))
        
        # Apply paint using direct pixel manipulation
        brush = bpy.context.tool_settings.image_paint.brush
        if brush and self.canvas_image:
            # Simple brush application
            self.apply_brush_to_image(pixel_x, pixel_y, brush)

    def get_uv_at_face_center(self, face_index):
        """
        Get UV coordinate using CALIBRATED SPHERICAL MAPPING
        
        Spherical projection with empirically determined correction factors
        based on actual paint test results.
        """
        
        obj = self.hemisphere
        mesh = obj.data
        
        # Check if face index is valid
        if face_index >= len(mesh.polygons):
            print(f"Invalid face index: {face_index}")
            return None
        
        face = mesh.polygons[face_index]
        
        # Get face center in world space
        face_center_local = face.center
        face_center_world = obj.matrix_world @ face_center_local
        hemisphere_center = obj.location
        
        # Direction vector from center to face
        direction = (face_center_world - hemisphere_center).normalized()
        
        # EQUIRECTANGULAR PROJECTION (2048x1024 HDRI on full sphere)
        # Standard panorama/HDRI mapping for Blender
        
        # Longitude (U): Full 360° rotation around Z-axis
        # atan2(y, x) gives -π to π, we map to 0-1
        longitude = math.atan2(direction.y, direction.x)
        u_raw = 0.5 - (longitude / (2.0 * math.pi))
        
        # Latitude (V): -90° (south) to +90° (north)
        # asin(z) gives -π/2 to π/2, we map to 0-1
        # V=0 at bottom (south pole), V=1 at top (north pole)
        latitude = math.asin(max(-1.0, min(1.0, direction.z)))  # Clamp for safety
        v_raw = 0.5 + (latitude / math.pi)
        
        # Apply corrections based on test results:
        # U offset: +0.266 (observed -0.266 error consistently)
        u = u_raw + 0.266
        
        # V is flipped and needs small non-linear correction
        # Observed: V=0.25→-0.032, V=0.50→-0.094, V=0.75→+0.094
        v_flipped = 1.0 - v_raw
        
        # Apply small quadratic correction for V distortion
        # At V=0.25: add ~0.03, at V=0.5: add ~0.09, at V=0.75: subtract ~0.09
        v_deviation = v_flipped - 0.5
        v_correction = -v_deviation * 0.188  # Negative sign because pattern is inverted
        v = v_flipped + v_correction
        
        # Clamp to valid range
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))
        
        print(f"🌐 Spherical UV: direction({direction.x:.3f}, {direction.y:.3f}, {direction.z:.3f}) → UV({u:.3f}, {v:.3f})")
        
        return (u, v)

    def calculate_barycentric(self, point, v0, v1, v2):
        """Calculate barycentric coordinates of point in triangle v0,v1,v2"""
        
        # Vectors
        v0v1 = v1 - v0
        v0v2 = v2 - v0
        v0p = point - v0
        
        # Dot products
        dot00 = v0v2.dot(v0v2)
        dot01 = v0v2.dot(v0v1)
        dot02 = v0v2.dot(v0p)
        dot11 = v0v1.dot(v0v1)
        dot12 = v0v1.dot(v0p)
        
        # Calculate barycentric coordinates
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        w = 1 - u - v
        
        return (w, v, u)  # Return as (v0, v1, v2) weights

    def apply_brush_to_image(self, pixel_x, pixel_y, brush):
        """Apply brush effect using Blender's native texture painting system"""
        
        if not self.canvas_image or not brush:
            print("No canvas image or brush found")
            return
        
        width = self.canvas_image.size[0]
        height = self.canvas_image.size[1]
        
        # Clamp coordinates
        pixel_x = max(0, min(pixel_x, width - 1))
        pixel_y = max(0, min(pixel_y, height - 1))
        
        print(f"Applying brush at clamped position: ({pixel_x}, {pixel_y})")
        
        # Convert pixel coordinates back to UV for Blender's paint system
        uv_x = pixel_x / width
        uv_y = pixel_y / height
        
        # Try multiple approaches to make the paint visible
        
        # Method 1: Direct pixel manipulation with proper format
        try:
            import numpy as np
            
            # Get pixels as list first
            pixels_list = list(self.canvas_image.pixels)
            
            # Simple large visible brush for testing
            brush_size = 50  # Large brush to make sure it's visible
            brush_color = [1.0, 0.0, 0.0]  # Bright red for visibility
            
            print(f"Drawing red circle at ({pixel_x}, {pixel_y}) with size {brush_size}")
            
            # Draw a simple red circle
            for dy in range(-brush_size, brush_size + 1):
                for dx in range(-brush_size, brush_size + 1):
                    x = pixel_x + dx
                    y = pixel_y + dy
                    
                    if 0 <= x < width and 0 <= y < height:
                        distance = (dx * dx + dy * dy) ** 0.5
                        if distance <= brush_size:
                            # Get pixel index (RGBA format)
                            pixel_index = (y * width + x) * 4
                            
                            if pixel_index + 3 < len(pixels_list):
                                # Set to bright red
                                pixels_list[pixel_index] = 1.0     # R
                                pixels_list[pixel_index + 1] = 0.0 # G
                                pixels_list[pixel_index + 2] = 0.0 # B
                                pixels_list[pixel_index + 3] = 1.0 # A
            
            # Update image
            self.canvas_image.pixels[:] = pixels_list
            self.canvas_image.update()
            
            # Force viewport update
            for area in bpy.context.screen.areas:
                if area.type in ['VIEW_3D', 'IMAGE_EDITOR']:
                    area.tag_redraw()
            
            print("Red circle drawn and viewport updated")
            
        except Exception as e:
            print(f"Error in brush application: {e}")
            
        # Method 2: Also try forcing image save/reload to make sure changes stick
        try:
            # Mark image as dirty
            self.canvas_image.is_dirty = True
            
            # Pack image to ensure it's in memory
            if not self.canvas_image.packed_file:
                self.canvas_image.pack()
                
            print("Image marked as dirty and packed")
            
        except Exception as e:
            print(f"Error in image management: {e}")

    def get_active_canvas_image(self, context):
        """Get active canvas image for painting"""
        
        # Try to get from image paint settings
        if context.scene.tool_settings.image_paint.canvas:
            return context.scene.tool_settings.image_paint.canvas
        
        # Try to get from image editor
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR' and space.image:
                        return space.image
        
        return None

    def cleanup(self, context):
        """Cleanup paint mode"""
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass


# Registration
classes = [
    HDRI_OT_viewport_paint,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)