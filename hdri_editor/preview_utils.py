import bpy
import bpy.utils.previews

# Preview collections
preview_collections = {}

def init_preview_collection():
    """Initialize or get the preview collection"""
    if "main" not in preview_collections:
        preview_collections["main"] = bpy.utils.previews.new()
    return preview_collections["main"]

def enum_previews_from_directory(self, context):
    """EnumProperty callback for hdri_previews"""
    enum_items = []
    
    # Start with None option
    enum_items.append(("NONE", "None", "", 0, 0))
    
    # Get the preview collection
    pcoll = init_preview_collection()
    
    # Add all images
    for i, image in enumerate(bpy.data.images, start=1):
        if image.type == 'IMAGE':
            name = image.name
            # Generate a thumbnail if it doesn't exist
            if name not in pcoll:
                thumb = pcoll.load(name, image.filepath, 'IMAGE', force_reload=True)
            enum_items.append((name, name, "", pcoll[name].icon_id, i))
    
    return enum_items

def update_preview(self, context):
    """Update callback for hdri_previews"""
    if self.hdri_previews != 'NONE':
        context.scene['hdri_editor_preview_image'] = self.hdri_previews

class HDRIEditorProperties(bpy.types.PropertyGroup):
    hdri_previews: bpy.props.EnumProperty(
        items=enum_previews_from_directory,
        update=update_preview,
        name="HDRI Previews",
        description="Preview of available HDRI images"
    )

def register():
    init_preview_collection()
    bpy.utils.register_class(HDRIEditorProperties)
    bpy.types.Scene.hdri_editor = bpy.props.PointerProperty(type=HDRIEditorProperties)

def unregister():
    del bpy.types.Scene.hdri_editor
    bpy.utils.unregister_class(HDRIEditorProperties)
    
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()