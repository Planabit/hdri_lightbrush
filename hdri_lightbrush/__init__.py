bl_info = {
    "name": "HDRI LightBrush",
    "author": "Tamas Laszlo (planabit@gmail.com)",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > HDRI LightBrush",
    "description": "Professional HDRI environment editor - Paint directly on world-representing sphere for precise studio lighting control",
    "category": "Lighting",
    "doc_url": "https://github.com/Planabit/hdri_lightbrush",
    "tracker_url": "https://github.com/Planabit/hdri_lightbrush/issues",
    "support": "COMMUNITY",
}

import bpy
from bpy.props import PointerProperty

from . import properties
from . import operators  
from . import ui
from . import utils
from . import simple_paint
from . import world_properties
from . import world_operators
from . import hdri_save
from . import sphere_tools
from . import continuous_paint_handler
from . import icons

modules = [
    icons,  # Load icons first
    properties,
    operators,
    ui, 
    utils,
    simple_paint,
    world_properties,
    world_operators,
    hdri_save,
    sphere_tools,
    continuous_paint_handler,
]


def register():
    """Register all addon modules"""
    for module in modules:
        module.register()
    
    bpy.types.Scene.hdri_studio = PointerProperty(type=properties.HDRIStudioProperties)
    bpy.types.Scene.hdri_studio_world = PointerProperty(type=world_properties.HDRIStudioWorldProperties)
    bpy.types.Scene.sphere_props = PointerProperty(type=sphere_tools.SphereProperties)


def unregister():
    """Unregister all addon modules"""
    if hasattr(bpy.types.Scene, 'hdri_studio'):
        del bpy.types.Scene.hdri_studio
    if hasattr(bpy.types.Scene, 'hdri_studio_world'):
        del bpy.types.Scene.hdri_studio_world
    if hasattr(bpy.types.Scene, 'sphere_props'):
        del bpy.types.Scene.sphere_props
    
    for module in reversed(modules):
        module.unregister()


if __name__ == "__main__":
    register()
