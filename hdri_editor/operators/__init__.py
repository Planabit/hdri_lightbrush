"""Operator modules for HDRI Editor"""
from . import background_tools
from . import hdri

def register():
    background_tools.register()
    hdri.register()

def unregister():
    hdri.unregister()
    background_tools.unregister()