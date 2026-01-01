"""
UI Module - Main HDRI Light Studio Panels
3-Step Workflow: Canvas → Sphere → World
"""

import bpy
from bpy.types import Panel


class HDRI_PT_main_panel(Panel):
    """Main HDRI Light Studio panel with 3-step workflow"""
    bl_label = "HDRI Light Studio"
    bl_idname = "HDRI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI Studio"
    
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
                # Sphere type selection
                row = step2_box.row()
                row.prop(sphere_props, "sphere_type", text="Type")
                
                # Add sphere button
                row = step2_box.row(align=True)
                row.scale_y = 1.5
                row.operator("hdri_studio.sphere_add", text="Add Sphere", icon='SPHERE')
        else:
            # Sphere exists - painting is automatic!
            row = step2_box.row()
            row.label(text=f"Type: {sphere_props.sphere_type.replace('_', ' ').title()}")
            
            # Info about automatic painting
            row = step2_box.row()
            row.label(text="Click & drag on sphere to paint", icon='INFO')
            
            # Info about brush settings
            info_box = step2_box.box()
            info_box.label(text="Configure brush in Image Editor:", icon='BRUSH_DATA')
            col = info_box.column(align=True)
            col.label(text="• Radius: Brush size")
            col.label(text="• Strength: Paint intensity")
            col.label(text="• Hardness: Edge softness")
            col.label(text="• Color: Paint color")
            
            # Scale slider
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


# World Settings Panel removed - controls integrated into main panel Step 3


classes = [
    HDRI_PT_main_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("UI panels registered")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("UI panels unregistered")
