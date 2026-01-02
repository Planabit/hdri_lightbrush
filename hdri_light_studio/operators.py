"""
Operators Module
Canvas creation and management operators for HDRI Light Studio
"""

import bpy
from bpy.types import Operator
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class HDRI_OT_create_canvas(Operator):
    """Create new HDRI canvas"""
    bl_idname = "hdri_studio.create_canvas"
    bl_label = "Create Canvas"
    bl_description = "Create a new HDRI canvas for editing"
    
    def execute(self, context):
        props = context.scene.hdri_studio
        
        # Set canvas dimensions - 2K = 2048x1024, 4K = 4096x2048
        if props.canvas_size == '2K':
            width, height = 2048, 1024
        else:
            width, height = 4096, 2048
        
        # Create canvas image
        self.create_canvas_image(context, width, height)
        
        # Setup viewport layout
        self.setup_viewport_layout(context)
        
        # Mark canvas as active
        props.canvas_active = True
        
        # Redraw UI
        for area in context.screen.areas:
            area.tag_redraw()
        
        self.report({'INFO'}, f"Canvas created: {width}x{height}")
        return {'FINISHED'}
    
    def create_canvas_image(self, context, width, height):
        """Create Blender image for canvas"""
        image_name = "HDRI_Canvas"
        
        # Remove existing image
        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[image_name])
        
        # Create new image
        canvas_image = bpy.data.images.new(image_name, width, height, alpha=True, float_buffer=True)
        
        # Initialize with black background
        pixels = np.zeros((height, width, 4), dtype=np.float32)
        pixels[:, :, 3] = 1.0  # Full alpha
        canvas_image.pixels[:] = pixels.flatten()
        canvas_image.update()
    
    def setup_viewport_layout(self, context):
        """Split viewport and setup Image Editor for canvas display"""
        # Find 3D viewport
        view3d_area = None
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                view3d_area = area
                break
        
        if not view3d_area:
            return
        
        # Count viewports before split
        view3d_count = len([a for a in context.screen.areas if a.type == 'VIEW_3D'])
        
        # Split viewport
        with context.temp_override(area=view3d_area):
            bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
        
        # Find new viewport (rightmost)
        view3d_areas = [a for a in context.screen.areas if a.type == 'VIEW_3D']
        if len(view3d_areas) > view3d_count:
            view3d_areas.sort(key=lambda a: a.x)
            rightmost = view3d_areas[-1]
            
            # Convert to Image Editor
            rightmost.type = 'IMAGE_EDITOR'
            
            # Configure Image Editor
            for space in rightmost.spaces:
                if space.type == 'IMAGE_EDITOR':
                    if "HDRI_Canvas" in bpy.data.images:
                        space.image = bpy.data.images["HDRI_Canvas"]
                    space.mode = 'PAINT'
                    break


class HDRI_OT_clear_canvas(Operator):
    """Clear HDRI canvas to black"""
    bl_idname = "hdri_studio.clear_canvas"
    bl_label = "Clear Canvas"
    bl_description = "Clear the canvas to black"
    
    def execute(self, context):
        if "HDRI_Canvas" not in bpy.data.images:
            self.report({'ERROR'}, "No HDRI canvas found")
            return {'CANCELLED'}
        
        canvas_image = bpy.data.images["HDRI_Canvas"]
        width, height = canvas_image.size[0], canvas_image.size[1]
        
        # Clear to black
        pixels = np.zeros((height * width * 4), dtype=np.float32)
        pixels[3::4] = 1.0  # Full alpha
        canvas_image.pixels[:] = pixels
        canvas_image.update()
        
        # Redraw
        for area in context.screen.areas:
            area.tag_redraw()
        
        self.report({'INFO'}, "Canvas cleared")
        return {'FINISHED'}


