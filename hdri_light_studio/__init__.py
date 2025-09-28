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
from . import ui_canvas
from . import utils
from . import image_paint
from . import simple_paint

# Module registration list
modules = [
    properties,
    operators,
    ui, 
    canvas_renderer,
    simple_canvas,
    ui_canvas,
    utils,
    image_paint,
    simple_paint,
]

def register():
    """Register all addon modules and properties"""
    try:
        # Register all modules
        for module in modules:
            module.register()
        
        # Register scene properties
        bpy.types.Scene.hdri_studio = PointerProperty(type=properties.HDRIStudioProperties)
        
        print("HDRI Light Studio registered successfully")
        
    except Exception as e:
        print(f"HDRI Light Studio registration failed: {e}")

def unregister():
    """Unregister all addon modules and properties"""
    try:
        # Unregister scene properties
        if hasattr(bpy.types.Scene, 'hdri_studio'):
            del bpy.types.Scene.hdri_studio
        
        # Unregister all modules in reverse order
        for module in reversed(modules):
            module.unregister()
            
        print("HDRI Light Studio unregistered successfully")
        
    except Exception as e:
        print(f"HDRI Light Studio unregistration failed: {e}")

if __name__ == "__main__":
    register()
