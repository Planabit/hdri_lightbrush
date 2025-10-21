"""Debug Paint Tracker - UV mapping accuracy testing tool""""""Debug Paint Tracker for UV mapping accuracy testing"""

import bpy

import bpyimport math

import math

tracking_data = {'enabled': False, 'test_points': [], 'clicks': []}

tracking_data = {

    'enabled': False,def draw_numbered_targets_on_canvas(canvas_image, num_points=9):

    'test_points': [],    width, height = canvas_image.size

    'clicks': []    pixels = list(canvas_image.pixels)

}    test_points = [

        (0.5, 0.5, 1, (1.0, 0.0, 0.0)), (0.5, 0.75, 2, (1.0, 0.5, 0.0)),

def draw_numbered_targets_on_canvas(canvas_image, num_points=9):        (0.75, 0.5, 3, (1.0, 1.0, 0.0)), (0.5, 0.25, 4, (0.0, 1.0, 0.0)),

    """Draw numbered target circles on canvas at known UV positions"""        (0.25, 0.5, 5, (0.0, 1.0, 1.0)), (0.25, 0.75, 6, (0.0, 0.0, 1.0)),

    width, height = canvas_image.size        (0.75, 0.75, 7, (1.0, 0.0, 1.0)), (0.75, 0.25, 8, (1.0, 1.0, 1.0)),

    pixels = list(canvas_image.pixels)        (0.25, 0.25, 9, (0.5, 0.5, 0.5))

        ]

    test_points = [    

        (0.5, 0.5, 1, (1.0, 0.0, 0.0)),    def set_pixel(x, y, color):

        (0.5, 0.75, 2, (1.0, 0.5, 0.0)),        if 0 <= x < width and 0 <= y < height:

        (0.75, 0.5, 3, (1.0, 1.0, 0.0)),            idx = (y * width + x) * 4

        (0.5, 0.25, 4, (0.0, 1.0, 0.0)),            if idx + 3 < len(pixels):

        (0.25, 0.5, 5, (0.0, 1.0, 1.0)),                pixels[idx:idx+4] = color + (1.0,) if len(color) == 3 else color

        (0.25, 0.75, 6, (0.0, 0.0, 1.0)),    

        (0.75, 0.75, 7, (1.0, 0.0, 1.0)),    def draw_circle(cx, cy, radius, color):

        (0.75, 0.25, 8, (1.0, 1.0, 1.0)),        for angle in range(0, 360, 2):

        (0.25, 0.25, 9, (0.5, 0.5, 0.5))            rad = math.radians(angle)

    ]            for r in range(radius - 3, radius + 3):

                    x, y = int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad))

    def set_pixel(x, y, color):                set_pixel(x, y, color)

        if 0 <= x < width and 0 <= y < height:    

            idx = (y * width + x) * 4    tracking_data['test_points'] = []

            if idx + 3 < len(pixels):    print("\n" + "="*60)

                if len(color) == 3:    print("DEBUG TARGETS DRAWN")

                    pixels[idx:idx+4] = color + (1.0,)    for u, v, number, color in test_points:

                else:        pixel_x, pixel_y = int(u * width), int((1.0 - v) * height)

                    pixels[idx:idx+4] = color        draw_circle(pixel_x, pixel_y, 40, color)

            draw_circle(pixel_x, pixel_y, 30, color)

    def draw_circle(cx, cy, radius, color):        for i in range(-20, 21):

        for angle in range(0, 360, 2):            set_pixel(pixel_x + i, pixel_y, color)

            rad = math.radians(angle)            set_pixel(pixel_x, pixel_y + i, color)

            for r in range(radius - 3, radius + 3):        tracking_data['test_points'].append({

                x = int(cx + r * math.cos(rad))            'number': number, 'uv': (u, v), 'pixel': (pixel_x, pixel_y), 'color': color

                y = int(cy + r * math.sin(rad))        })

                set_pixel(x, y, color)        print(f"  [{number}] UV({u:.2f}, {v:.2f}) Pixel({pixel_x:4d}, {pixel_y:4d})")

        canvas_image.pixels[:] = pixels

    tracking_data['test_points'] = []    canvas_image.update()

    print("\nDEBUG TARGETS DRAWN:")    print("="*60 + "\n")

        return len(test_points)

    for u, v, number, color in test_points:

        pixel_x = int(u * width)def start_tracking():

        pixel_y = int((1.0 - v) * height)    tracking_data['enabled'] = True

            tracking_data['clicks'] = []

        draw_circle(pixel_x, pixel_y, 40, color)    print("\nTRACKING STARTED - Click numbered targets in order\n")

        draw_circle(pixel_x, pixel_y, 30, color)

        def stop_tracking():

        for i in range(-20, 21):    tracking_data['enabled'] = False

            set_pixel(pixel_x + i, pixel_y, color)    print("\n" + "="*60)

            set_pixel(pixel_x, pixel_y + i, color)    print("TRACKING RESULTS")

            print("="*60)

        tracking_data['test_points'].append({    clicks, points = tracking_data['clicks'], tracking_data['test_points']

            'number': number,    if not clicks:

            'uv': (u, v),        print("No clicks recorded!")

            'pixel': (pixel_x, pixel_y),        return

            'color': color    for i, click in enumerate(clicks, 1):

        })        target_num = click.get('target_number', i)

                if target_num <= len(points):

        print(f"  [{number}] UV({u:.2f}, {v:.2f}) Pixel({pixel_x:4d}, {pixel_y:4d})")            expected = points[target_num - 1]

                actual_uv, actual_pixel = click.get('uv', (0, 0)), click.get('pixel', (0, 0))

    canvas_image.pixels[:] = pixels            uv_error_x, uv_error_y = actual_uv[0] - expected['uv'][0], actual_uv[1] - expected['uv'][1]

    canvas_image.update()            pixel_error_x, pixel_error_y = actual_pixel[0] - expected['pixel'][0], actual_pixel[1] - expected['pixel'][1]

                pixel_distance = math.sqrt(pixel_error_x**2 + pixel_error_y**2)

    return len(test_points)            print(f"\nClick {i} (Target {target_num}):")

            print(f"  Expected UV: ({expected['uv'][0]:.3f}, {expected['uv'][1]:.3f})")

