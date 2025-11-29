"""
Test script to show all available IMAGE_EDITOR overlay properties
Run this in Blender's Python Console to see what properties are available
"""

import bpy

# Find IMAGE_EDITOR
for area in bpy.context.screen.areas:
    if area.type == 'IMAGE_EDITOR':
        for space in area.spaces:
            if space.type == 'IMAGE_EDITOR':
                print("\n=== IMAGE_EDITOR Space Properties ===")
                print(f"Mode: {space.mode}")
                print(f"show_gizmo: {space.show_gizmo}")
                
                if hasattr(space, 'overlay'):
                    print("\n=== Overlay Properties ===")
                    print(f"show_overlays: {space.overlay.show_overlays}")
                    
                    # List ALL overlay attributes
                    overlay_attrs = [attr for attr in dir(space.overlay) if not attr.startswith('_')]
                    for attr in overlay_attrs:
                        try:
                            value = getattr(space.overlay, attr)
                            if not callable(value):
                                print(f"  {attr}: {value}")
                        except:
                            pass
                
                if hasattr(space, 'uv_editor'):
                    print("\n=== UV Editor Properties ===")
                    uv_attrs = [attr for attr in dir(space.uv_editor) if not attr.startswith('_')]
                    for attr in uv_attrs:
                        try:
                            value = getattr(space.uv_editor, attr)
                            if not callable(value):
                                print(f"  {attr}: {value}")
                        except:
                            pass
                
                print("\n=== Image Space Attributes ===")
                space_attrs = [attr for attr in dir(space) if 'grid' in attr.lower() or 'uv' in attr.lower()]
                for attr in space_attrs:
                    try:
                        value = getattr(space, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")
                    except:
                        pass
                
                break
        break
