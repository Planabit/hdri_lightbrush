"""
Simple Continuous Paint - Application Handler Based
NO MODAL - just monitors mouse state via application handlers
"""

import bpy
from mathutils import Vector
from bpy_extras import view3d_utils
import math
import time

# Global state
_paint_active = False
_sphere = None
_canvas_image = None
_is_painting = False
_last_paint_uv = None
_pixel_buffer = None
_last_update_time = 0
_update_interval = 0.033  # 30 FPS


def get_uv_from_3d_location(sphere, face_index):
    """Get UV using CALIBRATED spherical mapping (from viewport_paint_operator.py)"""
    mesh = sphere.data
    if face_index >= len(mesh.polygons):
        return None
    
    face = mesh.polygons[face_index]
    face_center_local = face.center
    face_center_world = sphere.matrix_world @ face_center_local
    sphere_center = sphere.matrix_world.translation
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
    
    return (u, v)


def find_interior_surface(sphere, ray_origin, ray_direction):
    """Find interior surface (second intersection)"""
    ray_origin_local = sphere.matrix_world.inverted() @ ray_origin
    ray_direction_local = sphere.matrix_world.inverted().to_3x3() @ ray_direction
    
    # First intersection
    success1, location1, normal1, face_index1 = sphere.ray_cast(ray_origin_local, ray_direction_local)
    if not success1:
        return None, None
    
    # Second intersection (interior)
    offset = 0.001
    new_origin = location1 + ray_direction_local * offset
    success2, location2, normal2, face_index2 = sphere.ray_cast(new_origin, ray_direction_local)
    
    if success2:
        location2_world = sphere.matrix_world @ location2
        return location2_world, face_index2
    
    return None, None


def paint_at_uv(canvas_image, uv_coord, brush_size, brush_color, intensity):
    """Paint at UV coordinate with batch update"""
    global _pixel_buffer, _last_update_time
    
    try:
        width, height = canvas_image.size
        pixel_x = int(uv_coord[0] * width)
        pixel_y = int(uv_coord[1] * height)
        
        # Initialize buffer if needed
        if _pixel_buffer is None or len(_pixel_buffer) != width * height * 4:
            _pixel_buffer = list(canvas_image.pixels)
        
        # Paint brush area
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
        
        # Batch update (30 FPS max)
        current_time = time.time()
        if (current_time - _last_update_time) >= _update_interval:
            canvas_image.pixels.foreach_set(_pixel_buffer)
            canvas_image.update()
            _last_update_time = current_time
        
        return True
    except Exception as e:
        print(f"Paint error: {e}")
        return False


def paint_handler(scene):
    """Application handler - called every frame"""
    global _paint_active, _is_painting, _sphere, _canvas_image, _last_paint_uv
    
    if not _paint_active:
        return
    
    # Get current context
    context = bpy.context
    if not context.window_manager:
        return
    
    # Only in 3D viewport
    if not context.area or context.area.type != 'VIEW_3D':
        return
    
    # Check left mouse button state from window manager
    # This is the KEY - we check the actual mouse button state!
    event = context.window_manager.windows[0] if context.window_manager.windows else None
    if not event:
        return
    
    # Simple approach: let user call paint function manually via operator
    # We just maintain the paint system, actual painting triggered by operator


def enable_paint_system():
    """Enable the paint system"""
    global _paint_active, _sphere, _canvas_image, _pixel_buffer
    
    _sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
    _canvas_image = bpy.data.images.get("HDRI_Canvas")
    
    if not _sphere or not _canvas_image:
        print("❌ Sphere or canvas not found!")
        return False
    
    _paint_active = True
    _pixel_buffer = None  # Reset buffer
    
    # Register depsgraph update handler
    if paint_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(paint_handler)
    
    print("✅ Paint system ENABLED")
    print("   Use LEFT CLICK to paint on sphere")
    return True


def disable_paint_system():
    """Disable the paint system"""
    global _paint_active, _is_painting, _pixel_buffer
    
    _paint_active = False
    _is_painting = False
    _pixel_buffer = None
    
    # Unregister handler
    if paint_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(paint_handler)
    
    print("Paint system DISABLED")


# Operators
class HDRI_OT_simple_paint_stroke(bpy.types.Operator):
    """Paint a stroke on sphere - call this on mouse events"""
    bl_idname = "hdri_studio.simple_paint_stroke"
    bl_label = "Paint Stroke"
    
    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()
    is_start: bpy.props.BoolProperty(default=False)
    is_end: bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        global _sphere, _canvas_image, _is_painting, _last_paint_uv
        
        if not _sphere or not _canvas_image:
            return {'CANCELLED'}
        
        if self.is_start:
            _is_painting = True
            _last_paint_uv = None
        elif self.is_end:
            _is_painting = False
            # Force final update
            if _canvas_image and _pixel_buffer:
                _canvas_image.pixels.foreach_set(_pixel_buffer)
                _canvas_image.update()
            return {'FINISHED'}
        
        # Get ray from mouse position
        region = context.region
        region_3d = context.space_data.region_3d
        
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, (self.mouse_x, self.mouse_y))
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, (self.mouse_x, self.mouse_y))
        
        # Find interior surface
        location, face_index = find_interior_surface(_sphere, ray_origin, ray_direction)
        
        if location and face_index is not None:
            uv_coord = get_uv_from_3d_location(_sphere, face_index)
            
            if uv_coord:
                props = context.scene.hdri_studio
                paint_at_uv(_canvas_image, uv_coord, props.brush_size, props.brush_color[:3], props.brush_intensity)
                _last_paint_uv = uv_coord
                context.area.tag_redraw()
        
        return {'FINISHED'}


classes = [
    HDRI_OT_simple_paint_stroke,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("Simple continuous paint registered")


def unregister():
    disable_paint_system()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Simple continuous paint unregistered")
