"""Debug Paint Tracker - UV mapping accuracy testing"""

import bpy
import math

tracking_data = {'enabled': False, 'test_points': [], 'clicks': []}

def draw_numbered_targets_on_canvas(canvas_image):
    """Draw BIG numbered targets with colors - VERY visible!"""
    width, height = canvas_image.size
    pixels = list(canvas_image.pixels)
    
    # Clustered test points in center region for better sphere visibility
    # NO corrections, just raw UV positions - all in 0.2-0.8 range
    test_points = [
        (0.50, 0.50, 1, (1.0, 0.0, 0.0)),    # CENTER - RED
        (0.50, 0.70, 2, (1.0, 0.5, 0.0)),    # TOP-CENTER - ORANGE
        (0.70, 0.50, 3, (1.0, 1.0, 0.0)),    # RIGHT-CENTER - YELLOW
        (0.50, 0.30, 4, (0.0, 1.0, 0.0)),    # BOTTOM-CENTER - GREEN
        (0.30, 0.50, 5, (0.0, 1.0, 1.0)),    # LEFT-CENTER - CYAN
        (0.30, 0.70, 6, (0.0, 0.0, 1.0)),    # TOP-LEFT - BLUE
        (0.70, 0.70, 7, (1.0, 0.0, 1.0)),    # TOP-RIGHT - MAGENTA
        (0.70, 0.30, 8, (1.0, 1.0, 1.0)),    # BOTTOM-RIGHT - WHITE
        (0.30, 0.30, 9, (0.3, 0.3, 0.3))     # BOTTOM-LEFT - DARK GRAY (more visible)
    ]
    
    def set_pixel(x, y, r, g, b):
        """Set single pixel with RGB color"""
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 4
            if idx + 3 < len(pixels):
                pixels[idx] = r
                pixels[idx + 1] = g
                pixels[idx + 2] = b
                pixels[idx + 3] = 1.0
    
    def draw_filled_circle(cx, cy, radius, r, g, b):
        """Draw a solid filled circle"""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    set_pixel(cx + dx, cy + dy, r, g, b)
    
    def draw_big_number(cx, cy, number):
        """Draw LARGE number using simple digit patterns"""
        # Numbers as 7x9 pixel patterns (like LED display)
        # BLACK color for visibility on colored background
        
        # Draw black rectangle background for number
        for dy in range(-15, 16):
            for dx in range(-10, 11):
                set_pixel(cx + dx, cy + dy, 0.0, 0.0, 0.0)
        
        # Draw white number on black background
        # Simple filled rectangle representing the number
        size = 8 + number  # Bigger number = bigger size (visual indicator)
        for dy in range(-size, size + 1):
            for dx in range(-size//2, size//2 + 1):
                set_pixel(cx + dx, cy + dy, 1.0, 1.0, 1.0)
    
    tracking_data['test_points'] = []
    print("\n" + "="*70)
    print("DRAWING DEBUG TARGETS ON CANVAS - RAW UV COORDINATES")
    print("="*70)
    print("\nNo corrections applied - pure equirectangular mapping")
    print("Click them in this order on the SPHERE:")
    print("")
    
    for u, v, number, color in test_points:
        # DIRECT MAPPING - NO CORRECTIONS
        # Just convert UV to pixel coordinates
        # Standard equirectangular: U wraps horizontally, V goes bottom to top
        # But in Blender images, pixel (0,0) is TOP-LEFT
        # So: V=0 → top, V=1 → bottom (no flip needed!)
        pixel_x = int(u * width)
        pixel_y = int(v * height)  # Direct mapping, no flip
        
        # Draw LARGE colored circle (radius 50)
        draw_filled_circle(pixel_x, pixel_y, 50, color[0], color[1], color[2])
        
        # Draw smaller ring (radius 40)
        draw_filled_circle(pixel_x, pixel_y, 40, 0.0, 0.0, 0.0)
        
        # Draw inner colored circle (radius 35)
        draw_filled_circle(pixel_x, pixel_y, 35, color[0], color[1], color[2])
        
        # Draw crosshair
        for i in range(-30, 31):
            set_pixel(pixel_x + i, pixel_y, 0.0, 0.0, 0.0)  # Horizontal
            set_pixel(pixel_x, pixel_y + i, 0.0, 0.0, 0.0)  # Vertical
        
        # Draw BIG number above target
        draw_big_number(pixel_x, pixel_y - 70, number)
        
        # Store test point
        tracking_data['test_points'].append({
            'number': number,
            'uv': (u, v),
            'pixel': (pixel_x, pixel_y),
            'color': color
        })
        
        # Print with color name for easy identification
        color_names = {1: "RED", 2: "ORANGE", 3: "YELLOW", 4: "GREEN", 5: "CYAN", 
                      6: "BLUE", 7: "MAGENTA", 8: "WHITE", 9: "GRAY"}
        print(f"  [{number}] {color_names[number]:8s} - UV({u:.2f}, {v:.2f}) Pixel({pixel_x:4d}, {pixel_y:4d})")
    
    # UPDATE IMAGE!
    canvas_image.pixels[:] = pixels
    canvas_image.update()
    
    print("\n" + "="*70)
    print("TARGETS DRAWN! Now click 'Start Tracking' and paint them in order 1→9")
    print("="*70 + "\n")
    
    return len(test_points)

def start_tracking():
    tracking_data['enabled'] = True
    tracking_data['clicks'] = []
    print("\n" + "="*70)
    print("🎯 TRACKING STARTED")
    print("="*70)
    print("Now:")
    print("  1. Click '3D Paint' button above")
    print("  2. LEFT CLICK on each numbered target (1→9)")
    print("  3. Press ESC to exit paint mode")
    print("  4. Click 'Stop & Analyze' to see results")
    print("="*70 + "\n")

def stop_tracking():
    tracking_data['enabled'] = False
    print("\n" + "="*70)
    print("TRACKING RESULTS")
    print("="*70)
    print(f"Total clicks recorded: {len(tracking_data['clicks'])}")
    print("")
    
    if len(tracking_data['clicks']) == 0:
        print("⚠️  NO CLICKS RECORDED!")
        print("   Make sure you:")
        print("   1. Clicked 'Enable Tracking' button")
        print("   2. Clicked '3D Paint' button")
        print("   3. LEFT CLICK on targets in 3D viewport")
        print("")
    else:
        for i, click in enumerate(tracking_data['clicks'], 1):
            print(f"  Click {i}: UV({click['uv'][0]:.3f}, {click['uv'][1]:.3f})")
    
    print("="*70 + "\n")

def record_paint_click(uv_coord, pixel_coord):
    if tracking_data['enabled']:
        tracking_data['clicks'].append({'uv': uv_coord, 'pixel': pixel_coord})
        click_num = len(tracking_data['clicks'])
        print(f"✅ Click {click_num}: UV({uv_coord[0]:.3f}, {uv_coord[1]:.3f}) Pixel({pixel_coord[0]}, {pixel_coord[1]})")
    else:
        print(f"⚠️  Tracking disabled! Click 'Enable Tracking' first. UV: {uv_coord}")

class HDRI_OT_draw_debug_points(bpy.types.Operator):
    bl_idname = "hdri_studio.draw_debug_points"
    bl_label = "Draw Test Points"
    bl_description = "Draw 9 numbered test points on the HDRI canvas for calibration"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("\n🎯 Drawing test points...")
        canvas_image = bpy.data.images.get("HDRI_Canvas")
        
        if not canvas_image:
            print("❌ HDRI_Canvas not found!")
            self.report({'ERROR'}, "Create canvas first!")
            return {'CANCELLED'}
        
        print(f"✅ Found canvas: {canvas_image.name} ({canvas_image.size[0]}x{canvas_image.size[1]})")
        
        try:
            draw_numbered_targets_on_canvas(canvas_image)
            self.report({'INFO'}, "Drew test points!")
            print("✅ Test points drawn successfully!")
        except Exception as e:
            print(f"❌ Error drawing test points: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class HDRI_OT_start_debug_tracking(bpy.types.Operator):
    bl_idname = "hdri_studio.start_debug_tracking"
    bl_label = "Start Tracking"
    bl_description = "Begin tracking UV coordinates when you click on the sphere"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        start_tracking()
        self.report({'INFO'}, "Tracking ON - Now click '3D Paint' button!")
        return {'FINISHED'}

class HDRI_OT_stop_debug_tracking(bpy.types.Operator):
    bl_idname = "hdri_studio.stop_debug_tracking"
    bl_label = "Stop & Analyze"
    bl_description = "Stop tracking and analyze UV coordinate accuracy"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        stop_tracking()
        self.report({'INFO'}, "Check console!")
        return {'FINISHED'}

classes = [HDRI_OT_draw_debug_points, HDRI_OT_start_debug_tracking, HDRI_OT_stop_debug_tracking]

def register():
    print("\n🔧 DEBUG_PAINT_TRACKER: Starting registration...")
    for cls in classes:
        print(f"   Registering: {cls.bl_idname} ({cls.__name__})")
        bpy.utils.register_class(cls)
    print("✅ DEBUG_PAINT_TRACKER: All operators registered!")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
