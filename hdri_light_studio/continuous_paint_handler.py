"""
HDRI Light Studio - Continuous Paint Handler (KeyShot-style)

Non-blocking continuous painting without modal operators.
Uses SpaceView3D draw handler to capture mouse events.

Key features:
- NON-MODAL: No blocking, all tools work normally
- AUTOMATIC: Just LEFT CLICK + DRAG to paint
- DEBUG COMPATIBLE: Works with debug tracking system
- CALIBRATED: Uses proven <65px accurate UV mapping
"""

import bpy
from bpy.app.handlers import persistent
from mathutils import Vector
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader
import math
import time  # For batch update timing
import numpy as np  # FAST pixel operations!


# ============================================================================
# COLOR CONVERSION
# ============================================================================

def srgb_to_linear(color):
    """Convert sRGB color to Linear color space.
    
    Blender's COLOR properties are in sRGB gamma-corrected space,
    but HDRI images use Linear Rec.709 color space.
    This conversion is essential for accurate color matching between
    2D painting (which Blender handles automatically) and 3D painting.
    """
    linear = []
    for component in color[:3]:  # Only RGB, not alpha
        if component <= 0.04045:
            linear.append(component / 12.92)
        else:
            linear.append(((component + 0.055) / 1.055) ** 2.4)
    return linear


# Global state
_paint_handler_active = False
_draw_handler = None
_mouse_handler = None
_is_painting = False
_last_mouse_pos = None
_last_paint_uv = None
_last_stable_u = 0.5  # For pole stabilization
_sphere = None
_canvas_image = None
_pixel_buffer = None
_stroke_paint_count = 0
_last_visual_update = 0
_visual_update_interval = 0.033  # 30 FPS visual updates

# Cursor drawing cache (to reduce lag)
_last_cursor_pos = None
_last_brush_radius = None
_cursor_batch = None
_cursor_shader = None


# ============================================================================
# CORE PAINTING FUNCTIONS (from working viewport_paint_operator.py)
# ============================================================================

def find_interior_surface(sphere, ray_origin, ray_direction):
    """Find the FAR (interior) surface we're looking at from inside the sphere.
    
    The camera might not be at the exact center, so we need to find the
    FAR surface, not the near one. We do this by:
    1. First raycast to find near surface
    2. Second raycast from just past the near surface to find far surface
    """
    
    # Transform to object space
    matrix_inv = sphere.matrix_world.inverted()
    ray_origin_local = matrix_inv @ ray_origin
    ray_direction_local = matrix_inv.to_3x3() @ ray_direction
    ray_direction_local.normalize()
    
    # First raycast - might hit near surface
    success1, location1, normal1, face_index1 = sphere.ray_cast(ray_origin_local, ray_direction_local)
    
    if not success1:
        return None, None, None
    
    # Try to find a second (far) surface by continuing the ray
    # Start from just past the first hit
    offset = 0.001  # Small offset to get past first surface
    new_origin = location1 + ray_direction_local * offset
    
    success2, location2, normal2, face_index2 = sphere.ray_cast(new_origin, ray_direction_local)
    
    if success2:
        # Found far surface - this is what we actually see!
        hit_world = sphere.matrix_world @ location2
        return hit_world, face_index2, location2
    else:
        # Only one surface found - camera must be inside, use first hit
        hit_world = sphere.matrix_world @ location1
        return hit_world, face_index1, location1


