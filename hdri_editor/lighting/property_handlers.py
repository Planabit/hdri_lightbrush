"""
Property update handlers for HDRI Lighting system.
Automatically updates Blender light objects when properties change.
"""

import bpy
import mathutils
from mathutils import Vector
import math

def update_light_property(self, context):
    """Update callback for light properties"""
    if not hasattr(context.scene, 'hdri_lighting'):
        return
        
    lighting = context.scene.hdri_lighting
    
    # Find which light was updated
    light_index = -1
    for i, light in enumerate(lighting.lights):
        if light == self:
            light_index = i
            break
            
    if light_index == -1:
        return
        
    # Update the corresponding Blender light object
    update_blender_light(context, self)

def update_blender_light(context, light_props):
    """Update Blender light object from properties"""
    if not light_props.name:
        return
        
    # Find or create light object
    light_obj = None
    light_data = None
    
    if light_props.name in bpy.data.objects:
        light_obj = bpy.data.objects[light_props.name]
        light_data = light_obj.data
        
        # Check if type changed - recreate if needed
        if light_data.type != light_props.light_type:
            # Remove old object and data
            bpy.data.objects.remove(light_obj, do_unlink=True)
            bpy.data.lights.remove(light_data)
            light_obj = None
            light_data = None
    
    # Create new light if needed
    if light_obj is None:
        light_data = bpy.data.lights.new(name=light_props.name, type=light_props.light_type)
        light_obj = bpy.data.objects.new(name=light_props.name, object_data=light_data)
        context.collection.objects.link(light_obj)
    
    try:
        # Update basic properties
        light_data.energy = light_props.intensity
        light_data.color = light_props.color
        
        # Update type-specific properties
        if light_props.light_type == 'AREA':
            light_data.size = light_props.size
            light_data.shape = light_props.area_shape
            if light_props.area_shape in ['RECTANGLE', 'ELLIPSE']:
                light_data.size_y = light_props.area_size_y
                
        elif light_props.light_type == 'SPOT':
            light_data.spot_size = math.radians(light_props.spot_angle)
            light_data.spot_blend = light_props.spot_blend
            light_data.shadow_soft_size = light_props.size
            
        elif light_props.light_type in ['POINT', 'SUN']:
            if light_props.light_type == 'POINT':
                light_data.shadow_soft_size = light_props.size
            elif light_props.light_type == 'SUN':
                light_data.angle = math.radians(light_props.size)  # Sun light uses angle instead of size
        
        # Update position using spherical coordinates
        position_light(light_obj, light_props)
        
        # Force viewport update
        if context.view_layer:
            context.view_layer.update()
            
    except Exception as e:
        print(f"HDRI Lighting: Error updating light {light_props.name}: {e}")

def position_light(light_obj, light_props):
    """Position light using spherical coordinates"""
    try:
        # Convert spherical to cartesian coordinates
        az_rad = math.radians(light_props.azimuth)
        el_rad = math.radians(light_props.elevation)
        
        x = light_props.distance * math.cos(el_rad) * math.cos(az_rad)
        y = light_props.distance * math.cos(el_rad) * math.sin(az_rad) 
        z = light_props.distance * math.sin(el_rad)
        
        light_obj.location = (x, y, z)
        
        # Point light towards origin (like KeyShot)
        direction = Vector((0, 0, 0)) - light_obj.location
        if direction.length > 0:
            light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        
    except Exception as e:
        print(f"HDRI Lighting: Error positioning light: {e}")

def auto_update_enabled(context):
    """Check if auto-update is enabled"""
    if not hasattr(context.scene, 'hdri_lighting'):
        return False
    return context.scene.hdri_lighting.auto_update

# Handler for scene updates
@bpy.app.handlers.persistent
def scene_update_handler(scene, depsgraph):
    """Handle scene updates for lighting synchronization"""
    if not hasattr(scene, 'hdri_lighting'):
        return
        
    lighting = scene.hdri_lighting
    if not lighting.auto_update:
        return
        
    # Check if any HDRI lights were moved in viewport
    for i, light_props in enumerate(lighting.lights):
        if light_props.name in bpy.data.objects:
            light_obj = bpy.data.objects[light_props.name]
            
            # Convert current object position back to spherical coordinates
            loc = light_obj.location
            if loc.length > 0.01:  # Avoid division by zero
                distance = loc.length
                
                # Calculate elevation (latitude)
                elevation = math.degrees(math.asin(loc.z / distance))
                
                # Calculate azimuth (longitude)
                azimuth = math.degrees(math.atan2(loc.y, loc.x))
                if azimuth < 0:
                    azimuth += 360
                
                # Update properties without triggering infinite loop
                if abs(light_props.distance - distance) > 0.1:
                    light_props.distance = distance
                if abs(light_props.elevation - elevation) > 1.0:
                    light_props.elevation = elevation  
                if abs(light_props.azimuth - azimuth) > 1.0:
                    light_props.azimuth = azimuth

def register_handlers():
    """Register update handlers"""
    # Add scene update handler if not already registered
    if scene_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(scene_update_handler)
        print("HDRI Lighting: Registered scene update handler")

def unregister_handlers():
    """Unregister update handlers"""
    # Remove scene update handler
    if scene_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(scene_update_handler)
        print("HDRI Lighting: Unregistered scene update handler")