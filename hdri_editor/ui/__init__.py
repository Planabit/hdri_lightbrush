"""UI modules for HDRI Editor"""
from . import panels
from . import image_editor_panel
from . import hdri_2d_simple

__all__ = ['register', 'unregister']

def register():
    """Register UI modules"""
    try:
        panels.register()
        print("HDRI Editor: Registered panels")
        image_editor_panel.register()
        print("HDRI Editor: Registered image editor panel")
        hdri_2d_simple.register()
        print("HDRI Editor: Registered simple 2D HDRI editor")
    except Exception as e:
        print(f"HDRI Editor: Error registering UI modules: {str(e)}")
        raise

def unregister():
    """Unregister UI modules"""
    try:
        hdri_2d_simple.unregister()
        print("HDRI Editor: Unregistered simple 2D HDRI editor")
        image_editor_panel.unregister()
        print("HDRI Editor: Unregistered image editor panel")
        panels.unregister()
        print("HDRI Editor: Unregistered panels")
    except Exception as e:
        print(f"HDRI Editor: Error unregistering UI modules: {str(e)}")
        raise