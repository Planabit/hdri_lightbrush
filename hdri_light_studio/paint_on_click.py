"""
Paint on Click - Simple operator based painting
NO MODAL - just one operator per click, extremely fast!
"""

import bpy
from mathutils import Vector
from bpy_extras import view3d_utils
import math
import time

# Global cache
_pixel_buffer = None
_last_update_time = 0
_update_interval = 0.016  # 60 FPS


def get_uv_from_3d_location(sphere, face_index):
    """Get UV using CALIBRATED spherical mapping - EXACT copy from continuous_paint_handler.py"""
    mesh = sphere.data
    if face_index >= len(mesh.polygons):
        return None
    
    face = mesh.polygons[face_index]
    face_center_local = face.center
    face_center_world = sphere.matrix_world @ face_center_local
    sphere_center = sphere.matrix_world.translation  # CORRECT: Use matrix_world.translation!
    direction = (face_center_world - sphere_center).normalized()
    
    # EQUIRECTANGULAR PROJECTION
    longitude = math.atan2(direction.y, direction.x)
    u_raw = 0.5 - (longitude / (2.0 * math.pi))
    
    latitude = math.asin(max(-1.0, min(1.0, direction.z)))
    v_raw = 0.5 + (latitude / math.pi)
    
    # CALIBRATED corrections
    u = u_raw - 0.008
    v_deviation = v_raw - 0.5
    if v_raw < 0.5:
        v_correction = -0.094 + (v_deviation * v_deviation * 2.0)
    else:
        v_correction = -0.094 + (v_deviation * v_deviation * 0.3)
    v = v_raw + v_correction
    
    u = max(0.0, min(1.0, u))
    v = max(0.0, min(1.0, v))
    
    # DEBUG OUTPUT
    print(f"🎯 paint_on_click UV: face={face_index}, dir=({direction.x:.3f},{direction.y:.3f},{direction.z:.3f}) → UV({u:.3f},{v:.3f})")
    
    return (u, v)


def find_interior_surface(sphere, ray_origin, ray_direction):
    """Find interior surface (second intersection)"""
    ray_origin_local = sphere.matrix_world.inverted() @ ray_origin
    ray_direction_local = sphere.matrix_world.inverted().to_3x3() @ ray_direction
    
    success1, location1, normal1, face_index1 = sphere.ray_cast(ray_origin_local, ray_direction_local)
    if not success1:
        return None, None
    
    offset = 0.001
    new_origin = location1 + ray_direction_local * offset
    success2, location2, normal2, face_index2 = sphere.ray_cast(new_origin, ray_direction_local)
    
    if success2:
        location2_world = sphere.matrix_world @ location2
        return location2_world, face_index2
    
    return None, None


def paint_at_uv(canvas_image, uv_coord, brush_size, brush_color, intensity):
    """ULTRA FAST paint at UV coordinate"""
    global _pixel_buffer, _last_update_time
    
    try:
        width, height = canvas_image.size
        pixel_x = int(uv_coord[0] * width)
        pixel_y = int(uv_coord[1] * height)
        
        # DEBUG OUTPUT
        print(f"🖌️ paint_at_uv: UV({uv_coord[0]:.3f},{uv_coord[1]:.3f}) → pixel({pixel_x},{pixel_y}) on {width}x{height}")
        
        if _pixel_buffer is None or len(_pixel_buffer) != width * height * 4:
            _pixel_buffer = list(canvas_image.pixels)
        
        brush_size_sq = brush_size * brush_size
        for ty in range(max(0, pixel_y - brush_size), min(height, pixel_y + brush_size + 1)):
            for tx in range(max(0, pixel_x - brush_size), min(width, pixel_x + brush_size + 1)):
                dx = tx - pixel_x
                dy = ty - pixel_y
                dist_sq = dx * dx + dy * dy
                
                if dist_sq <= brush_size_sq:
                    dist = dist_sq ** 0.5
                    alpha = intensity * max(0.0, 1.0 - (dist / brush_size))
                    
                    pixel_idx = (ty * width + tx) * 4
                    for c in range(3):
                        old_val = _pixel_buffer[pixel_idx + c]
                        new_val = brush_color[c]
                        _pixel_buffer[pixel_idx + c] = old_val * (1.0 - alpha) + new_val * alpha
        
        current_time = time.time()
        if (current_time - _last_update_time) >= _update_interval:
            canvas_image.pixels.foreach_set(_pixel_buffer)
            canvas_image.update()
            _last_update_time = current_time
        
        return True
    except:
        return False


class HDRI_OT_paint_click(bpy.types.Operator):
    """Paint on HDRI sphere with single click - FAST!"""
    bl_idname = "hdri_studio.paint_click"
    bl_label = "Paint Click"
    bl_options = {'REGISTER'}
    
    def invoke(self, context, event):
        # Only in 3D viewport
        if context.area.type != 'VIEW_3D':
            return {'PASS_THROUGH'}
        
        sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
        canvas_image = bpy.data.images.get("HDRI_Canvas")
        
        if not sphere or not canvas_image:
            return {'PASS_THROUGH'}
        
        # Get ray from mouse
        region = context.region
        region_3d = context.space_data.region_3d
        mouse_coord = (event.mouse_region_x, event.mouse_region_y)
        
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_coord)
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_coord)
        
        # Find interior surface
        location, face_index = find_interior_surface(sphere, ray_origin, ray_direction)
        
        if location and face_index is not None:
            uv_coord = get_uv_from_3d_location(sphere, face_index)
            
            if uv_coord:
                props = context.scene.hdri_studio
                paint_at_uv(canvas_image, uv_coord, props.brush_size, 
                          props.brush_color[:3], props.brush_intensity)
                context.area.tag_redraw()
        
        return {'FINISHED'}


# Keymap registration
addon_keymaps = []


def register():
    bpy.utils.register_class(HDRI_OT_paint_click)
    
    # Add keymap - paint on LEFT MOUSE in 3D view
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('hdri_studio.paint_click', 'LEFTMOUSE', 'PRESS')
        addon_keymaps.append((km, kmi))
    
    print("Paint on Click registered - LEFT MOUSE paints, NO blocking!")


def unregister():
    # Remove keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    bpy.utils.unregister_class(HDRI_OT_paint_click)
    print("Paint on Click unregistered")
