"""
HDRI 2D Editor Panel - KeyShot-style HDRI editing
Direct manipulation of HDRI images with light generation capabilities.
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty
import bmesh
import mathutils
from mathutils import Vector
import math

class HDRI_EDITOR_PT_hdri_2d_editor(Panel):
    """Main 2D HDRI editor panel - KeyShot style"""
    bl_label = "HDRI 2D Editor"
    bl_idname = "VIEW3D_PT_hdri_2d_editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='IMAGE_DATA')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Check if HDRI is loaded
        current_hdri = scene.hdri_editor.hdri_previews if hasattr(scene, 'hdri_editor') else 'NONE'
        
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            box = layout.box()
            box.label(text="No HDRI loaded", icon='INFO')
            box.operator("hdri_editor.load_hdri", text="Load HDRI File", icon='FILEBROWSER')
            return
            
        img = bpy.data.images[current_hdri]
        
        # HDRI Image Display
        display_box = layout.box()
        display_box.label(text=f"Editing: {img.name}", icon='IMAGE_DATA')
        
        # Calculate dynamic size for image display
        region = context.region
        panel_width = region.width if region else 300
        display_width = panel_width - 40  # Account for margins
        
        # Maintain 2:1 aspect ratio for HDRI
        display_height = display_width // 2
        
        # Image template with proper sizing
        col = display_box.column(align=True)
        
        # Create a more robust image display
        image_row = col.row()
        image_row.scale_y = 4  # Make it taller
        
        # Use template_preview for better image display
        if img.preview:
            image_row.template_preview(img.preview, show_buttons=False)
        else:
            # Fallback to simple image reference
            image_row.prop(img, "source", text="")
            
        # Alternative: Show image properties for debugging
        debug_col = col.column(align=True)
        debug_col.scale_y = 0.7
        debug_col.label(text=f"Loaded: {'Yes' if img.has_data else 'No'}")
        debug_col.label(text=f"Pixels: {len(img.pixels) if img.pixels else 0}")
        
        # Image info
        info_row = display_box.row()
        info_row.label(text=f"Size: {img.size[0]}x{img.size[1]}")
        info_row.label(text=f"Format: {img.file_format}")
        
        # HDRI Editing Tools
        tools_box = layout.box()
        tools_box.label(text="HDRI Editing Tools:", icon='TOOL_SETTINGS')
        
        # Light Generation Tools  
        light_row = tools_box.row(align=True)
        light_row.operator("hdri_2d.add_light_spot", text="Add Light", icon='LIGHT_SUN')
        light_row.operator("hdri_2d.add_sun_disk", text="Add Sun", icon='LIGHT')
        
        # Image editing tools
        edit_row = tools_box.row(align=True) 
        edit_row.operator("hdri_2d.paint_light", text="Paint Light", icon='BRUSH_DATA')
        edit_row.operator("hdri_2d.erase_area", text="Erase", icon='X')
        
        # Advanced tools
        advanced_box = layout.box()
        advanced_box.label(text="Advanced Tools:", icon='MODIFIER')
        
        adv_row1 = advanced_box.row(align=True)
        adv_row1.operator("hdri_2d.generate_gradient", text="Sky Gradient", icon='COLOR')
        adv_row1.operator("hdri_2d.add_horizon", text="Horizon Line", icon='MESH_PLANE')
        
        adv_row2 = advanced_box.row(align=True)
        adv_row2.operator("hdri_2d.blur_area", text="Blur", icon='SMOOTHCURVE')
        adv_row2.operator("hdri_2d.sharpen_lights", text="Sharpen", icon='SHARPCURVE')
        
        # Export options
        export_box = layout.box()
        export_box.label(text="Export Options:", icon='EXPORT')
        
        export_row = export_box.row(align=True)
        export_row.operator("hdri_2d.save_hdri", text="Save HDRI", icon='FILE_IMAGE')
        export_row.operator("hdri_2d.export_exr", text="Export EXR", icon='FILE_BLANK')

class HDRI_2D_OT_add_light_spot(Operator):
    """Add a bright light spot to HDRI at cursor position"""
    bl_idname = "hdri_2d.add_light_spot"
    bl_label = "Add Light Spot"
    bl_description = "Add a bright circular light spot to the HDRI"

    # Light properties
    intensity: FloatProperty(
        name="Intensity",
        description="Light intensity/brightness",
        default=5.0,
        min=0.1,
        max=50.0
    )
    
    size: FloatProperty(
        name="Size",
        description="Light spot radius",
        default=0.05,
        min=0.001,
        max=0.5
    )
    
    color_temp: FloatProperty(
        name="Color Temperature",
        description="Color temperature in Kelvin",
        default=5600,
        min=1000,
        max=12000
    )
    
    falloff: EnumProperty(
        name="Falloff",
        items=[
            ('LINEAR', 'Linear', 'Linear falloff'),
            ('SMOOTH', 'Smooth', 'Smooth falloff'),
            ('SPHERE', 'Spherical', 'Spherical falloff'),
        ],
        default='SMOOTH'
    )

    def execute(self, context):
        scene = context.scene
        
        # Get current HDRI
        current_hdri = scene.hdri_editor.hdri_previews if hasattr(scene, 'hdri_editor') else 'NONE'
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        # For now, add light at center - in full implementation this would be interactive
        center_u = 0.5
        center_v = 0.5
        
        self.add_light_to_hdri(img, center_u, center_v)
        
        self.report({'INFO'}, f"Added light spot to {img.name}")
        return {'FINISHED'}

    def add_light_to_hdri(self, img, u, v):
        """Add a bright light spot to HDRI image at UV coordinates"""
        if not img or not img.pixels:
            return
            
        width, height = img.size
        pixels = list(img.pixels)
        
        # Convert UV to pixel coordinates
        center_x = int(u * width)
        center_y = int(v * height)
        
        # Calculate light properties
        light_radius_px = int(self.size * min(width, height))
        
        # Convert color temperature to RGB
        light_color = self.kelvin_to_rgb(self.color_temp)
        
        # Apply light to pixels
        for y in range(max(0, center_y - light_radius_px), 
                      min(height, center_y + light_radius_px)):
            for x in range(max(0, center_x - light_radius_px), 
                          min(width, center_x + light_radius_px)):
                
                # Calculate distance from center
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= light_radius_px:
                    # Calculate falloff
                    if light_radius_px > 0:
                        falloff_factor = 1.0 - (distance / light_radius_px)
                        
                        if self.falloff == 'LINEAR':
                            intensity = falloff_factor
                        elif self.falloff == 'SMOOTH':
                            intensity = falloff_factor * falloff_factor * (3.0 - 2.0 * falloff_factor)
                        else:  # SPHERE
                            intensity = math.cos(falloff_factor * math.pi * 0.5)
                        
                        intensity *= self.intensity
                    else:
                        intensity = self.intensity
                    
                    # Calculate pixel index
                    pixel_index = (y * width + x) * 4
                    
                    if pixel_index < len(pixels) - 3:
                        # Add light color to existing pixel (additive)
                        pixels[pixel_index] = min(pixels[pixel_index] + light_color[0] * intensity, 50.0)
                        pixels[pixel_index + 1] = min(pixels[pixel_index + 1] + light_color[1] * intensity, 50.0)  
                        pixels[pixel_index + 2] = min(pixels[pixel_index + 2] + light_color[2] * intensity, 50.0)
                        # Alpha stays the same
        
        # Update image
        img.pixels = pixels
        img.update()
        
    def kelvin_to_rgb(self, temp):
        """Convert color temperature in Kelvin to RGB values"""
        temp = temp / 100.0
        
        if temp <= 66:
            red = 255
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0, min(255, red))
            
        if temp <= 66:
            green = temp
            green = 99.4708025861 * math.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = max(0, min(255, green))
        
        if temp >= 66:
            blue = 255
        else:
            if temp <= 19:
                blue = 0
            else:
                blue = temp - 10
                blue = 138.5177312231 * math.log(blue) - 305.0447927307
                blue = max(0, min(255, blue))
        
        return (red / 255.0, green / 255.0, blue / 255.0)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class HDRI_2D_OT_add_sun_disk(Operator):
    """Add a sun disk to HDRI"""
    bl_idname = "hdri_2d.add_sun_disk"
    bl_label = "Add Sun Disk"
    bl_description = "Add a realistic sun disk to the HDRI"

    sun_size: FloatProperty(
        name="Sun Size",
        description="Angular size of the sun",
        default=0.01,
        min=0.001,
        max=0.1
    )
    
    sun_intensity: FloatProperty(
        name="Sun Intensity", 
        description="Sun brightness",
        default=20.0,
        min=1.0,
        max=100.0
    )

    def execute(self, context):
        scene = context.scene
        
        # Get current HDRI
        current_hdri = scene.hdri_editor.hdri_previews if hasattr(scene, 'hdri_editor') else 'NONE'
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        # Add sun at default position (upper right)
        self.add_sun_to_hdri(img, 0.75, 0.7)
        
        self.report({'INFO'}, f"Added sun disk to {img.name}")
        return {'FINISHED'}

    def add_sun_to_hdri(self, img, u, v):
        """Add a realistic sun disk to HDRI"""
        if not img or not img.pixels:
            return
            
        width, height = img.size
        pixels = list(img.pixels)
        
        center_x = int(u * width)
        center_y = int(v * height)
        
        sun_radius_px = int(self.sun_size * min(width, height))
        
        # Sun color (yellowish-white)
        sun_color = (1.0, 0.98, 0.9)
        
        # Create sun disk with corona
        for y in range(max(0, center_y - sun_radius_px * 3), 
                      min(height, center_y + sun_radius_px * 3)):
            for x in range(max(0, center_x - sun_radius_px * 3), 
                          min(width, center_x + sun_radius_px * 3)):
                
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                pixel_index = (y * width + x) * 4
                
                if pixel_index < len(pixels) - 3:
                    if distance <= sun_radius_px:
                        # Core sun disk
                        intensity = self.sun_intensity
                        pixels[pixel_index] = min(pixels[pixel_index] + sun_color[0] * intensity, 100.0)
                        pixels[pixel_index + 1] = min(pixels[pixel_index + 1] + sun_color[1] * intensity, 100.0)
                        pixels[pixel_index + 2] = min(pixels[pixel_index + 2] + sun_color[2] * intensity, 100.0)
                    elif distance <= sun_radius_px * 3:
                        # Corona/glow
                        corona_factor = 1.0 - (distance - sun_radius_px) / (sun_radius_px * 2)
                        corona_factor = max(0, corona_factor)
                        corona_intensity = corona_factor * self.sun_intensity * 0.3
                        
                        pixels[pixel_index] = min(pixels[pixel_index] + sun_color[0] * corona_intensity, 100.0)
                        pixels[pixel_index + 1] = min(pixels[pixel_index + 1] + sun_color[1] * corona_intensity, 100.0)
                        pixels[pixel_index + 2] = min(pixels[pixel_index + 2] + sun_color[2] * corona_intensity, 100.0)
        
        # Update image
        img.pixels = pixels
        img.update()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class HDRI_2D_OT_paint_light(Operator):
    """Paint light areas on HDRI"""
    bl_idname = "hdri_2d.paint_light"
    bl_label = "Paint Light"
    bl_description = "Paint bright areas on the HDRI with a brush"

    def execute(self, context):
        # This would be implemented as an interactive painting tool
        self.report({'INFO'}, "Light painting tool (feature in development)")
        return {'FINISHED'}

class HDRI_2D_OT_generate_gradient(Operator):
    """Generate sky gradient"""
    bl_idname = "hdri_2d.generate_gradient"
    bl_label = "Generate Sky Gradient"
    bl_description = "Generate a realistic sky gradient"

    horizon_color: bpy.props.FloatVectorProperty(
        name="Horizon Color",
        subtype='COLOR',
        default=(0.8, 0.9, 1.0),
        min=0.0,
        max=1.0
    )
    
    zenith_color: bpy.props.FloatVectorProperty(
        name="Zenith Color",  
        subtype='COLOR',
        default=(0.2, 0.4, 0.8),
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        scene = context.scene
        
        current_hdri = scene.hdri_editor.hdri_previews if hasattr(scene, 'hdri_editor') else 'NONE'
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        self.generate_sky_gradient(img)
        
        self.report({'INFO'}, f"Generated sky gradient in {img.name}")
        return {'FINISHED'}

    def generate_sky_gradient(self, img):
        """Generate a realistic sky gradient"""
        if not img:
            return
            
        width, height = img.size
        pixels = [0.0] * (width * height * 4)
        
        for y in range(height):
            # V coordinate (0 at bottom, 1 at top)
            v = y / height
            
            # Create gradient from horizon to zenith
            factor = v
            
            # Interpolate colors
            r = self.horizon_color[0] + (self.zenith_color[0] - self.horizon_color[0]) * factor
            g = self.horizon_color[1] + (self.zenith_color[1] - self.horizon_color[1]) * factor  
            b = self.horizon_color[2] + (self.zenith_color[2] - self.horizon_color[2]) * factor
            
            for x in range(width):
                pixel_index = (y * width + x) * 4
                pixels[pixel_index] = r
                pixels[pixel_index + 1] = g
                pixels[pixel_index + 2] = b
                pixels[pixel_index + 3] = 1.0
        
        img.pixels = pixels
        img.update()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class HDRI_2D_OT_save_hdri(Operator):
    """Save HDRI to file"""
    bl_idname = "hdri_2d.save_hdri"
    bl_label = "Save HDRI"
    bl_description = "Save the edited HDRI to file"

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to save HDRI file",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.hdr;*.exr;*.png",
        options={'HIDDEN'}
    )

    def execute(self, context):
        scene = context.scene
        
        current_hdri = scene.hdri_editor.hdri_previews if hasattr(scene, 'hdri_editor') else 'NONE'
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        try:
            # Set file format based on extension
            if self.filepath.lower().endswith('.exr'):
                img.file_format = 'OPEN_EXR'
            elif self.filepath.lower().endswith('.hdr'):
                img.file_format = 'HDR'
            else:
                img.file_format = 'PNG'
                
            img.filepath_raw = self.filepath
            img.save()
            
            self.report({'INFO'}, f"Saved HDRI to {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save HDRI: {e}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Placeholder operators for other tools
class HDRI_2D_OT_erase_area(Operator):
    bl_idname = "hdri_2d.erase_area"
    bl_label = "Erase Area"
    def execute(self, context):
        self.report({'INFO'}, "Erase tool (feature in development)")
        return {'FINISHED'}

class HDRI_2D_OT_add_horizon(Operator):
    bl_idname = "hdri_2d.add_horizon"
    bl_label = "Add Horizon"
    def execute(self, context):
        self.report({'INFO'}, "Horizon tool (feature in development)")  
        return {'FINISHED'}

class HDRI_2D_OT_blur_area(Operator):
    bl_idname = "hdri_2d.blur_area"
    bl_label = "Blur Area"
    def execute(self, context):
        self.report({'INFO'}, "Blur tool (feature in development)")
        return {'FINISHED'}

class HDRI_2D_OT_sharpen_lights(Operator):
    bl_idname = "hdri_2d.sharpen_lights"  
    bl_label = "Sharpen Lights"
    def execute(self, context):
        self.report({'INFO'}, "Sharpen tool (feature in development)")
        return {'FINISHED'}

class HDRI_2D_OT_export_exr(Operator):
    bl_idname = "hdri_2d.export_exr"
    bl_label = "Export EXR"
    def execute(self, context):
        bpy.ops.hdri_2d.save_hdri('INVOKE_DEFAULT')
        return {'FINISHED'}

# Classes for registration
classes = (
    HDRI_EDITOR_PT_hdri_2d_editor,
    HDRI_2D_OT_add_light_spot,
    HDRI_2D_OT_add_sun_disk,
    HDRI_2D_OT_paint_light,
    HDRI_2D_OT_generate_gradient,
    HDRI_2D_OT_save_hdri,
    HDRI_2D_OT_erase_area,
    HDRI_2D_OT_add_horizon,
    HDRI_2D_OT_blur_area,
    HDRI_2D_OT_sharpen_lights,
    HDRI_2D_OT_export_exr,
)

def register():
    """Register 2D HDRI editor classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("HDRI Editor: Registered 2D HDRI editor")

def unregister():
    """Unregister 2D HDRI editor classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("HDRI Editor: Unregistered 2D HDRI editor")