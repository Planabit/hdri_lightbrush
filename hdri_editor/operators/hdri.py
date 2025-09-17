"""
HDRI file operators for HDRI Editor.
Handles HDRI file loading and management.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

class HDRI_EDITOR_OT_load_hdri(Operator):
    """Load an HDRI file"""
    bl_idname = "hdri_editor.load_hdri"
    bl_label = "Load HDRI"
    bl_description = "Load a new HDRI file"
    
    filepath: StringProperty(
        name="File Path",
        description="Path to HDRI file",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty(
        default="*.hdr;*.exr;*.jpg;*.jpeg;*.png;*.tif;*.tiff",
        options={'HIDDEN'}
    )

    def execute(self, context):
        try:
            # Load the image
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

class HDRI_EDITOR_OT_create_black_hdri(Operator):
    """Create a black HDRI image"""
    bl_idname = "hdri_editor.create_black_hdri"
    bl_label = "Create Black HDRI"
    bl_description = "Create a new black HDRI (2048x1024)"

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

# Classes for registration
__all__ = [
    'HDRI_EDITOR_OT_load_hdri',
    'HDRI_EDITOR_OT_create_black_hdri',
    'register',
    'unregister'
]

classes = (
    HDRI_EDITOR_OT_load_hdri,
    HDRI_EDITOR_OT_create_black_hdri,
)

def register():
    """Register the operators"""
    try:
        for cls in classes:
            try:
                bpy.utils.register_class(cls)
                print(f"HDRI Editor: Registered {cls.__name__}")
            except ValueError as e:
                print(f"HDRI Editor: Class {cls.__name__} already registered")
    except Exception as e:
        print(f"HDRI Editor: Error during registration: {str(e)}")
        raise

def unregister():
    """Unregister the operators"""
    try:
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
                print(f"HDRI Editor: Unregistered {cls.__name__}")
            except ValueError:
                print(f"HDRI Editor: Class {cls.__name__} already unregistered")
            except RuntimeError:
                print(f"HDRI Editor: Failed to unregister {cls.__name__}, may be in use")
    except Exception as e:
        print(f"HDRI Editor: Error during unregistration: {str(e)}")
        raise