def get_uv_from_hit_point(sphere, hit_point_world):
    """
    Get UV coordinate from EXACT hit point using spherical projection.
    
    This is more accurate than face center method because it uses
    the actual raycast intersection point.
    
    EQUIRECTANGULAR PROJECTION:
    - U (horizontal): 0 = left edge, 1 = right edge (wraps around)
    - V (vertical): 0 = bottom (south pole), 1 = top (north pole)
    
    NOTE: Material uses -Normal (inverted), so we must invert direction too!
    """
    global _last_stable_u
    
    # Get sphere center in world space
    sphere_center = sphere.matrix_world.translation
    
    # Direction from sphere center to hit point
    # This is the actual direction to the far surface we hit
    # NO inversion needed - we're using the real hit point now!
    direction = (hit_point_world - sphere_center).normalized()
    
    # Account for sphere rotation (important for rotation sync!)
    # Use rotation_euler to get ONLY rotation, not scale!
    from mathutils import Matrix
    rot_matrix = sphere.rotation_euler.to_matrix()
    inv_rot = rot_matrix.inverted()
    direction_local = inv_rot @ direction
    
    # Normalize again after rotation
    length = math.sqrt(direction_local.x**2 + direction_local.y**2 + direction_local.z**2)
    if length > 0.0001:
        direction_local = direction_local / length
    
    # EQUIRECTANGULAR PROJECTION (Standard HDRI projection)
    # This matches Blender's Environment Texture node with EQUIRECTANGULAR projection
    
    # Calculate xy_length for pole detection
    xy_length = math.sqrt(direction_local.x**2 + direction_local.y**2)
    
    # Latitude (V): Use asin for proper equirectangular mapping
    # asin(z) gives angle from equator: -π/2 (south) to +π/2 (north)
    latitude = math.asin(max(-1.0, min(1.0, direction_local.z)))
    
    # INVERTED formula to match material's -Normal direction
    # Material uses -Normal, so we need opposite mapping
    v = 0.5 + (latitude / math.pi)
    
    # Clamp V
    v = max(0.0, min(1.0, v))
    
    # U: Angle around Z axis
    longitude = math.atan2(direction_local.y, direction_local.x)
    # INVERTED formula to match material's -Normal direction
    u = 0.5 - (longitude / (2.0 * math.pi))
    
    # Wrap U to 0-1 range
    if u < 0.0:
        u += 1.0
    elif u > 1.0:
        u -= 1.0
    
    # POLE STABILIZATION: When near poles, U is unreliable
    # Keep track of last good U and use it when xy_length is small
    pole_threshold = 0.2  # ~11.5 degrees from pole
    
    if xy_length > pole_threshold:
        # Good U value - save it
        _last_stable_u = u
    else:
        # Near pole - check if U jumped unreasonably
        u_diff = abs(u - _last_stable_u)
        # Account for wraparound
        if u_diff > 0.5:
            u_diff = 1.0 - u_diff
        
        # If U jumped more than 0.1 (36 degrees), it's probably noise
        if u_diff > 0.1:
            # Use last stable U instead
            u = _last_stable_u
            # DEBUG
            print(f"🔧 POLE FIX: Using stable U={u:.3f} instead of noisy value | xy_len={xy_length:.3f}")
    
    # DEBUG: Log values around equator and southern hemisphere
    if v < 0.55 and v > 0.2:
        print(f"📍 UV: ({u:.3f}, {v:.3f}) | z={direction_local.z:.3f}")
    
    return (u, v)


