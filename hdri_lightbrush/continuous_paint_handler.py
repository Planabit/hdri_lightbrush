"""
HDRI LightBrush - Continuous Paint Handler
Non-blocking continuous painting on 3D sphere surface.
"""

import bpy
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader
import math
import time
import numpy as np


# =============================================================================
# GLOBAL STATE
# =============================================================================

_paint_handler_active = False
_draw_handler = None
_is_painting = False
_last_mouse_pos = None
_last_paint_uv = None
_last_stable_u = 0.5
_sphere = None
_canvas_image = None
_pixel_buffer = None
_stroke_base_pixels = None
_stroke_alpha_buffer = None
_stroke_paint_count = 0
_last_visual_update = 0
_visual_update_interval = 0.033

# Performance optimization for large textures
_dirty_region = None  # Track only changed region
_update_throttle = 0.016  # 60 FPS cap
_last_update_time = 0

# Cursor cache
_last_cursor_pos = None
_last_brush_radius = None
_cursor_batch = None
_cursor_shader = None


# =============================================================================
# COLOR CONVERSION
# =============================================================================

def srgb_to_linear(color):
    """Convert sRGB color to Linear color space."""
    linear = []
    for c in color[:3]:
        if c <= 0.04045:
            linear.append(c / 12.92)
        else:
            linear.append(((c + 0.055) / 1.055) ** 2.4)
    return linear


# =============================================================================
# RAYCASTING
# =============================================================================

def find_interior_surface(sphere, ray_origin, ray_direction):
    """Find the interior (far) surface of the sphere from camera view."""
    # Ensure mesh is up to date for raycasting
    depsgraph = bpy.context.evaluated_depsgraph_get()
    sphere_eval = sphere.evaluated_get(depsgraph)
    
    matrix_inv = sphere_eval.matrix_world.inverted()
    ray_origin_local = matrix_inv @ ray_origin
    ray_direction_local = matrix_inv.to_3x3() @ ray_direction
    ray_direction_local.normalize()
    
    # Use evaluated mesh for ray_cast
    success1, location1, normal1, face_index1 = sphere_eval.ray_cast(ray_origin_local, ray_direction_local)
    
    if not success1:
        return None, None, None
    
    # Find second (far) surface
    new_origin = location1 + ray_direction_local * 0.001
    success2, location2, normal2, face_index2 = sphere_eval.ray_cast(new_origin, ray_direction_local)
    
    if success2:
        return sphere.matrix_world @ location2, face_index2, location2
    return sphere.matrix_world @ location1, face_index1, location1


# =============================================================================
# UV MAPPING
# =============================================================================

def get_uv_from_hit_point(sphere, hit_point_world):
    """Get UV coordinate from hit point using equirectangular projection."""
    global _last_stable_u
    
    sphere_center = sphere.matrix_world.translation
    direction = (hit_point_world - sphere_center).normalized()
    
    # Account for sphere rotation
    rot_matrix = sphere.rotation_euler.to_matrix()
    inv_rot = rot_matrix.inverted()
    direction_local = inv_rot @ direction
    
    length = math.sqrt(direction_local.x**2 + direction_local.y**2 + direction_local.z**2)
    if length > 0.0001:
        direction_local = direction_local / length
    
    xy_length = math.sqrt(direction_local.x**2 + direction_local.y**2)
    
    # Latitude (V)
    latitude = math.asin(max(-1.0, min(1.0, direction_local.z)))
    v = 0.5 + (latitude / math.pi)
    v = max(0.0, min(1.0, v))
    
    # Longitude (U)
    longitude = math.atan2(direction_local.y, direction_local.x)
    u = 0.5 - (longitude / (2.0 * math.pi))
    if u < 0.0:
        u += 1.0
    elif u > 1.0:
        u -= 1.0
    
    # Pole stabilization
    if xy_length > 0.2:
        _last_stable_u = u
    else:
        u_diff = abs(u - _last_stable_u)
        if u_diff > 0.5:
            u_diff = 1.0 - u_diff
        if u_diff > 0.1:
            u = _last_stable_u
    
    return (u, v)


# =============================================================================
# PAINTING
# =============================================================================

