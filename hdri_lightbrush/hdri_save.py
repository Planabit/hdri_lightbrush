"""
HDRI Save and Load Operators
Functions for saving and loading HDRI canvas files
"""

import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD OPERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class HDRI_OT_load_canvas(Operator, ImportHelper):
    """Load HDRI file as canvas for editing"""
    bl_idname = "hdri_studio.load_canvas"
    bl_label = "Load HDRI"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
        default="*.exr;*.hdr;*.png;*.jpg;*.jpeg;*.tiff;*.tif",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        try:
            loaded_image = bpy.data.images.load(self.filepath)
            if not loaded_image:
                self.report({'ERROR'}, "Failed to load image file")
                return {'CANCELLED'}
            
            # Remove existing canvas
            if "HDRI_Canvas" in bpy.data.images:
                bpy.data.images.remove(bpy.data.images["HDRI_Canvas"])
            
            loaded_image.name = "HDRI_Canvas"
            
            # Set float buffer for HDR handling
            if not loaded_image.is_float:
                loaded_image.use_half_precision = False
            
            # Set colorspace
            colorspace_options = ['Linear Rec.709', 'Linear', 'Linear CIE-XYZ E', 'Raw', 'Non-Color', 'sRGB']
            for cs_name in colorspace_options:
                try:
                    loaded_image.colorspace_settings.name = cs_name
                    break
                except:
                    continue
            
            # Mark canvas active
            props = context.scene.hdri_studio
            props.canvas_active = True
            
            # Setup Image Editor
            self._setup_image_editor(context, loaded_image)
            
            # Setup paint settings
            self._setup_paint_settings(context, loaded_image)
            
            # Update sphere and world
            self._update_sphere_with_image(context, loaded_image)
            self._update_world_with_image(context, loaded_image)
            
            filename = os.path.basename(self.filepath)
            self.report({'INFO'}, f"HDRI loaded: {filename}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Load failed: {e}")
            return {'CANCELLED'}
    
    def _setup_image_editor(self, context, image):
        """Setup Image Editor with loaded image"""
        image_editor = None
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                image_editor = area
                break
        
        if image_editor:
            for space in image_editor.spaces:
                if space.type == 'IMAGE_EDITOR':
                    space.image = image
                    space.mode = 'PAINT'
                    space.show_region_ui = True
                    image_editor.tag_redraw()
                    break
        else:
            # Split viewport and create Image Editor
            viewport = None
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    viewport = area
                    break
            
            if viewport:
                with context.temp_override(area=viewport):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
                
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D' and area != viewport:
                        area.type = 'IMAGE_EDITOR'
                        for space in area.spaces:
                            if space.type == 'IMAGE_EDITOR':
                                space.image = image
                                space.mode = 'PAINT'
                                space.show_region_ui = True
                                area.tag_redraw()
                                break
                        break
    
    def _setup_paint_settings(self, context, image):
        """Setup texture paint settings"""
        if context.tool_settings and context.tool_settings.image_paint:
            settings = context.tool_settings.image_paint
            settings.canvas = image
            
            if not settings.brush:
                if "HDRI_Brush" in bpy.data.brushes:
                    settings.brush = bpy.data.brushes["HDRI_Brush"]
                else:
                    brush = bpy.data.brushes.new("HDRI_Brush", mode='TEXTURE_PAINT')
                    brush.color = (1.0, 1.0, 1.0)
                    brush.size = 50
                    brush.strength = 1.0
                    brush.blend = 'MIX'
                    settings.brush = brush
    
    def _update_sphere_with_image(self, context, image):
        """Update preview sphere material with loaded image"""
        sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
        if not sphere or not sphere.active_material:
            return
        
        material = sphere.active_material
        if not material.use_nodes:
            return
        
        def update_textures(node_tree, depth=0):
            if not node_tree or depth > 5:
                return
            for node in node_tree.nodes:
                if node.type in ['TEX_ENVIRONMENT', 'TEX_IMAGE']:
                    node.image = image
                elif hasattr(node, 'node_tree') and node.node_tree:
                    update_textures(node.node_tree, depth + 1)
        
        update_textures(material.node_tree)
        material.update_tag()
        
        for area in context.screen.areas:
            area.tag_redraw()
    
    def _update_world_with_image(self, context, image):
        """Update world environment texture with loaded image"""
        world = context.scene.world
        if not world or not world.use_nodes:
            return
        
        for node in world.node_tree.nodes:
            if node.type == 'TEX_ENVIRONMENT':
                node.image = image
                world.node_tree.update_tag()
                break
        
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ═══════════════════════════════════════════════════════════════════════════════
# SAVE OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class HDRI_OT_save_canvas(Operator, ExportHelper):
    """Save HDRI canvas to file"""
    bl_idname = "hdri_studio.save_canvas"
    bl_label = "Save HDRI"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".exr"
    
    filter_glob: StringProperty(
        default="*.exr;*.hdr;*.png;*.jpg",
        options={'HIDDEN'}
    )
    
    file_format: EnumProperty(
        name="Format",
        items=[
            ('OPEN_EXR', 'OpenEXR (.exr)', 'High dynamic range EXR format'),
            ('HDR', 'Radiance HDR (.hdr)', 'Traditional HDR format'),
            ('PNG', 'PNG (.png)', 'Standard PNG format'),
            ('JPEG', 'JPEG (.jpg)', 'Standard JPEG format'),
        ],
        default='OPEN_EXR'
    )
    
    color_depth: EnumProperty(
        name="Color Depth",
        items=[
            ('16', '16 bit (Half Float)', 'Half precision'),
            ('32', '32 bit (Full Float)', 'Full precision'),
        ],
        default='32'
    )
    
    def execute(self, context):
        try:
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "No HDRI canvas found")
                return {'CANCELLED'}
            
            canvas = bpy.data.images["HDRI_Canvas"]
            original_format = canvas.file_format
            
            # Set format and extension
            format_ext = {
                'OPEN_EXR': '.exr',
                'HDR': '.hdr',
                'PNG': '.png',
                'JPEG': '.jpg'
            }
            
            canvas.file_format = self.file_format
            if hasattr(canvas, 'use_half_precision') and self.file_format == 'OPEN_EXR':
                canvas.use_half_precision = (self.color_depth == '16')
            
            ext = format_ext.get(self.file_format, '.exr')
            if not self.filepath.lower().endswith(ext):
                self.filepath = os.path.splitext(self.filepath)[0] + ext
            
            # Save
            canvas.filepath_raw = self.filepath
            canvas.save()
            canvas.file_format = original_format
            
            self.report({'INFO'}, f"HDRI saved: {self.filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Save failed: {e}")
            return {'CANCELLED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "file_format", text="Format")
        if self.file_format == 'OPEN_EXR':
            layout.prop(self, "color_depth", text="Depth")


class HDRI_OT_quick_save_canvas(Operator):
    """Quick save HDRI canvas"""
    bl_idname = "hdri_studio.quick_save_canvas"
    bl_label = "Quick Save HDRI"
    
    def execute(self, context):
        try:
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "No HDRI canvas found")
                return {'CANCELLED'}
            
            canvas = bpy.data.images["HDRI_Canvas"]
            
            # Determine filepath
            if canvas.filepath and os.path.exists(bpy.path.abspath(canvas.filepath)):
                filepath = bpy.path.abspath(canvas.filepath)
            else:
                if bpy.data.filepath:
                    blend_dir = os.path.dirname(bpy.data.filepath)
                    blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
                    filename = f"{blend_name}_hdri.exr"
                else:
                    blend_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                    filename = "hdri_canvas.exr"
                
                filepath = os.path.join(blend_dir, filename)
                
                # Ensure unique filename
                counter = 1
                base = filepath
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(base)
                    filepath = f"{name}_{counter:03d}{ext}"
                    counter += 1
            
            # Set format based on extension
            ext = os.path.splitext(filepath)[1].lower()
            original_format = canvas.file_format
            
            format_map = {
                '.exr': 'OPEN_EXR',
                '.hdr': 'HDR',
                '.png': 'PNG',
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG'
            }
            canvas.file_format = format_map.get(ext, 'OPEN_EXR')
            
            # Save
            canvas.filepath_raw = filepath
            canvas.save()
            
            try:
                canvas.filepath = bpy.path.relpath(filepath)
            except:
                canvas.filepath = filepath
            
            canvas.file_format = original_format
            
            self.report({'INFO'}, f"HDRI saved: {os.path.basename(filepath)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Quick save failed: {e}")
            return {'CANCELLED'}


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def register():
    bpy.utils.register_class(HDRI_OT_load_canvas)
    bpy.utils.register_class(HDRI_OT_save_canvas)
    bpy.utils.register_class(HDRI_OT_quick_save_canvas)


def unregister():
    bpy.utils.unregister_class(HDRI_OT_quick_save_canvas)
    bpy.utils.unregister_class(HDRI_OT_save_canvas)
    bpy.utils.unregister_class(HDRI_OT_load_canvas)