def get_uv_from_face_center(sphere, face_index):
    """
    Get UV coordinate using CALIBRATED SPHERICAL MAPPING
    
    COPIED FROM viewport_paint_operator.py - PROVEN TO WORK!
    Spherical projection with empirically determined correction factors.
    
    NOTE: Material uses -Normal, so we invert direction!
    """
    
    mesh = sphere.data
    
    if face_index >= len(mesh.polygons):
        return None
    
    # Get the face
    face = mesh.polygons[face_index]
    
    # Calculate face center in WORLD SPACE
    face_center_local = face.center
    face_center_world = sphere.matrix_world @ face_center_local
    
    # Convert to sphere local space for UV calculation
    sphere_center = sphere.matrix_world.translation
    direction = (face_center_world - sphere_center).normalized()
    
    # EQUIRECTANGULAR PROJECTION - INVERTED to match material's -Normal
    import math
    
    # Longitude (U): Full 360° rotation around Z-axis
    # INVERTED formula to match material's -Normal direction
    longitude = math.atan2(direction.y, direction.x)
    u_raw = 0.5 - (longitude / (2.0 * math.pi))
    
    # Latitude (V): -90° (south) to +90° (north)
    # INVERTED formula to match material's -Normal direction
    latitude = math.asin(max(-1.0, min(1.0, direction.z)))  # Clamp for safety
    v_raw = 0.5 + (latitude / math.pi)
    
    # Apply empirical corrections (EXACT COPY from viewport_paint_operator.py):
    u = u_raw - 0.008
    
    # V correction with asymmetric quadratic
    v_deviation = v_raw - 0.5
    
    if v_raw < 0.5:
        # Below center
        v_correction = -0.094 + (v_deviation * v_deviation * 2.0)
    else:
        # Above center
        v_correction = -0.094 + (v_deviation * v_deviation * 0.3)
    
    v = v_raw + v_correction
    
    # Clamp to valid range
    u = max(0.0, min(1.0, u))
    v = max(0.0, min(1.0, v))
    
    # 🔍 DEBUG: Disabled to reduce lag - uncomment if needed
    # if face_index % 50 == 0:
    #     print(f"🎯 UV calculated: ({u:.4f}, {v:.4f}) | Face: {face_index}")
    
    return (u, v)


def interpolate_uv(uv_start, uv_end, steps=5):
    """Interpolate between two UV coordinates for smooth brush strokes with wraparound detection"""
    if not uv_start or not uv_end:
        return [uv_end] if uv_end else []
    
    # Check for large jumps - DON'T interpolate if too far apart
    u_diff = abs(uv_end[0] - uv_start[0])
    v_diff = abs(uv_end[1] - uv_start[1])
    
    # If U difference is > 0.3, we're likely crossing the seam or at a pole
    if u_diff > 0.3:
        print(f"⚠️ U SKIP: U jumped {u_diff:.3f} | start={uv_start} end={uv_end}")
        return [uv_end]
    
    # If V difference is > 0.05, mouse moved too fast - don't draw long lines
    # This prevents the "brush stretching" effect
    if v_diff > 0.05:
        print(f"⚠️ V SKIP: V jumped {v_diff:.3f} | start=({uv_start[0]:.3f}, {uv_start[1]:.3f}) end=({uv_end[0]:.3f}, {uv_end[1]:.3f})")
        return [uv_end]
    
    interpolated = []
    for i in range(steps + 1):
        t = i / steps
        u = uv_start[0] * (1 - t) + uv_end[0] * t
        v = uv_start[1] * (1 - t) + uv_end[1] * t
        interpolated.append((u, v))
    
    return interpolated


