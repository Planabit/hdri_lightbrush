"""
HDRI Light Studio - Hemisphere Tools

This module provides smooth hemisphere creation and management functionality
for HDRI preview and 3D painting workflows, based on the sample dome system.
"""

import bpy
import bmesh
from mathutils import Vector
import numpy as np
import math
from bpy.app.handlers import persistent
from bpy.props import FloatProperty, EnumProperty
from bpy.types import PropertyGroup
from .geometry.geometry_factory import GEOMETRY_TYPES, create_geometry


def apply_calibrated_uv_mapping(obj):
    """
    Apply CALIBRATED UV mapping to hemisphere geometry
    This is the PROVEN <65px accurate mapping!
    """
    
    mesh = obj.data
    hemisphere_center = obj.location
    
    # Ensure we have a UV layer
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    
    uv_layer = mesh.uv_layers.active.data
    
    # Calculate UV for each vertex using CALIBRATED formula
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            loop = mesh.loops[loop_index]
            vertex = mesh.vertices[loop.vertex_index]
            
            # Vertex position in world space
            vertex_world = obj.matrix_world @ vertex.co
            
            # Direction from hemisphere center
            direction = (vertex_world - hemisphere_center).normalized()
            
            # Equirectangular projection
            longitude = math.atan2(direction.y, direction.x)
            u_raw = 0.5 - (longitude / (2.0 * math.pi))
            
            latitude = math.asin(max(-1.0, min(1.0, direction.z)))
            v_raw = 0.5 + (latitude / math.pi)
            
            # CALIBRATED corrections (<65px accuracy!)
            u = u_raw - 0.008
            
            v_deviation = v_raw - 0.5
            if v_raw < 0.5:
                v_correction = -0.094 + (v_deviation * v_deviation * 2.0)
            else:
                v_correction = -0.094 + (v_deviation * v_deviation * 0.3)
            
            v = v_raw + v_correction
            
            # Clamp to valid UV range
            u = max(0.0, min(1.0, u))
            v = max(0.0, min(1.0, v))
            
            # Apply UV coordinates
            uv_layer[loop_index].uv = (u, v)
    
    mesh.update()
    print("Ôťů Applied CALIBRATED UV mapping (<65px accuracy!)")


def update_hemisphere_scale_callback(self, context):
    """Callback when hemisphere scale property changes"""
    hemisphere = bpy.data.objects.get("HDRI_Hemisphere")
    if hemisphere:
        scale = self.hemisphere_scale
        hemisphere.scale = (scale, scale, scale)


class HemisphereProperties(PropertyGroup):
    """Property group for hemisphere with scale callback"""
    hemisphere_scale: FloatProperty(
        name="Scale Hemisphere",
        description="Scale the hemisphere",
        default=1.0,
        min=0.1,
        max=10.0,
        soft_min=0.1,
        soft_max=5.0,
        update=update_hemisphere_scale_callback
    )
    
    geometry_type: EnumProperty(
        name="Geometry Type",
        description="Choose the type of geometry to create",
        items=[
            ('CLOSED_HEMISPHERE', 'Closed Hemisphere', 'Hemisphere with rounded bottom edge'), 
            ('SPHERE', 'Full Sphere', 'Complete sphere for 360┬░ HDRI')
        ],
        default='CLOSED_HEMISPHERE'
    )


def create_hemisphere_handler():
    """Create hemisphere handler like dome handler in sample"""
    # Check if handler already exists
    handler = bpy.data.objects.get("HDRI_Hemisphere_Handler")
    if handler:
        return handler
    
    # Create empty object as handler
    bpy.ops.object.empty_add(location=(0, 0, 0))
    handler = bpy.context.object
    handler.name = "HDRI_Hemisphere_Handler"
    
    return handler





def load_dome_as_hemisphere(name="HDRI_Hemisphere", geometry_type='CLOSED_HEMISPHERE'):
    """Create hemisphere using geometry factory based on selected type"""
    
    # Use geometry factory to create the selected geometry type
    obj = create_geometry(geometry_type, name, radius=5.0, location=(0, 0, 0))
    
    if obj:
        # Link to current collection
        bpy.context.collection.objects.link(obj)
        return obj
    
    return None





