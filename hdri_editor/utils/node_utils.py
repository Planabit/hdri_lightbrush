"""
Node utility functions for HDRI Editor.
Contains functions for managing Blender node system, particularly for
world nodes used in HDRI backgrounds.
"""

import bpy

__all__ = [
    "get_or_create_world_nodes",
    "get_world_setup"
]

def get_or_create_world_nodes(context):
    """Get or create world and background nodes."""
    try:
        if not context.scene.world:
            world = bpy.data.worlds.new(name="HDRI World")
            context.scene.world = world
        else:
            world = context.scene.world

        world.use_nodes = True
        nodes = world.node_tree.nodes
        nodes.clear()

        background = nodes.new("ShaderNodeBackground")
        background.location = (200, 300)

        output = nodes.new("ShaderNodeOutputWorld")
        output.location = (400, 300)

        world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])

        return world, background

    except Exception as e:
        print(f"Error setting up world nodes: {e}")
        return None, None

def get_world_setup(context):
    """Get current world node setup."""
    if not context.scene.world or not context.scene.world.use_nodes:
        return None, None, None

    world = context.scene.world
    nodes = world.node_tree.nodes

    background = next((n for n in nodes if n.type == "BACKGROUND"), None)
    mapping = next((n for n in nodes if n.type == "MAPPING"), None)

    return world, background, mapping
