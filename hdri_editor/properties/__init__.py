"""Property modules for HDRI Editor"""
from . import world_properties

__all__ = ['register', 'unregister']

def register():
    """Register all property classes"""
    try:
        world_properties.register()
        print("HDRI Editor: Registered property modules")
    except Exception as e:
        print(f"HDRI Editor: Error registering property modules: {str(e)}")
        raise

def unregister():
    """Unregister all property classes"""
    try:
        world_properties.unregister()
        print("HDRI Editor: Unregistered property modules")
    except Exception as e:
        print(f"HDRI Editor: Error unregistering property modules: {str(e)}")
        raise