def paint_at_uv(canvas_image, uv_coord, brush_size, brush_color, brush_strength, 
                brush_hardness, brush_curve=None, is_stroke_start=False, write_to_canvas=True,
                blend_mode='MIX'):
    """Paint at UV coordinate using Blender's brush curve for falloff."""
    global _pixel_buffer, _stroke_base_pixels, _stroke_alpha_buffer
    
    try:
        width, height = canvas_image.size
        pixel_x = int(uv_coord[0] * width)
        pixel_y = int(uv_coord[1] * height)
        
        # Initialize stroke buffers
        if is_stroke_start or _pixel_buffer is None or len(_pixel_buffer) != width * height * 4:
            _pixel_buffer = np.array(canvas_image.pixels[:], dtype=np.float32)
            _stroke_base_pixels = _pixel_buffer.copy()
            _stroke_alpha_buffer = np.zeros((height, width), dtype=np.float32)
        
        # Brush bounds
        x_min = max(0, pixel_x - brush_size)
        x_max = min(width, pixel_x + brush_size + 1)
        y_min = max(0, pixel_y - brush_size)
        y_max = min(height, pixel_y + brush_size + 1)
        
        if x_max - x_min <= 0 or y_max - y_min <= 0:
            return True
        
        # Distance calculation
        yy, xx = np.ogrid[y_min-pixel_y:y_max-pixel_y, x_min-pixel_x:x_max-pixel_x]
        dist_sq = xx*xx + yy*yy
        mask = dist_sq <= brush_size * brush_size
        
        if not np.any(mask):
            return True
        
        dist = np.sqrt(dist_sq)
        normalized_dist = dist / brush_size
        
        # Calculate falloff using brush curve
        if brush_curve is not None:
            flat_dist = normalized_dist.flatten()
            flat_falloff = np.array([
                brush_curve.evaluate(brush_curve.curves[0], d) if d <= 1.0 else 0.0
                for d in flat_dist
            ])
            falloff = np.clip(flat_falloff.reshape(normalized_dist.shape), 0, 1)
        else:
            # Fallback hardness-based
            if brush_hardness >= 0.99:
                falloff = np.ones_like(dist)
            else:
                falloff = np.ones_like(dist)
                outer_mask = normalized_dist > brush_hardness
                if np.any(outer_mask) and brush_hardness < 1.0:
                    outer_dist = (normalized_dist[outer_mask] - brush_hardness) / (1.0 - brush_hardness)
                    falloff[outer_mask] = 1.0 - outer_dist * outer_dist
                falloff = np.clip(falloff, 0, 1)
        
        # Calculate alpha and apply stroke buffer (prevents accumulation)
        dab_alpha = (falloff * brush_strength) * mask
        alpha_region = _stroke_alpha_buffer[y_min:y_max, x_min:x_max]
        np.maximum(alpha_region, dab_alpha, out=alpha_region)
        
        # Blend colors based on blend mode
        base_2d = _stroke_base_pixels.reshape((height, width, 4))
        pixels_2d = _pixel_buffer.reshape((height, width, 4))
        
        base_region = base_2d[y_min:y_max, x_min:x_max, :3]
        region = pixels_2d[y_min:y_max, x_min:x_max, :3]
        
        alpha_3d = alpha_region[:, :, np.newaxis]
        brush_rgb = np.array(srgb_to_linear(brush_color), dtype=np.float32)
        
        # Apply different blend modes
        if blend_mode == 'MIX':
            # Normal blend - replaces color
            blended = brush_rgb
        elif blend_mode == 'ADD':
            # Add - brightens
            blended = base_region + brush_rgb
        elif blend_mode == 'MULTIPLY':
            # Multiply - darkens
            blended = base_region * brush_rgb
        elif blend_mode == 'LIGHTEN':
            # Lighten - only lightens pixels
            blended = np.maximum(base_region, brush_rgb)
        elif blend_mode == 'DARKEN':
            # Darken - only darkens pixels
            blended = np.minimum(base_region, brush_rgb)
        elif blend_mode == 'ERASE':
            # Erase to black
            blended = np.zeros_like(brush_rgb)
        else:
            blended = brush_rgb
        
        region[:] = base_region * (1.0 - alpha_3d) + blended * alpha_3d
        
        # Clamp values
        np.clip(region, 0.0, None, out=region)  # Allow HDR values > 1.0
        
        if write_to_canvas:
            canvas_image.pixels.foreach_set(_pixel_buffer)
        
        return True
        
    except Exception:
        return False


