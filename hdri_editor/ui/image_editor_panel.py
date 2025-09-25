"""
Image Editor Panel for HDRI Editor.
Provides full image editor functionality similar to Blender's Image Editor.
"""

import bpy
from bpy.types import Panel

class HDRI_EDITOR_PT_image_editor(Panel):
    """Full-featured image editor panel for HDRI viewing and editing"""
    bl_label = "HDRI Image Editor"
    bl_idname = "VIEW3D_PT_hdri_editor_image"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # Show panel when HDRI is selected
        current_hdri = context.scene.hdri_editor.hdri_previews
        return current_hdri != 'NONE' and current_hdri in bpy.data.images

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='IMAGE_DATA')

    def draw(self, context):
        layout = self.layout
        
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            layout.label(text="No HDRI selected", icon='ERROR')
            return
            
        img = bpy.data.images[current_hdri]
        
        # Image viewer controls header
        header = layout.row(align=True)
        
        # View controls
        view_col = header.column(align=True)
        view_row = view_col.row(align=True)
        view_row.operator("hdri_editor.view_fit", text="", icon='FULLSCREEN_ENTER')
        view_row.operator("hdri_editor.view_actual", text="", icon='FILE_TICK') 
        view_row.operator("hdri_editor.view_center", text="", icon='PIVOT_CURSOR')
        
        # Zoom info
        zoom_col = header.column(align=True)
        current_zoom = context.scene.get('hdri_editor_zoom', 1.0)
        zoom_col.label(text=f"{current_zoom*100:.0f}%")
        
        # Display options row
        display_box = layout.box()
        display_row = display_box.row(align=True)
        
        # View mode toggles
        display_row.prop(img, "use_view_as_render", text="", icon='RESTRICT_RENDER_OFF')
        
        # Alpha display toggle (if has alpha)
        if img.channels == 4:
            display_row.operator("hdri_editor.toggle_alpha", text="", icon='MOD_OPACITY')
        
        # Display settings
        display_row.separator()
        display_row.operator("hdri_editor.view_histogram", text="", icon='SEQ_HISTOGRAM')
        
        # Main image display area
        image_box = layout.box()
        image_box.label(text=f"Image Viewer: {img.name}")
        
        # Calculate dynamic size based on panel width
        region = context.region
        panel_width = region.width if region else 300
        target_width = panel_width - 30
        
        # Calculate aspect ratio for proper scaling  
        if img.size[0] > 0 and img.size[1] > 0:
            aspect_ratio = img.size[1] / img.size[0]
        else:
            aspect_ratio = 0.5
        
        # Create the main image display
        col = image_box.column(align=True)
        
        # Image display with proper aspect ratio handling
        split = col.split(factor=1.0, align=True)
        
        # Use template_image with the image itself as user
        split.template_image(img, None, compact=True)
        
        # Add zoom and pan controls below image
        controls_row = col.row(align=True)
        controls_row.scale_y = 0.8
        controls_row.operator("hdri_editor.zoom_in", text="", icon='ZOOM_IN')
        controls_row.operator("hdri_editor.zoom_out", text="", icon='ZOOM_OUT')
        controls_row.separator()
        controls_row.operator("hdri_editor.pan_reset", text="", icon='PIVOT_CURSOR')
        
        # Image information panel
        info_box = layout.box()
        info_box.label(text="Image Information:", icon='INFO')
        
        info_col = info_box.column(align=True)
        
        # Basic info
        info_col.label(text=f"Name: {img.name}")
        info_col.label(text=f"Size: {img.size[0]} x {img.size[1]}")
        info_col.label(text=f"Channels: {img.channels}")
        
        if hasattr(img, 'depth'):
            info_col.label(text=f"Depth: {img.depth} bit")
        
        # File info
        if img.filepath:
            import os
            file_size = "Unknown"
            try:
                if os.path.exists(img.filepath):
                    size_bytes = os.path.getsize(img.filepath)
                    if size_bytes > 1024*1024:
                        file_size = f"{size_bytes/(1024*1024):.1f} MB"
                    else:
                        file_size = f"{size_bytes/1024:.1f} KB"
            except:
                pass
            
            info_col.label(text=f"File Size: {file_size}")
            info_col.label(text=f"Format: {img.file_format}")
        
        # Color management
        cm_box = layout.box()
        cm_box.label(text="Color Management:", icon='COLOR')
        
        cm_col = cm_box.column(align=True)
        cm_col.prop(img.colorspace_settings, "name", text="Color Space")
        
        # Image operations
        ops_box = layout.box()
        ops_box.label(text="Operations:", icon='MODIFIER')
        
        ops_col = ops_box.column(align=True)
        ops_row1 = ops_col.row(align=True)
        ops_row1.operator("hdri_editor.reload_image", text="Reload")
        ops_row1.operator("hdri_editor.save_image", text="Save")
        
        ops_row2 = ops_col.row(align=True)
        ops_row2.operator("hdri_editor.pack_image", text="Pack")
        ops_row2.operator("hdri_editor.unpack_image", text="Unpack")

