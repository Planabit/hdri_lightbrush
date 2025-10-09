"""
HDRI Save and Load Operators
Functions for saving and loading HDRI canvas files
"""

import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

class HDRI_OT_load_canvas(Operator, ImportHelper):
    """Load HDRI file as canvas for editing"""
    bl_idname = "hdri_studio.load_canvas"
    bl_label = "Load HDRI"
    bl_description = "Load HDRI file and set up for editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    # File extension filter
    filter_glob: StringProperty(
        default="*.exr;*.hdr;*.png;*.jpg;*.jpeg;*.tiff;*.tif",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        try:
            # Load the image
            loaded_image = bpy.data.images.load(self.filepath)
            
            if not loaded_image:
                self.report({'ERROR'}, "Failed to load image file")
                return {'CANCELLED'}
            
            # Remove existing canvas if any
            if "HDRI_Canvas" in bpy.data.images:
                bpy.data.images.remove(bpy.data.images["HDRI_Canvas"])
            
            # Rename loaded image to HDRI_Canvas
            loaded_image.name = "HDRI_Canvas"
            
            # Ensure proper colorspace for HDRI work
            try:
                loaded_image.colorspace_settings.name = 'Linear Rec.709'
            except:
                try:
                    loaded_image.colorspace_settings.name = 'sRGB'
                except:
                    pass
            
            # Mark canvas as active
            props = context.scene.hdri_studio
            props.canvas_active = True
            
            # Check if Image Editor already exists
            image_editor_area = None
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    image_editor_area = area
                    break
            
            if image_editor_area:
                # Use existing Image Editor - just update it with new image
                for space in image_editor_area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = loaded_image
                        space.mode = 'PAINT'
                        space.show_gizmo = True
                        space.show_region_ui = True  # Show brush settings sidebar
                        image_editor_area.tag_redraw()
                        print("Loaded HDRI in existing Image Editor with paint mode")
                        break
            else:
                # No Image Editor exists - split viewport and create one
                viewport_area = None
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        viewport_area = area
                        break
                
                if viewport_area:
                    # Split the 3D Viewport vertically
                    with context.temp_override(area=viewport_area):
                        bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
                    
                    # Find the new area (it will be the rightmost one)
                    new_area = None
                    for area in context.screen.areas:
                        if area.type == 'VIEW_3D' and area != viewport_area:
                            new_area = area
                            break
                    
                    # Convert the new area to Image Editor by directly changing type
                    if new_area:
                        # Change area type directly
                        new_area.type = 'IMAGE_EDITOR'
                        
                        # Setup the Image Editor for painting
                        for space in new_area.spaces:
                            if space.type == 'IMAGE_EDITOR':
                                space.image = loaded_image
                                space.mode = 'PAINT'
                                space.show_gizmo = True
                                space.show_region_ui = True  # Show brush settings sidebar
                                new_area.tag_redraw()
                                print("Created new Image Editor with loaded HDRI")
                                break
            
            # Setup texture paint settings and activate brush
            if context.tool_settings and context.tool_settings.image_paint:
                settings = context.tool_settings.image_paint
                settings.canvas = loaded_image
                
                # Create or get brush
                if not settings.brush:
                    if "HDRI_Brush" in bpy.data.brushes:
                        settings.brush = bpy.data.brushes["HDRI_Brush"]
                    else:
                        # Create new brush for HDRI painting
                        brush = bpy.data.brushes.new("HDRI_Brush", mode='TEXTURE_PAINT')
                        brush.color = (1.0, 1.0, 1.0)  # White for light painting
                        brush.size = 50
                        brush.strength = 1.0
                        brush.blend = 'MIX'
                        settings.brush = brush
                        print("Created HDRI brush for loaded image")
            
            filename = os.path.basename(self.filepath)
            self.report({'INFO'}, f"HDRI loaded: {filename} - Ready for editing!")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Load failed: {e}")
            return {'CANCELLED'}

class HDRI_OT_save_canvas(Operator, ExportHelper):
    """Save HDRI canvas to file"""
    bl_idname = "hdri_studio.save_canvas"
    bl_label = "Save HDRI"
    bl_description = "Save the HDRI canvas to file"
    bl_options = {'REGISTER', 'UNDO'}
    
    # File extension filter
    filename_ext = ".exr"
    
    filter_glob: StringProperty(
        default="*.exr;*.hdr;*.png;*.jpg",
        options={'HIDDEN'}
    )
    
    # Format selection
    file_format: EnumProperty(
        name="Format",
        description="File format for saving",
        items=[
            ('OPEN_EXR', 'OpenEXR (.exr)', 'High dynamic range EXR format'),
            ('HDR', 'Radiance HDR (.hdr)', 'Traditional HDR format'),
            ('PNG', 'PNG (.png)', 'Standard PNG format (tone-mapped)'),
            ('JPEG', 'JPEG (.jpg)', 'Standard JPEG format (tone-mapped)'),
        ],
        default='OPEN_EXR'
    )
    
    # Color depth for EXR
    color_depth: EnumProperty(
        name="Color Depth",
        description="Bit depth for the saved image",
        items=[
            ('16', '16 bit (Half Float)', 'Half precision floating point'),
            ('32', '32 bit (Full Float)', 'Full precision floating point'),
        ],
        default='32'
    )
    
    def execute(self, context):
        try:
            # Check if canvas exists
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "No HDRI canvas found! Create canvas first.")
                return {'CANCELLED'}
            
            canvas_image = bpy.data.images["HDRI_Canvas"]
            
            # Set up image settings based on format
            original_format = canvas_image.file_format
            original_depth = canvas_image.use_half_precision if hasattr(canvas_image, 'use_half_precision') else False
            
            # Configure image format
            if self.file_format == 'OPEN_EXR':
                canvas_image.file_format = 'OPEN_EXR'
                if hasattr(canvas_image, 'use_half_precision'):
                    canvas_image.use_half_precision = (self.color_depth == '16')
                # Update file extension
                if not self.filepath.lower().endswith('.exr'):
                    self.filepath = os.path.splitext(self.filepath)[0] + '.exr'
                    
            elif self.file_format == 'HDR':
                canvas_image.file_format = 'HDR'
                if not self.filepath.lower().endswith('.hdr'):
                    self.filepath = os.path.splitext(self.filepath)[0] + '.hdr'
                    
            elif self.file_format == 'PNG':
                canvas_image.file_format = 'PNG'
                if not self.filepath.lower().endswith('.png'):
                    self.filepath = os.path.splitext(self.filepath)[0] + '.png'
                    
            elif self.file_format == 'JPEG':
                canvas_image.file_format = 'JPEG'
                if not self.filepath.lower().endswith(('.jpg', '.jpeg')):
                    self.filepath = os.path.splitext(self.filepath)[0] + '.jpg'
            
            # Save the image
            canvas_image.save_render(filepath=self.filepath)
            
            # Restore original settings
            canvas_image.file_format = original_format
            if hasattr(canvas_image, 'use_half_precision'):
                canvas_image.use_half_precision = original_depth
            
            self.report({'INFO'}, f"HDRI saved to: {self.filepath}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Save failed: {e}")
            return {'CANCELLED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Format selection
        layout.prop(self, "file_format", text="Format")
        
        # Additional options for EXR
        if self.file_format == 'OPEN_EXR':
            layout.prop(self, "color_depth", text="Depth")

class HDRI_OT_quick_save_canvas(Operator):
    """Quick save HDRI canvas with default settings"""
    bl_idname = "hdri_studio.quick_save_canvas"
    bl_label = "Quick Save HDRI"
    bl_description = "Quick save HDRI canvas to default location"
    
    def execute(self, context):
        try:
            # Check if canvas exists
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "No HDRI canvas found! Create canvas first.")
                return {'CANCELLED'}
            
            canvas_image = bpy.data.images["HDRI_Canvas"]
            
            # Check if canvas has an original filepath (was loaded from file)
            original_filepath = None
            if hasattr(canvas_image, 'filepath') and canvas_image.filepath:
                original_filepath = bpy.path.abspath(canvas_image.filepath)
            
            if original_filepath and os.path.exists(original_filepath):
                # Save back to the original file location
                filepath = original_filepath
                self.report({'INFO'}, f"Saving changes to original file: {os.path.basename(filepath)}")
            else:
                # No original file - create new one based on blend file or default location
                if bpy.data.filepath:
                    blend_dir = os.path.dirname(bpy.data.filepath)
                    blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
                    filename = f"{blend_name}_hdri.exr"
                else:
                    # Use desktop as default location
                    blend_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                    filename = "hdri_canvas.exr"
                
                filepath = os.path.join(blend_dir, filename)
                
                # Ensure unique filename for new files
                counter = 1
                base_path = filepath
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(base_path)
                    filepath = f"{name}_{counter:03d}{ext}"
                    counter += 1
                
                self.report({'INFO'}, f"Creating new file: {os.path.basename(filepath)}")
            
            # Determine best format based on file extension or default to EXR
            file_ext = os.path.splitext(filepath)[1].lower()
            original_format = canvas_image.file_format
            
            if file_ext == '.exr':
                canvas_image.file_format = 'OPEN_EXR'
            elif file_ext == '.hdr':
                canvas_image.file_format = 'HDR'
            elif file_ext == '.png':
                canvas_image.file_format = 'PNG'
            elif file_ext in ['.jpg', '.jpeg']:
                canvas_image.file_format = 'JPEG'
            else:
                # Default to EXR for HDRI work
                canvas_image.file_format = 'OPEN_EXR'
                if not filepath.endswith('.exr'):
                    filepath = os.path.splitext(filepath)[0] + '.exr'
            
            # Save the image
            canvas_image.save_render(filepath=filepath)
            
            # Update the image's filepath to track where it was saved
            try:
                # Try to use relative path, but fall back to absolute if on different drives
                canvas_image.filepath = bpy.path.relpath(filepath)
            except:
                # If relpath fails (different drives), use absolute path
                canvas_image.filepath = filepath
            
            # Restore original format
            canvas_image.file_format = original_format
            
            self.report({'INFO'}, f"HDRI saved: {os.path.basename(filepath)}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Quick save failed: {e}")
            return {'CANCELLED'}

def register():
    """Register save and load operators"""
    bpy.utils.register_class(HDRI_OT_load_canvas)
    bpy.utils.register_class(HDRI_OT_save_canvas)
    bpy.utils.register_class(HDRI_OT_quick_save_canvas)
    print("HDRI save and load operators registered")

def unregister():
    """Unregister save and load operators"""
    bpy.utils.unregister_class(HDRI_OT_quick_save_canvas)
    bpy.utils.unregister_class(HDRI_OT_save_canvas)
    bpy.utils.unregister_class(HDRI_OT_load_canvas)
    print("HDRI save and load operators unregistered")