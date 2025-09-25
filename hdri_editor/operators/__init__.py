"""
Operators for HDRI Editor.
"""

from . import background_tools

__all__ = [
    'background_tools',
]

def register():
    """Register all operator classes"""
    try:
        background_tools.register()
        print("HDRI Editor: Registered operator modules")
    except Exception as e:
        print(f"HDRI Editor: Error registering operator modules: {str(e)}")
        raise

def unregister():
    """Unregister all operator classes"""
    try:
        background_tools.unregister()
        print("HDRI Editor: Unregistered operator modules")
    except Exception as e:
        print(f"HDRI Editor: Error unregistering operator modules: {str(e)}")
        raise