"""
Additional lighting operators for HDRI Editor.
Keyshot-inspired lighting controls.
"""

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty
import mathutils
from mathutils import Vector
import math

class HDRI_LIGHTING_OT_remove_specific_light(Operator):
    """Remove a specific light by index"""
    bl_idname = "hdri_lighting.remove_specific_light"
    bl_label = "Remove Specific Light"
    bl_description = "Remove a specific light from the setup"

    light_index: IntProperty()

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        if self.light_index < 0 or self.light_index >= len(lighting.lights):
            return {'CANCELLED'}
            
        # Remove Blender object
        light_props = lighting.lights[self.light_index]
        self.remove_blender_light(context, light_props.name)
        
        # Remove from list
        lighting.lights.remove(self.light_index)
        
        # Adjust active index
        if lighting.active_light_index == self.light_index:
            lighting.active_light_index = -1
        elif lighting.active_light_index > self.light_index:
            lighting.active_light_index -= 1
            
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

class HDRI_LIGHTING_OT_duplicate_light(Operator):
    """Duplicate the active light"""
    bl_idname = "hdri_lighting.duplicate_light"
    bl_label = "Duplicate Light"
    bl_description = "Duplicate the currently selected light"

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        if lighting.active_light_index < 0 or lighting.active_light_index >= len(lighting.lights):
            self.report({'WARNING'}, "No light selected")
            return {'CANCELLED'}
            
        # Get source light
        source_light = lighting.lights[lighting.active_light_index]
        
        # Create new light
        new_light = lighting.lights.add()
        
        # Copy properties
        for prop in source_light.__annotations__.keys():
            if hasattr(source_light, prop) and hasattr(new_light, prop):
                setattr(new_light, prop, getattr(source_light, prop))
        
        # Modify name and position slightly
        new_light.name = f"{source_light.name}_copy"
        new_light.azimuth = (source_light.azimuth + 30) % 360
        
        # Create Blender object
        self.create_blender_light(context, new_light, len(lighting.lights) - 1)
        
        # Select new light
        lighting.active_light_index = len(lighting.lights) - 1
        
        self.report({'INFO'}, f"Duplicated light: {new_light.name}")
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
            light_data.spot_size = math.radians(light_props.spot_angle)
            light_data.spot_blend = light_props.spot_blend
            
        elif light_props.light_type in ['POINT', 'SPOT']:
            light_data.shadow_soft_size = light_props.size

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

class HDRI_LIGHTING_OT_focus_light(Operator):
    """Focus viewport on the active light"""
    bl_idname = "hdri_lighting.focus_light"
    bl_label = "Focus on Light"
    bl_description = "Focus the 3D viewport on the selected light"

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        if lighting.active_light_index < 0 or lighting.active_light_index >= len(lighting.lights):
            self.report({'WARNING'}, "No light selected")
            return {'CANCELLED'}
            
        light = lighting.lights[lighting.active_light_index]
        
        # Find light object
        if light.name in bpy.data.objects:
            light_obj = bpy.data.objects[light.name]
            
            # Select and make active
            bpy.ops.object.select_all(action='DESELECT')
            light_obj.select_set(True)
            context.view_layer.objects.active = light_obj
            
            # Focus view
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = context.copy()
                            override['area'] = area
                            override['region'] = region
                            with context.temp_override(**override):
                                bpy.ops.view3d.view_selected(use_all_regions=False)
                            break
                    break
            
            self.report({'INFO'}, f"Focused on {light.name}")
        else:
            self.report({'WARNING'}, f"Light object {light.name} not found")
            
        return {'FINISHED'}

class HDRI_LIGHTING_OT_reset_light(Operator):
    """Reset light properties to defaults"""
    bl_idname = "hdri_lighting.reset_light"
    bl_label = "Reset Light"
    bl_description = "Reset the selected light to default properties"

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        if lighting.active_light_index < 0 or lighting.active_light_index >= len(lighting.lights):
            self.report({'WARNING'}, "No light selected")
            return {'CANCELLED'}
            
        light = lighting.lights[lighting.active_light_index]
        
        # Reset properties
        light.intensity = 100.0
        light.color = (1.0, 1.0, 1.0)
        light.size = 1.0
        light.azimuth = 0.0
        light.elevation = 0.0
        light.distance = 10.0
        light.spot_angle = 45.0
        light.spot_blend = 0.15
        light.area_size_y = 1.0
        
        # Update Blender object
        self.update_blender_light(context, light)
        
        self.report({'INFO'}, f"Reset {light.name}")
        return {'FINISHED'}

    def update_blender_light(self, context, light_props):
        """Update Blender light object properties"""
        if light_props.name in bpy.data.objects:
            light_obj = bpy.data.objects[light_props.name]
            light_data = light_obj.data
            
            # Update properties
            light_data.energy = light_props.intensity
            light_data.color = light_props.color
            
            if light_props.light_type == 'AREA':
                light_data.size = light_props.size
                if light_props.area_shape in ['RECTANGLE', 'ELLIPSE']:
                    light_data.size_y = light_props.area_size_y
                    
            elif light_props.light_type == 'SPOT':
                light_data.spot_size = math.radians(light_props.spot_angle)
                light_data.spot_blend = light_props.spot_blend
                
            elif light_props.light_type in ['POINT', 'SPOT']:
                light_data.shadow_soft_size = light_props.size
            
            # Update position
            self.position_light(light_obj, light_props)

    def position_light(self, light_obj, light_props):
        """Position light using spherical coordinates"""
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

