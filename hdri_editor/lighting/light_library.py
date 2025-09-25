"""
Light Library for HDRI Editor.
Pre-configured lighting setups inspired by KeyShot.
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import EnumProperty

# Light presets library
LIGHT_PRESETS = {
    'STUDIO_3POINT': {
        'name': 'Studio 3-Point',
        'description': 'Classic 3-point lighting setup',
        'lights': [
            {
                'name': 'Key_Light',
                'type': 'AREA',
                'intensity': 200.0,
                'color': (1.0, 1.0, 1.0),
                'size': 2.0,
                'azimuth': 45.0,
                'elevation': 30.0,
                'distance': 8.0,
                'area_shape': 'RECTANGLE',
                'area_size_y': 1.5
            },
            {
                'name': 'Fill_Light',
                'type': 'AREA',
                'intensity': 80.0,
                'color': (1.0, 0.95, 0.9),
                'size': 3.0,
                'azimuth': -60.0,
                'elevation': 15.0,
                'distance': 10.0,
                'area_shape': 'SQUARE'
            },
            {
                'name': 'Rim_Light',
                'type': 'AREA',
                'intensity': 150.0,
                'color': (0.9, 0.95, 1.0),
                'size': 1.5,
                'azimuth': 135.0,
                'elevation': 45.0,
                'distance': 6.0,
                'area_shape': 'SQUARE'
            }
        ]
    },
    'PRODUCT_SOFT': {
        'name': 'Product Soft',
        'description': 'Soft product lighting',
        'lights': [
            {
                'name': 'Main_Soft',
                'type': 'AREA',
                'intensity': 300.0,
                'color': (1.0, 1.0, 1.0),
                'size': 4.0,
                'azimuth': 0.0,
                'elevation': 60.0,
                'distance': 12.0,
                'area_shape': 'RECTANGLE',
                'area_size_y': 2.0
            },
            {
                'name': 'Fill_Ambient',
                'type': 'AREA',
                'intensity': 120.0,
                'color': (1.0, 1.0, 1.0),
                'size': 5.0,
                'azimuth': 180.0,
                'elevation': 30.0,
                'distance': 15.0,
                'area_shape': 'SQUARE'
            }
        ]
    },
    'DRAMATIC_HIGH': {
        'name': 'Dramatic High',
        'description': 'High-contrast dramatic lighting',
        'lights': [
            {
                'name': 'Key_Dramatic',
                'type': 'SPOT',
                'intensity': 400.0,
                'color': (1.0, 0.9, 0.8),
                'size': 0.5,
                'azimuth': 60.0,
                'elevation': 70.0,
                'distance': 8.0,
                'spot_angle': 30.0,
                'spot_blend': 0.3
            },
            {
                'name': 'Accent_Light',
                'type': 'POINT',
                'intensity': 100.0,
                'color': (0.8, 0.9, 1.0),
                'size': 0.2,
                'azimuth': -45.0,
                'elevation': 20.0,
                'distance': 5.0
            }
        ]
    },
    'OUTDOOR_SUN': {
        'name': 'Outdoor Sun',
        'description': 'Natural outdoor sun lighting',
        'lights': [
            {
                'name': 'Sun',
                'type': 'SUN',
                'intensity': 500.0,
                'color': (1.0, 0.95, 0.85),
                'size': 2.0,  # Sun angle
                'azimuth': 120.0,
                'elevation': 60.0,
                'distance': 50.0
            },
            {
                'name': 'Sky_Fill',
                'type': 'AREA',
                'intensity': 80.0,
                'color': (0.7, 0.8, 1.0),
                'size': 8.0,
                'azimuth': 0.0,
                'elevation': 90.0,
                'distance': 25.0,
                'area_shape': 'DISK'
            }
        ]
    },
    'AUTOMOTIVE': {
        'name': 'Automotive',
        'description': 'Car photography lighting',
        'lights': [
            {
                'name': 'Front_Key',
                'type': 'AREA',
                'intensity': 250.0,
                'color': (1.0, 1.0, 1.0),
                'size': 3.0,
                'azimuth': 30.0,
                'elevation': 45.0,
                'distance': 10.0,
                'area_shape': 'RECTANGLE',
                'area_size_y': 1.0
            },
            {
                'name': 'Side_Fill',
                'type': 'AREA',
                'intensity': 150.0,
                'color': (1.0, 1.0, 1.0),
                'size': 4.0,
                'azimuth': 90.0,
                'elevation': 30.0,
                'distance': 12.0,
                'area_shape': 'RECTANGLE',
                'area_size_y': 2.0
            },
            {
                'name': 'Rear_Accent',
                'type': 'AREA',
                'intensity': 180.0,
                'color': (0.9, 0.95, 1.0),
                'size': 2.0,
                'azimuth': 150.0,
                'elevation': 60.0,
                'distance': 8.0,
                'area_shape': 'SQUARE'
            }
        ]
    }
}

class HDRI_EDITOR_PT_light_library(Panel):
    """Light library panel with presets"""
    bl_label = "Light Library"
    bl_idname = "VIEW3D_PT_hdri_light_library"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'
    bl_parent_id = "VIEW3D_PT_hdri_lighting_manager"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PRESET')

    def draw(self, context):
        layout = self.layout
        
        # Preset categories
        box = layout.box()
        box.label(text="Lighting Presets:", icon='LIGHT_DATA')
        
        # Studio presets
        studio_col = box.column(align=True)
        studio_col.label(text="Studio:", icon='CAMERA_STEREO')
        
        row = studio_col.row(align=True)
        op = row.operator("hdri_lighting.apply_preset", text="3-Point")
        op.preset_name = 'STUDIO_3POINT'
        
        op = row.operator("hdri_lighting.apply_preset", text="Soft Product")
        op.preset_name = 'PRODUCT_SOFT'
        
        # Artistic presets
        artistic_col = box.column(align=True)
        artistic_col.label(text="Artistic:", icon='BRUSH_DATA')
        
        row = artistic_col.row(align=True)
        op = row.operator("hdri_lighting.apply_preset", text="Dramatic")
        op.preset_name = 'DRAMATIC_HIGH'
        
        op = row.operator("hdri_lighting.apply_preset", text="Outdoor")
        op.preset_name = 'OUTDOOR_SUN'
        
        # Specialized presets
        spec_col = box.column(align=True)  
        spec_col.label(text="Specialized:", icon='AUTO')
        
        row = spec_col.row(align=True)
        op = row.operator("hdri_lighting.apply_preset", text="Automotive")
        op.preset_name = 'AUTOMOTIVE'
        
        # Preset controls
        controls_box = layout.box()
        controls_box.label(text="Preset Controls:")
        
        controls_row = controls_box.row(align=True)
        controls_row.operator("hdri_lighting.clear_all_lights", text="Clear All", icon='TRASH')
        controls_row.operator("hdri_lighting.save_preset", text="Save Preset", icon='FILE_NEW')

class HDRI_LIGHTING_OT_apply_preset(Operator):
    """Apply a lighting preset"""
    bl_idname = "hdri_lighting.apply_preset"
    bl_label = "Apply Lighting Preset"
    bl_description = "Apply a pre-configured lighting setup"

    preset_name: EnumProperty(
        name="Preset",
        items=[
            ('STUDIO_3POINT', 'Studio 3-Point', 'Classic 3-point lighting'),
            ('PRODUCT_SOFT', 'Product Soft', 'Soft product lighting'),
            ('DRAMATIC_HIGH', 'Dramatic High', 'High-contrast dramatic'),
            ('OUTDOOR_SUN', 'Outdoor Sun', 'Natural outdoor lighting'),
            ('AUTOMOTIVE', 'Automotive', 'Car photography lighting'),
        ]
    )

    def execute(self, context):
        if self.preset_name not in LIGHT_PRESETS:
            self.report({'ERROR'}, f"Preset {self.preset_name} not found")
            return {'CANCELLED'}
            
        preset = LIGHT_PRESETS[self.preset_name]
        scene = context.scene
        
        # Initialize lighting manager if needed
        if not hasattr(scene, 'hdri_lighting'):
            return {'CANCELLED'}
            
        lighting = scene.hdri_lighting
        
        # Clear existing lights
        bpy.ops.hdri_lighting.clear_all_lights()
        
        # Create lights from preset
        for light_data in preset['lights']:
            # Add new light
            new_light = lighting.lights.add()
            
            # Apply preset properties
            for prop, value in light_data.items():
                if hasattr(new_light, prop):
                    setattr(new_light, prop, value)
            
            # Create Blender object
            self.create_blender_light(context, new_light, len(lighting.lights) - 1)
        
        # Select first light
        if len(lighting.lights) > 0:
            lighting.active_light_index = 0
        
        self.report({'INFO'}, f"Applied preset: {preset['name']}")
        return {'FINISHED'}

    def create_blender_light(self, context, light_props, index):
        """Create Blender light object from properties"""
        import math
        from mathutils import Vector
        
        # Create light data
        light_data = bpy.data.lights.new(name=light_props.name, type=light_props.light_type)
        
        # Set properties
        light_data.energy = light_props.intensity
        light_data.color = light_props.color
        
        if light_props.light_type == 'AREA':
            light_data.size = light_props.size
            light_data.shape = light_props.area_shape
            if light_props.area_shape in ['RECTANGLE', 'ELLIPSE']:
                light_data.size_y = light_props.area_size_y
                
        elif light_props.light_type == 'SPOT':
            light_data.spot_size = math.radians(light_props.spot_angle)
            light_data.spot_blend = light_props.spot_blend
            light_data.shadow_soft_size = light_props.size
            
        elif light_props.light_type in ['POINT']:
            light_data.shadow_soft_size = light_props.size
            
        elif light_props.light_type == 'SUN':
            light_data.angle = math.radians(light_props.size)

        # Create object
        light_obj = bpy.data.objects.new(name=light_props.name, object_data=light_data)
        
        # Position light
        self.position_light(light_obj, light_props)
        
        # Add to scene
        context.collection.objects.link(light_obj)
        
        # Tag for HDRI lighting system
        light_obj["hdri_light_index"] = index

    def position_light(self, light_obj, light_props):
        """Position light using spherical coordinates"""
        import math
        from mathutils import Vector
        
        # Convert spherical to cartesian
        az_rad = math.radians(light_props.azimuth)
        el_rad = math.radians(light_props.elevation)
        
        x = light_props.distance * math.cos(el_rad) * math.cos(az_rad)
        y = light_props.distance * math.cos(el_rad) * math.sin(az_rad) 
        z = light_props.distance * math.sin(el_rad)
        
        light_obj.location = (x, y, z)
        
        # Point light towards origin
        direction = Vector((0, 0, 0)) - light_obj.location
        if direction.length > 0:
            light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

class HDRI_LIGHTING_OT_clear_all_lights(Operator):
    """Clear all lights from the scene"""
    bl_idname = "hdri_lighting.clear_all_lights"
    bl_label = "Clear All Lights"
    bl_description = "Remove all HDRI lights from the scene"

    def execute(self, context):
        scene = context.scene
        
        if not hasattr(scene, 'hdri_lighting'):
            return {'CANCELLED'}
            
        lighting = scene.hdri_lighting
        
        # Remove all Blender light objects
        for light in lighting.lights:
            self.remove_blender_light(context, light.name)
        
        # Clear the list
        lighting.lights.clear()
        lighting.active_light_index = -1
        
        self.report({'INFO'}, "Cleared all lights")
        return {'FINISHED'}

    def remove_blender_light(self, context, light_name):
        """Remove Blender light object and data"""
        if light_name in bpy.data.objects:
            obj = bpy.data.objects[light_name]
            bpy.data.objects.remove(obj, do_unlink=True)
        if light_name in bpy.data.lights:
            light_data = bpy.data.lights[light_name]
            bpy.data.lights.remove(light_data)

class HDRI_LIGHTING_OT_save_preset(Operator):
    """Save current lighting as preset"""
    bl_idname = "hdri_lighting.save_preset"
    bl_label = "Save Lighting Preset"
    bl_description = "Save current lighting setup as a custom preset"

    def execute(self, context):
        # This is a placeholder - in a full implementation you'd 
        # save to a file or addon preferences
        scene = context.scene
        
        if not hasattr(scene, 'hdri_lighting'):
            self.report({'WARNING'}, "No lighting system found")
            return {'CANCELLED'}
            
        lighting = scene.hdri_lighting
        
        if len(lighting.lights) == 0:
            self.report({'WARNING'}, "No lights to save")
            return {'CANCELLED'}
        
        # For now, just report success
        self.report({'INFO'}, f"Saved {len(lighting.lights)} lights as preset (feature in development)")
        return {'FINISHED'}

# Classes for registration
classes = (
    HDRI_EDITOR_PT_light_library,
    HDRI_LIGHTING_OT_apply_preset,
    HDRI_LIGHTING_OT_clear_all_lights,
    HDRI_LIGHTING_OT_save_preset,
)

def register():
    """Register light library classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("HDRI Editor: Registered light library")

def unregister():
    """Unregister light library classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("HDRI Editor: Unregistered light library")