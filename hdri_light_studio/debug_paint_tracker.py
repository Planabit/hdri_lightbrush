"""Debug Paint Tracker - UV mapping accuracy testing"""

import bpy
import math

tracking_data = {'enabled': False, 'test_points': [], 'clicks': []}

def draw_numbered_targets_on_canvas(canvas_image):
    """Draw BIG numbered targets with colors - VERY visible!"""
    width, height = canvas_image.size
    pixels = list(canvas_image.pixels)
    
    # 9 test points with BRIGHT colors
    test_points = [
        (0.5, 0.5, 1, (1.0, 0.0, 0.0)),    # CENTER - RED
        (0.5, 0.75, 2, (1.0, 0.5, 0.0)),   # TOP - ORANGE
        (0.75, 0.5, 3, (1.0, 1.0, 0.0)),   # RIGHT - YELLOW
        (0.5, 0.25, 4, (0.0, 1.0, 0.0)),   # BOTTOM - GREEN
        (0.25, 0.5, 5, (0.0, 1.0, 1.0)),   # LEFT - CYAN
        (0.25, 0.75, 6, (0.0, 0.0, 1.0)),  # TOP-LEFT - BLUE
        (0.75, 0.75, 7, (1.0, 0.0, 1.0)),  # TOP-RIGHT - MAGENTA
        (0.75, 0.25, 8, (1.0, 1.0, 1.0)),  # BOTTOM-RIGHT - WHITE
        (0.25, 0.25, 9, (0.8, 0.8, 0.8))   # BOTTOM-LEFT - GRAY
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
    print("DRAWING DEBUG TARGETS ON CANVAS")
    print("="*70)
    print("\nClick them in this order on the HEMISPHERE:")
    print("")
    
    for u, v, number, color in test_points:
        pixel_x = int(u * width)
        pixel_y = int((1.0 - v) * height)
        
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
    print("TRACKING STARTED")

def stop_tracking():
    tracking_data['enabled'] = False
    print("TRACKING RESULTS:")
    for i, click in enumerate(tracking_data['clicks'], 1):
        print(f"  Click {i}: UV({click['uv'][0]:.3f}, {click['uv'][1]:.3f})")

def record_paint_click(uv_coord, pixel_coord):
    if tracking_data['enabled']:
        tracking_data['clicks'].append({'uv': uv_coord, 'pixel': pixel_coord})
        print(f"Recorded click {len(tracking_data['clicks'])}: UV({uv_coord[0]:.3f}, {uv_coord[1]:.3f})")

class HDRI_OT_draw_debug_points(bpy.types.Operator):
    bl_idname = "hdri_studio.draw_debug_points"
    bl_label = "Draw Test Points"
    def execute(self, context):
        canvas_image = bpy.data.images.get("HDRI_Canvas")
        if canvas_image:
            draw_numbered_targets_on_canvas(canvas_image)
            self.report({'INFO'}, "Drew test points!")
        return {'FINISHED'}

class HDRI_OT_start_debug_tracking(bpy.types.Operator):
    bl_idname = "hdri_studio.start_debug_tracking"
    bl_label = "Start Tracking"
    def execute(self, context):
        start_tracking()
        self.report({'INFO'}, "Tracking ON - Now click '3D Paint' button!")
        return {'FINISHED'}

class HDRI_OT_stop_debug_tracking(bpy.types.Operator):
    bl_idname = "hdri_studio.stop_debug_tracking"
    bl_label = "Stop & Analyze"
    def execute(self, context):
        stop_tracking()
        self.report({'INFO'}, "Check console!")
        return {'FINISHED'}

classes = [HDRI_OT_draw_debug_points, HDRI_OT_start_debug_tracking, HDRI_OT_stop_debug_tracking]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