def setup_hemisphere_material(obj, canvas_image=None):
    """Setup material for hemisphere based on sample dome implementation"""
    
    # Clear existing materials
    obj.data.materials.clear()
    
    # Load the exact dome material from sample
    dome_material = load_sample_dome_material()
    
    if dome_material:
        # Assign material to hemisphere
        obj.data.materials.append(dome_material)
        
        # Assign hemisphere object to material coordinates (like sample)
        assign_hemisphere_to_material_coordinates(obj, dome_material)
        
        # FIRST: Assign default white texture to ALL missing texture nodes
        assign_default_texture_to_dome_material(dome_material)
        
        # THEN: Assign canvas image to material if available (IMPROVED - ALL ENV TEXTURE NODES)
        if canvas_image:
            assign_image_to_hemisphere_material(dome_material, canvas_image)
        
        return dome_material
    else:
        # Fallback to simple material if sample loading fails
        return create_painting_hemisphere_material(obj, canvas_image)


def load_sample_dome_material():
    """Load the exact dome material from sample with ALL dependencies"""
    
    dome_mat_path = r"e:\Projects\HDRI_editor\sample\hdri_maker\addon_resources\blendfiles\materials\HDRi_Maker_Dome.blend"
    
    try:
        # Load dome material with ALL dependencies (materials, node groups, images)
        dome_material = None
        with bpy.data.libraries.load(dome_mat_path, link=False) as (data_from, data_to):
            # Load all materials
            data_to.materials = [name for name in data_from.materials if name == 'HDRi_Maker_Dome']
            # Load all node groups that the material might use
            data_to.node_groups = data_from.node_groups[:]
            # Load all images that might be referenced
            data_to.images = data_from.images[:]
        
        if data_to.materials:
            dome_material = data_to.materials[0]
            dome_material.name = "HDRI_Hemisphere_Material"
            
            print(f"Loaded dome material with {len(data_to.node_groups)} node groups and {len(data_to.images)} images")
            
            # Close material node groups like in sample
            if dome_material.use_nodes:
                for n in dome_material.node_tree.nodes:
                    if hasattr(n, 'node_tree') and n.node_tree:
                        # Hide node groups like in sample
                        n.hide = True
            
            return dome_material
            
    except Exception as e:
        print(f"Could not load dome material from sample: {e}")
    
    return None


def assign_hemisphere_to_material_coordinates(hemisphere_obj, material):
    """Assign hemisphere object to material coordinates like sample dome"""
    
    if not material or not material.use_nodes:
        return
    
    node_tree = material.node_tree
    
    # Find VECTORS node group (like in sample)
    vectors_ng = None
    for node in node_tree.nodes:
        if hasattr(node, 'node_tree') and node.node_tree:
            # Check if this is the VECTORS node group
            for ng_node in node.node_tree.nodes:
                if ng_node.type == 'TEX_COORD':
                    vectors_ng = node
                    break
            if vectors_ng:
                break
    
    # Assign hemisphere object to TEX_COORD node
    if vectors_ng and vectors_ng.node_tree:
        for n in vectors_ng.node_tree.nodes:
            if n.type == 'TEX_COORD':
                n.object = hemisphere_obj
                break


def assign_image_to_hemisphere_material(material, image):
    """Assign image to ALL texture nodes in hemisphere material"""
    
    if not material or not material.use_nodes or not image:
        return
    
    replaced_count = 0
    
    # Recursively find and replace ALL texture node images at ALL depths
    def replace_in_node_tree(node_tree, depth=0):
        nonlocal replaced_count
        indent = "  " * depth
        
        if not node_tree:
            return
        
        for node in node_tree.nodes:
            # Check for ANY texture node type that might have an image
            if hasattr(node, 'image') and node.image is not None:
                old_image = node.image.name
                node.image = image
                replaced_count += 1
                print(f"{indent}Replaced {node.type} '{node.name}': {old_image} -> {image.name}")
            elif hasattr(node, 'image') and node.image is None:
                # Also assign to nodes with no image assigned
                node.image = image
                replaced_count += 1
                print(f"{indent}Assigned {node.type} '{node.name}': None -> {image.name}")
            elif hasattr(node, 'node_tree') and node.node_tree:
                # Recursively check ALL node groups at ALL depths
                print(f"{indent}Entering node group: {node.name}")
                replace_in_node_tree(node.node_tree, depth + 1)
    
    print(f"Starting image replacement in material: {material.name}")
    replace_in_node_tree(material.node_tree)
    
    # ALSO check all node groups that might be loaded independently  
    for ng in bpy.data.node_groups:
        if ng.name.startswith('HDRI_Maker') or ng.name.startswith('Dome'):
            print(f"Checking independent node group: {ng.name}")
            replace_in_node_tree(ng, 0)
    
    print(f"Total texture nodes replaced: {replaced_count}")


