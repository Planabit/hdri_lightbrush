"""
Direct Image Editor Painting
Paint directly in Image Editor like texture painting
"""

import bpy
from bpy.types import Operator
import bmesh
import mathutils
import numpy as np

class HDRI_OT_image_paint_mode(Operator):
    """Switch to Image Editor paint mode"""
    bl_idname = "hdri_studio.image_paint_mode"
    bl_label = "Image Paint Mode"
    bl_description = "Switch Image Editor to paint mode for direct painting"
    
    def execute(self, context):
        try:
            # Find Image Editor area
            image_editor_area = None
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    image_editor_area = area
                    break
            
            if not image_editor_area:
                self.report({'ERROR'}, "No Image Editor found")
                return {'CANCELLED'}
            
            # Switch Image Editor to paint mode
            for space in image_editor_area.spaces:
                if space.type == 'IMAGE_EDITOR':
                    space.mode = 'PAINT'
                    space.show_gizmo = True
                    
                    # Ensure we have the canvas image
                    if "HDRI_Canvas" in bpy.data.images:
                        space.image = bpy.data.images["HDRI_Canvas"]
                    
                    image_editor_area.tag_redraw()
                    break
            
            # Switch to Texture Paint workspace if available
            if "Texture Paint" in bpy.data.workspaces:
                bpy.context.window.workspace = bpy.data.workspaces["Texture Paint"]
                self.report({'INFO'}, "Switched to Texture Paint workspace")
            else:
                self.report({'INFO'}, "Image Editor switched to Paint mode")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to switch to paint mode: {e}")
            return {'CANCELLED'}

class HDRI_OT_direct_paint(Operator):
    """Direct painting on canvas image"""
    bl_idname = "hdri_studio.direct_paint"
    bl_label = "Direct Paint"
    bl_description = "Paint directly on canvas image"
    
    def __init__(self):
        self.drawing = False
        self.last_pos = None
    
    def modal(self, context, event):
        if context.area.type != 'IMAGE_EDITOR':
            return {'CANCELLED'}
            
        props = context.scene.hdri_studio
        
        if event.type == 'MOUSEMOVE':
            if self.drawing and context.space_data.image:
                # Get image editor space
                space = context.space_data
                
                # Convert mouse position to image coordinates
                region = context.region
                rv2d = region.view2d
                
                # Mouse coordinates in region
                mouse_x = event.mouse_region_x
                mouse_y = event.mouse_region_y
                
                # Convert to image space
                image_coords = rv2d.region_to_view(mouse_x, mouse_y)
                
                # Get image dimensions
                image = space.image
                if image:
                    img_width, img_height = image.size
                    
                    # Convert normalized coordinates to pixel coordinates
                    pixel_x = int(image_coords[0] * img_width)
                    pixel_y = int(image_coords[1] * img_height)
                    
                    # Clamp to image bounds
                    pixel_x = max(0, min(pixel_x, img_width - 1))
                    pixel_y = max(0, min(pixel_y, img_height - 1))
                    
                    # Paint on image
                    self.paint_on_image(image, pixel_x, pixel_y, props)
                    
                    # Update world if this is HDRI canvas
                    if image.name == "HDRI_Canvas":
                        from .operators import update_world_hdri
                        update_world_hdri(context)
                        
        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.drawing = True
            elif event.value == 'RELEASE':
                self.drawing = False
                
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}
    
    def paint_on_image(self, image, x, y, props):
        """Paint directly on image pixels"""
        try:
            if props.use_temperature:
                from ..utils import kelvin_to_rgb
                color = kelvin_to_rgb(props.color_temperature)
            else:
                color = props.brush_color[:3]
            
            # Get image dimensions
            width, height = image.size
            brush_size = props.brush_size
            intensity = props.brush_intensity
            
            # Paint circular brush
            radius = brush_size // 2
            pixels = list(image.pixels)  # Get current pixels
            
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px = x + dx
                    py = y + dy
                    
                    if 0 <= px < width and 0 <= py < height:
                        distance = (dx*dx + dy*dy) ** 0.5
                        if distance <= radius:
                            # Calculate falloff
                            falloff = max(0, 1.0 - (distance / radius)) if radius > 0 else 1.0
                            alpha = intensity * falloff
                            
                            # Calculate pixel index (RGBA)
                            idx = (py * width + px) * 4
                            
                            if idx + 3 < len(pixels):
                                # Blend colors
                                pixels[idx] = (1 - alpha) * pixels[idx] + alpha * color[0]       # R
                                pixels[idx + 1] = (1 - alpha) * pixels[idx + 1] + alpha * color[1] # G
                                pixels[idx + 2] = (1 - alpha) * pixels[idx + 2] + alpha * color[2] # B
                                # Alpha stays the same
            
            # Update image
            image.pixels[:] = pixels
            image.update()
            
        except Exception as e:
            print(f"Direct painting failed: {e}")
    
    def invoke(self, context, event):
        if context.area.type == 'IMAGE_EDITOR':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Must be run from Image Editor")
            return {'CANCELLED'}

class HDRI_OT_setup_texture_paint(Operator):
    """Setup proper texture painting environment"""
    bl_idname = "hdri_studio.setup_texture_paint"
    bl_label = "Setup Texture Paint"
    bl_description = "Setup proper texture painting for HDRI editing"
    
    def execute(self, context):
        try:
            # Ensure we have a canvas image
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "No HDRI Canvas found. Create canvas first.")
                return {'CANCELLED'}
            
            canvas_image = bpy.data.images["HDRI_Canvas"]
            
            # Create or get a plane for texture painting
            plane_name = "HDRI_Paint_Plane"
            
            # Remove existing plane if present
            if plane_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[plane_name])
            
            # Create new plane
            bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
            plane = context.active_object
            plane.name = plane_name
            
            # Create material for the plane
            material = bpy.data.materials.new("HDRI_Paint_Material")
            material.use_nodes = True
            
            # Clear default nodes
            material.node_tree.nodes.clear()
            
            # Add Image Texture node
            img_tex = material.node_tree.nodes.new('ShaderNodeTexImage')
            img_tex.image = canvas_image
            img_tex.location = (-400, 300)
            
            # Add Principled BSDF
            bsdf = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 300)
            
            # Add Material Output
            output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
            output.location = (300, 300)
            
            # Link nodes
            material.node_tree.links.new(img_tex.outputs['Color'], bsdf.inputs['Base Color'])
            material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
            
            # Assign material to plane
            plane.data.materials.append(material)
            
            # Switch to Texture Paint mode
            bpy.context.view_layer.objects.active = plane
            bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
            
            # Set paint image
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    for space in area.spaces:
                        if space.type == 'IMAGE_EDITOR':
                            space.image = canvas_image
                            space.mode = 'PAINT'
            
            self.report({'INFO'}, "Texture paint setup complete. Start painting in Image Editor!")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Setup failed: {e}")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(HDRI_OT_image_paint_mode)
    bpy.utils.register_class(HDRI_OT_direct_paint)
    bpy.utils.register_class(HDRI_OT_setup_texture_paint)

def unregister():
    bpy.utils.unregister_class(HDRI_OT_setup_texture_paint)
    bpy.utils.unregister_class(HDRI_OT_direct_paint)
    bpy.utils.unregister_class(HDRI_OT_image_paint_mode)