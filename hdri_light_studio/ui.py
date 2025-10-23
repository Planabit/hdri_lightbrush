"""
UI Module - Main HDRI Light Studio Panels
"""

import bpy
from bpy.types import Panel


class HDRI_PT_main_panel(Panel):
    bl_label = "HDRI Light Studio"
    bl_idname = "HDRI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI Studio"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.hdri_studio
        
        box = layout.box()
        box.label(text="HDRI Canvas", icon='IMAGE_DATA')
        row = box.row()
        row.prop(props, "canvas_size")
        
        if not props.canvas_active:
            row = box.row(align=True)
            row.scale_y = 1.5
            row.operator("hdri_studio.create_canvas_and_paint", text="Create Canvas", icon='ADD')
        else:
            row = box.row(align=True)
            row.operator("hdri_studio.quick_save_canvas", text="Quick Save", icon='FILE_TICK')


class HDRI_PT_hemisphere_panel(Panel):
    bl_label = "Hemisphere"
    bl_idname = "HDRI_PT_hemisphere"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Studio'
    bl_parent_id = "HDRI_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        hemisphere_exists = "HDRI_Hemisphere" in bpy.data.objects
        
        if not hemisphere_exists:
            row = col.row()
            row.scale_y = 1.5
            row.operator("hdri_studio.hemisphere_add", text="Add Hemisphere", icon='MESH_UVSPHERE')
        else:
            row = col.row(align=True)
            row.operator("hdri_studio.hemisphere_remove", text="Remove", icon='X')


classes = [
    HDRI_PT_main_panel,
    HDRI_PT_hemisphere_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("UI panels registered")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("UI panels unregistered")