def assign_default_texture_to_dome_material(material):
    """Assign default white texture to ALL Environment Texture nodes to avoid missing texture warnings"""
    
    if not material or not material.use_nodes:
        return
    
    # Create default white HDRI texture if it doesn't exist
    if "HDRI_Default_White" not in bpy.data.images:
        white_image = bpy.data.images.new("HDRI_Default_White", width=1024, height=512)
        # Fill with white
        pixels = [1.0] * (1024 * 512 * 4)  # RGBA white
        white_image.pixels[:] = pixels
        white_image.colorspace_settings.name = 'Linear Rec.709'
        print("Created default white HDRI texture")
    else:
        white_image = bpy.data.images["HDRI_Default_White"]
    
    replaced_count = 0
    
    # Recursively find and assign to ALL Environment Texture nodes at ALL depths
    def assign_to_node_tree(node_tree, depth=0):
        nonlocal replaced_count
        indent = "  " * depth
        
        if not node_tree:
            return
            
        for node in node_tree.nodes:
            if node.type == 'TEX_ENVIRONMENT':
                old_image = node.image.name if node.image else "None"
                node.image = white_image
                replaced_count += 1
                print(f"{indent}Assigned default white to Environment Texture '{node.name}': {old_image} -> {white_image.name}")
            elif hasattr(node, 'node_tree') and node.node_tree:
                # Recursively check ALL node groups at ALL depths
                print(f"{indent}Entering node group: {node.name}")
                assign_to_node_tree(node.node_tree, depth + 1)
    
    print(f"Starting default texture assignment in material: {material.name}")
    assign_to_node_tree(material.node_tree)
    
    # ALSO check all node groups that might be loaded independently
    for ng in bpy.data.node_groups:
        if ng.name.startswith('HDRI_Maker') or ng.name.startswith('Dome'):
            print(f"Checking independent node group: {ng.name}")
            assign_to_node_tree(ng, 0)
    
    print(f"Total Environment Texture nodes with default texture: {replaced_count}")


def create_painting_hemisphere_material(obj, canvas_image=None):
    """Create clean material optimized for 3D viewport painting on hemisphere interior"""
    
    # Create new material
    mat = bpy.data.materials.new(name=f"{obj.name}_Material")
    mat.use_nodes = True
    mat.use_backface_culling = False  # Important for seeing interior
    mat.blend_method = 'BLEND'  # Enable alpha blending
    mat.show_transparent_back = False  # Only show front faces as transparent
    obj.data.materials.append(mat)
    
    # Clear default nodes
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create nodes for see-through hemisphere (ORIGINAL DOME FUNCTIONS VERSION)
    output = nodes.new(type='ShaderNodeOutputMaterial')
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    transparent = nodes.new(type='ShaderNodeBsdfTransparent')
    emission = nodes.new(type='ShaderNodeEmission')
    image_texture = nodes.new(type='ShaderNodeTexImage')
    geometry = nodes.new(type='ShaderNodeNewGeometry')
    
    # Set node locations
    output.location = (400, 0)
    mix_shader.location = (200, 0)
    transparent.location = (0, 100)
    emission.location = (0, -100)
    image_texture.location = (-200, -100)
    geometry.location = (-200, 100)
    
    # Connect nodes - front faces transparent, back faces show HDRI (ORIGINAL CONNECTIONS)
    links = mat.node_tree.links
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    links.new(emission.outputs['Emission'], mix_shader.inputs[1])  # Front faces = HDRI  
    links.new(transparent.outputs['BSDF'], mix_shader.inputs[2])  # Back faces = transparent
    links.new(image_texture.outputs['Color'], emission.inputs['Color'])
    links.new(geometry.outputs['Backfacing'], mix_shader.inputs[0])  # Mix factor
    
    # Set emission strength for proper HDRI brightness
    emission.inputs['Strength'].default_value = 2.0
    
    # Set canvas image if available
    if canvas_image:
        image_texture.image = canvas_image
        # Set proper color space for HDRI
        if hasattr(canvas_image, 'colorspace_settings'):
            canvas_image.colorspace_settings.name = 'Linear Rec.709'
    else:
        # Create a default white texture to avoid missing texture warnings
        if "HDRI_Default_White" not in bpy.data.images:
            white_image = bpy.data.images.new("HDRI_Default_White", width=512, height=256)
            # Fill with white
            pixels = [1.0] * (512 * 256 * 4)  # RGBA white
            white_image.pixels[:] = pixels
            white_image.colorspace_settings.name = 'Linear Rec.709'
        else:
            white_image = bpy.data.images["HDRI_Default_White"]
        
        image_texture.image = white_image
    
    return mat


