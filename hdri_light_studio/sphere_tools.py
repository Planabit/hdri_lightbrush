"""
HDRI Light Studio - Sphere Tools

This module provides smooth sphere creation and management functionality
for HDRI preview and 3D painting workflows, based on the sample dome system.
"""

import bpy
import bmesh
from mathutils import Vector
import numpy as np
import math
from bpy.app.handlers import persistent
from bpy.props import FloatProperty, EnumProperty, StringProperty
from bpy.types import PropertyGroup
from .geometry.geometry_factory import GEOMETRY_TYPES, create_geometry


def apply_calibrated_uv_mapping(obj):
    """
    Apply CALIBRATED UV mapping to sphere geometry
    This is the PROVEN <65px accurate mapping!
    """
    
    mesh = obj.data
    sphere_center = obj.location
    
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
            
            # Direction from sphere center
            direction = (vertex_world - sphere_center).normalized()
            
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
    print("✅ Applied CALIBRATED UV mapping (<65px accuracy!)")


def update_sphere_scale_callback(self, context):
    """Callback when sphere scale property changes"""
    sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
    if sphere:
        scale = self.sphere_scale
        sphere.scale = (scale, scale, scale)


class SphereProperties(PropertyGroup):
    """Property group for sphere with scale callback"""
    
    sphere_name: StringProperty(
        name="Sphere Name",
        description="Name of the preview sphere object",
        default="HDRI_Preview_Sphere"
    )
    
    sphere_scale: FloatProperty(
        name="Scale Sphere",
        description="Scale the sphere",
        default=1.0,
        min=0.1,
        max=10.0,
        soft_min=0.1,
        soft_max=5.0,
        update=update_sphere_scale_callback
    )
    
    sphere_type: EnumProperty(
        name="Geometry Type",
        description="Choose the type of geometry to create",
        items=[
            ('SPHERE', 'Full Sphere', 'Complete sphere for 360° HDRI (Recommended)'),
            ('HALF_SPHERE', 'Half Sphere (180°)', 'Half sphere for 180° HDRI')
        ],
        default='SPHERE'  # Changed to SPHERE as default!
    )


def create_sphere_handler():
    """Create sphere handler like dome handler in sample"""
    # Check if handler already exists
    handler = bpy.data.objects.get("HDRI_Preview_Sphere_Handler")
    if handler:
        return handler
    
    # Create empty object as handler
    bpy.ops.object.empty_add(location=(0, 0, 0))
    handler = bpy.context.object
    handler.name = "HDRI_Preview_Sphere_Handler"
    
    return handler





def load_dome_as_sphere(name="HDRI_Sphere", sphere_type='SPHERE'):
    """Create sphere using geometry factory based on selected type.
    Uses our own sphere geometry with proper normals for interior viewing.
    """
    
    # Use geometry factory to create the selected geometry type
    obj = create_geometry(sphere_type, name, radius=5.0, location=(0, 0, 0))
    
    if obj:
        # Link to current collection
        bpy.context.collection.objects.link(obj)
        print(f"✅ Created {sphere_type} geometry: '{name}'")
        return obj
    
    return None





def set_material_to_equirectangular(material):
    """Set all Environment Texture nodes in material to EQUIRECTANGULAR projection"""
    if not material or not material.use_nodes:
        return
    
    def process_node_tree(node_tree, depth=0):
        """Recursively process node tree and nested node groups"""
        for node in node_tree.nodes:
            if node.type == 'TEX_ENVIRONMENT':
                if node.projection != 'EQUIRECTANGULAR':
                    print(f"  {'  '*depth}Setting {node.name} projection to EQUIRECTANGULAR (was {node.projection})")
                    node.projection = 'EQUIRECTANGULAR'
            # Process nested node groups
            if hasattr(node, 'node_tree') and node.node_tree:
                process_node_tree(node.node_tree, depth + 1)
    
    print(f"Setting material '{material.name}' to EQUIRECTANGULAR projection...")
    process_node_tree(material.node_tree)


def setup_sphere_material(obj, canvas_image=None):
    """Setup transparent HDRI material for sphere interior viewing.
    Creates our own material with proper transparency settings.
    """
    
    # Clear existing materials
    obj.data.materials.clear()
    
    # Create our transparent HDRI material
    mat = create_painting_sphere_material(obj, canvas_image)
    
    return mat


