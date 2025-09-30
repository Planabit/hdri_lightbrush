"""
World Settings UI Panel
World background controls for HDRI Light Studio
"""

import bpy
from bpy.types import Panel

class HDRI_PT_world_settings(Panel):
    """World settings panel for HDRI Light Studio"""
    bl_label = "World Settings"
    bl_idname = "HDRI_PT_world_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Studio'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Check if world properties exist
        if not hasattr(scene, 'hdri_studio_world'):
            box = layout.box()
            box.label(text="World properties not found", icon='ERROR')
            return
        
        world_props = scene.hdri_studio_world
        
        # World Background Section
        box = layout.box()
        row = box.row()
        row.label(text="World Background", icon='WORLD')
        
        # Set/Remove background buttons
        row = box.row(align=True)
        row.operator("hdri_studio.set_world_background", text="Set Background", icon='WORLD_DATA')
        row.operator("hdri_studio.remove_world_background", text="Remove", icon='X')
        
        # Background Strength
        row = box.row()
        row.prop(world_props, "background_strength", text="Strength")
        
        # Background Rotation  
        row = box.row()
        row.prop(world_props, "background_rotation", text="Rotation", slider=True)
        
        # Background Blur (placeholder for future implementation)
        row = box.row()
        row.prop(world_props, "background_blur", text="Blur")
        row.enabled = False  # Disabled until blur is implemented
        
        # Viewport Display Options
        box = layout.box()
        row = box.row()
        row.label(text="Viewport Display", icon='VIEW3D')
        
        row = box.row()
        row.prop(world_props, "use_world_in_viewport", text="Show World in Viewport")
        
        # Auto Update
        row = box.row()
        row.prop(world_props, "auto_update", text="Auto Update")
        
        # Manual update button
        if not world_props.auto_update:
            row = box.row()
            row.operator("hdri_studio.update_world_background", text="Update World", icon='FILE_REFRESH')
        
        # World Information
        if context.scene.world:
            box = layout.box()
            row = box.row()
            row.label(text="World Info", icon='INFO')
            
            world = context.scene.world
            row = box.row()
            row.label(text=f"World: {world.name}")
            
            if world.use_nodes and world.node_tree:
                env_nodes = [n for n in world.node_tree.nodes if n.type == 'TEX_ENVIRONMENT']
                if env_nodes:
                    env_node = env_nodes[0]
                    if env_node.image:
                        row = box.row()
                        row.label(text=f"HDRI: {env_node.image.name}")
                        
                        # Display image size
                        if env_node.image.size:
                            size_text = f"{env_node.image.size[0]}x{env_node.image.size[1]}"
                            row = box.row()
                            row.label(text=f"Size: {size_text}")

def register():
    """Register world UI panel"""
    bpy.utils.register_class(HDRI_PT_world_settings)
    print("World UI panel registered")

def unregister():
    """Unregister world UI panel"""  
    bpy.utils.unregister_class(HDRI_PT_world_settings)
    print("World UI panel unregistered")