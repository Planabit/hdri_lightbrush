"""
Preview utility functions for HDRI Editor.
"""

import bpy
import bpy.utils.previews
from bpy.props import EnumProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup

# Preview collections dictionary
preview_collections = {}

class HDRIEditorPreviewCollection:
    """Class to manage preview collection for HDRI files"""
    def __init__(self):
        """Initialize preview collection"""
        self.previews = bpy.utils.previews.new()
        preview_collections["main"] = self.previews
    
    def load_preview(self, image):
        """Load preview for a specific image.
        
        Args:
            image: Blender image object
            
        Returns:
            Preview object or None on error
        """
        if not image or image.name == 'NONE':
            return None
            
        try:
            if image.name not in self.previews:
                self.previews.load(image.name, image.filepath, 'IMAGE')
            return self.previews[image.name]
        except Exception as e:
            print(f"Failed to load preview for {image.name}: {e}")
            return None
    
    def clear_preview(self, name):
        """Clear a specific preview from collection.
        
        Args:
            name: Name of preview to clear
        """
        if name in self.previews:
            del self.previews[name]
    
    def clear_all(self):
        """Clear all previews"""
        self.previews.clear()

def get_preview_collection():
    """Get or create the preview collection.
    
    Returns:
        Preview collection object
    """
    if "main" not in preview_collections:
        HDRIEditorPreviewCollection()
    return preview_collections["main"]

def enum_previews_from_images(self, context):
    """EnumProperty callback for hdri_previews.
    
    Args:
        self: Property owner
        context: Blender context
        
    Returns:
        List of enum items for preview selection
    """
    enum_items = []
    
    # Add None option
    enum_items.append(('NONE', 'None', '', 0, 0))
    
    # Get preview collection
    pcoll = get_preview_collection()
    
    # Add all compatible images
    for i, image in enumerate(bpy.data.images, start=1):
        if image.type == 'IMAGE' and image.size[0] > 0 and image.size[1] > 0:
            name = image.name
            try:
                if name not in pcoll:
                    thumb = pcoll.load(name, image.filepath, 'IMAGE')
                enum_items.append((name, name, '', pcoll[name].icon_id, i))
            except Exception as e:
                print(f"Failed to load preview for {name}: {e}")
                continue
    
    return enum_items

def update_preview_selection(self, context):
    """Callback when preview selection changes.
    
    Args:
        self: Property owner
        context: Blender context
    """
    if self.hdri_previews != 'NONE':
        context.scene['hdri_editor_preview_image'] = self.hdri_previews
        
        # Update world background if auto-update is enabled
        if self.auto_update_world:
            try:
                bpy.ops.hdri_editor.set_background('EXEC_DEFAULT')
            except Exception as e:
                print(f"Failed to auto-update world: {e}")

class HDRIEditorPreferences(PropertyGroup):
    """Properties for HDRI Editor preview system"""
    hdri_previews: EnumProperty(
        items=enum_previews_from_images,
        update=update_preview_selection,
        name="HDRI Previews",
        description="Preview of available HDRI images"
    )
    
    auto_update_world: BoolProperty(
        name="Auto Update World",
        description="Automatically update world when selecting a new HDRI",
        default=False
    )
    
    last_selected: StringProperty(
        name="Last Selected",
        description="Name of last selected HDRI",
        default="NONE"
    )

# Classes and registration info
__all__ = [
    'HDRIEditorPreferences',
    'register',
    'unregister',
    'get_preview_collection',
    'enum_previews_from_images',
    'update_preview_selection'
]

classes = (
    HDRIEditorPreferences,
)

def register():
    """Register preview system"""
    try:
        # Register property group
        for cls in classes:
            try:
                bpy.utils.register_class(cls)
                print(f"HDRI Editor: Registered {cls.__name__}")
            except ValueError as e:
                print(f"HDRI Editor: Class {cls.__name__} already registered")
        
        bpy.types.Scene.hdri_editor = bpy.props.PointerProperty(type=HDRIEditorPreferences)
        
        # Initialize preview collection
        get_preview_collection()
        print("HDRI Editor: Preview system initialized")
        
    except Exception as e:
        print(f"HDRI Editor: Error during preview registration: {str(e)}")
        raise

def unregister():
    """Unregister preview system"""
    try:
        # Clear preview collections first
        for pcoll in preview_collections.values():
            try:
                bpy.utils.previews.remove(pcoll)
            except Exception as e:
                print(f"HDRI Editor: Error removing preview collection: {str(e)}")
        preview_collections.clear()
        
        # Unregister property group
        try:
            del bpy.types.Scene.hdri_editor
        except Exception as e:
            print(f"HDRI Editor: Error removing scene property: {str(e)}")
        
        # Unregister classes
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
                print(f"HDRI Editor: Unregistered {cls.__name__}")
            except ValueError:
                print(f"HDRI Editor: Class {cls.__name__} already unregistered")
            except RuntimeError:
                print(f"HDRI Editor: Failed to unregister {cls.__name__}, may be in use")
                
        print("HDRI Editor: Preview system unregistered")
        
    except Exception as e:
        print(f"HDRI Editor: Error during preview unregistration: {str(e)}")
        raise