"""
Lighting package initialization for HDRI Editor
"""

def register():
    """Register all lighting components in correct order"""
    try:
        # Import and register core lighting system first
        from . import lighting_core
        lighting_core.register()
        print("HDRI Editor: Registered lighting core")
        
        # Then register operators
        from . import light_operators
        light_operators.register()  
        print("HDRI Editor: Registered lighting operators")
        
        # Finally register library (depends on panels being registered)
        from . import light_library
        light_library.register()
        print("HDRI Editor: Registered light library")
        
    except Exception as e:
        print(f"HDRI Editor: Error in lighting registration: {e}")
        raise

def unregister():
    """Unregister all lighting components in reverse order"""
    try:
        # Unregister in reverse order
        from . import light_library
        light_library.unregister()
        print("HDRI Editor: Unregistered light library")
        
        from . import light_operators  
        light_operators.unregister()
        print("HDRI Editor: Unregistered lighting operators")
        
        from . import lighting_core
        lighting_core.unregister()
        print("HDRI Editor: Unregistered lighting core")
        
    except Exception as e:
        print(f"HDRI Editor: Error in lighting unregistration: {e}")
        raise