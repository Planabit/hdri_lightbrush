"""
HDRI Editor - Alternatív Kép Megjelenítési Módszerek Teszt

Blender-ben többféle módon lehet képeket megjeleníteni:

1. template_icon_view - amit eddig használtunk (kis méret)
2. template_image - közvetlen kép megjelenítés 
3. template_ID_preview - ID előnézet nagy ikonnal
4. Egyedi operator kép megjelenítéssel
5. Image datablock direkt kezelés
6. Custom image widget
7. Panel background image
8. Operator modal megjelenítés

Teszteljük ezeket egyenként!
"""

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, FloatProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ImportHelper

bl_info = {"name": "HDRI Editor - Alternative Display", "version": (1, 1, 0), "blender": (4, 0, 0), "category": "3D View"}

class HDRI_AlternativePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    display_method: EnumProperty(
        name="Display Method",
        description="Choose how to display HDRI images",
        items=[
            ('TEMPLATE_IMAGE', 'Template Image', 'Direct image template'),
            ('TEMPLATE_ID', 'Template ID Preview', 'ID preview with large icon'),
            ('CUSTOM_DRAW', 'Custom Draw', 'Custom image drawing'),
            ('OPERATOR_MODAL', 'Operator Modal', 'Modal operator display'),
            ('IMAGE_VIEWER', 'Image Viewer', 'Built-in image viewer')
        ],
        default='TEMPLATE_IMAGE'
    )
    
    image_scale: FloatProperty(
        name="Image Scale",
        description="Scale factor for image display",
        default=2.0,
        min=0.5,
        max=10.0
    )

class HDRI_Properties(PropertyGroup):
    current_image: bpy.props.PointerProperty(type=bpy.types.Image)

class HDRI_OT_load(Operator, ImportHelper):
    bl_idname = "hdri.load_alt"
    bl_label = "Load HDRI"
    
    filename_ext = ".hdr"
    filter_glob: StringProperty(default="*.hdr;*.exr;*.jpg;*.png", options={"HIDDEN"})

    def execute(self, context):
        try:
            img = bpy.data.images.load(self.filepath)
            context.scene.hdri_properties.current_image = img
            self.report({"INFO"}, f"Loaded HDRI: {img.name}")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to load HDRI: {str(e)}")
            return {"CANCELLED"}

class HDRI_OT_show_image_viewer(Operator):
    bl_idname = "hdri.show_image_viewer"
    bl_label = "Open in Image Editor"
    
    def execute(self, context):
        if context.scene.hdri_properties.current_image:
            # Find or create image editor area
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = context.scene.hdri_properties.current_image
                    return {"FINISHED"}
            
            # If no image editor found, try to create one
            self.report({"INFO"}, "Switch to Image Editor workspace to view")
        else:
            self.report({"WARNING"}, "No image loaded")
        return {"FINISHED"}

class HDRI_OT_image_modal(Operator):
    bl_idname = "hdri.image_modal"  
    bl_label = "Modal Image Display"
    
    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.scene.hdri_properties.current_image:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({"WARNING"}, "No image loaded")
            return {'CANCELLED'}

class HDRI_PT_alternative_panel(Panel):
    bl_label = "HDRI Editor - Alternative Display"
    bl_idname = "HDRI_PT_alternative"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "HDRI Editor"

    def draw(self, context):
        layout = self.layout
        props = context.scene.hdri_properties
        prefs = context.preferences.addons[__name__].preferences
        
        layout.operator("hdri.load_alt", text="Load HDRI", icon="FILE_IMAGE")
        
        # Display method selector
        layout.prop(prefs, "display_method")
        layout.prop(prefs, "image_scale")
        
        if props.current_image:
            img = props.current_image
            
            box = layout.box()
            box.label(text=f"File: {img.name}", icon="IMAGE_DATA")
            if img.size[0] > 0:
                box.label(text=f"Size: {img.size[0]} x {img.size[1]}")
            
            if img.has_data:
                preview_box = layout.box()
                preview_box.label(text="Image Display:", icon="IMAGE_DATA")
                
                # Different display methods
                if prefs.display_method == 'TEMPLATE_IMAGE':
                    # Method 1: Direct template_image
                    try:
                        preview_box.template_image(img, img.image_user if hasattr(img, 'image_user') else None, 
                                                 compact=False, multiview=False)
                    except Exception as e:
                        preview_box.label(text=f"Template Image Error: {str(e)}", icon='ERROR')
                
                elif prefs.display_method == 'TEMPLATE_ID':
                    # Method 2: template_ID_preview with large scale
                    try:
                        row = preview_box.row()
                        row.scale_y = prefs.image_scale * 3
                        row.template_ID_preview(context.scene.hdri_properties, "current_image", 
                                              new="image.new", open="image.open", 
                                              rows=int(prefs.image_scale), cols=int(prefs.image_scale))
                    except Exception as e:
                        preview_box.label(text=f"Template ID Error: {str(e)}", icon='ERROR')
                
                elif prefs.display_method == 'CUSTOM_DRAW':
                    # Method 3: Custom drawing approach
                    try:
                        col = preview_box.column()
                        col.scale_y = prefs.image_scale
                        
                        # Use operator to display image
                        col.operator("hdri.show_image_viewer", text="Open in Image Editor", icon="IMAGE_DATA")
                        col.operator("hdri.image_modal", text="Modal Display", icon="FULLSCREEN_ENTER")
                        
                        # Try to show image info
                        if img.preview:
                            img.preview_ensure()
                            icon_id = img.preview.icon_id if img.preview.icon_id else 'FILE_IMAGE'
                            row = col.row()
                            row.scale_y = prefs.image_scale * 2
                            row.label(text=img.name, icon_value=icon_id if isinstance(icon_id, int) else 0)
                        
                    except Exception as e:
                        preview_box.label(text=f"Custom Draw Error: {str(e)}", icon='ERROR')
                
                elif prefs.display_method == 'OPERATOR_MODAL':
                    # Method 4: Operator-based display
                    preview_box.operator("hdri.image_modal", text="Show Image Modal", icon="FULLSCREEN_ENTER")
                    preview_box.operator("hdri.show_image_viewer", text="Open in Image Editor", icon="IMAGE_DATA")
                
                elif prefs.display_method == 'IMAGE_VIEWER':
                    # Method 5: Force image editor
                    preview_box.operator("hdri.show_image_viewer", text="Open in Image Editor", icon="IMAGE_DATA")
                    preview_box.label(text="Switch to Image Editor workspace", icon="INFO")

def register():
    bpy.utils.register_class(HDRI_AlternativePreferences)
    bpy.utils.register_class(HDRI_Properties)
    bpy.utils.register_class(HDRI_OT_load)
    bpy.utils.register_class(HDRI_OT_show_image_viewer)
    bpy.utils.register_class(HDRI_OT_image_modal)
    bpy.utils.register_class(HDRI_PT_alternative_panel)
    
    bpy.types.Scene.hdri_properties = bpy.props.PointerProperty(type=HDRI_Properties)

def unregister():
    del bpy.types.Scene.hdri_properties
    
    bpy.utils.unregister_class(HDRI_PT_alternative_panel)
    bpy.utils.unregister_class(HDRI_OT_image_modal)
    bpy.utils.unregister_class(HDRI_OT_show_image_viewer)
    bpy.utils.unregister_class(HDRI_OT_load)
    bpy.utils.unregister_class(HDRI_Properties)
    bpy.utils.unregister_class(HDRI_AlternativePreferences)

if __name__ == "__main__":
    register()