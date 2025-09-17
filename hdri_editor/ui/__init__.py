"""UI modules for HDRI Editor"""
from . import panels

__all__ = ['register', 'unregister']

def register():
    """Register UI modules"""
    try:
        panels.register()
        print("HDRI Editor: Registered UI modules")
    except Exception as e:
        print(f"HDRI Editor: Error registering UI modules: {str(e)}")
        raise

def unregister():
    """Unregister UI modules"""
    try:
        panels.unregister()
        print("HDRI Editor: Unregistered UI modules")
    except Exception as e:
        print(f"HDRI Editor: Error unregistering UI modules: {str(e)}")
        raise