class HDRI_LIGHTING_OT_copy_light(Operator):
    """Copy light settings to clipboard"""
    bl_idname = "hdri_lighting.copy_light"
    bl_label = "Copy Light Settings"
    bl_description = "Copy current light settings for pasting"

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        if lighting.active_light_index < 0 or lighting.active_light_index >= len(lighting.lights):
            self.report({'WARNING'}, "No light selected")
            return {'CANCELLED'}
            
        light = lighting.lights[lighting.active_light_index]
        
        # Store in scene for later pasting
        if not hasattr(context.scene, 'hdri_lighting_clipboard'):
            context.scene['hdri_lighting_clipboard'] = {}
            
        clipboard = {}
        for prop in light.__annotations__.keys():
            if hasattr(light, prop):
                value = getattr(light, prop)
                if isinstance(value, mathutils.Color):
                    clipboard[prop] = tuple(value)
                else:
                    clipboard[prop] = value
                    
        context.scene['hdri_lighting_clipboard'] = clipboard
        
        self.report({'INFO'}, f"Copied settings from {light.name}")
        return {'FINISHED'}

class HDRI_LIGHTING_OT_paste_light(Operator):
    """Paste light settings from clipboard"""
    bl_idname = "hdri_lighting.paste_light"
    bl_label = "Paste Light Settings"
    bl_description = "Paste copied light settings to current light"

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        if lighting.active_light_index < 0 or lighting.active_light_index >= len(lighting.lights):
            self.report({'WARNING'}, "No light selected")
            return {'CANCELLED'}
            
        if 'hdri_lighting_clipboard' not in context.scene:
            self.report({'WARNING'}, "No copied light settings")
            return {'CANCELLED'}
            
        light = lighting.lights[lighting.active_light_index]
        clipboard = context.scene['hdri_lighting_clipboard']
        
        # Apply settings (except name)
        for prop, value in clipboard.items():
            if prop != 'name' and hasattr(light, prop):
                setattr(light, prop, value)
        
        # Update Blender object
        self.update_blender_light(context, light)
        
        self.report({'INFO'}, f"Pasted settings to {light.name}")
        return {'FINISHED'}

    def update_blender_light(self, context, light_props):
        """Update Blender light object properties"""
        if light_props.name in bpy.data.objects:
            light_obj = bpy.data.objects[light_props.name]
            light_data = light_obj.data
            
            # Update properties
            light_data.energy = light_props.intensity
            light_data.color = light_props.color
            
            if light_props.light_type == 'AREA':
                light_data.size = light_props.size
                if light_props.area_shape in ['RECTANGLE', 'ELLIPSE']:
                    light_data.size_y = light_props.area_size_y
                    
            elif light_props.light_type == 'SPOT':
                light_data.spot_size = math.radians(light_props.spot_angle)
                light_data.spot_blend = light_props.spot_blend
                
            elif light_props.light_type in ['POINT', 'SPOT']:
                light_data.shadow_soft_size = light_props.size
            
            # Update position
            self.position_light(light_obj, light_props)

    def position_light(self, light_obj, light_props):
        """Position light using spherical coordinates"""
        az_rad = math.radians(light_props.azimuth)
        el_rad = math.radians(light_props.elevation)
        
        x = light_props.distance * math.cos(el_rad) * math.cos(az_rad)
        y = light_props.distance * math.cos(el_rad) * math.sin(az_rad) 
        z = light_props.distance * math.sin(el_rad)
        
        light_obj.location = (x, y, z)
        
        # Point light towards origin
        direction = Vector((0, 0, 0)) - light_obj.location
        light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

class HDRI_LIGHTING_OT_update_all_lights(Operator):
    """Update all light objects from properties"""
    bl_idname = "hdri_lighting.update_all_lights"
    bl_label = "Update All Lights"
    bl_description = "Update all Blender light objects from stored properties"

    def execute(self, context):
        lighting = context.scene.hdri_lighting
        
        updated_count = 0
        for i, light in enumerate(lighting.lights):
            if self.update_blender_light(context, light):
                updated_count += 1
        
        self.report({'INFO'}, f"Updated {updated_count} lights")
        return {'FINISHED'}

    def update_blender_light(self, context, light_props):
        """Update individual Blender light object"""
        if light_props.name not in bpy.data.objects:
            return False
            
        light_obj = bpy.data.objects[light_props.name]
        light_data = light_obj.data
        
        try:
            # Update properties
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
                
            elif light_props.light_type in ['POINT', 'SPOT']:
                light_data.shadow_soft_size = light_props.size
            
            # Update position
            self.position_light(light_obj, light_props)
            return True
            
        except Exception as e:
            print(f"Error updating light {light_props.name}: {e}")
            return False

    def position_light(self, light_obj, light_props):
        """Position light using spherical coordinates"""
        az_rad = math.radians(light_props.azimuth)
        el_rad = math.radians(light_props.elevation)
        
        x = light_props.distance * math.cos(el_rad) * math.cos(az_rad)
        y = light_props.distance * math.cos(el_rad) * math.sin(az_rad) 
        z = light_props.distance * math.sin(el_rad)
        
        light_obj.location = (x, y, z)
        
        # Point light towards origin
        direction = Vector((0, 0, 0)) - light_obj.location
        light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Classes for registration
classes = (
    HDRI_LIGHTING_OT_remove_specific_light,
    HDRI_LIGHTING_OT_duplicate_light,
    HDRI_LIGHTING_OT_focus_light,
    HDRI_LIGHTING_OT_reset_light,
    HDRI_LIGHTING_OT_copy_light,
    HDRI_LIGHTING_OT_paste_light,
    HDRI_LIGHTING_OT_update_all_lights,
)

def register():
    """Register lighting operator classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("HDRI Editor: Registered lighting operators")

def unregister():
    """Unregister lighting operator classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("HDRI Editor: Unregistered lighting operators")