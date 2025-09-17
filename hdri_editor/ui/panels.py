import bpy
from bpy.types import Panel

class HDRI_EDITOR_PT_world_settings(Panel):
    bl_label = "World Settings"
    bl_idname = "VIEW3D_PT_hdri_editor_world"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.world is not None and context.scene.world.use_nodes

    def draw(self, context):
        layout = self.layout
        world_props = context.scene.hdri_editor_world
        
        # Background settings
        col = layout.column(align=True)
        row = col.row(align=True)
        
        # Strength
        row = col.row(align=True)
        row.prop(world_props, "background_strength")
        
        # Rotation
        row = col.row(align=True)
        row.prop(world_props, "background_rotation")
        
        # Blur (if supported)
        row = col.row(align=True)
        row.prop(world_props, "background_blur")
        
        col.separator()
        
        # Viewport options
        row = col.row(align=True)
        row.prop(world_props, "use_world_in_viewport")
        
        # Auto update option
        row = col.row(align=True)
        row.prop(world_props, "auto_update")
        
        # Update button (if auto-update is off)
        if not world_props.auto_update:
            col.operator("hdri_editor.update_world_background", text="Update World")

# Classes for registration
__all__ = [
    'HDRI_EDITOR_PT_world_settings',
    'register',
    'unregister'
]

classes = (
    HDRI_EDITOR_PT_world_settings,
)

def register():
    """Register panel classes"""
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
    """Unregister panel classes"""
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