def update_3d_viewport():
    """Force 3D viewport texture refresh with throttling for performance."""
    global _canvas_image, _sphere, _last_update_time, _update_throttle
    
    # Throttle updates for large textures (prevents lag on 4K-8K)
    current_time = time.time()
    if current_time - _last_update_time < _update_throttle:
        return  # Skip update if too soon
    
    _last_update_time = current_time
    
    if _canvas_image:
        # Force GPU texture update - critical for Blender 5.0
        _canvas_image.update()
        _canvas_image.gl_free()  # Free old GPU texture
        _canvas_image.gl_load()  # Reload to GPU
    
    if _sphere and _sphere.active_material:
        _sphere.active_material.update_tag()
        # Force node tree update for texture refresh
        if _sphere.active_material.use_nodes:
            _sphere.active_material.node_tree.update_tag()
    
    # Force depsgraph update
    if bpy.context.view_layer:
        bpy.context.view_layer.update()
    
    # Tag all 3D viewports for redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# =============================================================================
# UI REGION CHECK
# =============================================================================

def is_mouse_in_main_region(context, event):
    """Check if mouse is in main 3D viewport (not over UI panels)."""
    mouse_x, mouse_y = event.mouse_x, event.mouse_y
    
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            if area.x <= mouse_x < area.x + area.width and area.y <= mouse_y < area.y + area.height:
                for region in area.regions:
                    if region.x <= mouse_x < region.x + region.width and region.y <= mouse_y < region.y + region.height:
                        return region.type == 'WINDOW'
    return False


# =============================================================================
# EVENT HANDLING
# =============================================================================

def mouse_event_handler(context, event):
    """Handle mouse events for painting."""
    global _is_painting, _last_mouse_pos, _last_stable_u
    
    _last_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
    
    if context.area.type != 'VIEW_3D':
        return
    
    if not is_mouse_in_main_region(context, event):
        if _is_painting and event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            _is_painting = False
            _last_mouse_pos = None
        return
    
    if event.type == 'LEFTMOUSE':
        if event.value == 'PRESS':
            _is_painting = True
            _last_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            _last_stable_u = 0.5
            paint_at_mouse(context, event, is_stroke_start=True)
        elif event.value == 'RELEASE':
            if _is_painting:
                paint_at_mouse(context, event, is_stroke_end=True)
            _is_painting = False
            _last_mouse_pos = None
    elif event.type == 'MOUSEMOVE' and _is_painting:
        paint_at_mouse(context, event, is_stroke_continue=True)


