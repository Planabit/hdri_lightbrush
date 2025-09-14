bl_info = {
    "name": "HDRI Editor",
    "author": "",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > HDRI Editor",
    "description": "Studio HDRI-k létrehozása és szerkesztése Keyshot mintára.",
    "category": "3D View"
}

import bpy
from . import preview_utils

class HDRIEditorPanel(bpy.types.Panel):
    bl_label = "HDRI Editor"
    bl_idname = "VIEW3D_PT_hdri_editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'

    def draw(self, context):
        layout = self.layout
        layout.operator("hdri_editor.load_hdri", text="Load HDRI")
        layout.operator("hdri_editor.create_black_hdri", text="Create Black HDRI (2048x1024)")

        # Preview section
        box = layout.box()
        box.label(text="HDRI Preview:")
        
        # HDRI preview grid with thumbnails
        box.template_icon_view(context.scene.hdri_editor, "hdri_previews", 
                            show_labels=True, scale=8)
        
        # Show selected HDRI name
        if context.scene.hdri_editor.hdri_previews != 'NONE':
            box.label(text=f"Selected: {context.scene.hdri_editor.hdri_previews}")
        
# File selector and load operator
class HDRIEditor_OT_LoadHDRI(bpy.types.Operator):
    bl_idname = "hdri_editor.load_hdri"
    bl_label = "Load HDRI"
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to HDRI file",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    filter_glob: bpy.props.StringProperty(
        default="*.hdr;*.exr;*.jpg;*.jpeg;*.png;*.tif;*.tiff",
        options={'HIDDEN'}
    )

    def execute(self, context):
        try:
            # First load the image
            img = bpy.data.images.load(self.filepath, check_existing=True)
            img.reload()
            
            # Force redraw of UI
            context.area.tag_redraw()
            
            # Set to None first
            context.scene.hdri_editor.hdri_previews = 'NONE'
            context.scene['hdri_editor_preview_image'] = 'NONE'
            
            # Small delay to ensure image is loaded
            def delayed_update():
                context.scene.hdri_editor.hdri_previews = img.name
                context.scene['hdri_editor_preview_image'] = img.name
                
            bpy.app.timers.register(delayed_update, first_interval=0.1)
            
            self.report({'INFO'}, f"Loaded HDRI: {img.name}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load HDRI: {e}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Create black HDRI operator
class HDRIEditor_OT_CreateBlackHDRI(bpy.types.Operator):
    bl_idname = "hdri_editor.create_black_hdri"
    bl_label = "Create Black HDRI"

    def execute(self, context):
        try:
            # Create the image
            img = bpy.data.images.new("Black_HDRI", width=2048, height=1024)
            pixels = [0.0, 0.0, 0.0, 1.0] * (2048 * 1024)
            img.pixels = pixels
            
            # Force redraw of UI
            context.area.tag_redraw()
            
            # Set to None first
            context.scene.hdri_editor.hdri_previews = 'NONE'
            context.scene['hdri_editor_preview_image'] = 'NONE'
            
            # Small delay to ensure image is loaded
            def delayed_update():
                context.scene.hdri_editor.hdri_previews = img.name
                context.scene['hdri_editor_preview_image'] = img.name
                
            bpy.app.timers.register(delayed_update, first_interval=0.1)
            
            self.report({'INFO'}, "Created black HDRI (2048x1024)")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create HDRI: {e}")
            return {'CANCELLED'}

# Registration
classes = [
    HDRIEditorPanel,
    HDRIEditor_OT_LoadHDRI,
    HDRIEditor_OT_CreateBlackHDRI,
]

def register():
    preview_utils.register()
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    preview_utils.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()