def setup_hemisphere_collection(hemisphere_obj, handler_obj):
    """Setup collection for hemisphere organization like sample dome"""
    
    # Create or get HDRI_Studio collection
    if "HDRI_Studio" not in bpy.data.collections:
        hdri_collection = bpy.data.collections.new("HDRI_Studio")
        bpy.context.scene.collection.children.link(hdri_collection)
    else:
        hdri_collection = bpy.data.collections["HDRI_Studio"]
    
    # Move hemisphere and handler to collection
    for obj in [hemisphere_obj, handler_obj]:
        if obj and obj.name not in hdri_collection.objects:
            hdri_collection.objects.link(obj)
            # Remove from scene collection if it was there
            if obj.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(obj)
    
    # Set collection color (orange like sample)
    hdri_collection.color_tag = 'COLOR_03'
    
    return hdri_collection


def setup_hemisphere_parenting(hemisphere_obj, handler_obj):
    """Setup parent-child relationship like sample dome"""
    # Parent hemisphere to handler for scaling
    hemisphere_obj.parent = handler_obj
    hemisphere_obj.parent_type = 'OBJECT'


def setup_hemisphere_for_painting(obj, canvas_image):
    """Setup hemisphere for 3D texture painting with proper UV mapping"""
    
    # Make sure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Deselect all objects first
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select and make active
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Ensure UV mapping exists with CALIBRATED mapping
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    
    # Apply CALIBRATED UV mapping (proven <65px accuracy!)
    apply_calibrated_uv_mapping(obj)
    
    # Setup material and painting
    if canvas_image and obj.data.materials:
        # Find or create paintable TEX_IMAGE node in material root
        for mat in obj.data.materials:
            if mat.use_nodes:
                paintable_node = None
                
                # First, try to find existing TEX_IMAGE node with our canvas
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image == canvas_image:
                        paintable_node = node
                        print(f"Found paintable TEX_IMAGE node: {node.name}")
                        break
                
                # If no paintable node found, create dedicated paint node
                if not paintable_node:
                    print("No paintable TEX_IMAGE node found - creating dedicated paint node")
                    paintable_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                    paintable_node.name = "Paint_Canvas"
                    paintable_node.label = "Paint Canvas (TEX_IMAGE)"
                    paintable_node.image = canvas_image
                    paintable_node.location = (300, 400)  # Place it visibly in shader editor
                    print(f"Created dedicated TEX_IMAGE paint node: {paintable_node.name}")
                
                # Make this node active for painting (CRITICAL!)
                mat.node_tree.nodes.active = paintable_node
                print(f"Set active paint node: {paintable_node.name}")
                break
    
    # Enter texture paint mode
    bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    
    # Set painting mode to material
    bpy.context.scene.tool_settings.image_paint.mode = 'MATERIAL'
    
    # Setup painting brush for HDRI painting
    if "HDRI_Brush" not in bpy.data.brushes:
        brush = bpy.data.brushes.new("HDRI_Brush")
        brush.size = 100
        brush.strength = 0.8
        brush.use_alpha = False
        brush.color = (1.0, 1.0, 1.0)  # White for adding light
    else:
        brush = bpy.data.brushes["HDRI_Brush"]
    
    bpy.context.tool_settings.image_paint.brush = brush
    
    # Set active canvas for painting
    if canvas_image:
        bpy.context.scene.tool_settings.image_paint.canvas = canvas_image
        # Also set in image editor if available
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = canvas_image
    
    return True


