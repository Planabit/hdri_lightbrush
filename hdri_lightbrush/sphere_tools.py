"""
HDRI LightBrush - Sphere Tools
Sphere creation and material setup for HDRI preview and 3D painting
"""

import bpy
import math
from bpy.props import FloatProperty, EnumProperty, StringProperty
from bpy.types import PropertyGroup
from .geometry.geometry_factory import GEOMETRY_TYPES, create_geometry


# ═══════════════════════════════════════════════════════════════════════════════
# PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

def update_sphere_scale_callback(self, context):
    """Callback when sphere scale property changes"""
    sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
    if sphere:
        scale = self.sphere_scale
        sphere.scale = (scale, scale, scale)


class SphereProperties(PropertyGroup):
    """Property group for sphere settings"""
    
    sphere_name: StringProperty(
        name="Sphere Name",
        default="HDRI_Preview_Sphere"
    )
    
    sphere_scale: FloatProperty(
        name="Scale Sphere",
        default=1.0,
        min=0.1,
        max=10.0,
        update=update_sphere_scale_callback
    )
    
    sphere_type: EnumProperty(
        name="Geometry Type",
        items=[
            ('SPHERE', 'Full Sphere', 'Complete sphere for 360° HDRI'),
        ],
        default='SPHERE'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SPHERE CREATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_sphere_handler():
    """Create empty object as sphere parent for scaling"""
    handler = bpy.data.objects.get("HDRI_Preview_Sphere_Handler")
    if handler:
        return handler
    
    bpy.ops.object.empty_add(location=(0, 0, 0))
    handler = bpy.context.object
    handler.name = "HDRI_Preview_Sphere_Handler"
    return handler


def load_dome_as_sphere(name="HDRI_Sphere", sphere_type='SPHERE'):
    """Create sphere using geometry factory"""
    obj = create_geometry(sphere_type, name, radius=5.0, location=(0, 0, 0))
    if obj:
        bpy.context.collection.objects.link(obj)
    return obj


# ═══════════════════════════════════════════════════════════════════════════════
# MATERIAL SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def create_painting_sphere_material(obj, canvas_image=None):
    """Create transparent HDRI material for viewing from inside sphere"""
    mat = bpy.data.materials.new(name=f"{obj.name}_Material")
    mat.use_nodes = True
    mat.use_backface_culling = False
    mat.blend_method = 'HASHED'
    # Only set shadow_method if it exists (Blender <4.3)
    if hasattr(mat, "shadow_method"):
        mat.shadow_method = 'NONE'
    mat.show_transparent_back = True
    obj.data.materials.append(mat)
    
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
    vec_math = nodes.new(type='ShaderNodeVectorMath')
    vec_math.operation = 'SCALE'
    vec_math.inputs[3].default_value = -1.0
    
    # Position nodes
    output.location = (600, 0)
    mix_shader.location = (400, 0)
    transparent.location = (200, 150)
    emission.location = (200, -50)
    env_texture.location = (0, -50)
    vec_math.location = (-100, -50)
    tex_coord.location = (-300, -50)
    geometry.location = (200, 300)
    
    # Connect nodes
    links.new(geometry.outputs['Backfacing'], mix_shader.inputs['Fac'])
    links.new(transparent.outputs['BSDF'], mix_shader.inputs[1])
    links.new(emission.outputs['Emission'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
    links.new(tex_coord.outputs['Normal'], vec_math.inputs[0])
    links.new(vec_math.outputs['Vector'], env_texture.inputs['Vector'])
    links.new(env_texture.outputs['Color'], emission.inputs['Color'])
    
    # Configure
    env_texture.projection = 'EQUIRECTANGULAR'
    emission.inputs['Strength'].default_value = 1.0
    
    if canvas_image:
        env_texture.image = canvas_image
        # Force GPU texture refresh for Blender 5.0
        try:
            canvas_image.gl_free()
            canvas_image.gl_load()
        except Exception:
            pass
    
    return mat


def setup_sphere_material(obj, canvas_image=None):
    """Setup transparent HDRI material for sphere"""
    obj.data.materials.clear()
    mat = create_painting_sphere_material(obj, canvas_image)
    
    # Force material and node tree update for Blender 5.0
    if mat:
        mat.update_tag()
        if mat.use_nodes and mat.node_tree:
            mat.node_tree.update_tag()
    
    return mat


# ═══════════════════════════════════════════════════════════════════════════════
# SPHERE SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def setup_sphere_collection(sphere_obj, handler_obj):
    """Setup collection for sphere organization"""
    if "HDRI_Studio" not in bpy.data.collections:
        hdri_collection = bpy.data.collections.new("HDRI_Studio")
        bpy.context.scene.collection.children.link(hdri_collection)
    else:
        hdri_collection = bpy.data.collections["HDRI_Studio"]
    
    for obj in [sphere_obj, handler_obj]:
        if obj and obj.name not in hdri_collection.objects:
            hdri_collection.objects.link(obj)
            if obj.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(obj)
    
    hdri_collection.color_tag = 'COLOR_03'
    return hdri_collection


def setup_sphere_parenting(sphere_obj, handler_obj):
    """Parent sphere to handler for scaling"""
    sphere_obj.parent = handler_obj
    sphere_obj.parent_type = 'OBJECT'


def setup_sphere_for_painting(obj, canvas_image):
    """Setup sphere for 3D texture painting"""
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Create UV mapping if needed
    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.sphere_project()
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Setup paintable node in material
    if canvas_image and obj.data.materials:
        for mat in obj.data.materials:
            if mat.use_nodes:
                paintable_node = None
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image == canvas_image:
                        paintable_node = node
                        break
                
                if not paintable_node:
                    paintable_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                    paintable_node.name = "Paint_Canvas"
                    paintable_node.image = canvas_image
                    paintable_node.location = (300, 400)
                
                mat.node_tree.nodes.active = paintable_node
                break
    
    # Enter texture paint mode
    bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    bpy.context.scene.tool_settings.image_paint.mode = 'MATERIAL'
    
    # Use existing brush from image_paint - whatever user has set in 2D Image Editor
    # Don't create custom brush - let user control everything from Image Editor
    
    # Check Blender version for compatibility
    blender_version = bpy.app.version
    if blender_version >= (5, 0, 0):
        # Blender 5.0+: Use workspace tool system with temp_override
        try:
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                with bpy.context.temp_override(window=window, area=area, region=region):
                                    bpy.ops.wm.tool_set_by_id(name="builtin_brush.TexturePaint")
                                break
                        break
        except Exception:
            pass
    
    if canvas_image:
        bpy.context.scene.tool_settings.image_paint.canvas = canvas_image
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = canvas_image
    
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class HDRI_OT_sphere_add(bpy.types.Operator):
    """Add sphere for 360° HDRI preview and painting"""
    bl_idname = "hdri_studio.sphere_add"
    bl_label = "Add Preview Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sphere_props = context.scene.sphere_props
        
        if sphere_props.sphere_name in bpy.data.objects:
            self.report({'WARNING'}, "Preview sphere already exists")
            return {'CANCELLED'}
        
        # Get canvas image
        canvas_image = None
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR' and space.image:
                        canvas_image = space.image
                        break
        
        # Create sphere
        handler_obj = create_sphere_handler()
        sphere_obj = load_dome_as_sphere("HDRI_Preview_Sphere", sphere_props.sphere_type)
        
        if not sphere_obj:
            self.report({'ERROR'}, "Failed to create sphere")
            return {'CANCELLED'}
        
        # Setup sphere
        setup_sphere_parenting(sphere_obj, handler_obj)
        setup_sphere_collection(sphere_obj, handler_obj)
        setup_sphere_material(sphere_obj, canvas_image)
        setup_sphere_for_painting(sphere_obj, canvas_image)
        
        # Set viewport shading
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        break
        
        sphere_obj.hide_select = False
        sphere_obj.hide_viewport = False
        sphere_obj.show_transparent = True
        
        # Disable UV overlay in Image Editor
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        # Disable all overlays for cleaner HDRI view
                        if hasattr(space, 'overlay'):
                            space.overlay.show_overlays = False
                        break
        
        # Start continuous paint handler
        try:
            from . import continuous_paint_handler
            if continuous_paint_handler.enable_continuous_paint(context):
                self.report({'INFO'}, "Preview Sphere added - 3D Paint active!")
            else:
                self.report({'INFO'}, "Preview Sphere added")
        except Exception:
            self.report({'INFO'}, "Preview Sphere added")
        
        # Force full viewport refresh for Blender 5.0
        if canvas_image:
            try:
                canvas_image.update()
                canvas_image.gl_free()
                canvas_image.gl_load()
            except Exception:
                pass
        
        # Force depsgraph update
        context.view_layer.update()
        bpy.context.view_layer.depsgraph.update()
        
        # Tag all viewports for redraw
        for area in context.screen.areas:
            area.tag_redraw()
        
        return {'FINISHED'}


class HDRI_OT_sphere_remove(bpy.types.Operator):
    """Remove preview sphere"""
    bl_idname = "hdri_studio.sphere_remove"
    bl_label = "Remove Preview Sphere"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sphere_obj = bpy.data.objects.get("HDRI_Preview_Sphere")
        handler_obj = bpy.data.objects.get("HDRI_Preview_Sphere_Handler")
        
        removed = False
        if sphere_obj:
            bpy.data.objects.remove(sphere_obj, do_unlink=True)
            removed = True
        if handler_obj:
            bpy.data.objects.remove(handler_obj, do_unlink=True)
            removed = True
        
        if removed:
            self.report({'INFO'}, "Sphere removed")
        else:
            self.report({'WARNING'}, "No sphere found")
        
        return {'FINISHED'}


class HDRI_OT_sphere_paint_setup(bpy.types.Operator):
    """Setup sphere for 3D painting"""
    bl_idname = "hdri_studio.sphere_paint_setup"
    bl_label = "Setup 3D Paint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sphere_obj = bpy.data.objects.get("HDRI_Preview_Sphere")
        if not sphere_obj:
            self.report({'WARNING'}, "No sphere found")
            return {'CANCELLED'}
        
        canvas_image = None
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR' and space.image:
                        canvas_image = space.image
                        break
        
        if not canvas_image:
            self.report({'WARNING'}, "No canvas image found")
            return {'CANCELLED'}
        
        if setup_sphere_for_painting(sphere_obj, canvas_image):
            self.report({'INFO'}, "3D painting setup complete")
        else:
            self.report({'ERROR'}, "Failed to setup 3D painting")
        
        return {'FINISHED'}


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

classes = [
    SphereProperties,
    HDRI_OT_sphere_add,
    HDRI_OT_sphere_remove,
    HDRI_OT_sphere_paint_setup,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
