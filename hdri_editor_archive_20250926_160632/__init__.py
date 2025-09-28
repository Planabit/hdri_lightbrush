bl_info = {
    "name": "HDRI Editor",
    "version": (2, 0, 0),
    "blender": (3, 0, 0),
    "category": "3D View"
}

import bpy
from bpy.types import Operator

class HDRIEditor_OT_LoadHDRI(Operator):
    """Load HDRI file"""
    bl_idname = "hdri_editor.load_hdri"
    bl_label = "Load HDRI"
    
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(
        default="*.hdr;*.exr;*.jpg;*.jpeg;*.png;*.tif;*.tiff",
        options={'HIDDEN'}
    )

    def execute(self, context):
        try:
            img = bpy.data.images.load(self.filepath)
            if self.filepath.lower().endswith(('.hdr', '.exr')):
                img.colorspace_settings.name = 'Linear Rec.709'
            img.pack()
            context.scene.hdri_editor.hdri_previews = img.name
            self.report({'INFO'}, f"Loaded HDRI: {img.name}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load HDRI: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class HDRIEditorProperties(bpy.types.PropertyGroup):
    """Properties for HDRI Editor"""
    hdri_previews: bpy.props.StringProperty(
        name="Current HDRI",
        description="Currently loaded HDRI image",
        default="NONE"
    )

def register():
    # Register basic properties
    bpy.utils.register_class(HDRIEditorProperties)
    bpy.utils.register_class(HDRIEditor_OT_LoadHDRI)
    bpy.types.Scene.hdri_editor = bpy.props.PointerProperty(type=HDRIEditorProperties)
    
    # Register properties and operators
    from . import properties
    properties.register()
    
    from . import operators
    operators.register()
    
    # Register UI
    from . import ui
    ui.register()
    
    print("HDRI Editor: Registered")

def unregister():
    # Unregister UI
    from . import ui  
    ui.unregister()
    
    # Unregister operators
    from . import operators
    operators.unregister()
    
    # Unregister properties
    from . import properties
    properties.unregister()
    
    # Clean up scene properties
    if hasattr(bpy.types.Scene, 'hdri_editor'):
        del bpy.types.Scene.hdri_editor
    
    # Unregister basic classes
    bpy.utils.unregister_class(HDRIEditor_OT_LoadHDRI)
    bpy.utils.unregister_class(HDRIEditorProperties)
    
    print("HDRI Editor: Unregistered")
