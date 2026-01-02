"""
World Operators Module  
World background controls for HDRI LightBrush
"""

import bpy
from bpy.types import Operator

class HDRI_OT_set_world_background(Operator):
    """Set current HDRI canvas as world background"""
    bl_idname = "hdri_studio.set_world_background"
    bl_label = "Set as World Background"
    bl_description = "Set the current HDRI canvas as world background"
    
    def execute(self, context):
        try:
            # Check if we have a canvas image
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "No HDRI Canvas found. Create canvas first.")
                return {'CANCELLED'}
            
            canvas_image = bpy.data.images["HDRI_Canvas"]
            
            # Get or create world
            world = context.scene.world
            if not world:
                world = bpy.data.worlds.new("HDRI_World")
                context.scene.world = world
                
            world.use_nodes = True
            nodes = world.node_tree.nodes
            links = world.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Add Environment Texture node
            env_tex = nodes.new(type='ShaderNodeTexEnvironment')
            env_tex.location = (-400, 300)
            env_tex.image = canvas_image
            
            # Add Mapping node for rotation control
            mapping = nodes.new(type='ShaderNodeMapping')
            mapping.location = (-600, 300)
            
            # Add Texture Coordinate node
            tex_coord = nodes.new(type='ShaderNodeTexCoord')
            tex_coord.location = (-800, 300)
            
            # Add Background node
            background = nodes.new(type='ShaderNodeBackground')
            background.location = (-200, 300)
            
            # Add World Output node
            world_output = nodes.new(type='ShaderNodeOutputWorld')
            world_output.location = (0, 300)
            
            # Link nodes
            links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
            links.new(env_tex.outputs['Color'], background.inputs['Color'])
            links.new(background.outputs['Background'], world_output.inputs['Surface'])
            
            # Apply world properties if available
            if hasattr(context.scene, 'hdri_studio_world'):
                world_props = context.scene.hdri_studio_world
                background.inputs['Strength'].default_value = world_props.background_strength
                mapping.inputs['Rotation'].default_value = (0, 0, world_props.background_rotation)
            
            # Set viewport shading to show world
            self.setup_viewport_shading(context)
            
            self.report({'INFO'}, "HDRI Canvas set as world background")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to set world background: {e}")
            return {'CANCELLED'}
    
    def setup_viewport_shading(self, context):
        """Setup viewport to show world background in both material and rendered modes"""
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        # Enable scene world for both material and rendered preview
                        space.shading.use_scene_world = True
                        space.shading.use_scene_world_render = True
                        area.tag_redraw()

class HDRI_OT_update_world_background(Operator):
    """Update world background with current settings"""
    bl_idname = "hdri_studio.update_world_background"
    bl_label = "Update World Background"
    bl_description = "Update world background with current settings"
    
    def execute(self, context):
        try:
            world = context.scene.world
            if not world or not world.use_nodes:
                self.report({'WARNING'}, "No world nodes setup")
                return {'CANCELLED'}
            
            nodes = world.node_tree.nodes
            
            # Find background and mapping nodes
            background_node = None
            mapping_node = None
            
            for node in nodes:
                if node.type == 'BACKGROUND':
                    background_node = node
                elif node.type == 'MAPPING':
                    mapping_node = node
            
            if not background_node:
                self.report({'WARNING'}, "No background node found")
                return {'CANCELLED'}
            
            # Apply world properties
            if hasattr(context.scene, 'hdri_studio_world'):
                world_props = context.scene.hdri_studio_world
                
                # Update strength
                background_node.inputs['Strength'].default_value = world_props.background_strength
                
                # Update rotation if mapping node exists
                if mapping_node:
                    mapping_node.inputs['Rotation'].default_value = (0, 0, world_props.background_rotation)
                
                # Update viewport display
                if world_props.use_world_in_viewport:
                    self.setup_viewport_shading(context, True)
                else:
                    self.setup_viewport_shading(context, False)
            
            # Force viewport redraw
            for area in context.screen.areas:
                area.tag_redraw()
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to update world: {e}")
            return {'CANCELLED'}
    
    def setup_viewport_shading(self, context, show_world):
        """Setup viewport world display"""
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if show_world:
                            space.shading.type = 'MATERIAL'
                            space.shading.use_scene_world = True
                        area.tag_redraw()

class HDRI_OT_remove_world_background(Operator):
    """Remove world background"""
    bl_idname = "hdri_studio.remove_world_background"
    bl_label = "Remove World Background"
    bl_description = "Remove HDRI from world background"
    
    def execute(self, context):
        try:
            world = context.scene.world
            if not world or not world.use_nodes:
                self.report({'WARNING'}, "No world setup to remove")
                return {'CANCELLED'}
            
            nodes = world.node_tree.nodes
            
            # Find and remove environment texture nodes
            for node in list(nodes):
                if node.type in ['TEX_ENVIRONMENT', 'MAPPING', 'TEX_COORD']:
                    nodes.remove(node)
            
            # Reset background to black
            for node in nodes:
                if node.type == 'BACKGROUND':
                    node.inputs['Color'].default_value = (0, 0, 0, 1)  # Black
                    node.inputs['Strength'].default_value = 1.0
                    break
            
            # Reset world properties
            if hasattr(context.scene, 'hdri_studio_world'):
                world_props = context.scene.hdri_studio_world
                world_props.background_strength = 1.0
                world_props.background_rotation = 0.0
            
            self.report({'INFO'}, "World background removed")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove background: {e}")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(HDRI_OT_set_world_background)
    bpy.utils.register_class(HDRI_OT_update_world_background) 
    bpy.utils.register_class(HDRI_OT_remove_world_background)


def unregister():
    bpy.utils.unregister_class(HDRI_OT_remove_world_background)
    bpy.utils.unregister_class(HDRI_OT_update_world_background)
    bpy.utils.unregister_class(HDRI_OT_set_world_background)