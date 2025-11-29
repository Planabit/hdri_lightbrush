"""
HDRI Light Studio - 3D Viewport Paint Operator (Simplified)

Simple click-to-paint approach that uses Blender's native texture painting
with proper viewport refresh.
"""

import bpy
import bmesh
from mathutils import Vector
from bpy_extras import view3d_utils
import numpy as np


class HDRI_OT_enable_3d_paint(bpy.types.Operator):
    """Enable 3D painting mode on sphere"""
    bl_idname = "hdri_studio.enable_3d_paint"
    bl_label = "Enable 3D Paint"
    bl_description = "Enable 3D painting mode for sphere interior"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Find sphere
        sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
        if not sphere:
            self.report({'ERROR'}, "No HDRI Sphere found. Create one first.")
            return {'CANCELLED'}

        # Get canvas image
        canvas_image = self.get_active_canvas_image(context)
        if not canvas_image:
            self.report({'ERROR'}, "No canvas image found. Setup painting first.")
            return {'CANCELLED'}

        # Select sphere
        bpy.ops.object.select_all(action='DESELECT')
        sphere.select_set(True)
        context.view_layer.objects.active = sphere

        # Enter texture paint mode
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        context.scene.tool_settings.image_paint.mode = 'MATERIAL'

        # Setup brush for interior painting
        if "HDRI_Interior_Brush" not in bpy.data.brushes:
            brush = bpy.data.brushes.new("HDRI_Interior_Brush")
            brush.size = 50
            brush.strength = 0.5
            brush.use_alpha = False
            brush.color = (1.0, 1.0, 1.0)  # White for light
            brush.falloff_shape = 'SPHERE'
        else:
            brush = bpy.data.brushes["HDRI_Interior_Brush"]

        context.tool_settings.image_paint.brush = brush
        context.scene.tool_settings.image_paint.canvas = canvas_image

        # Force material preview mode for better visibility
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        break

        self.report({'INFO'}, "3D Paint enabled. Use standard Blender paint tools to paint on interior.")
        return {'FINISHED'}

    def get_active_canvas_image(self, context):
        """Get active canvas image"""
        if context.scene.tool_settings.image_paint.canvas:
            return context.scene.tool_settings.image_paint.canvas
        
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR' and space.image:
                        return space.image
        return None


class HDRI_OT_smart_paint_click(bpy.types.Operator):
    """Smart paint click that finds interior surface"""
    bl_idname = "hdri_studio.smart_paint_click"
    bl_label = "Smart Paint Click"
    bl_description = "Paint on sphere interior with smart surface detection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'PAINT_TEXTURE' and 
                bpy.data.objects.get("HDRI_Preview_Sphere") is not None)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        """Paint at mouse cursor position on interior surface"""
        
        sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
        if not sphere or context.mode != 'PAINT_TEXTURE':
            return {'CANCELLED'}

        # Get 3D ray from mouse position
        region = context.region
        region_3d = context.space_data.region_3d
        mouse_coord = (event.mouse_region_x, event.mouse_region_y)
        
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, mouse_coord)
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, mouse_coord)

        # Find interior surface intersection
        interior_location = self.find_interior_surface(sphere, ray_origin, ray_direction)
        
        if interior_location:
            # Convert back to 2D screen coordinates for native paint
            screen_coord = view3d_utils.location_3d_to_region_2d(region, region_3d, interior_location)
            
            if screen_coord:
                # Use Blender's native paint stroke at the corrected location
                bpy.ops.paint.image_paint(stroke=[{
                    "name": "",
                    "location": (0, 0, 0),
                    "mouse": screen_coord,
                    "mouse_event": (0, 0),
                    "pressure": 1.0,
                    "size": context.tool_settings.image_paint.brush.size,
                    "pen_flip": False,
                    "x_tilt": 0.0,
                    "y_tilt": 0.0,
                    "time": 0.0,
                    "is_start": True
                }])
                
                # Force viewport update
                context.area.tag_redraw()
                
                print(f"Painted at interior surface: {interior_location}")
                return {'FINISHED'}

        print("No interior surface found")
        return {'CANCELLED'}

    def find_interior_surface(self, sphere, ray_origin, ray_direction):
        """Find the interior surface intersection point"""
        
        # Transform ray to object space
        ray_origin_local = sphere.matrix_world.inverted() @ ray_origin
        ray_direction_local = sphere.matrix_world.inverted().to_3x3() @ ray_direction
        
        # Find first intersection
        success1, location1, normal1, face_index1 = sphere.ray_cast(ray_origin_local, ray_direction_local)
        
        if success1:
            # Find second intersection by casting from slightly past the first hit
            offset_distance = 0.001
            new_origin = location1 + ray_direction_local * offset_distance
            
            success2, location2, normal2, face_index2 = sphere.ray_cast(new_origin, ray_direction_local)
            
            if success2:
                # Return second intersection in world space (interior surface)
                return sphere.matrix_world @ location2
        
        return None


# Key binding setup for easy painting
class HDRI_OT_setup_paint_hotkey(bpy.types.Operator):
    """Setup hotkey for smart painting"""
    bl_idname = "hdri_studio.setup_paint_hotkey"
    bl_label = "Setup Paint Hotkey"
    bl_description = "Setup Ctrl+Click for smart interior painting"

    def execute(self, context):
        # This would need proper keymap registration
        self.report({'INFO'}, "Use the Smart Paint Click operator while in texture paint mode")
        return {'FINISHED'}


# Registration
classes = [
    HDRI_OT_enable_3d_paint,
    HDRI_OT_smart_paint_click,
    HDRI_OT_setup_paint_hotkey,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)