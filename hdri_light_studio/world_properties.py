"""
World Properties Module
World background settings for HDRI Light Studio
"""

import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import PropertyGroup

def update_world_background(self, context):
    """Update callback for world background properties - ALSO SYNCS SPHERE"""
    if self.auto_update and context.scene.world:
        # Call update operator
        try:
            bpy.ops.hdri_studio.update_world_background()
        except:
            pass  # Operator might not be available during registration
    
    # SYNC sphere material rotation with world rotation
    sync_sphere_rotation(self.background_rotation)

def sync_sphere_rotation(rotation_value):
    """Sync sphere rotation with world rotation by rotating the object itself"""
    import math
    
    # Find preview sphere
    sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
    if not sphere:
        print("⚠️ Sphere not found for rotation sync")
        return
    
    # SOLUTION: Rotate the sphere OBJECT itself on Z axis
    # This is simpler and works regardless of material type
    # Negate the rotation because we're inside the sphere looking out
    sphere.rotation_euler[2] = -rotation_value
    
    print(f"🔄 Sphere object rotated to {math.degrees(-rotation_value):.1f}°")
    
    # Force viewport update
    if bpy.context.view_layer:
        bpy.context.view_layer.update()

class HDRIStudioWorldProperties(PropertyGroup):
    """World background settings for HDRI Studio"""
    
    # Background Strength
    background_strength: FloatProperty(
        name="Background Strength",
        description="Strength of the background lighting",
        default=1.0,
        min=0.0,
        max=10.0,
        soft_min=0.0,
        soft_max=5.0,
        step=0.1,
        precision=2,
        update=update_world_background
    )
    
    # Background Rotation 
    background_rotation: FloatProperty(
        name="Background Rotation",
        description="Rotation of the background HDRI in radians",
        default=0.0,
        min=-6.28318,  # -2*pi
        max=6.28318,   # 2*pi
        soft_min=-3.14159,  # -pi
        soft_max=3.14159,   # pi
        step=0.1,
        precision=3,
        subtype='ANGLE',
        update=update_world_background
    )
    
    # Background Blur (placeholder for future implementation)
    background_blur: FloatProperty(
        name="Background Blur",
        description="Blur amount for background HDRI",
        default=0.0,
        min=0.0,
        max=1.0,
        step=0.01,
        precision=3,
        update=update_world_background
    )
    
    # Viewport Display
    use_world_in_viewport: BoolProperty(
        name="Show World in Viewport",
        description="Display world background in 3D viewport",
        default=True,
        update=update_world_background
    )
    
    # Auto Update
    auto_update: BoolProperty(
        name="Auto Update",
        description="Automatically update world when properties change",
        default=True
    )

def register():
    """Register world properties"""
    bpy.utils.register_class(HDRIStudioWorldProperties)
    print("World properties module registered")

def unregister():
    """Unregister world properties"""
    bpy.utils.unregister_class(HDRIStudioWorldProperties)
    print("World properties module unregistered")