def paint_at_uv(canvas_image, uv_coord, brush_size, brush_color, brush_strength, brush_hardness, is_stroke_start=False, write_to_canvas=True):
    """
    FULLY VECTORIZED numpy paint with Blender-style falloff curve.
    
    Args:
        brush_hardness: 0.0 (soft/smooth falloff) to 1.0 (hard edge)
    """
    global _pixel_buffer
    
    try:
        width, height = canvas_image.size
        pixel_x = int(uv_coord[0] * width)
        pixel_y = int(uv_coord[1] * height)
        
        # Load pixels: FRESH at stroke start, cached during stroke
        if is_stroke_start or _pixel_buffer is None or len(_pixel_buffer) != width * height * 4:
            _pixel_buffer = np.array(canvas_image.pixels[:], dtype=np.float32)
        
        # Brush bounds
        x_min = max(0, pixel_x - brush_size)
        x_max = min(width, pixel_x + brush_size + 1)
        y_min = max(0, pixel_y - brush_size)
        y_max = min(height, pixel_y + brush_size + 1)
        
        bw = x_max - x_min
        bh = y_max - y_min
        if bw <= 0 or bh <= 0:
            return True
        
        # Vectorized distance calculation
        yy, xx = np.ogrid[y_min-pixel_y:y_max-pixel_y, x_min-pixel_x:x_max-pixel_x]
        dist_sq = xx*xx + yy*yy
        brush_size_sq = brush_size * brush_size
        mask = dist_sq <= brush_size_sq
        
        if not np.any(mask):
            return True
        
        # Vectorized alpha calculation with Blender-style falloff
        dist = np.sqrt(dist_sq)
        
        # Blender falloff curve based on hardness:
        # hardness = 0.0 -> smooth falloff (soft brush)
        # hardness = 1.0 -> no falloff (hard brush)
        if brush_hardness >= 0.99:  # Hard brush (no falloff)
            falloff = 1.0
        else:
            # Normalized distance (0 at center, 1 at edge)
            normalized_dist = np.clip(dist / brush_size, 0, 1)
            
            # Blender's falloff: smooth curve affected by hardness
            # Higher hardness = steeper falloff at edges
            # Formula approximates Blender's curve behavior
            if brush_hardness > 0.5:
                # Sharp falloff (preserve edge)
                power = 1.0 + (brush_hardness - 0.5) * 4.0  # 1.0 to 3.0
                falloff = 1.0 - np.power(normalized_dist, power)
            else:
                # Smooth falloff (soft brush)
                power = 0.4 + brush_hardness  # 0.4 to 0.9
                falloff = 1.0 - np.power(normalized_dist, power)
            
            falloff = np.clip(falloff, 0, 1)
        
        alpha = (falloff * brush_strength) * mask
        
        # Reshape pixel buffer to 2D for easy indexing
        pixels_2d = _pixel_buffer.reshape((height, width, 4))
        
        # Extract brush region
        region = pixels_2d[y_min:y_max, x_min:x_max, :3]
        
        # Vectorized blend
        alpha_3d = alpha[:, :, np.newaxis]
        # Convert brush color from sRGB to Linear to match canvas color space
        brush_rgb_linear = np.array(srgb_to_linear(brush_color), dtype=np.float32)
        region[:] = region * (1.0 - alpha_3d) + brush_rgb_linear * alpha_3d
        
        # Only write to canvas when requested
        if write_to_canvas:
            canvas_image.pixels.foreach_set(_pixel_buffer)
        
        return True
        
    except Exception as e:
        print(f"Paint error: {e}")
        return False


def update_3d_viewport():
    """Force 3D viewport to show updated texture - Blender 4.x method"""
    global _canvas_image, _sphere
    
    if _canvas_image:
        # Mark image as updated
        _canvas_image.update()
        # Pack/unpack trick forces GPU reload
        if _canvas_image.packed_file:
            _canvas_image.unpack(method='USE_ORIGINAL')
        # Update tag for dependency graph
        _canvas_image.update_tag()
    
    # Force material update
    if _sphere and _sphere.active_material:
        _sphere.active_material.update_tag()
        # Touch the node tree to trigger refresh
        if _sphere.active_material.use_nodes:
            _sphere.active_material.node_tree.update_tag()
    
    # Force depsgraph update
    if bpy.context.view_layer:
        bpy.context.view_layer.update()


# ============================================================================
# MOUSE EVENT HANDLER
# ============================================================================

def mouse_event_handler(context, event):
    """Handle mouse events for continuous painting with smooth brush strokes"""
    global _is_painting, _last_mouse_pos, _sphere, _canvas_image
    global _paint_throttle_counter, _paint_throttle_interval
    global _last_stable_u
    
    # Update mouse position for cursor drawing
    _last_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
    
    # Only in 3D viewport
    if context.area.type != 'VIEW_3D':
        return
    
    # LEFT MOUSE BUTTON
    if event.type == 'LEFTMOUSE':
        if event.value == 'PRESS':
            # Start painting - NEW STROKE
            _is_painting = True
            _last_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            _paint_throttle_counter = 0
            _last_stable_u = 0.5  # Reset for new stroke
            paint_at_mouse(context, event, is_stroke_start=True)
            
        elif event.value == 'RELEASE':
            # Stop painting - END STROKE
            if _is_painting:
                paint_at_mouse(context, event, is_stroke_end=True)
            _is_painting = False
            _last_mouse_pos = None
            _paint_throttle_counter = 0
    
    # MOUSE MOVE while painting - CONTINUOUS STROKE (no throttle!)
    elif event.type == 'MOUSEMOVE' and _is_painting:
        paint_at_mouse(context, event, is_stroke_continue=True)


