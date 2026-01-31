"""
UI Module - Main HDRI LightBrush Panels
3-Step Workflow: Canvas -> Sphere -> World
"""

import bpy
from bpy.types import Panel
from . import icons


class HDRI_PT_main_panel(Panel):
    """Main HDRI LightBrush panel with 3-step workflow"""
    bl_label = "HDRI LightBrush"
    bl_idname = "HDRI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI LightBrush"
    
    def draw_header(self, context):
        """Draw custom logo in panel header"""
        layout = self.layout
        icon_id = icons.get_icon("logo_small")
        if icon_id:
            layout.label(text="", icon_value=icon_id)
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.hdri_studio
        sphere_props = context.scene.sphere_props
        
        # Determine current workflow step
        has_canvas = props.canvas_active
        sphere_obj = context.scene.objects.get(sphere_props.sphere_name)
        has_sphere = sphere_obj is not None
        
        # ═══════════════════════════════════════════════════════
        # STEP 1: Canvas
        # ═══════════════════════════════════════════════════════
        step1_box = layout.box()
        step1_header = step1_box.row()
        
        if has_canvas:
            step1_header.label(text="Step 1: Canvas ✓", icon='CHECKMARK')
        else:
            step1_header.label(text="Step 1: Create Canvas", icon='IMAGE_DATA')
        
        if not has_canvas:
            # Canvas size selection
            row = step1_box.row()
            row.prop(props, "canvas_size", text="Size")
            
            # Create new canvas
            row = step1_box.row(align=True)
            row.scale_y = 1.5
            row.operator("hdri_studio.create_canvas_and_paint", text="New Canvas", icon='ADD')
            row.operator("hdri_studio.load_canvas", text="Load", icon='FILEBROWSER')
        else:
            # Canvas active - compact info
            row = step1_box.row()
            row.label(text=f"Active: {props.canvas_size}")
            
            # Save buttons
            row = step1_box.row(align=True)
            row.operator("hdri_studio.quick_save_canvas", text="Save", icon='FILE_TICK')
            row.operator("hdri_studio.save_canvas", text="Save As", icon='EXPORT')
            
            # Reset/Load different
            row = step1_box.row(align=True)
            row.operator("hdri_studio.clear_canvas", text="Clear", icon='BRUSH_DATA')
            row.operator("hdri_studio.load_canvas", text="Load", icon='FILEBROWSER')
        
        # ═══════════════════════════════════════════════════════
        # STEP 2: Preview Sphere
        # ═══════════════════════════════════════════════════════
        step2_box = layout.box()
        step2_header = step2_box.row()
        
        if has_sphere:
            step2_header.label(text="Step 2: Sphere ✓", icon='CHECKMARK')
        else:
            step2_header.label(text="Step 2: Add Sphere", icon='SPHERE')
        
        # Only enable if canvas exists
        step2_box.enabled = has_canvas
        
        if not has_sphere:
            if not has_canvas:
                row = step2_box.row()
                row.label(text="Create canvas first", icon='INFO')
            else:
                # Add sphere button
                row = step2_box.row(align=True)
                row.scale_y = 1.5
                row.operator("hdri_studio.sphere_add", text="Add Sphere", icon='SPHERE')
        else:
            # Sphere exists - painting is automatic!
            row = step2_box.row()
            row.label(text="Click & drag on sphere to paint", icon='INFO')
            
            # ═══════════════════════════════════════════════════════
            # BRUSH SETTINGS BOX
            # ═══════════════════════════════════════════════════════
            brush_box = step2_box.box()
            brush_box.label(text="Brush Settings", icon='BRUSH_DATA')
            
            # Color picker (large, prominent)
            col = brush_box.column()
            col.template_color_picker(props, "paint_color", value_slider=True)
            row = brush_box.row()
            row.prop(props, "paint_color", text="")
            
            brush_box.separator()
            
            # Size with slider
            row = brush_box.row(align=True)
            row.prop(props, "paint_size", text="Size", slider=True)
            
            # Strength with slider  
            row = brush_box.row(align=True)
            row.prop(props, "paint_strength", text="Strength", slider=True)
            
            # Hardness with slider
            row = brush_box.row(align=True)
            row.prop(props, "paint_hardness", text="Hardness", slider=True)
            
            # Blend mode dropdown
            row = brush_box.row()
            row.prop(props, "paint_blend", text="Blend")
            
            # Scale slider
            step2_box.separator()
            row = step2_box.row()
            row.prop(sphere_props, "sphere_scale", text="Sphere Scale", slider=True)
            
            # Remove sphere
            row = step2_box.row()
            row.operator("hdri_studio.sphere_remove", text="Remove Sphere", icon='X')
        
        # ═══════════════════════════════════════════════════════
        # STEP 3: Apply to World
        # ═══════════════════════════════════════════════════════
        step3_box = layout.box()
        step3_header = step3_box.row()
        step3_header.label(text="Step 3: World Background", icon='WORLD')
        
        # Only enable if canvas exists
        step3_box.enabled = has_canvas
        
        if not has_canvas:
            row = step3_box.row()
            row.label(text="Create canvas first", icon='INFO')
        else:
            # World background controls
            row = step3_box.row(align=True)
            row.scale_y = 1.4
            row.operator("hdri_studio.set_world_background", text="Set Background", icon='WORLD_DATA')
            row.operator("hdri_studio.remove_world_background", text="Remove", icon='X')
            
            # World properties (if available)
            if hasattr(context.scene, 'hdri_studio_world'):
                world_props = context.scene.hdri_studio_world
                
                row = step3_box.row()
                row.prop(world_props, "background_strength", text="Strength")
                
                row = step3_box.row()
                row.prop(world_props, "background_rotation", text="Rotation", slider=True)
        
        # ═══════════════════════════════════════════════════════
        # PERFORMANCE SETTINGS (for 4K-8K textures)
        # ═══════════════════════════════════════════════════════
        if has_canvas:
            perf_box = layout.box()
            perf_header = perf_box.row()
            perf_header.label(text="Performance", icon='PREFERENCES')
            
            # Auto-suggest performance mode for large textures
            canvas_image = bpy.data.images.get("HDRI_Canvas")
            if canvas_image and canvas_image.size[0] >= 4096:
                row = perf_box.row()
                row.alert = not props.performance_mode
                row.prop(props, "performance_mode", text="Enable for 4K+ Textures")
            else:
                row = perf_box.row()
                row.prop(props, "performance_mode", text="Performance Mode")
            
            if props.performance_mode or (canvas_image and canvas_image.size[0] >= 4096):
                row = perf_box.row()
                row.prop(props, "update_rate", text="Update Rate")


