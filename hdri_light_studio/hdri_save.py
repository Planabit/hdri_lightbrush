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
            
            # IMPORTANT: Set float buffer for proper HDRI handling
            # This prevents magenta/pink color issues
            if not loaded_image.is_float:
                loaded_image.use_half_precision = False
            
            # Ensure proper colorspace for HDRI work
            # Try multiple colorspace names (different Blender versions use different names)
            colorspace_options = ['Linear Rec.709', 'Linear', 'Linear CIE-XYZ E', 'Raw', 'Non-Color', 'sRGB']
            colorspace_set = False
            for cs_name in colorspace_options:
                try:
                    loaded_image.colorspace_settings.name = cs_name
                    colorspace_set = True
                    print(f"Set colorspace to: {cs_name}")
                    break
                except:
                    continue
            
            if not colorspace_set:
                print("Warning: Could not set linear colorspace, using default")
            
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
            
            # UPDATE SPHERE MATERIAL with loaded image!
            self.update_sphere_with_image(context, loaded_image)
            
            # UPDATE WORLD with loaded image if world is set up!
            self.update_world_with_image(context, loaded_image)
            
            filename = os.path.basename(self.filepath)
            self.report({'INFO'}, f"HDRI loaded: {filename} - Ready for editing!")
            
            return {'FINISHED'}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Load failed: {e}")
            return {'CANCELLED'}
    
    def update_sphere_with_image(self, context, image):
        """Update preview sphere material with loaded image"""
        try:
            # Find preview sphere
            sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
            if not sphere:
                print("No preview sphere found - will use image when sphere is created")
                return
            
            # Get sphere material
            if not sphere.active_material:
                print("Sphere has no material")
                return
            
            material = sphere.active_material
            if not material.use_nodes:
                print("Sphere material doesn't use nodes")
                return
            
            # Find and update ALL image/environment texture nodes
            def update_textures_in_tree(node_tree, depth=0):
                if not node_tree or depth > 5:
                    return 0
                
                count = 0
                for node in node_tree.nodes:
                    # Update Environment Texture nodes
                    if node.type == 'TEX_ENVIRONMENT':
                        node.image = image
                        count += 1
                        print(f"Updated TEX_ENVIRONMENT: {node.name}")
                    # Update Image Texture nodes
                    elif node.type == 'TEX_IMAGE':
                        node.image = image
                        count += 1
                        print(f"Updated TEX_IMAGE: {node.name}")
                    # Recurse into node groups
                    elif hasattr(node, 'node_tree') and node.node_tree:
                        count += update_textures_in_tree(node.node_tree, depth + 1)
                
                return count
            
            updated = update_textures_in_tree(material.node_tree)
            print(f"Updated {updated} texture nodes in sphere material")
            
            # Force material update
            material.update_tag()
            
            # Force viewport refresh
            for area in context.screen.areas:
                area.tag_redraw()
                
        except Exception as e:
            print(f"Error updating sphere: {e}")
    
    def update_world_with_image(self, context, image):
        """Update world environment texture with loaded image"""
        try:
            world = context.scene.world
            if not world or not world.use_nodes:
                print("No world or world doesn't use nodes - skip world update")
                return
            
            # Find Environment Texture node in world
            env_tex = None
            for node in world.node_tree.nodes:
                if node.type == 'TEX_ENVIRONMENT':
                    env_tex = node
                    break
            
            if env_tex:
                env_tex.image = image
                print(f"Updated world environment texture with: {image.name}")
                
                # Force world update
                world.node_tree.update_tag()
                
                # Refresh viewports
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
            else:
                print("No environment texture node found in world")
                
        except Exception as e:
            print(f"Error updating world: {e}")

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
            
            # Save the image - use filepath_raw + save() instead of save_render()
            # save_render causes issues with the canvas data
            canvas_image.filepath_raw = self.filepath
            canvas_image.save()
            
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
            
            # Save the image - use filepath_raw + save() instead of save_render()
            # save_render causes issues with the canvas data
            canvas_image.filepath_raw = filepath
            canvas_image.save()
            
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