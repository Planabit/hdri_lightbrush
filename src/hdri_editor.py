bl_info = {
    "name": "HDRI Editor",
    "author": "Your Name",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > HDRI Editor",
    "description": "HDRI képek szerkesztése Blenderben.",
    "category": "3D View",
}

import bpy

class HDRIEditorPanel(bpy.types.Panel):
    bl_label = "HDRI Editor"
    bl_idname = "VIEW3D_PT_hdri_editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Üdv a HDRI Editorban!")

classes = [HDRIEditorPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