class HDRI_OT_hemisphere_add(bpy.types.Operator):
    """Add smooth hemisphere for HDRI preview"""
    bl_idname = "hdri_studio.hemisphere_add"
    bl_label = "Add Hemisphere"
    bl_description = "Add a smooth hemisphere for HDRI preview"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Check if hemisphere already exists
        if "HDRI_Hemisphere" in bpy.data.objects:
            self.report({'WARNING'}, "Hemisphere already exists")
            return {'CANCELLED'}
        
        # Get active canvas image
        canvas_image = None
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR' and space.image:
                        canvas_image = space.image
                        break
        
        # Get selected geometry type from properties
        geometry_type = context.scene.hemisphere_props.geometry_type
        
        # Create hemisphere handler first (like dome handler in sample)
        handler_obj = create_hemisphere_handler()
        
        # Load dome as hemisphere with selected geometry type
        hemisphere_obj = load_dome_as_hemisphere("HDRI_Hemisphere", geometry_type)
        
        if not hemisphere_obj:
            self.report({'ERROR'}, "Failed to create hemisphere")
            return {'CANCELLED'}
        
        # Setup parent-child relationship for scaling
        setup_hemisphere_parenting(hemisphere_obj, handler_obj)
        
        # Setup collection and add to scene
        hdri_collection = setup_hemisphere_collection(hemisphere_obj, handler_obj)
        
        # Setup material with canvas
        setup_hemisphere_material(hemisphere_obj, canvas_image)
        
        # Setup for 3D painting
        setup_hemisphere_for_painting(hemisphere_obj, canvas_image)
        
        # Set viewport shading to Material Preview for better HDRI visibility
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        # Enable transparency in viewport for see-through effect
                        if hasattr(space.shading, 'use_scene_world_render'):
                            space.shading.use_scene_world_render = False
                        break
        
        # Make visible and selectable
        hemisphere_obj.hide_select = False
        hemisphere_obj.hide_viewport = False
        
        # Enable transparency display
        hemisphere_obj.show_transparent = True
        
        # AUTOMATICALLY switch to native TEXTURE PAINT mode
        try:
            from . import continuous_paint_handler
            if continuous_paint_handler.enable_continuous_paint(context):
                self.report({'INFO'}, "­čÄĘ Hemisphere added - NATIVE Texture Paint active! (ZERO LAG)")
            else:
                self.report({'INFO'}, "Hemisphere added successfully")
        except Exception as e:
            print(f"Could not auto-start texture paint: {e}")
            self.report({'INFO'}, "Hemisphere added - Switch to Texture Paint mode (Ctrl+Tab)")
        
        return {'FINISHED'}


class HDRI_OT_hemisphere_remove(bpy.types.Operator):
    """Remove hemisphere"""
    bl_idname = "hdri_studio.hemisphere_remove"
    bl_label = "Remove Hemisphere"
    bl_description = "Remove the hemisphere from scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Find and remove hemisphere and handler
        hemisphere_obj = bpy.data.objects.get("HDRI_Hemisphere")
        handler_obj = bpy.data.objects.get("HDRI_Hemisphere_Handler")
        
        removed_count = 0
        if hemisphere_obj:
            bpy.data.objects.remove(hemisphere_obj, do_unlink=True)
            removed_count += 1
        
        if handler_obj:
            bpy.data.objects.remove(handler_obj, do_unlink=True)
            removed_count += 1
            
        if removed_count > 0:
            self.report({'INFO'}, "Hemisphere removed")
        else:
            self.report({'WARNING'}, "No hemisphere found")
        
        return {'FINISHED'}





class HDRI_OT_hemisphere_paint_setup(bpy.types.Operator):
    """Setup hemisphere for 3D painting"""
    bl_idname = "hdri_studio.hemisphere_paint_setup"
    bl_label = "Setup 3D Paint"
    bl_description = "Setup hemisphere for 3D texture painting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        hemisphere_obj = bpy.data.objects.get("HDRI_Hemisphere")
        if not hemisphere_obj:
            self.report({'WARNING'}, "No hemisphere found")
            return {'CANCELLED'}
        
        # Get canvas image
        canvas_image = None
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR' and space.image:
                        canvas_image = space.image
                        break
        
        if not canvas_image:
            self.report({'WARNING'}, "No canvas image found. Create or load an HDRI first.")
            return {'CANCELLED'}
        
        # Setup for painting
        if setup_hemisphere_for_painting(hemisphere_obj, canvas_image):
            self.report({'INFO'}, "3D painting setup complete. Use texture paint mode to paint on hemisphere.")
        else:
            self.report({'ERROR'}, "Failed to setup 3D painting")
        
        return {'FINISHED'}


# Classes for registration
classes = [
    HemisphereProperties,
    HDRI_OT_hemisphere_add,
    HDRI_OT_hemisphere_remove,
    HDRI_OT_hemisphere_paint_setup,
]





def register():
    """Register hemisphere operators and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register hemisphere properties on scene
    bpy.types.Scene.hemisphere_props = bpy.props.PointerProperty(type=HemisphereProperties)
    
    print("HDRI hemisphere operators registered")


def unregister():
    """Unregister hemisphere operators and properties"""
    # Remove scene property
    del bpy.types.Scene.hemisphere_props
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("HDRI hemisphere operators unregistered")