def update_material_object_reference(material, sphere_obj):
    """Update TEX_COORD nodes in material to reference the sphere object"""
    if not material or not material.use_nodes:
        return
    
    def update_in_node_tree(node_tree):
        for node in node_tree.nodes:
            if node.type == 'TEX_COORD':
                # Set the sphere as the reference object
                node.object = sphere_obj
                print(f"  Updated TEX_COORD '{node.name}' object reference to '{sphere_obj.name}'")
            # Recursively update in node groups
            if hasattr(node, 'node_tree') and node.node_tree:
                update_in_node_tree(node.node_tree)
    
    update_in_node_tree(material.node_tree)


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
            dome_material.name = "HDRI_Preview_Sphere_Material"
            
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


def assign_sphere_to_material_coordinates(sphere_obj, material):
    """Assign sphere object to material coordinates like sample dome"""
    
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
    
    # Assign sphere object to TEX_COORD node
    if vectors_ng and vectors_ng.node_tree:
        for n in vectors_ng.node_tree.nodes:
            if n.type == 'TEX_COORD':
                n.object = sphere_obj
                break


def assign_image_to_sphere_material(material, image):
    """Assign image to ALL texture nodes in sphere material"""
    
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


def create_painting_sphere_material(obj, canvas_image=None):
    """Create transparent EQUIRECTANGULAR material for viewing HDRI from inside sphere.
    
    Based on sample dome material analysis:
    - Uses Blend Method: HASHED for transparency
    - Uses Geometry node Backfacing to show only interior
    - Mix between Transparent BSDF (exterior) and Emission (interior)
    """
    
    # Create new material with transparency settings like sample dome
    mat = bpy.data.materials.new(name=f"{obj.name}_Material")
    mat.use_nodes = True
    mat.use_backface_culling = False
    mat.blend_method = 'HASHED'  # KEY: This enables transparency!
    mat.shadow_method = 'NONE'
    mat.show_transparent_back = True
    obj.data.materials.append(mat)
    
    # Clear default nodes
    nodes = mat.node_tree.nodes
    nodes.clear()
    links = mat.node_tree.links
    
    # Create nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    transparent = nodes.new(type='ShaderNodeBsdfTransparent')
    emission = nodes.new(type='ShaderNodeEmission')
    env_texture = nodes.new(type='ShaderNodeTexEnvironment')
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    geometry = nodes.new(type='ShaderNodeNewGeometry')
    
    # Vector Math node to INVERT the normal (for interior viewing)
    vec_math = nodes.new(type='ShaderNodeVectorMath')
    vec_math.operation = 'SCALE'
    vec_math.inputs[3].default_value = -1.0  # Scale factor = -1 (invert)
    
    # Position nodes
    output.location = (600, 0)
    mix_shader.location = (400, 0)
    transparent.location = (200, 150)
    emission.location = (200, -50)
    env_texture.location = (0, -50)
    vec_math.location = (-100, -50)
    tex_coord.location = (-300, -50)
    geometry.location = (200, 300)
    
    # Connect nodes:
    # Geometry.Backfacing -> Mix.Fac (1=backface=interior, 0=frontface=exterior)
    # Transparent -> Mix.Shader1 (exterior - invisible)
    # Emission -> Mix.Shader2 (interior - shows HDRI)
    links.new(geometry.outputs['Backfacing'], mix_shader.inputs['Fac'])
    links.new(transparent.outputs['BSDF'], mix_shader.inputs[1])  # Shader 1
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])  # Shader 2
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    
    # Environment texture chain:
    # TexCoord.Normal gives surface normal direction (outward from sphere center)
    # We INVERT it (*-1) because we're viewing from INSIDE
    # This makes the texture stick to the sphere surface AND match world mapping!
    links.new(tex_coord.outputs['Normal'], vec_math.inputs[0])
    links.new(vec_math.outputs['Vector'], env_texture.inputs['Vector'])
    links.new(env_texture.outputs['Color'], emission.inputs['Color'])
    
    # Configure nodes
    env_texture.projection = 'EQUIRECTANGULAR'
    emission.inputs['Strength'].default_value = 1.0
    
    if canvas_image:
        env_texture.image = canvas_image
    
    print(f"✅ Created transparent HDRI material with HASHED blend method")
    return mat


def setup_sphere_collection(sphere_obj, handler_obj):
    """Setup collection for sphere organization like sample dome"""
    
    # Create or get HDRI_Studio collection
    if "HDRI_Studio" not in bpy.data.collections:
        hdri_collection = bpy.data.collections.new("HDRI_Studio")
        bpy.context.scene.collection.children.link(hdri_collection)
    else:
        hdri_collection = bpy.data.collections["HDRI_Studio"]
    
    # Move sphere and handler to collection
    for obj in [sphere_obj, handler_obj]:
        if obj and obj.name not in hdri_collection.objects:
            hdri_collection.objects.link(obj)
            # Remove from scene collection if it was there
            if obj.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(obj)
    
    # Set collection color (orange like sample)
    hdri_collection.color_tag = 'COLOR_03'
    
    return hdri_collection


