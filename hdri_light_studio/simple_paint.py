"""
Simple Paint Setup
Use Blender's built-in texture painting system
"""

import bpy
from bpy.types import Operator

class HDRI_OT_create_canvas_and_paint(Operator):
    """Create canvas and setup painting in Image Editor with brush active"""
    bl_idname = "hdri_studio.create_canvas_and_paint"
    bl_label = "Create Canvas & Paint"
    bl_description = "Create HDRI canvas and setup painting with active brush"
    
    def execute(self, context):
        try:
            # Get canvas properties
            props = context.scene.hdri_studio
            
            # Create HDRI image
            canvas_size = props.canvas_size
            size_map = {
                '512': 512, '1024': 1024, '2048': 2048, 
                '4096': 4096, '8192': 8192
            }
            size = size_map.get(canvas_size, 2048)
            
            # Remove existing canvas if any
            if "HDRI_Canvas" in bpy.data.images:
                bpy.data.images.remove(bpy.data.images["HDRI_Canvas"])
            
            # Create new canvas image
            canvas_image = bpy.data.images.new(
                name="HDRI_Canvas",
                width=size,
                height=size//2,  # HDRI aspect ratio 2:1
                alpha=False,
                float_buffer=True
            )
            
            # Set colorspace for HDRI work
            try:
                canvas_image.colorspace_settings.name = 'Linear Rec.709'
            except:
                try:
                    canvas_image.colorspace_settings.name = 'sRGB'
                except:
                    pass
            
            # Mark canvas as active
            props.canvas_active = True
            
            # Split 3D Viewport and create Image Editor
            viewport_area = None
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    viewport_area = area
                    break
            
            if viewport_area:
                # Split the 3D Viewport vertically
                with context.temp_override(area=viewport_area):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
                
                # Find the new area (it will be the rightmost one)
                new_area = None
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D' and area != viewport_area:
                        new_area = area
                        break
                
                # Convert the new area to Image Editor by directly changing type
                if new_area:
                    # Change area type directly
                    new_area.type = 'IMAGE_EDITOR'
                    
                    # Setup the Image Editor for painting
                    for space in new_area.spaces:
                        if space.type == 'IMAGE_EDITOR':
                            space.image = canvas_image
                            space.mode = 'PAINT'
                            space.show_gizmo = True
                            space.show_region_ui = True  # Show brush settings sidebar
                            new_area.tag_redraw()
                            print("Created Image Editor in split area with paint mode")
                            break
            
            # Setup texture paint settings and activate brush
            if context.tool_settings and context.tool_settings.image_paint:
                settings = context.tool_settings.image_paint
                settings.canvas = canvas_image
                
                # Create or get brush
                if not settings.brush:
                    if "HDRI_Brush" in bpy.data.brushes:
                        settings.brush = bpy.data.brushes["HDRI_Brush"]
                    else:
                        # Create new brush for HDRI painting
                        brush = bpy.data.brushes.new("HDRI_Brush", mode='TEXTURE_PAINT')
                        brush.color = (1.0, 1.0, 1.0)  # White for light painting
                        brush.size = 50
                        brush.strength = 1.0
                        brush.blend = 'MIX'
                        settings.brush = brush
                        print("Created HDRI brush")
            
            # NO workspace switch - keep current workspace to preserve addon panel
            
            self.report({'INFO'}, "Canvas created! Paint mode activated in Image Editor")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Canvas creation failed: {e}")
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
            self.paint_at_pixel(canvas_image, center_x, center_y, props.brush_radius, color, props.brush_intensity)
            
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
                            # Square the falloff for softer blend (matches 3D painting)
                            falloff_squared = falloff * falloff
                            alpha = intensity * falloff_squared
                            
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
    bpy.utils.register_class(HDRI_OT_create_canvas_and_paint)
    bpy.utils.register_class(HDRI_OT_paint_brush_stroke)

def unregister():
    bpy.utils.unregister_class(HDRI_OT_paint_brush_stroke)
    bpy.utils.unregister_class(HDRI_OT_create_canvas_and_paint)