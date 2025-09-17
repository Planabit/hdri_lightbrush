"""
HDRI Editor addon for Blender.
Provides tools for creating and editing studio HDRI backgrounds.
"""

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
from bpy.types import Panel, Operator

class HDRIEditorMainPanel(Panel):
    """Main panel for HDRI Editor"""
    bl_label = "HDRI Editor"
    bl_idname = "VIEW3D_PT_hdri_editor_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'

    def draw(self, context):
        layout = self.layout
        
        # HDRI file operations
        box = layout.box()
        box.label(text="HDRI Files:")
        box.operator("hdri_editor.load_hdri", text="Load HDRI")
        box.operator("hdri_editor.create_black_hdri", text="Create Black HDRI")

        # Preview section
        box = layout.box()
        box.label(text="HDRI Preview:")
        box.template_icon_view(context.scene.hdri_editor, "hdri_previews", 
                             show_labels=True, scale=8)
        
        # Background controls
        if context.scene.hdri_editor.hdri_previews != 'NONE':
            box = layout.box()
            box.label(text=f"Selected: {context.scene.hdri_editor.hdri_previews}")
            row = box.row(align=True)
            row.operator("hdri_editor.set_background", text="Set as Background")
            row.operator("hdri_editor.remove_background", text="Remove")
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

# Collection of all classes that need to be registered
classes = (
    HDRIEditorMainPanel,
    HDRIEditor_OT_LoadHDRI,
    HDRIEditor_OT_CreateBlackHDRI,
)

def register():
    """Register the addon"""
    try:
        # Register main classes first
        for cls in classes:
            try:
                bpy.utils.register_class(cls)
                print(f"HDRI Editor: Registered {cls.__name__}")
            except ValueError as e:
                print(f"HDRI Editor: Class {cls.__name__} already registered")

        # Then register submodules
        from .operators import background_tools
        try:
            background_tools.register()
            print("HDRI Editor: Registered background tools")
        except:
            print("HDRI Editor: Background tools already registered")

        from .properties import world_properties
        try:
            world_properties.register()
            print("HDRI Editor: Registered world properties")
        except:
            print("HDRI Editor: World properties already registered")

        from .ui import panels
        try:
            panels.register()
            print("HDRI Editor: Registered UI panels")
        except:
            print("HDRI Editor: UI panels already registered")

        from .utils import preview_utils
        try:
            preview_utils.register()
            print("HDRI Editor: Registered preview utils")
        except:
            print("HDRI Editor: Preview utils already registered")

        print("HDRI Editor: All modules registered successfully")

    except Exception as e:
        print(f"HDRI Editor: Error during registration: {str(e)}")
        raise

def unregister():
    """Unregister the addon"""
    try:
        # Unregister submodules first
        from .operators import background_tools
        try:
            background_tools.unregister()
            print("HDRI Editor: Unregistered background tools")
        except:
            print("HDRI Editor: Background tools already unregistered")

        from .properties import world_properties
        try:
            world_properties.unregister()
            print("HDRI Editor: Unregistered world properties")
        except:
            print("HDRI Editor: World properties already unregistered")

        from .ui import panels
        try:
            panels.unregister()
            print("HDRI Editor: Unregistered UI panels")
        except:
            print("HDRI Editor: UI panels already unregistered")

        from .utils import preview_utils
        try:
            preview_utils.unregister()
            print("HDRI Editor: Unregistered preview utils")
        except:
            print("HDRI Editor: Preview utils already unregistered")

        # Then unregister main classes
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
                print(f"HDRI Editor: Unregistered {cls.__name__}")
            except ValueError:
                print(f"HDRI Editor: Class {cls.__name__} already unregistered")
            except RuntimeError:
                print(f"HDRI Editor: Failed to unregister {cls.__name__}, may be in use")

        print("HDRI Editor: All modules unregistered successfully")

    except Exception as e:
        print(f"HDRI Editor: Error during unregistration: {str(e)}")
        raise

if __name__ == "__main__":
    register()