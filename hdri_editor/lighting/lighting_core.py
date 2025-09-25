"""
HDRI Lighting System for HDRI Editor.
Keyshot-inspired lighting tools for adding and managing lights in HDRI environments.
"""

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, EnumProperty, BoolProperty, IntProperty
import bmesh
import mathutils
from mathutils import Vector, Euler

# Import update handlers
from .property_handlers import update_light_property

class HDRILightProperties(PropertyGroup):
    """Properties for individual HDRI lights"""
    
    name: StringProperty(
        name="Light Name",
        description="Name of the light",
        default="Light"
    )
    
    light_type: EnumProperty(
        name="Light Type",
        description="Type of light",
        items=[
            ('SUN', 'Sun Light', 'Directional sun light'),
            ('POINT', 'Point Light', 'Omnidirectional point light'),
            ('SPOT', 'Spot Light', 'Cone-shaped spot light'),
            ('AREA', 'Area Light', 'Rectangular area light'),
        ],
        default='AREA'
    )
    
    intensity: FloatProperty(
        name="Intensity",
        description="Light intensity",
        default=100.0,
        min=0.0,
        max=10000.0,
        soft_max=1000.0,
        update=update_light_property
    )
    
    color: FloatVectorProperty(
        name="Color",
        description="Light color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        update=update_light_property
    )
    
    size: FloatProperty(
        name="Size",
        description="Light size",
        default=1.0,
        min=0.01,
        max=100.0,
        update=update_light_property
    )
    
    # Position in spherical coordinates (for HDRI placement)
    azimuth: FloatProperty(
        name="Azimuth",
        description="Horizontal angle (0-360 degrees)",
        default=0.0,
        min=0.0,
        max=360.0,
        subtype='ANGLE',
        update=update_light_property
    )
    
    elevation: FloatProperty(
        name="Elevation", 
        description="Vertical angle (-90 to 90 degrees)",
        default=0.0,
        min=-90.0,
        max=90.0,
        subtype='ANGLE',
        update=update_light_property
    )
    
    distance: FloatProperty(
        name="Distance",
        description="Distance from center",
        default=10.0,
        min=0.1,
        max=100.0,
        update=update_light_property
    )
    
    # Spot light specific
    spot_angle: FloatProperty(
        name="Spot Angle",
        description="Cone angle for spot light",
        default=45.0,
        min=1.0,
        max=180.0,
        subtype='ANGLE'
    )
    
    spot_blend: FloatProperty(
        name="Spot Blend",
        description="Spot light edge softness",
        default=0.15,
        min=0.0,
        max=1.0
    )
    
    # Area light specific
    area_shape: EnumProperty(
        name="Area Shape",
        description="Shape of area light",
        items=[
            ('SQUARE', 'Square', 'Square area light'),
            ('RECTANGLE', 'Rectangle', 'Rectangular area light'),
            ('DISK', 'Disk', 'Circular area light'),
            ('ELLIPSE', 'Ellipse', 'Elliptical area light'),
        ],
        default='SQUARE'
    )
    
    area_size_y: FloatProperty(
        name="Area Size Y",
        description="Area light Y size (for rectangle/ellipse)",
        default=1.0,
        min=0.01,
        max=100.0
    )

class HDRILightingManager(PropertyGroup):
    """Main lighting manager properties"""
    
    lights: bpy.props.CollectionProperty(type=HDRILightProperties)
    active_light_index: IntProperty(default=-1)
    
    show_light_objects: BoolProperty(
        name="Show Light Objects",
        description="Show light objects in 3D viewport",
        default=True
    )
    
    auto_update: BoolProperty(
        name="Auto Update",
        description="Automatically update lighting when properties change",
        default=True
    )

class HDRI_EDITOR_PT_lighting_manager(Panel):
    """Main lighting manager panel"""
    bl_label = "HDRI Lighting Studio"
    bl_idname = "VIEW3D_PT_hdri_lighting_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='LIGHT')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if not hasattr(scene, 'hdri_lighting'):
            layout.label(text="Lighting system not initialized", icon='ERROR')
            return
            
        lighting = scene.hdri_lighting
        
        # Main controls
        box = layout.box()
        box.label(text="Light Controls:", icon='LIGHT_SUN')
        
        row = box.row(align=True)
        row.operator("hdri_lighting.add_light", text="Add Light", icon='ADD')
        row.operator("hdri_lighting.remove_light", text="Remove", icon='REMOVE')
        row.operator("hdri_lighting.duplicate_light", text="Duplicate", icon='DUPLICATE')
        
        # Settings
        settings_row = box.row(align=True)
        settings_row.prop(lighting, "show_light_objects", toggle=True, icon='HIDE_OFF')
        settings_row.prop(lighting, "auto_update", toggle=True, icon='FILE_REFRESH')
        
        # Light list
        if len(lighting.lights) > 0:
            list_box = layout.box()
            list_box.label(text=f"Lights ({len(lighting.lights)}):", icon='OUTLINER_OB_LIGHT')
            
            for i, light in enumerate(lighting.lights):
                light_row = list_box.row(align=True)
                
                # Selection highlight
                if i == lighting.active_light_index:
                    light_row.alert = True
                
                # Light icon based on type
                icons = {'SUN': 'LIGHT_SUN', 'POINT': 'LIGHT_POINT', 
                        'SPOT': 'LIGHT_SPOT', 'AREA': 'LIGHT_AREA'}
                icon = icons.get(light.light_type, 'LIGHT')
                
                # Light name and selection
                op = light_row.operator("hdri_lighting.select_light", 
                                      text=f"{light.name} ({light.light_type})", 
                                      icon=icon)
                op.light_index = i
                
                # Quick intensity control
                light_row.prop(light, "intensity", text="")
                
                # Delete button
                op_del = light_row.operator("hdri_lighting.remove_specific_light", 
                                          text="", icon='X')
                op_del.light_index = i
        else:
            layout.label(text="No lights added", icon='INFO')

