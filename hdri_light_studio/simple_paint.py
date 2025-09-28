"""
Simple Paint Setup
Use Blender's built-in texture painting system
"""

import bpy
from bpy.types import Operator

class HDRI_OT_simple_paint_setup(Operator):
    """Setup simple painting using Blender's texture paint"""
    bl_idname = "hdri_studio.simple_paint_setup"
    bl_label = "Simple Paint Setup"
    bl_description = "Setup simple texture painting on HDRI canvas"
    
    def execute(self, context):
        try:
            # Ensure we have canvas image
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "Create canvas first!")
                return {'CANCELLED'}
            
            canvas_image = bpy.data.images["HDRI_Canvas"]
            
            # Set Image Editor to paint mode
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    for space in area.spaces:
                        if space.type == 'IMAGE_EDITOR':
                            space.image = canvas_image
                            space.mode = 'PAINT'
                            space.show_gizmo = True
                            area.tag_redraw()
                            print("Image Editor set to paint mode")
            
            # Instructions for user
            self.report({'INFO'}, "Canvas ready! Use Image Editor paint tools or switch to Texture Paint workspace")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Setup failed: {e}")
            return {'CANCELLED'}

class HDRI_OT_paint_brush_stroke(Operator):
    """Single brush stroke operator"""
    bl_idname = "hdri_studio.paint_brush_stroke"  
    bl_label = "Paint Stroke"
    bl_description = "Paint a single stroke on canvas"
    
    def execute(self, context):
        try:
            if "HDRI_Canvas" not in bpy.data.images:
                return {'CANCELLED'}
                
            canvas_image = bpy.data.images["HDRI_Canvas"]
            props = context.scene.hdri_studio
            
            # Get mouse position (this would be called from modal)
            # For now, paint at center as example
            width, height = canvas_image.size
            center_x = width // 2
            center_y = height // 2
            
            # Get color
            if props.use_temperature:
                from .utils import kelvin_to_rgb
                color = kelvin_to_rgb(props.color_temperature)
            else:
                color = props.brush_color[:3]
            
            # Paint at center
            self.paint_at_pixel(canvas_image, center_x, center_y, props.brush_size, color, props.brush_intensity)
            
            # Update world
            from .operators import update_world_hdri
            update_world_hdri(context)
            
            return {'FINISHED'}
            
        except Exception as e:
            print(f"Paint stroke failed: {e}")
            return {'CANCELLED'}
    
    def paint_at_pixel(self, image, x, y, brush_size, color, intensity):
        """Paint at specific pixel coordinates"""
        try:
            width, height = image.size
            pixels = list(image.pixels)
            
            radius = brush_size // 2
            
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px = x + dx
                    py = y + dy
                    
                    if 0 <= px < width and 0 <= py < height:
                        distance = (dx*dx + dy*dy) ** 0.5
                        if distance <= radius:
                            falloff = max(0, 1.0 - (distance / radius)) if radius > 0 else 1.0
                            alpha = intensity * falloff
                            
                            idx = (py * width + px) * 4
                            if idx + 3 < len(pixels):
                                pixels[idx] = (1 - alpha) * pixels[idx] + alpha * color[0]
                                pixels[idx + 1] = (1 - alpha) * pixels[idx + 1] + alpha * color[1]  
                                pixels[idx + 2] = (1 - alpha) * pixels[idx + 2] + alpha * color[2]
            
            image.pixels[:] = pixels
            image.update()
            
        except Exception as e:
            print(f"Pixel painting failed: {e}")

def register():
    bpy.utils.register_class(HDRI_OT_simple_paint_setup)
    bpy.utils.register_class(HDRI_OT_paint_brush_stroke)

def unregister():
    bpy.utils.unregister_class(HDRI_OT_paint_brush_stroke)
    bpy.utils.unregister_class(HDRI_OT_simple_paint_setup)