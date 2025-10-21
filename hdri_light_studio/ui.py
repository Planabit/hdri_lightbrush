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


class HDRI_PT_HemispherePanel(bpy.types.Panel):
    bl_label = "Hemisphere Preview"
    bl_idname = "HDRI_PT_hemisphere"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Studio'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        # Check if hemisphere exists
        hemisphere_exists = "HDRI_Hemisphere" in bpy.data.objects
        handler_exists = "HDRI_Hemisphere_Handler" in bpy.data.objects
        
        if not hemisphere_exists:
            # Geometry type selection
            col.label(text="Geometry Type:")
            col.prop(context.scene.hemisphere_props, "geometry_type", text="")
            
            # Add hemisphere button
            row = col.row()
            row.scale_y = 1.2
            row.operator("hdri_studio.hemisphere_add", text="Add Hemisphere", icon='MESH_UVSPHERE')
        else:
            # Hemisphere management buttons
            row = col.row(align=True)
            row.operator("hdri_studio.hemisphere_remove", text="Remove", icon='X')
            row.operator("hdri_studio.hemisphere_paint_setup", text="Setup Paint", icon='TPAINT_HLT')
            
            # Working 3D painting with second intersection (RESTORED)
            row = col.row()
            row.scale_y = 1.3
            row.operator("hdri_studio.viewport_paint", text="🎯 3D Paint (Interior)", icon='BRUSH_DATA')
            
            # Scale controls like sample dome system
            if handler_exists:
                col.separator()
                col.label(text="Scale Hemisphere:")
                col.prop(context.scene.hemisphere_props, "hemisphere_scale", text="Scale", slider=True)
            
            # Debug UV Mapping section
            col.separator()
            box = layout.box()
            box.label(text="🔍 Debug UV Mapping", icon='GHOST_ENABLED')
            
            debug_col = box.column(align=True)
            debug_col.operator("hdri_studio.draw_debug_points", text="1. Draw Test Points", icon='OUTLINER_OB_POINTCLOUD')
            debug_col.operator("hdri_studio.start_debug_tracking", text="2. Start Tracking", icon='REC')
            debug_col.operator("hdri_studio.stop_debug_tracking", text="3. Stop & Analyze", icon='CHECKMARK')
            
            debug_col.separator()
            debug_col.label(text="How to use:", icon='INFO')
            debug_col.label(text="1. Draw test points on canvas")
            debug_col.label(text="2. Start tracking")
            debug_col.label(text="3. Paint numbered targets")
            debug_col.label(text="4. Stop & check console")


# Panel classes list  
classes = [
    HDRI_PT_main_panel,
    HDRI_PT_HemispherePanel,
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