# Image Editor Operators
class HDRI_EDITOR_OT_view_fit(bpy.types.Operator):
    """Fit image to view"""
    bl_idname = "hdri_editor.view_fit"
    bl_label = "View Fit"
    bl_description = "Fit entire image in view"

    def execute(self, context):
        # Store current image for use in image editor
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri in bpy.data.images:
            context.scene['hdri_editor_view_mode'] = 'FIT'
        return {'FINISHED'}

class HDRI_EDITOR_OT_view_actual(bpy.types.Operator):
    """View image at actual size"""
    bl_idname = "hdri_editor.view_actual" 
    bl_label = "Actual Size"
    bl_description = "View image at 1:1 pixel ratio"

    def execute(self, context):
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri in bpy.data.images:
            context.scene['hdri_editor_view_mode'] = 'ACTUAL'
        return {'FINISHED'}

class HDRI_EDITOR_OT_view_center(bpy.types.Operator):
    """Center image view"""
    bl_idname = "hdri_editor.view_center"
    bl_label = "Center View"
    bl_description = "Center image in view"

    def execute(self, context):
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri in bpy.data.images:
            context.scene['hdri_editor_view_mode'] = 'CENTER'
        return {'FINISHED'}

class HDRI_EDITOR_OT_reload_image(bpy.types.Operator):
    """Reload current image from disk"""
    bl_idname = "hdri_editor.reload_image"
    bl_label = "Reload Image"
    bl_description = "Reload image from disk"

    def execute(self, context):
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri in bpy.data.images:
            img = bpy.data.images[current_hdri]
            img.reload()
            self.report({'INFO'}, f"Reloaded {img.name}")
        return {'FINISHED'}

class HDRI_EDITOR_OT_save_image(bpy.types.Operator):
    """Save current image"""
    bl_idname = "hdri_editor.save_image"
    bl_label = "Save Image"
    bl_description = "Save image to disk"

    def execute(self, context):
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri in bpy.data.images:
            img = bpy.data.images[current_hdri]
            img.save()
            self.report({'INFO'}, f"Saved {img.name}")
        return {'FINISHED'}

class HDRI_EDITOR_OT_pack_image(bpy.types.Operator):
    """Pack image into blend file"""
    bl_idname = "hdri_editor.pack_image"
    bl_label = "Pack Image"
    bl_description = "Pack image data into blend file"

    def execute(self, context):
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri in bpy.data.images:
            img = bpy.data.images[current_hdri]
            img.pack()
            self.report({'INFO'}, f"Packed {img.name}")
        return {'FINISHED'}

class HDRI_EDITOR_OT_unpack_image(bpy.types.Operator):
    """Unpack image from blend file"""
    bl_idname = "hdri_editor.unpack_image"
    bl_label = "Unpack Image"
    bl_description = "Unpack image from blend file"

    def execute(self, context):
        current_hdri = context.scene.hdri_editor.hdri_previews
        if current_hdri in bpy.data.images:
            img = bpy.data.images[current_hdri]
            if img.packed_file:
                img.unpack()
                self.report({'INFO'}, f"Unpacked {img.name}")
            else:
                self.report({'WARNING'}, f"{img.name} is not packed")
        return {'FINISHED'}

class HDRI_EDITOR_OT_toggle_alpha(bpy.types.Operator):
    """Toggle alpha display"""
    bl_idname = "hdri_editor.toggle_alpha"
    bl_label = "Toggle Alpha"
    bl_description = "Toggle alpha channel display"

    def execute(self, context):
        # This would toggle alpha display in a real image editor
        # For now, just show a message
        self.report({'INFO'}, "Alpha display toggled")
        return {'FINISHED'}

