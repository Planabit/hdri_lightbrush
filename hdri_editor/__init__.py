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
    
    @classmethod
    def poll(cls, context):
        # Always show panel
        return True

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
        
        # Calculate dynamic scale based on panel width
        region = context.region
        panel_width = region.width if region else 300
        target_width = panel_width - 20  # Minimal margin for tight fit
        base_icon_size = 64
        dynamic_scale = max(3, min(20, target_width // base_icon_size))
        
        # Create a sub-layout without extra padding
        col = box.column(align=True)
        col.template_icon_view(context.scene.hdri_editor, "hdri_previews", 
                             show_labels=False, scale=dynamic_scale, 
                             scale_popup=1.0)
        
        # Add current image info if image is loaded
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri != 'NONE' and current_hdri in bpy.data.images:
            img = bpy.data.images[current_hdri]
            aspect_ratio = img.size[1] / img.size[0] if img.size[0] > 0 else 0.5
            info_text = f"Size: {img.size[0]}x{img.size[1]} | AR: {aspect_ratio:.2f}"
            box.label(text=info_text, icon='INFO')
        
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
            # Load the image and ensure it's properly loaded
            img = bpy.data.images.load(self.filepath, check_existing=True)
            
            # Ensure the image is loaded into memory
            img.reload()
            
            # Force update of the image data
            if not img.has_data:
                # Try to pack the image to force loading
                img.pack()
                
            # Update preview system
            context.scene.hdri_editor.hdri_previews = img.name
            context.scene['hdri_editor_preview_image'] = img.name
            
            # Set colorspace for HDRI files
            if self.filepath.lower().endswith(('.hdr', '.exr')):
                img.colorspace_settings.name = 'Linear'
            else:
                img.colorspace_settings.name = 'sRGB'
            
            # Force UI redraw
            for area in context.screen.areas:
                area.tag_redraw()
            
            self.report({'INFO'}, f"Loaded HDRI: {img.name} ({img.size[0]}x{img.size[1]})")
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

        from . import ui
        try:
            ui.register()
            print("HDRI Editor: Registered UI modules")
        except:
            print("HDRI Editor: UI modules already registered")

        from .utils import preview_utils
        try:
            preview_utils.register()
            print("HDRI Editor: Registered preview utils")
        except:
            print("HDRI Editor: Preview utils already registered")

        # Register lighting system components
        try:
            from . import lighting
            lighting.register()
            print("HDRI Editor: Registered lighting system")
        except Exception as e:
            print(f"HDRI Editor: Error registering lighting system: {e}")

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

        from . import ui
        try:
            ui.unregister()
            print("HDRI Editor: Unregistered UI modules")
        except:
            print("HDRI Editor: UI modules already unregistered")

        from .utils import preview_utils
        try:
            preview_utils.unregister()
            print("HDRI Editor: Unregistered preview utils")
        except:
            print("HDRI Editor: Preview utils already unregistered")

        # Unregister lighting system
        # Unregister lighting system
        try:
            from . import lighting
            lighting.unregister()
            print("HDRI Editor: Unregistered lighting system")
        except Exception as e:
            print(f"HDRI Editor: Error unregistering lighting system: {e}")

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