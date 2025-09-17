"""
Utility modules for HDRI Editor.

This package contains various utility modules used throughout the HDRI Editor addon:
- node_utils: Functions for managing Blender node systems
- preview_utils: HDRI preview system and image management
"""

import bpy
from . import node_utils
from . import preview_utils

__all__ = ['register', 'unregister']

def register():
    """Register utility modules"""
    try:
        preview_utils.register()
        print("HDRI Editor: Registered utility modules")
    except Exception as e:
        print(f"HDRI Editor: Error registering utility modules: {str(e)}")
        raise

def unregister():
    """Unregister utility modules"""
    try:
        preview_utils.unregister()
        print("HDRI Editor: Unregistered utility modules")
    except Exception as e:
        print(f"HDRI Editor: Error unregistering utility modules: {str(e)}")
        raise