def paint_at_mouse(context, event, is_stroke_start=False, is_stroke_continue=False, is_stroke_end=False):
    """Paint at current mouse position with SMOOTH interpolation for continuous brush feel"""
    global _sphere, _canvas_image, _last_paint_uv, _stroke_paint_count, _last_visual_update
    
    # ALWAYS refresh canvas reference - important when loading new HDRIs!
    _canvas_image = bpy.data.images.get("HDRI_Canvas")
    
    if not _sphere or not _canvas_image:
        return
    
    try:
        # Get ray from mouse
        region = context.region
        region_3d = context.space_data.region_3d
        mouse_coord = (event.mouse_region_x, event.mouse_region_y)
        
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_coord)
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_coord)
        
        # Find interior surface (second intersection) - now returns exact hit point
        interior_location, face_index, local_hit = find_interior_surface(_sphere, ray_origin, ray_direction)
        
        if interior_location and face_index is not None:
            # Get UV from EXACT hit point (more accurate than face center!)
            uv_coord = get_uv_from_hit_point(_sphere, interior_location)
            
            if uv_coord:
                # Get Blender brush directly from tool_settings (NOT from bpy.data!)
                try:
                    # Get the LIVE brush reference from scene tool_settings
                    ts = bpy.context.scene.tool_settings
                    ip = ts.image_paint
                    brush = ip.brush
                    
                    if not brush:
                        print("❌ No active Image Paint brush!")
                        return
                    
                    # Check for unified paint settings (size)
                    ups = ts.unified_paint_settings
                    if ups.use_unified_size:
                        brush_radius = int(ups.size)
                    else:
                        brush_radius = int(brush.size)
                    
                    # Check for unified strength
                    if ups.use_unified_strength:
                        brush_strength = ups.strength
                    else:
                        brush_strength = brush.strength
                    
                    brush_color = tuple(brush.color[:3])
                    brush_hardness = brush.hardness
                    
                    # Debug output (only at stroke start)
                    if is_stroke_start:
                        unified_info = f"unified_size={ups.use_unified_size}, unified_strength={ups.use_unified_strength}"
                        print(f"🎨 Brush '{brush.name}': radius={brush_radius}px, strength={brush_strength:.2f}, hardness={brush_hardness:.2f} ({unified_info})")
                    
                except Exception as e:
                    print(f"❌ Failed to get brush settings: {e}")
                    import traceback
                    traceback.print_exc()
                    return
                
                # Smooth interpolation for connected brush strokes (like Blender Image Paint)
                uv_coords_to_paint = []
                
                if is_stroke_start or _last_paint_uv is None:
                    uv_coords_to_paint = [uv_coord]
                    _stroke_paint_count = 0
                else:
                    # Interpolate based on distance to get smooth lines
                    uv_coords_to_paint = interpolate_uv(_last_paint_uv, uv_coord, steps=3)
                
                # Paint all interpolated positions
                for i, uv in enumerate(uv_coords_to_paint):
                    is_first = (is_stroke_start and i == 0)
                    is_last = (i == len(uv_coords_to_paint) - 1)
                    paint_at_uv(
                        _canvas_image,
                        uv,
                        brush_radius,
                        brush_color,
                        brush_strength,
                        brush_hardness,  # Pass hardness for falloff curve
                        is_stroke_start=is_first,
                        write_to_canvas=is_last  # Only write once at end
                    )
                    _stroke_paint_count += 1
                
                # Remember position
                _last_paint_uv = uv_coord
                
                # THROTTLED VISUAL UPDATE - every 50ms for smooth feedback without lag
                current_time = time.time()
                should_update = (current_time - _last_visual_update) >= _visual_update_interval
                
                if is_stroke_end or should_update:
                    update_3d_viewport()
                    _last_visual_update = current_time
                    
                    if is_stroke_end:
                        _last_paint_uv = None
    
    except Exception as e:
        print(f"Paint error: {e}")


