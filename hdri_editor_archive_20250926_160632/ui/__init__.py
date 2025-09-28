"""UI modules for HDRI Editor - Simplified"""
from . import hdri_2d_simple

def register():
    """Register UI modules"""
    try:
        hdri_2d_simple.register()
        print("HDRI Editor: Registered 2D HDRI editor")
    except Exception as e:
        print(f"HDRI Editor: Error registering UI: {str(e)}")

def unregister():
    """Unregister UI modules"""
    try:
        hdri_2d_simple.unregister()
        print("HDRI Editor: Unregistered 2D HDRI editor")
    except Exception as e:
        print(f"HDRI Editor: Error unregistering UI: {str(e)}")