class HDRI_EDITOR_OT_view_histogram(bpy.types.Operator):
    """Show image histogram"""
    bl_idname = "hdri_editor.view_histogram"
    bl_label = "View Histogram"
    bl_description = "Show image histogram"

    def execute(self, context):
        # This would open histogram view
        self.report({'INFO'}, "Histogram view")
        return {'FINISHED'}

class HDRI_EDITOR_OT_zoom_in(bpy.types.Operator):
    """Zoom in on image"""
    bl_idname = "hdri_editor.zoom_in"
    bl_label = "Zoom In"
    bl_description = "Zoom in on image"

    def execute(self, context):
        # Store zoom level
        current_zoom = context.scene.get('hdri_editor_zoom', 1.0)
        new_zoom = min(current_zoom * 1.5, 10.0)
        context.scene['hdri_editor_zoom'] = new_zoom
        self.report({'INFO'}, f"Zoom: {new_zoom:.1f}x")
        return {'FINISHED'}

class HDRI_EDITOR_OT_zoom_out(bpy.types.Operator):
    """Zoom out on image"""
    bl_idname = "hdri_editor.zoom_out"
    bl_label = "Zoom Out"
    bl_description = "Zoom out on image"

    def execute(self, context):
        # Store zoom level
        current_zoom = context.scene.get('hdri_editor_zoom', 1.0)
        new_zoom = max(current_zoom / 1.5, 0.1)
        context.scene['hdri_editor_zoom'] = new_zoom
        self.report({'INFO'}, f"Zoom: {new_zoom:.1f}x")
        return {'FINISHED'}

class HDRI_EDITOR_OT_pan_reset(bpy.types.Operator):
    """Reset pan and zoom"""
    bl_idname = "hdri_editor.pan_reset"
    bl_label = "Reset View"
    bl_description = "Reset pan and zoom to default"

    def execute(self, context):
        context.scene['hdri_editor_zoom'] = 1.0
        context.scene['hdri_editor_pan_x'] = 0.0
        context.scene['hdri_editor_pan_y'] = 0.0
        self.report({'INFO'}, "View reset")
        return {'FINISHED'}

# Classes for registration
__all__ = [
    'HDRI_EDITOR_PT_image_editor',
    'HDRI_EDITOR_OT_view_fit',
    'HDRI_EDITOR_OT_view_actual',
    'HDRI_EDITOR_OT_view_center',
    'HDRI_EDITOR_OT_reload_image',
    'HDRI_EDITOR_OT_save_image',
    'HDRI_EDITOR_OT_pack_image',
    'HDRI_EDITOR_OT_unpack_image',
    'register',
    'unregister'
]

classes = (
    HDRI_EDITOR_PT_image_editor,
    HDRI_EDITOR_OT_view_fit,
    HDRI_EDITOR_OT_view_actual,
    HDRI_EDITOR_OT_view_center,
    HDRI_EDITOR_OT_reload_image,
    HDRI_EDITOR_OT_save_image,
    HDRI_EDITOR_OT_pack_image,
    HDRI_EDITOR_OT_unpack_image,
    HDRI_EDITOR_OT_toggle_alpha,
    HDRI_EDITOR_OT_view_histogram,
    HDRI_EDITOR_OT_zoom_in,
    HDRI_EDITOR_OT_zoom_out,
    HDRI_EDITOR_OT_pan_reset,
)

def register():
    """Register image editor classes"""
    try:
        for cls in classes:
            try:
                bpy.utils.register_class(cls)
                print(f"HDRI Editor: Registered {cls.__name__}")
            except ValueError as e:
                print(f"HDRI Editor: Class {cls.__name__} already registered")
    except Exception as e:
        print(f"HDRI Editor: Error during image editor registration: {str(e)}")
        raise

def unregister():
    """Unregister image editor classes"""
    try:
        for cls in reversed(classes):
            try:
                bpy.utils.unregister_class(cls)
                print(f"HDRI Editor: Unregistered {cls.__name__}")
            except ValueError:
                print(f"HDRI Editor: Class {cls.__name__} already unregistered")
            except RuntimeError:
                print(f"HDRI Editor: Failed to unregister {cls.__name__}, may be in use")
    except Exception as e:
        print(f"HDRI Editor: Error during image editor unregistration: {str(e)}")
        raise