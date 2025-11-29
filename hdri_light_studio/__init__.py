bl_info = {
    "name": "HDRI Light Studio",
    "author": "HDRI Light Studio Team",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > HDRI Studio",
    "description": "KeyShot-style HDRI editor with inline canvas editing",
    "category": "Lighting",
}

import bpy
from bpy.props import PointerProperty

# Import addon modules
from . import properties
from . import operators  
from . import ui
from . import canvas_renderer
from . import simple_canvas
from . import utils
from . import simple_paint
from . import world_properties
from . import world_operators
from . import world_ui
from . import hdri_save
from . import sphere_tools  # Sphere preview tools
from . import viewport_paint_operator  # Working 3D painting with second intersection
from . import debug_paint_tracker  # UV mapping debug tool
from . import continuous_paint_handler  # RESTORED: This paints to CORRECT location!
# from . import paint_on_click  # DISABLED - wrong location

# Module registration list
modules = [
    properties,
    operators,
    ui, 
    canvas_renderer,
    simple_canvas,
    utils,
    simple_paint,
    world_properties,
    world_operators,
    world_ui,
    hdri_save,
    sphere_tools,
    viewport_paint_operator,
    debug_paint_tracker,
    continuous_paint_handler,  # RESTORED: Correct location painting!
    # paint_on_click,  # DISABLED
]

def register():
    """Register all addon modules and properties"""
    try:
        # Register all modules
        for module in modules:
            module.register()
        
        # Register scene properties
        bpy.types.Scene.hdri_studio = PointerProperty(type=properties.HDRIStudioProperties)
        bpy.types.Scene.hdri_studio_world = PointerProperty(type=world_properties.HDRIStudioWorldProperties)
        bpy.types.Scene.sphere_props = PointerProperty(type=sphere_tools.SphereProperties)
        
        print("HDRI Light Studio registered successfully")
        
    except Exception as e:
        print(f"HDRI Light Studio registration failed: {e}")

def unregister():
    """Unregister all addon modules and properties"""
    try:
        # Unregister scene properties
        if hasattr(bpy.types.Scene, 'hdri_studio'):
            del bpy.types.Scene.hdri_studio
        if hasattr(bpy.types.Scene, 'hdri_studio_world'):
            del bpy.types.Scene.hdri_studio_world
        if hasattr(bpy.types.Scene, 'sphere_props'):
            del bpy.types.Scene.sphere_props
        
        # Unregister all modules in reverse order
        for module in reversed(modules):
            module.unregister()
            
        print("HDRI Light Studio unregistered successfully")
        
    except Exception as e:
        print(f"HDRI Light Studio unregistration failed: {e}")

if __name__ == "__main__":
    register()
