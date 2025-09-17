"""
World property definitions for HDRI Editor.
"""

import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup

class HDRIEditorWorldProperties(PropertyGroup):
    """World background settings for HDRI Editor"""
    
    def update_world_background(self, context):
        """Update callback for world settings"""
        try:
            if self.auto_update:
                if context.scene.hdri_editor.hdri_previews != 'NONE':
                    bpy.ops.hdri_editor.update_world_background()
        except Exception as e:
            print(f"HDRI Editor: Update callback error: {e}")
    
    # Background strength
    background_strength: FloatProperty(
        name="Strength",
        description="Background light strength",
        default=1.0,
        min=0.0,
        soft_max=10.0,
        step=10,
        precision=3,
        update=update_world_background
    )
    
    # Background rotation
    background_rotation: FloatProperty(
        name="Rotation",
        description="Rotate the background image",
        default=0.0,
        min=-360.0,
        max=360.0,
        step=10,
        subtype='ANGLE',
        update=update_world_background
    )
    
    # Use world in viewport
    use_world_in_viewport: BoolProperty(
        name="Show in Viewport",
        description="Display world in 3D viewport",
        default=True,
        update=update_world_background
    )
    
    # Auto-update background
    auto_update: BoolProperty(
        name="Auto Update",
        description="Automatically update world when changing settings",
        default=True
    )
    
    # Background blur
    background_blur: FloatProperty(
        name="Blur",
        description="Blur the background",
        default=0.0,
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
        update=update_world_background
    )

# Classes for registration
classes = (
    HDRIEditorWorldProperties,
)

def register():
    """Register property classes and add them to scenes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.hdri_editor_world = bpy.props.PointerProperty(type=HDRIEditorWorldProperties)

def unregister():
    """Unregister property classes and remove them from scenes"""
    del bpy.types.Scene.hdri_editor_world
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)