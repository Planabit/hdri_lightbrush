"""
UI Module
Simple HDRI Light Studio Panel
"""

import bpy
from bpy.types import Panel

class HDRI_PT_main_panel(Panel):
    """Main HDRI Light Studio Panel with inline canvas display"""
    bl_label = "HDRI Light Studio"
    bl_idname = "HDRI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI Studio"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.hdri_studio
        
        # Canvas controls
        box = layout.box()
        box.label(text="Canvas", icon='IMAGE_DATA')
        
        row = box.row()
        row.prop(props, "canvas_size")
        
        row = box.row()
        if not props.canvas_active:
            row.operator("hdri_studio.create_canvas_and_paint", text="Create Canvas & Paint", icon='TPAINT_HLT')
        else:
            row.operator("hdri_studio.clear_canvas", icon='X')

# Simple UI without canvas draw handler

# Panel classes list  
classes = [
    HDRI_PT_main_panel,
]

def register():
    """Register UI classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("UI module registered")

def unregister():
    """Unregister UI classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("UI module unregistered")