def paint_at_mouse(context, event, is_stroke_start=False, is_stroke_continue=False, is_stroke_end=False):
    """Paint at mouse position with spacing-based interpolation."""
    global _sphere, _canvas_image, _last_paint_uv, _stroke_paint_count, _last_visual_update
    
    _canvas_image = bpy.data.images.get("HDRI_Canvas")
    if not _sphere or not _canvas_image:
        return
    
    try:
        region = context.region
        region_3d = context.space_data.region_3d
        mouse_coord = (event.mouse_region_x, event.mouse_region_y)
        
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_coord)
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_coord)
        
        interior_location, face_index, _ = find_interior_surface(_sphere, ray_origin, ray_direction)
        
        if interior_location and face_index is not None:
            uv_coord = get_uv_from_hit_point(_sphere, interior_location)
            
            if uv_coord:
                try:
                    ts = bpy.context.scene.tool_settings
                except Exception:
                    return
                
                # Get brush settings from our addon properties (Blender 5.0 compatible)
                props = bpy.context.scene.hdri_studio
                
                # Read our custom brush settings
                brush_color = tuple(props.paint_color[:3])
                brush_radius = props.paint_size
                brush_strength = props.paint_strength
                brush_hardness = props.paint_hardness
                blend_mode = props.paint_blend
                
                # Get brush reference for curve/spacing (optional)
                brush = None
                brush_curve = None
                brush_spacing = 0.25  # Default 25%
                try:
                    if ts.image_paint and ts.image_paint.brush:
                        brush = ts.image_paint.brush
                        # Blender 5.0+: brush.curve renamed to brush.curve_distance_falloff
                        try:
                            if hasattr(brush, 'curve_distance_falloff'):
                                brush_curve = brush.curve_distance_falloff
                            elif hasattr(brush, 'curve'):
                                brush_curve = brush.curve
                        except:
                            pass
                        brush_spacing = getattr(brush, 'spacing', 25) / 100.0
                except:
                    pass
                
                width, height = _canvas_image.size
                spacing_px = max(1, brush_spacing * brush_radius * 2)
                
                if is_stroke_start or _last_paint_uv is None:
                    try:
                        paint_at_uv(_canvas_image, uv_coord, brush_radius, brush_color,
                                   brush_strength, brush_hardness, brush_curve,
                                   is_stroke_start=True, write_to_canvas=True, blend_mode=blend_mode)
                    except Exception:
                        pass
                    _stroke_paint_count += 1
                    _last_paint_uv = uv_coord
                else:
                    dx = uv_coord[0] - _last_paint_uv[0]
                    dy = uv_coord[1] - _last_paint_uv[1]
                    
                    # Wrap-around detection
                    if abs(dx) > 0.5:
                        paint_at_uv(_canvas_image, uv_coord, brush_radius, brush_color,
                                   brush_strength, brush_hardness, brush_curve,
                                   is_stroke_start=False, write_to_canvas=True, blend_mode=blend_mode)
                        _stroke_paint_count += 1
                        _last_paint_uv = uv_coord
                    else:
                        dx_px = dx * width
                        dy_px = dy * height
                        distance_px = (dx_px*dx_px + dy_px*dy_px) ** 0.5
                        
                        if distance_px >= spacing_px:
                            num_dabs = int(distance_px / spacing_px)
                            for i in range(1, num_dabs + 1):
                                t = (i * spacing_px) / distance_px
                                interp_uv = (_last_paint_uv[0] + dx * t, _last_paint_uv[1] + dy * t)
                                paint_at_uv(_canvas_image, interp_uv, brush_radius, brush_color,
                                           brush_strength, brush_hardness, brush_curve,
                                           is_stroke_start=False, write_to_canvas=(i == num_dabs), blend_mode=blend_mode)
                                _stroke_paint_count += 1
                            
                            final_t = (num_dabs * spacing_px) / distance_px
                            _last_paint_uv = (_last_paint_uv[0] + dx * final_t, _last_paint_uv[1] + dy * final_t)
                
                # Throttled update
                current_time = time.time()
                if is_stroke_end or (current_time - _last_visual_update) >= _visual_update_interval:
                    update_3d_viewport()
                    _last_visual_update = current_time
                    if is_stroke_end:
                        _last_paint_uv = None
    
    except Exception:
        pass


# =============================================================================
# CURSOR DRAWING
# =============================================================================

def draw_handler_callback():
    """Draw brush cursor circle."""
    global _last_mouse_pos, _paint_handler_active
    global _last_cursor_pos, _last_brush_radius, _cursor_batch, _cursor_shader
    
    if not _paint_handler_active or not _last_mouse_pos:
        return
    
    context = bpy.context
    if not context.area or context.area.type != 'VIEW_3D':
        return
    
    # Get brush radius
    try:
        ts = bpy.context.scene.tool_settings
        brush = ts.image_paint.brush if ts.image_paint else None
        # Blender 5.0: no unified_paint_settings - use brush.size directly
        brush_radius_px = int(brush.size) if brush else 50
    except:
        brush_radius_px = 50
    
    # Update cursor if needed
    if _last_cursor_pos != _last_mouse_pos or _last_brush_radius != brush_radius_px or _cursor_batch is None:
        _last_cursor_pos = _last_mouse_pos
        _last_brush_radius = brush_radius_px
        
        segments = 32
        vertices = []
        cx, cy = _last_mouse_pos
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            vertices.append((cx + brush_radius_px * math.cos(angle), cy + brush_radius_px * math.sin(angle)))
        
        # Blender 5.0+: shader names changed
        try:
            _cursor_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        except ValueError:
            # Blender 5.0+ uses '2D_UNIFORM_COLOR'
            _cursor_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        _cursor_batch = batch_for_shader(_cursor_shader, 'LINE_STRIP', {"pos": vertices})
    
    # Draw
    if _cursor_batch and _cursor_shader:
        try:
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(2.0)
            _cursor_shader.bind()
            _cursor_shader.uniform_float("color", (1.0, 1.0, 1.0, 0.8))
            _cursor_batch.draw(_cursor_shader)
            gpu.state.line_width_set(1.0)
            gpu.state.blend_set('NONE')
        except:
            pass