# World Settings Panel removed - controls integrated into main panel Step 3


# Support panel disabled for Blender Extensions compliance
# (Advertisements/donation links not allowed in UI)
# For support options, see: https://github.com/Planabit/hdri_lightbrush
"""
class HDRI_PT_Support(bpy.types.Panel):
    \"\"\"Support panel for donations and custom development\"\"\"
    bl_label = "Support Development"
    bl_idname = "HDRI_PT_support"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI LightBrush"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        \"\"\"Draw custom logo in support panel header\"\"\"
        layout = self.layout
        icon_id = icons.get_icon("logo_small")
        if icon_id:
            layout.label(text="", icon_value=icon_id)

    def draw(self, context):
        layout = self.layout
        
        # Logo banner at top (if available)
        icon_id = icons.get_icon("logo_full")
        if icon_id:
            box = layout.box()
            box.template_icon(icon_value=icon_id, scale=5.0)
        
        box = layout.box()
        box.label(text="Enjoying HDRI LightBrush?", icon='HEART')
        
        col = box.column(align=True)
        col.operator("wm.url_open", text="Buy Me a Coffee", icon='URL').url = "https://ko-fi.com/tamaslaszlo"
        col.operator("wm.url_open", text="Support on Patreon", icon='URL').url = "https://patreon.com/TamasLaszlo"
        
        box.separator()
        box.label(text="Need custom features?", icon='MODIFIER')
        box.operator("wm.url_open", text="Contact for Development", icon='MAIL').url = "mailto:planabit@gmail.com?subject=HDRI%20LightBrush%20-%20Custom%20Development"
        
        box.separator()
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="Free & Open Source - GPL-3.0-or-later", icon='INFO')
"""


classes = [
    HDRI_PT_main_panel,
    # HDRI_PT_Support removed - not allowed in Blender Extensions
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