class HDRI_OT_add_light(Operator):
    """Add light shape to canvas"""
    bl_idname = "hdri_studio.add_light"
    bl_label = "Add Light"
    bl_description = "Add a light shape to the canvas"
    
    def execute(self, context):
        if "HDRI_Canvas" not in bpy.data.images:
            self.report({'ERROR'}, "No HDRI canvas found")
            return {'CANCELLED'}
        
        props = context.scene.hdri_studio
        canvas_image = bpy.data.images["HDRI_Canvas"]
        width, height = canvas_image.size[0], canvas_image.size[1]
        
        # Get current pixels
        pixels = np.array(canvas_image.pixels[:]).reshape(height, width, 4)
        
        # Get light color
        if props.use_temperature:
            from .utils import kelvin_to_rgb
            color = kelvin_to_rgb(props.color_temperature)
        else:
            # Use brush color from paint settings
            ts = context.tool_settings
            brush = ts.image_paint.brush if ts.image_paint else None
            color = brush.color[:3] if brush else (1.0, 1.0, 1.0)
        
        # Add light at center
        center_x, center_y = width // 2, height // 2
        size = int(props.light_size)
        intensity = props.light_intensity
        
        # Create light based on shape
        if props.light_shape == 'CIRCLE':
            self.add_circle_light(pixels, center_x, center_y, size, color, intensity)
        elif props.light_shape == 'SQUARE':
            self.add_square_light(pixels, center_x, center_y, size, color, intensity)
        else:  # RECTANGLE
            self.add_rectangle_light(pixels, center_x, center_y, size, color, intensity)
        
        # Update canvas
        canvas_image.pixels[:] = pixels.flatten()
        canvas_image.update()
        
        # Redraw
        for area in context.screen.areas:
            area.tag_redraw()
        
        self.report({'INFO'}, f"Added {props.light_shape.lower()} light")
        return {'FINISHED'}
    
    def add_circle_light(self, pixels, cx, cy, size, color, intensity):
        """Add circular light"""
        height, width = pixels.shape[:2]
        radius = size // 2
        
        for y in range(max(0, cy - radius), min(height, cy + radius)):
            for x in range(max(0, cx - radius), min(width, cx + radius)):
                dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                if dist < radius:
                    falloff = 1.0 - (dist / radius)
                    pixels[y, x, 0] = min(1.0, pixels[y, x, 0] + color[0] * intensity * falloff)
                    pixels[y, x, 1] = min(1.0, pixels[y, x, 1] + color[1] * intensity * falloff)
                    pixels[y, x, 2] = min(1.0, pixels[y, x, 2] + color[2] * intensity * falloff)
    
    def add_square_light(self, pixels, cx, cy, size, color, intensity):
        """Add square light"""
        height, width = pixels.shape[:2]
        half = size // 2
        
        for y in range(max(0, cy - half), min(height, cy + half)):
            for x in range(max(0, cx - half), min(width, cx + half)):
                pixels[y, x, 0] = min(1.0, pixels[y, x, 0] + color[0] * intensity)
                pixels[y, x, 1] = min(1.0, pixels[y, x, 1] + color[1] * intensity)
                pixels[y, x, 2] = min(1.0, pixels[y, x, 2] + color[2] * intensity)
    
    def add_rectangle_light(self, pixels, cx, cy, size, color, intensity):
        """Add rectangular light (2:1 aspect)"""
        height, width = pixels.shape[:2]
        half_w = size // 2
        half_h = size // 4
        
        for y in range(max(0, cy - half_h), min(height, cy + half_h)):
            for x in range(max(0, cx - half_w), min(width, cx + half_w)):
                pixels[y, x, 0] = min(1.0, pixels[y, x, 0] + color[0] * intensity)
                pixels[y, x, 1] = min(1.0, pixels[y, x, 1] + color[1] * intensity)
                pixels[y, x, 2] = min(1.0, pixels[y, x, 2] + color[2] * intensity)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

classes = [
    HDRI_OT_create_canvas,
    HDRI_OT_clear_canvas,
    HDRI_OT_add_light,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
