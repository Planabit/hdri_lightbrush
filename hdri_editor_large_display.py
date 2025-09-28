bl_info = {"name": "HDRI Editor - Large Display", "version": (1, 2, 0), "blender": (4, 0, 0), "category": "3D View"}

import bpy
import gpu
import gpu_extras
from gpu_extras.batch import batch_for_shader
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, FloatProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ImportHelper
import mathutils

class HDRI_LargeDisplayPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    display_height: IntProperty(
        name="Display Height",
        description="Height of the image display in pixels",
        default=400,
        min=100,
        max=1000
    )
    
    display_width: IntProperty(
        name="Display Width", 
        description="Width of the image display in pixels",
        default=600,
        min=200,
        max=1200
    )

class HDRI_LargeProperties(PropertyGroup):
    current_image: bpy.props.PointerProperty(type=bpy.types.Image)

class HDRI_OT_load_large(Operator, ImportHelper):
    bl_idname = "hdri.load_large"
    bl_label = "Load HDRI for Large Display"
    
    filename_ext = ".hdr"
    filter_glob: StringProperty(default="*.hdr;*.exr;*.jpg;*.png", options={"HIDDEN"})

    def execute(self, context):
        try:
            img = bpy.data.images.load(self.filepath)
            context.scene.hdri_large_properties.current_image = img
            
            # Force high-quality preview
            if hasattr(img, 'preview'):
                img.preview_ensure()
            
            self.report({"INFO"}, f"Loaded HDRI: {img.name}")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to load HDRI: {str(e)}")
            return {"CANCELLED"}

class HDRI_OT_open_image_editor(Operator):
    bl_idname = "hdri.open_image_editor"
    bl_label = "Open in Image Editor"
    bl_description = "Open the HDRI in a separate Image Editor window"
    
    def execute(self, context):
        img = context.scene.hdri_large_properties.current_image
        if not img:
            self.report({"WARNING"}, "No image loaded")
            return {"CANCELLED"}
        
        # Create new window with image editor
        bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        
        # Find the new area and set it to image editor
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'PROPERTIES':  # Usually the duplicated area
                    area.type = 'IMAGE_EDITOR'
                    area.spaces.active.image = img
                    break
        
        return {"FINISHED"}

class HDRI_OT_create_image_window(Operator):
    bl_idname = "hdri.create_image_window"
    bl_label = "Create Image Window"
    bl_description = "Create a dedicated window for image viewing"
    
    def execute(self, context):
        img = context.scene.hdri_large_properties.current_image
        if not img:
            self.report({"WARNING"}, "No image loaded")
            return {"CANCELLED"}
        
        # Create new window
        bpy.ops.wm.window_new()
        
        # Set the new window to image editor
        new_window = context.window_manager.windows[-1]
        area = new_window.screen.areas[0]
        area.type = 'IMAGE_EDITOR'
        
        with context.temp_override(window=new_window, area=area):
            area.spaces.active.image = img
            # Set zoom to fit
            bpy.ops.image.view_all('INVOKE_DEFAULT', fit_view=True)
        
        return {"FINISHED"}

