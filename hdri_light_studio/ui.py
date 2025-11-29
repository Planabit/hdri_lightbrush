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
        
        # HDRI Canvas Section
        box = layout.box()
        box.label(text="HDRI Canvas", icon='IMAGE_DATA')
        
        # Canvas size selection
        row = box.row()
        row.prop(props, "canvas_size")
        
        if not props.canvas_active:
            # Create new canvas WITH automatic paint mode
            row = box.row(align=True)
            row.scale_y = 1.5
            row.operator("hdri_studio.create_canvas_and_paint", text="Create Canvas", icon='ADD')
            
            # Load existing HDRI
            row = box.row()
            row.operator("hdri_studio.load_canvas", text="Load HDRI...", icon='FILEBROWSER')
        else:
            # Canvas is active - show info
            info_row = box.row()
            info_row.label(text=f"✓ Canvas: {props.canvas_size}", icon='CHECKMARK')
            
            # Save options
            save_box = box.box()
            save_box.label(text="Save Options:", icon='EXPORT')
            
            row = save_box.row(align=True)
            row.scale_y = 1.3
            row.operator("hdri_studio.quick_save_canvas", text="Quick Save", icon='FILE_TICK')
            row.operator("hdri_studio.save_canvas", text="Save As...", icon='EXPORT')
            
            # Canvas management
            row = box.row(align=True)
            row.operator("hdri_studio.clear_canvas", text="Clear", icon='X')
            row.operator("hdri_studio.load_canvas", text="Load Different", icon='FILEBROWSER')


class HDRI_PT_sphere_panel(Panel):
    bl_label = "Preview Sphere"
    bl_idname = "HDRI_PT_sphere_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI Studio"
    bl_parent_id = "HDRI_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sphere_props_obj = scene.sphere_props
        
        box = layout.box()
        
        # Check if sphere/sphere exists
        sphere_obj = scene.objects.get(sphere_props_obj.sphere_name)
        
        if sphere_obj:
            # Sphere exists - show controls
            box.label(text="✓ Preview Sphere Active", icon='CHECKMARK')
            
            # 3D Paint button
            paint_box = box.box()
            paint_box.label(text="3D Painting:", icon='BRUSH_DATA')
            row = paint_box.row(align=True)
            row.scale_y = 1.5
            row.operator("hdri_studio.continuous_paint_enable", text="Start 3D Paint", icon='BRUSH_DATA')
            row.operator("hdri_studio.continuous_paint_disable", text="Stop", icon='PANEL_CLOSE')
            
            # Scale control
            scale_box = box.box()
            scale_box.label(text="Sphere Size:", icon='FULLSCREEN_ENTER')
            row = scale_box.row()
            row.prop(sphere_props_obj, "sphere_scale", text="Scale", slider=True)
            
            # Geometry type info
            row = box.row()
            row.label(text=f"Type: {sphere_props_obj.sphere_type.replace('_', ' ').title()}")
            
            # Remove button
            row = box.row(align=True)
            row.scale_y = 1.2
            row.operator("hdri_studio.sphere_remove", text="Remove Sphere", icon='X')
        else:
            # No sphere - show add button
            row = box.row()
            row.prop(sphere_props_obj, "sphere_type", text="Type")
            
            row = box.row(align=True)
            row.scale_y = 1.5
            row.operator("hdri_studio.sphere_add", text="Add Preview Sphere", icon='SPHERE')


class HDRI_PT_debug_panel(Panel):
    """UV Calibration Debug Panel"""
    bl_label = "UV Calibration Debug"
    bl_idname = "HDRI_PT_debug_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI Studio"
    bl_parent_id = "HDRI_PT_main_panel"
    # Panel is always open (no DEFAULT_CLOSED)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="UV Mapping Calibration", icon='UV')
        
        col = box.column(align=True)
        col.scale_y = 1.3
        
        # Step 1: Draw test points
        col.operator("hdri_studio.draw_debug_points", text="1. Draw Test Points", icon='OUTLINER_OB_POINTCLOUD')
        
        # Step 2: Start tracking
        col.operator("hdri_studio.start_debug_tracking", text="2. Start Tracking", icon='REC')
        
        # Step 3: Instructions
        info_box = box.box()
        info_box.label(text="3. Click 'Start 3D Paint' above")
        info_box.label(text="4. Click targets on sphere (1→9)")
        info_box.label(text="5. Press ESC when done")
        
        # Step 4: Stop and analyze
        col.operator("hdri_studio.stop_debug_tracking", text="6. Stop & Analyze", icon='CONSOLE')
        
        # Info
        info = box.box()
        info.scale_y = 0.8
        info.label(text="Check Console for results!", icon='INFO')


classes = [
    HDRI_PT_main_panel,
    HDRI_PT_sphere_panel,
    HDRI_PT_debug_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("UI panels registered")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("UI panels unregistered")