# ============================================================================
# DRAW HANDLER (for continuous event capture)
# ============================================================================

def draw_handler_callback():
    """Draw handler to show brush cursor - optimized to reduce lag"""
    global _last_mouse_pos, _sphere, _paint_handler_active
    global _last_cursor_pos, _last_brush_radius, _cursor_batch, _cursor_shader
    
    if not _paint_handler_active or not _last_mouse_pos:
        return
    
    # Get current context
    context = bpy.context
    if not context.area or context.area.type != 'VIEW_3D':
        return
    
    # Get brush radius from Blender - check unified paint settings!
    try:
        ts = bpy.context.scene.tool_settings
        ip = ts.image_paint
        ups = ts.unified_paint_settings
        
        if ip.brush:
            # Use unified size if enabled, otherwise brush size
            # Note: brush.size IS the radius (not diameter)
            if ups.use_unified_size:
                brush_radius_px = int(ups.size)
            else:
                brush_radius_px = int(ip.brush.size)
        else:
            brush_radius_px = 50
    except Exception as e:
        print(f"Cursor brush error: {e}")
        brush_radius_px = 50
    
    # Update cursor if mouse moved OR radius changed
    radius_changed = (_last_brush_radius != brush_radius_px)
    mouse_moved = (_last_cursor_pos != _last_mouse_pos)
    
    if mouse_moved or radius_changed or _cursor_batch is None:
        _last_cursor_pos = _last_mouse_pos
        _last_brush_radius = brush_radius_px
        
        # Create circle vertices
        segments = 32
        vertices = []
        center_x, center_y = _last_mouse_pos
        
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            x = center_x + brush_radius_px * math.cos(angle)
            y = center_y + brush_radius_px * math.sin(angle)
            vertices.append((x, y))
        
        # Cache shader and batch
        _cursor_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        _cursor_batch = batch_for_shader(_cursor_shader, 'LINE_STRIP', {"pos": vertices})
    
    # Draw cached cursor
    if _cursor_batch and _cursor_shader:
        try:
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(2.0)
            
            _cursor_shader.bind()
            _cursor_shader.uniform_float("color", (1.0, 1.0, 1.0, 0.8))
            _cursor_batch.draw(_cursor_shader)
            
            gpu.state.line_width_set(1.0)
            gpu.state.blend_set('NONE')
        except Exception as e:
            # Silently ignore errors
            pass


# ============================================================================
# ENABLE/DISABLE
# ============================================================================

def enable_continuous_paint(context):
    """
    Enable continuous painting with REAL UV from mesh (sphere_project)
    Uses modal operator for event capture with PASS_THROUGH
    """
    global _paint_handler_active, _draw_handler, _sphere, _canvas_image
    
    # Find objects
    _sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
    _canvas_image = bpy.data.images.get("HDRI_Canvas")
    
    if not _sphere or not _canvas_image:
        print("❌ Sphere or canvas not found!")
        return False
    
    # DON'T change mode - let user stay in whatever mode they want!
    # The modal will handle 3D viewport painting independently
    
    # Register draw handler for visual feedback
    if _draw_handler is None:
        _draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_handler_callback,
            (),
            'WINDOW',
            'POST_PIXEL'
        )
    
    _paint_handler_active = True
    
    # Start modal operator for event capture
    bpy.ops.hdri_studio.continuous_paint_modal('INVOKE_DEFAULT')
    
    print("✅ Continuous paint ENABLED!")
    print("   - LEFT CLICK + DRAG to paint in 3D viewport")
    print("   - 2D paint works independently in IMAGE_EDITOR")
    print("   - Press ESC to exit")
    return True


def disable_continuous_paint():
    """Disable continuous painting mode"""
    global _paint_handler_active, _draw_handler, _is_painting
    
    # Stop painting
    _is_painting = False
    
    # Remove draw handler
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None
    
    _paint_handler_active = False
    
    print("Continuous paint DISABLED")


