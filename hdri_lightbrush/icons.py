"""
Icon Manager - Custom Icons for HDRI LightBrush
Handles loading and managing custom addon icons
"""

import bpy
import bpy.utils.previews
import os

# Global icon collection
preview_collections = {}


def get_icon(icon_name):
    """Get custom icon ID by name"""
    pcoll = preview_collections.get("main")
    if pcoll and icon_name in pcoll:
        return pcoll[icon_name].icon_id
    return 0  # Return default icon if not found


def register():
    """Load custom icons"""
    import bpy.utils.previews
    
    pcoll = bpy.utils.previews.new()
    
    # Get the icons directory
    icons_dir = os.path.join(os.path.dirname(__file__), "img")
    
    # Load icons
    if os.path.exists(icons_dir):
        # Load small logo for UI
        logo_small = os.path.join(icons_dir, "HDRI lightbrush small.png")
        if os.path.exists(logo_small):
            pcoll.load("logo_small", logo_small, 'IMAGE')
        
        # Load full logo
        logo_full = os.path.join(icons_dir, "HDRI lightbrush.png")
        if os.path.exists(logo_full):
            pcoll.load("logo_full", logo_full, 'IMAGE')
    
    preview_collections["main"] = pcoll


def unregister():
    """Unload custom icons"""
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