class HDRI_EDITOR_PT_light_properties(Panel):
    """Light properties panel"""
    bl_label = "Light Properties"
    bl_idname = "VIEW3D_PT_hdri_light_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'
    bl_parent_id = "VIEW3D_PT_hdri_lighting_manager"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (hasattr(context.scene, 'hdri_lighting') and 
                context.scene.hdri_lighting.active_light_index >= 0 and
                len(context.scene.hdri_lighting.lights) > 0)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PROPERTIES')

    def draw(self, context):
        layout = self.layout
        lighting = context.scene.hdri_lighting
        
        if lighting.active_light_index < 0 or lighting.active_light_index >= len(lighting.lights):
            layout.label(text="No light selected", icon='INFO')
            return
            
        light = lighting.lights[lighting.active_light_index]
        
        # Basic properties
        basic_box = layout.box()
        basic_box.label(text="Basic Properties:")
        basic_box.prop(light, "name")
        basic_box.prop(light, "light_type")
        basic_box.prop(light, "intensity")
        basic_box.prop(light, "color")
        
        # Position properties
        pos_box = layout.box()
        pos_box.label(text="Position (Spherical):")
        pos_box.prop(light, "azimuth", slider=True)
        pos_box.prop(light, "elevation", slider=True)
        pos_box.prop(light, "distance")
        
        # Type-specific properties
        if light.light_type in ['AREA', 'SPOT']:
            size_box = layout.box()
            size_box.label(text="Size Properties:")
            size_box.prop(light, "size")
            
            if light.light_type == 'AREA':
                size_box.prop(light, "area_shape")
                if light.area_shape in ['RECTANGLE', 'ELLIPSE']:
                    size_box.prop(light, "area_size_y")
                    
            elif light.light_type == 'SPOT':
                size_box.prop(light, "spot_angle", slider=True)
                size_box.prop(light, "spot_blend", slider=True)
        
        # Quick actions
        actions_box = layout.box()
        actions_box.label(text="Actions:")
        actions_row = actions_box.row(align=True)
        actions_row.operator("hdri_lighting.focus_light", text="Focus", icon='ZOOM_SELECTED')
        actions_row.operator("hdri_lighting.reset_light", text="Reset", icon='RECOVER_LAST')
        
        copy_paste_row = actions_box.row(align=True)
        copy_paste_row.operator("hdri_lighting.copy_light", text="Copy", icon='COPYDOWN')
        copy_paste_row.operator("hdri_lighting.paste_light", text="Paste", icon='PASTEDOWN')
        
        update_row = actions_box.row()
        update_row.operator("hdri_lighting.update_all_lights", text="Update All Lights", icon='FILE_REFRESH')