# ============================================================================
# OPERATORS
# ============================================================================

class HDRI_OT_continuous_paint_enable(bpy.types.Operator):
    """Enable continuous painting (KeyShot-style)"""
    bl_idname = "hdri_studio.continuous_paint_enable"
    bl_label = "Enable Continuous Paint"
    bl_description = "Non-blocking continuous painting - just click and drag!"
    
    def execute(self, context):
        if enable_continuous_paint(context):
            self.report({'INFO'}, "Continuous paint enabled - LEFT CLICK + DRAG!")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to enable - create sphere and canvas first")
            return {'CANCELLED'}


class HDRI_OT_continuous_paint_disable(bpy.types.Operator):
    """Disable continuous painting"""
    bl_idname = "hdri_studio.continuous_paint_disable"
    bl_label = "Disable Continuous Paint"
    bl_description = "Stop continuous painting mode"
    
    def execute(self, context):
        disable_continuous_paint()
        self.report({'INFO'}, "Continuous paint disabled")
        return {'FINISHED'}


# ============================================================================
# EVENT MONITORING MODAL (captures mouse events)
# ============================================================================

class HDRI_OT_continuous_paint_modal(bpy.types.Operator):
    """Modal operator to capture mouse events (runs in background)"""
    bl_idname = "hdri_studio.continuous_paint_modal"
    bl_label = "Continuous Paint Modal"
    bl_description = "Background event capture for continuous painting"
    
    _timer = None
    
    def modal(self, context, event):
        global _paint_handler_active, _is_painting
        
        # Stop if disabled
        if not _paint_handler_active:
            self.cancel(context)
            return {'CANCELLED'}
        
        # Timer event - keep modal alive
        if event.type == 'TIMER':
            return {'PASS_THROUGH'}
        
        # ESC to cancel
        if event.type == 'ESC' and event.value == 'PRESS':
            self.cancel(context)
            disable_continuous_paint()
            return {'CANCELLED'}
        
        # ONLY handle events in 3D VIEW - everything else passes through!
        if not context.area or context.area.type != 'VIEW_3D':
            return {'PASS_THROUGH'}
        
        # Check if mouse is over the sphere before consuming event
        sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
        if not sphere:
            return {'PASS_THROUGH'}
        
        # LEFT MOUSE PRESS - check if clicking on sphere
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Test if ray hits sphere
            region = context.region
            region_3d = context.space_data.region_3d
            mouse_coord = (event.mouse_region_x, event.mouse_region_y)
            
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_coord)
            ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_coord)
            
            # Check if ray hits sphere (now returns 3 values)
            location, face_index, _ = find_interior_surface(sphere, ray_origin, ray_direction)
            
            if location is not None:
                # Ray hits sphere - START painting and consume event
                mouse_event_handler(context, event)
                return {'RUNNING_MODAL'}
            else:
                # Ray missed sphere - let other tools handle it (selection, etc)
                return {'PASS_THROUGH'}
        
        # LEFT MOUSE RELEASE - always handle if we were painting
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if _is_painting:
                mouse_event_handler(context, event)
            return {'PASS_THROUGH'}  # Always pass through release
        
        # MOUSE MOVE while painting
        elif event.type == 'MOUSEMOVE' and _is_painting:
            mouse_event_handler(context, event)
            return {'PASS_THROUGH'}  # Pass through to allow viewport updates
        
        # Everything else passes through
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        # Add timer to keep modal alive without blocking
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            self._timer = None


# ============================================================================
# REGISTRATION
# ============================================================================

classes = [
    HDRI_OT_continuous_paint_enable,
    HDRI_OT_continuous_paint_disable,
    HDRI_OT_continuous_paint_modal,  # Using REAL mesh UV coordinates!
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("Continuous paint handler registered (MATHEMATICAL UV - HEUREKA version)")


def unregister():
    disable_continuous_paint()
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Continuous paint handler unregistered")