def start_tracking():            print(f"  Actual UV:   ({actual_uv[0]:.3f}, {actual_uv[1]:.3f})")

    """Enable paint click tracking"""            print(f"  Pixel Error: {pixel_distance:.0f} px {'GOOD' if pixel_distance < 50 else 'OK' if pixel_distance < 100 else 'BAD'}")

    tracking_data['enabled'] = True    print("="*60 + "\n")

    tracking_data['clicks'] = []

    print("\nTRACKING STARTED - Click numbered targets in order")def record_paint_click(uv_coord, pixel_coord, target_number=None):

    if not tracking_data['enabled']:

def stop_tracking():        return

    """Stop tracking and analyze results"""    tracking_data['clicks'].append({

    tracking_data['enabled'] = False        'uv': uv_coord, 'pixel': pixel_coord,

            'target_number': target_number or (len(tracking_data['clicks']) + 1)

    clicks = tracking_data['clicks']    })

    points = tracking_data['test_points']    print(f"Recorded click {len(tracking_data['clicks'])}: UV({uv_coord[0]:.3f}, {uv_coord[1]:.3f}) Pixel{pixel_coord}")

    

    if not clicks:class HDRI_OT_draw_debug_points(bpy.types.Operator):

        print("No clicks recorded!")    bl_idname, bl_label = "hdri_studio.draw_debug_points", "Draw Test Points"

        return    bl_description = "Draw numbered target circles on canvas"

        def execute(self, context):

    print("\nTRACKING RESULTS:")        canvas_image = bpy.data.images.get("HDRI_Canvas")

            if not canvas_image:

    for i, click in enumerate(clicks, 1):            self.report({'ERROR'}, "No HDRI Canvas found!")

        target_num = click.get('target_number', i)            return {'CANCELLED'}

                num_points = draw_numbered_targets_on_canvas(canvas_image)

        if target_num <= len(points):        self.report({'INFO'}, f"Drew {num_points} test points!")

            expected = points[target_num - 1]        return {'FINISHED'}

            actual_uv = click.get('uv', (0, 0))

            actual_pixel = click.get('pixel', (0, 0))class HDRI_OT_start_debug_tracking(bpy.types.Operator):

                bl_idname, bl_label = "hdri_studio.start_debug_tracking", "Start Tracking"

            pixel_error_x = actual_pixel[0] - expected['pixel'][0]    bl_description = "Start tracking paint positions"

            pixel_error_y = actual_pixel[1] - expected['pixel'][1]    def execute(self, context):

            pixel_distance = math.sqrt(pixel_error_x**2 + pixel_error_y**2)        start_tracking()

                    self.report({'INFO'}, "Tracking started!")

            print(f"\nClick {i} (Target {target_num}):")        bpy.ops.hdri_studio.viewport_paint('INVOKE_DEFAULT')

            print(f"  Expected: UV({expected['uv'][0]:.3f}, {expected['uv'][1]:.3f})")        return {'FINISHED'}

            print(f"  Actual:   UV({actual_uv[0]:.3f}, {actual_uv[1]:.3f})")

            print(f"  Error: {pixel_distance:.0f} pixels")class HDRI_OT_stop_debug_tracking(bpy.types.Operator):

    bl_idname, bl_label = "hdri_studio.stop_debug_tracking", "Stop & Analyze"

