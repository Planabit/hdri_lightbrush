"""
Background operators for HDRI Editor.
Handles all world background related operations.
"""

import bpy
from bpy.types import Operator

from ..utils import node_utils

class HDRI_EDITOR_OT_set_background(Operator):
    """Set current HDRI as world background"""
    bl_idname = "hdri_editor.set_background"
    bl_label = "Set as Background"
    bl_description = "Set the selected HDRI as the world background"
    
    def execute(self, context):
        try:
            # Get the selected HDRI
            selected_hdri = context.scene.hdri_editor.hdri_previews
            if selected_hdri == 'NONE':
                self.report({'ERROR'}, "No HDRI selected")
                return {'CANCELLED'}
            
            # Get or create world nodes
            world, background = node_utils.get_or_create_world_nodes(context)
            if not world or not background:
                self.report({'ERROR'}, "Failed to set up world nodes")
                return {'CANCELLED'}
            
            # Clear existing nodes except Background and World Output
            nodes = world.node_tree.nodes
            links = world.node_tree.links
            for node in nodes:
                if node.type not in {'BACKGROUND', 'OUTPUT_WORLD'}:
                    nodes.remove(node)
            
            # Create texture node
            texture = nodes.new('ShaderNodeTexEnvironment')
            texture.location = (-400, 300)
            
            # Create mapping node
            mapping = nodes.new('ShaderNodeMapping')
            mapping.location = (-200, 300)
            
            # Create texture coordinate node
            texcoord = nodes.new('ShaderNodeTexCoord')
            texcoord.location = (-600, 300)
            
            # Connect nodes
            links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], texture.inputs['Vector'])
            links.new(texture.outputs['Color'], background.inputs['Color'])
            
            # Set the image
            image = bpy.data.images[selected_hdri]
            texture.image = image
            
            # Get world properties
            props = context.scene.hdri_editor_world
            
            # Set initial values
            background.inputs['Strength'].default_value = props.background_strength
            mapping.inputs['Rotation'].default_value[2] = props.background_rotation
            
            # Enable world background in viewport if set
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    space = area.spaces[0]
                    # Set shading type to MATERIAL if it's SOLID
                    if space.shading.type == 'SOLID':
                        space.shading.type = 'MATERIAL'
                    # Enable world background in viewport
                    space.shading.use_scene_world = True
                    space.shading.use_scene_world_render = True
                    # Note: Don't modify studio_light when using world HDRI background
                    # Update UI
                    area.tag_redraw()
            
            self.report({'INFO'}, f"Set {image.name} as background")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to set background: {e}")
            return {'CANCELLED'}

class HDRI_EDITOR_OT_update_background(Operator):
    """Update world background with current settings"""
    bl_idname = "hdri_editor.update_world_background"
    bl_label = "Update World Background"
    bl_description = "Update world background with current settings"
    
    def execute(self, context):
        try:
            # Get world and nodes
            world, background, mapping = node_utils.get_world_setup(context)
            if not all((world, background, mapping)):
                self.report({'ERROR'}, "Required nodes not found")
                return {'CANCELLED'}
            
            # Get settings
            props = context.scene.hdri_editor_world
            
            # Update settings
            background.inputs['Strength'].default_value = props.background_strength
            mapping.inputs['Rotation'].default_value[2] = props.background_rotation
            
            # Update viewport
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    space = area.spaces[0]
                    # Ensure we're in a mode that can show world
                    if space.shading.type == 'SOLID':
                        space.shading.type = 'MATERIAL'
                    # Update world visibility
                    space.shading.use_scene_world = props.use_world_in_viewport
                    space.shading.use_scene_world_render = props.use_world_in_viewport
                    # Update UI
                    area.tag_redraw()
            
            self.report({'INFO'}, "Background settings updated")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to update world: {e}")
            return {'CANCELLED'}

class HDRI_EDITOR_OT_remove_background(Operator):
    """Remove world background nodes"""
    bl_idname = "hdri_editor.remove_background"
    bl_label = "Remove Background"
    bl_description = "Remove all nodes from the world shader"
    
    def execute(self, context):
        try:
            if not context.scene.world:
                return {'CANCELLED'}
            
            # Get or create base nodes
            world, background = node_utils.get_or_create_world_nodes(context)
            if not world or not background:
                self.report({'ERROR'}, "Failed to set up world nodes")
                return {'CANCELLED'}
            
            # Set background color to black
            background.inputs['Color'].default_value = (0, 0, 0, 1)
            background.inputs['Strength'].default_value = 0
            
            # Update properties
            context.scene.hdri_editor_world.background_strength = 0
            context.scene.hdri_editor_world.background_rotation = 0
            context.scene.hdri_editor_world.use_world_in_viewport = False
            
            # Update viewport
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    space = area.spaces[0]
                    # Reset to default shading
                    space.shading.type = 'SOLID'
                    space.shading.use_scene_world = False
                    space.shading.use_scene_world_render = False
                    # Reset to default studio light (use basic.sl as safe default)
                    try:
                        space.shading.studio_light = 'basic.sl'
                    except:
                        pass  # Ignore if studio light setting fails
                    # Update UI
                    area.tag_redraw()
            
            self.report({'INFO'}, "World background removed")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove background: {e}")
            return {'CANCELLED'}

# Classes for registration
classes = (
    HDRI_EDITOR_OT_set_background,
    HDRI_EDITOR_OT_update_background,
    HDRI_EDITOR_OT_remove_background,
)

def register():
    """Register the operators"""
    try:
        for cls in classes:
            try:
                bpy.utils.register_class(cls)
                print(f"HDRI Editor: Registered {cls.__name__}")
            except ValueError:
                print(f"HDRI Editor: Class {cls.__name__} already registered")
            except RuntimeError:
                print(f"HDRI Editor: Failed to register {cls.__name__}, may be duplicate")
    except Exception as e:
        print(f"HDRI Editor: Error during registration: {str(e)}")
        raise

def unregister():
    """Unregister the operators"""
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