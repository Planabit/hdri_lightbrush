"""
Node utility functions for HDRI Editor.
Contains functions for managing Blender's node system, particularly for
world nodes used in HDRI backgrounds.
"""

import bpy

__all__ = [
    'get_or_create_world_nodes',
    'get_world_setup'
]

def get_or_create_world_nodes(context):
    """Get or create world and background nodes.
    
    This function ensures that the scene has a world with proper node setup
    for HDRI backgrounds. It will create the world and necessary nodes if
    they don't exist, and clean up any existing nodes to provide a fresh setup.
    
    Args:
        context: Blender context
        
    Returns:
        tuple: (world, background_node) or (None, None) on error
    
    Example:
        world, background = get_or_create_world_nodes(context)
        if world and background:
            # Do something with the nodes
    """
    try:
        # Get or create world
        if not context.scene.world:
            world = bpy.data.worlds.new(name='HDRI World')
            context.scene.world = world
        else:
            world = context.scene.world
        
        # Enable nodes
        world.use_nodes = True
        nodes = world.node_tree.nodes
        
        # Clear all nodes
        nodes.clear()
        
        # Create background node
        background = nodes.new('ShaderNodeBackground')
        background.location = (200, 300)
        
        # Create world output node
        output = nodes.new('ShaderNodeOutputWorld')
        output.location = (400, 300)
        
        # Link background to output
        world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return world, background
        
    except Exception as e:
        print(f"Error setting up world nodes: {e}")
        return None, None

def get_world_setup(context):
    """Get current world node setup.
    
    Args:
        context: Blender context
    
    Returns:
        tuple: (world, background_node, mapping_node) or None values if not found
    """
    if not context.scene.world or not context.scene.world.use_nodes:
        return None, None, None
    
    world = context.scene.world
    nodes = world.node_tree.nodes
    
    # Find required nodes
    background = next((n for n in nodes if n.type == 'BACKGROUND'), None)
    mapping = next((n for n in nodes if n.type == 'MAPPING'), None)
    
    return world, background, mapping