class HDRI_PT_large_display_panel(Panel):
    bl_label = "HDRI Editor - Large Display"
    bl_idname = "HDRI_PT_large_display"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "HDRI Editor"

    def draw(self, context):
        layout = self.layout
        props = context.scene.hdri_large_properties
        prefs = context.preferences.addons[__name__].preferences
        
        layout.operator("hdri.load_large", text="Load HDRI", icon="FILE_IMAGE")
        
        # Display settings
        layout.label(text="Display Settings:")
        layout.prop(prefs, "display_height")
        layout.prop(prefs, "display_width")
        
        if props.current_image:
            img = props.current_image
            
            # Image info
            box = layout.box()
            box.label(text=f"File: {img.name}", icon="IMAGE_DATA")
            if img.size[0] > 0:
                box.label(text=f"Size: {img.size[0]} x {img.size[1]}")
                aspect_ratio = img.size[0] / img.size[1] if img.size[1] > 0 else 1.0
                box.label(text=f"Aspect: {aspect_ratio:.2f}")
            
            # Large display methods
            display_box = layout.box()
            display_box.label(text="Large Display Options:", icon="FULLSCREEN_ENTER")
            
            # Method 1: Template ID with maximum size
            col = display_box.column()
            col.label(text="Method 1: Large Template ID", icon="IMAGE_DATA")
            
            try:
                # Calculate rows/cols based on preferences
                max_size = max(prefs.display_width // 100, prefs.display_height // 100)
                row = col.row()
                row.scale_y = prefs.display_height / 100
                row.template_ID_preview(
                    context.scene.hdri_large_properties, "current_image",
                    new="image.new", open="image.open",
                    rows=max_size, cols=max_size
                )
            except Exception as e:
                col.label(text=f"Template ID Error: {str(e)}", icon='ERROR')
            
            # Method 2: Dedicated window
            col = display_box.column()
            col.label(text="Method 2: Dedicated Windows", icon="WINDOW")
            row = col.row(align=True)
            row.operator("hdri.open_image_editor", text="Image Editor", icon="IMAGE")
            row.operator("hdri.create_image_window", text="New Window", icon="WINDOW")
            
            # Method 3: Template image with user settings
            col = display_box.column()
            col.label(text="Method 3: Template Image", icon="IMAGE_DATA")
            
            try:
                # Create image user for template_image
                if not hasattr(img, 'image_user_custom'):
                    # Create a simple image user-like object
                    pass
                
                col_img = col.column()
                col_img.scale_y = prefs.display_height / 200
                
                # Try direct template_image
                col_img.template_image(img, None, compact=False)
                
            except Exception as e:
                col.label(text=f"Template Image Error: {str(e)}", icon='ERROR')
            
            # Method 4: Icon view with maximum scale
            col = display_box.column()
            col.label(text="Method 4: Large Icon View", icon="COLLAPSEMENU")
            
            try:
                # Create large icon display
                icon_row = col.row()
                icon_row.scale_y = prefs.display_height / 50
                
                if img.preview:
                    icon_id = img.preview.icon_id
                    if icon_id:
                        icon_row.label(text="", icon_value=icon_id)
                    else:
                        icon_row.label(text="Preview generating...", icon="TIME")
                else:
                    icon_row.label(text="No preview", icon="IMAGE_DATA")
                    
            except Exception as e:
                col.label(text=f"Icon View Error: {str(e)}", icon='ERROR')
            
            # Method 5: Combination display
            col = display_box.column()
            col.label(text="Method 5: Combination", icon="SETTINGS")
            
            split = col.split(factor=0.5)
            
            # Left side: Large icon
            left_col = split.column()
            try:
                left_col.scale_y = 3.0
                left_col.template_ID_preview(
                    context.scene.hdri_large_properties, "current_image",
                    rows=4, cols=4
                )
            except:
                left_col.label(text="Preview", icon="IMAGE_DATA")
            
            # Right side: Information and controls
            right_col = split.column()
            right_col.label(text="Quick Actions:")
            right_col.operator("hdri.create_image_window", text="Full View")
            right_col.separator()
            right_col.label(text="Image Info:")
            if img.size[0] > 0:
                right_col.label(text=f"{img.size[0]}×{img.size[1]}")
                right_col.label(text=f"Channels: {img.channels}")
                right_col.label(text=f"Depth: {img.depth}")

def register():
    bpy.utils.register_class(HDRI_LargeDisplayPreferences)
    bpy.utils.register_class(HDRI_LargeProperties)
    bpy.utils.register_class(HDRI_OT_load_large)
    bpy.utils.register_class(HDRI_OT_open_image_editor)
    bpy.utils.register_class(HDRI_OT_create_image_window)
    bpy.utils.register_class(HDRI_PT_large_display_panel)
    
    bpy.types.Scene.hdri_large_properties = bpy.props.PointerProperty(type=HDRI_LargeProperties)

def unregister():
    del bpy.types.Scene.hdri_large_properties
    
    bpy.utils.unregister_class(HDRI_PT_large_display_panel)
    bpy.utils.unregister_class(HDRI_OT_create_image_window)
    bpy.utils.unregister_class(HDRI_OT_open_image_editor)
    bpy.utils.unregister_class(HDRI_OT_load_large)
    bpy.utils.unregister_class(HDRI_LargeProperties)
    bpy.utils.unregister_class(HDRI_LargeDisplayPreferences)

if __name__ == "__main__":
    register()