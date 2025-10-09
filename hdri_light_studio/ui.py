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
        
        # HDRI File Operations
        box = layout.box()
        box.label(text="HDRI Files", icon='IMAGE_DATA')
        
        # Canvas size selection
        row = box.row()
        row.prop(props, "canvas_size")
        
        # Main action buttons
        if not props.canvas_active:
            # Create new or load existing
            row = box.row(align=True)
            row.scale_y = 1.3
            row.operator("hdri_studio.create_canvas_and_paint", text="New HDRI", icon='ADD')
            row.operator("hdri_studio.load_canvas", text="Load HDRI", icon='FILEBROWSER')
        else:
            # Canvas management and save options
            row = box.row()
            row.operator("hdri_studio.clear_canvas", text="Clear Canvas", icon='X')
            
            # Save buttons
            row = box.row(align=True)
            row.scale_y = 1.2
            row.operator("hdri_studio.quick_save_canvas", text="Quick Save", icon='FILE_TICK')
            row.operator("hdri_studio.save_canvas", text="Save As...", icon='EXPORT')
            
            # Load new HDRI (replace current)
            row = box.row()
            row.operator("hdri_studio.load_canvas", text="Load Different HDRI", icon='FILEBROWSER')

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