def record_paint_click(uv_coord, pixel_coord, target_number=None):    bl_description = "Stop tracking and show results"

    """Record a paint click for analysis"""    def execute(self, context):

    if not tracking_data['enabled']:        stop_tracking()

        return        self.report({'INFO'}, "Check console for results!")

            return {'FINISHED'}

    tracking_data['clicks'].append({

        'uv': uv_coord,classes = [HDRI_OT_draw_debug_points, HDRI_OT_start_debug_tracking, HDRI_OT_stop_debug_tracking]

        'pixel': pixel_coord,

        'target_number': target_number or (len(tracking_data['clicks']) + 1)def register():

    })    for cls in classes:

            bpy.utils.register_class(cls)

    print(f"Recorded click {len(tracking_data['clicks'])}: UV({uv_coord[0]:.3f}, {uv_coord[1]:.3f})")

def unregister():

class HDRI_OT_draw_debug_points(bpy.types.Operator):    for cls in reversed(classes):

    bl_idname = "hdri_studio.draw_debug_points"        bpy.utils.unregister_class(cls)

    bl_label = "Draw Test Points"
    bl_description = "Draw numbered target circles on canvas"
    
    def execute(self, context):
        canvas_image = bpy.data.images.get("HDRI_Canvas")
        if not canvas_image:
            self.report({'ERROR'}, "No HDRI Canvas found!")
            return {'CANCELLED'}
        
        num_points = draw_numbered_targets_on_canvas(canvas_image)
        self.report({'INFO'}, f"Drew {num_points} test points!")
        return {'FINISHED'}

class HDRI_OT_start_debug_tracking(bpy.types.Operator):
    bl_idname = "hdri_studio.start_debug_tracking"
    bl_label = "Start Tracking"
    bl_description = "Start tracking paint positions"
    
    def execute(self, context):
        start_tracking()
        self.report({'INFO'}, "Tracking started!")
        bpy.ops.hdri_studio.viewport_paint('INVOKE_DEFAULT')
        return {'FINISHED'}

class HDRI_OT_stop_debug_tracking(bpy.types.Operator):
    bl_idname = "hdri_studio.stop_debug_tracking"
    bl_label = "Stop & Analyze"
    bl_description = "Stop tracking and show results"
    
    def execute(self, context):
        stop_tracking()
        self.report({'INFO'}, "Check console for results!")
        return {'FINISHED'}

classes = [
    HDRI_OT_draw_debug_points,
    HDRI_OT_start_debug_tracking,
    HDRI_OT_stop_debug_tracking
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