def setup_sphere_parenting(sphere_obj, handler_obj):
    """Setup parent-child relationship like sample dome"""
    # Parent sphere to handler for scaling
    sphere_obj.parent = handler_obj
    sphere_obj.parent_type = 'OBJECT'


def setup_sphere_for_painting(obj, canvas_image):
    """Setup sphere for 3D texture painting with proper UV mapping"""
    
    # Make sure we're in object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Deselect all objects first
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select and make active
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Ensure UV mapping exists using Blender's sphere projection
    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.sphere_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"✅ Created UV mapping with sphere_project()")
    
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


class HDRI_OT_sphere_add(bpy.types.Operator):
    """Add sphere for 360° HDRI preview and painting"""
    bl_idname = "hdri_studio.sphere_add"
    bl_label = "Add Preview Sphere"
    bl_description = "Add a sphere for 360° HDRI preview and painting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sphere_props_obj = context.scene.sphere_props
        
        # Check if sphere already exists
        if sphere_props_obj.sphere_name in bpy.data.objects:
            self.report({'WARNING'}, "Preview sphere already exists")
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
        sphere_type = context.scene.sphere_props.sphere_type
        
        # Create sphere handler first (like dome handler in sample)
        handler_obj = create_sphere_handler()
        
        # Load dome as sphere with selected geometry type
        sphere_obj = load_dome_as_sphere("HDRI_Preview_Sphere", sphere_type)
        
        if not sphere_obj:
            self.report({'ERROR'}, "Failed to create sphere")
            return {'CANCELLED'}
        
        # Setup parent-child relationship for scaling
        setup_sphere_parenting(sphere_obj, handler_obj)
        
        # Setup collection and add to scene
        hdri_collection = setup_sphere_collection(sphere_obj, handler_obj)
        
        # Setup material with canvas
        setup_sphere_material(sphere_obj, canvas_image)
        
        # Setup for 3D painting
        setup_sphere_for_painting(sphere_obj, canvas_image)
        
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
        sphere_obj.hide_select = False
        sphere_obj.hide_viewport = False
        
        # Enable transparency display
        sphere_obj.show_transparent = True
        
        # RESTORED: Auto-start continuous paint modal (correct location!)
        try:
            from . import continuous_paint_handler
            if continuous_paint_handler.enable_continuous_paint(context):
                self.report({'INFO'}, "🎨 Preview Sphere added - 3D Paint active!")
            else:
                self.report({'INFO'}, "Preview Sphere added successfully")
        except Exception as e:
            print(f"Could not auto-start 3D paint: {e}")
            self.report({'INFO'}, "Preview Sphere added")
        
        return {'FINISHED'}


class HDRI_OT_sphere_remove(bpy.types.Operator):
    """Remove preview sphere"""
    bl_idname = "hdri_studio.sphere_remove"
    bl_label = "Remove Preview Sphere"
    bl_description = "Remove the preview sphere from scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Find and remove sphere and handler
        sphere_obj = bpy.data.objects.get("HDRI_Preview_Sphere")
        handler_obj = bpy.data.objects.get("HDRI_Preview_Sphere_Handler")
        
        removed_count = 0
        if sphere_obj:
            bpy.data.objects.remove(sphere_obj, do_unlink=True)
            removed_count += 1
        
        if handler_obj:
            bpy.data.objects.remove(handler_obj, do_unlink=True)
            removed_count += 1
            
        if removed_count > 0:
            self.report({'INFO'}, "Sphere removed")
        else:
            self.report({'WARNING'}, "No sphere found")
        
        return {'FINISHED'}





class HDRI_OT_sphere_paint_setup(bpy.types.Operator):
    """Setup sphere for 3D painting"""
    bl_idname = "hdri_studio.sphere_paint_setup"
    bl_label = "Setup 3D Paint"
    bl_description = "Setup sphere for 3D texture painting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sphere_obj = bpy.data.objects.get("HDRI_Preview_Sphere")
        if not sphere_obj:
            self.report({'WARNING'}, "No sphere found")
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
        if setup_sphere_for_painting(sphere_obj, canvas_image):
            self.report({'INFO'}, "3D painting setup complete. Use texture paint mode to paint on sphere.")
        else:
            self.report({'ERROR'}, "Failed to setup 3D painting")
        
        return {'FINISHED'}


# Classes for registration
classes = [
    SphereProperties,
    HDRI_OT_sphere_add,
    HDRI_OT_sphere_remove,
    HDRI_OT_sphere_paint_setup,
]





def register():
    """Register sphere operators and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("HDRI sphere operators registered")


def unregister():
    """Unregister sphere operators and properties"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("HDRI sphere operators unregistered")