# Operators
class HDRI_LIGHTING_OT_add_light(Operator):
    """Add a new light to the HDRI setup"""
    bl_idname = "hdri_lighting.add_light"
    bl_label = "Add HDRI Light"
    bl_description = "Add a new light to the HDRI lighting setup"

    light_type: EnumProperty(
        name="Light Type",
        items=[
            ('SUN', 'Sun Light', 'Add sun light'),
            ('POINT', 'Point Light', 'Add point light'),
            ('SPOT', 'Spot Light', 'Add spot light'),
            ('AREA', 'Area Light', 'Add area light'),
        ],
        default='AREA'
    )

    def execute(self, context):
        scene = context.scene
        
        # Initialize lighting manager if needed
        if not hasattr(scene, 'hdri_lighting'):
            return {'CANCELLED'}
            
        lighting = scene.hdri_lighting
        
        # Create new light properties
        new_light = lighting.lights.add()
        new_light.name = f"Light_{len(lighting.lights):02d}"
        new_light.light_type = self.light_type
        
        # Set default position based on number of lights
        angle_step = 360.0 / max(1, len(lighting.lights))
        new_light.azimuth = (len(lighting.lights) - 1) * angle_step
        new_light.elevation = 30.0
        
        # Create actual Blender light object
        self.create_blender_light(context, new_light, len(lighting.lights) - 1)
        
        # Select the new light
        lighting.active_light_index = len(lighting.lights) - 1
        
        self.report({'INFO'}, f"Added {self.light_type} light")
        return {'FINISHED'}

    def create_blender_light(self, context, light_props, index):
        """Create actual Blender light object"""
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
            light_data.spot_size = light_props.spot_angle
            light_data.spot_blend = light_props.spot_blend
            
        elif light_props.light_type in ['POINT', 'SPOT']:
            light_data.shadow_soft_size = light_props.size

        # Create object
        light_obj = bpy.data.objects.new(name=light_props.name, object_data=light_data)
        
        # Position light using spherical coordinates
        self.position_light(light_obj, light_props)
        
        # Add to scene
        context.collection.objects.link(light_obj)
        
        # Tag for HDRI lighting system
        light_obj["hdri_light_index"] = index

    def position_light(self, light_obj, light_props):
        """Position light using spherical coordinates"""
        import math
        
        # Convert spherical to cartesian
        az_rad = math.radians(light_props.azimuth)
        el_rad = math.radians(light_props.elevation)
        
        x = light_props.distance * math.cos(el_rad) * math.cos(az_rad)
        y = light_props.distance * math.cos(el_rad) * math.sin(az_rad) 
        z = light_props.distance * math.sin(el_rad)
        
        light_obj.location = (x, y, z)
        
        # Point light towards origin
        direction = Vector((0, 0, 0)) - light_obj.location
        light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class HDRI_LIGHTING_OT_remove_light(Operator):
    """Remove the active light"""
    bl_idname = "hdri_lighting.remove_light"
    bl_label = "Remove Active Light"
    bl_description = "Remove the currently selected light"

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        if lighting.active_light_index < 0 or lighting.active_light_index >= len(lighting.lights):
            self.report({'WARNING'}, "No light selected")
            return {'CANCELLED'}
            
        # Remove Blender object
        light_props = lighting.lights[lighting.active_light_index]
        self.remove_blender_light(context, light_props.name)
        
        # Remove from list
        lighting.lights.remove(lighting.active_light_index)
        
        # Adjust active index
        if lighting.active_light_index >= len(lighting.lights):
            lighting.active_light_index = len(lighting.lights) - 1
            
        self.report({'INFO'}, "Light removed")
        return {'FINISHED'}

    def remove_blender_light(self, context, light_name):
        """Remove Blender light object"""
        if light_name in bpy.data.objects:
            obj = bpy.data.objects[light_name]
            bpy.data.objects.remove(obj, do_unlink=True)
        if light_name in bpy.data.lights:
            light_data = bpy.data.lights[light_name]
            bpy.data.lights.remove(light_data)

class HDRI_LIGHTING_OT_select_light(Operator):
    """Select a specific light"""
    bl_idname = "hdri_lighting.select_light"
    bl_label = "Select Light"
    bl_description = "Select a specific light for editing"

    light_index: IntProperty()

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        lighting.active_light_index = self.light_index
        
        # Select object in viewport
        light = lighting.lights[self.light_index]
        if light.name in bpy.data.objects:
            bpy.context.view_layer.objects.active = bpy.data.objects[light.name]
            
        return {'FINISHED'}

# Import additional operators
from .light_operators import (
    HDRI_LIGHTING_OT_remove_specific_light,
    HDRI_LIGHTING_OT_duplicate_light,
    HDRI_LIGHTING_OT_focus_light,
    HDRI_LIGHTING_OT_reset_light,
    HDRI_LIGHTING_OT_copy_light,
    HDRI_LIGHTING_OT_paste_light,
    HDRI_LIGHTING_OT_update_all_lights,
)

# Classes for registration
classes = (
    HDRILightProperties,
    HDRILightingManager,
    HDRI_EDITOR_PT_lighting_manager,
    HDRI_EDITOR_PT_light_properties,
    HDRI_LIGHTING_OT_add_light,
    HDRI_LIGHTING_OT_remove_light,
    HDRI_LIGHTING_OT_select_light,
    HDRI_LIGHTING_OT_remove_specific_light,
    HDRI_LIGHTING_OT_duplicate_light,
    HDRI_LIGHTING_OT_focus_light,
    HDRI_LIGHTING_OT_reset_light,
    HDRI_LIGHTING_OT_copy_light,
    HDRI_LIGHTING_OT_paste_light,
    HDRI_LIGHTING_OT_update_all_lights,
)

def register():
    """Register lighting system classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add properties to scene
    bpy.types.Scene.hdri_lighting = bpy.props.PointerProperty(type=HDRILightingManager)
    
    # Register property handlers
    from .property_handlers import register_handlers
    register_handlers()
    
    print("HDRI Editor: Registered lighting system")

def unregister():
    """Unregister lighting system classes"""
    # Unregister property handlers
    from .property_handlers import unregister_handlers
    unregister_handlers()
    
    # Remove properties
    if hasattr(bpy.types.Scene, 'hdri_lighting'):
        del bpy.types.Scene.hdri_lighting
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("HDRI Editor: Unregistered lighting system")