# =============================================================================
# ENABLE/DISABLE
# =============================================================================

def enable_continuous_paint(context):
    """Enable continuous painting mode."""
    global _paint_handler_active, _draw_handler, _sphere, _canvas_image
    
    _sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
    _canvas_image = bpy.data.images.get("HDRI_Canvas")
    
    if not _sphere or not _canvas_image:
        return False
    
    if _draw_handler is None:
        _draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_handler_callback, (), 'WINDOW', 'POST_PIXEL')
    
    _paint_handler_active = True
    bpy.ops.hdri_studio.continuous_paint_modal('INVOKE_DEFAULT')
    return True


def disable_continuous_paint():
    """Disable continuous painting mode."""
    global _paint_handler_active, _draw_handler, _is_painting
    
    _is_painting = False
    
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None
    
    _paint_handler_active = False


# =============================================================================
# OPERATORS
# =============================================================================

class HDRI_OT_continuous_paint_enable(bpy.types.Operator):
    """Enable continuous painting"""
    bl_idname = "hdri_studio.continuous_paint_enable"
    bl_label = "Enable Continuous Paint"
    
    def execute(self, context):
        if enable_continuous_paint(context):
            return {'FINISHED'}
        self.report({'ERROR'}, "Create sphere and canvas first")
        return {'CANCELLED'}


class HDRI_OT_continuous_paint_disable(bpy.types.Operator):
    """Disable continuous painting"""
    bl_idname = "hdri_studio.continuous_paint_disable"
    bl_label = "Disable Continuous Paint"
    
    def execute(self, context):
        disable_continuous_paint()
        return {'FINISHED'}


class HDRI_OT_continuous_paint_modal(bpy.types.Operator):
    """Modal operator for event capture"""
    bl_idname = "hdri_studio.continuous_paint_modal"
    bl_label = "Continuous Paint Modal"
    bl_options = {'REGISTER', 'UNDO'}
    
    _timer = None
    
    def modal(self, context, event):
        global _paint_handler_active, _is_painting, _last_mouse_pos
        
        if not _paint_handler_active:
            self.cancel(context)
            return {'CANCELLED'}
        
        if event.type == 'TIMER':
            # Force redraw for cursor update
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            return {'PASS_THROUGH'}
        
        if event.type == 'ESC' and event.value == 'PRESS':
            self.cancel(context)
            disable_continuous_paint()
            return {'CANCELLED'}
        
        # Update mouse position for cursor drawing
        if event.type == 'MOUSEMOVE':
            _last_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        
        if not context.area or context.area.type != 'VIEW_3D':
            return {'PASS_THROUGH'}
        
        if not is_mouse_in_main_region(context, event):
            if _is_painting and event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                _is_painting = False
            return {'PASS_THROUGH'}
        
        sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
        if not sphere:
            return {'PASS_THROUGH'}
        
        # Handle painting events
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                region = context.region
                region_3d = context.space_data.region_3d
                mouse_coord = (event.mouse_region_x, event.mouse_region_y)
                
                ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_coord)
                ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_coord)
                location, _, _ = find_interior_surface(sphere, ray_origin, ray_direction)
                
                if location is not None:
                    mouse_event_handler(context, event)
                    context.area.tag_redraw()
                    return {'RUNNING_MODAL'}
                return {'PASS_THROUGH'}
            
            elif event.value == 'RELEASE':
                if _is_painting:
                    mouse_event_handler(context, event)
                    context.area.tag_redraw()
                return {'PASS_THROUGH'}
        
        elif event.type == 'MOUSEMOVE':
            if _is_painting:
                mouse_event_handler(context, event)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.05, window=context.window)  # 50ms for better responsiveness
        wm.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if context.area:
            context.area.tag_redraw()


# =============================================================================
# REGISTRATION
# =============================================================================

classes = [
    HDRI_OT_continuous_paint_enable,
    HDRI_OT_continuous_paint_disable,
    HDRI_OT_continuous_paint_modal,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    disable_continuous_paint()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
