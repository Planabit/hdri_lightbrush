"""
Simple HDRI 2D Editor Panel - KeyShot-style
Simplified version for testing
"""

import bpy
from bpy.types import Panel, Operator
from bpy.props import PointerProperty

class HDRI_EDITOR_PT_hdri_2d_simple(Panel):
    """Simple 2D HDRI editor panel"""
    bl_label = "HDRI 2D Editor"
    bl_idname = "VIEW3D_PT_hdri_2d_simple"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HDRI Editor'

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='IMAGE_DATA')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Check if HDRI is loaded
        current_hdri = 'NONE'
        if hasattr(scene, 'hdri_editor') and hasattr(scene.hdri_editor, 'hdri_previews'):
            current_hdri = scene.hdri_editor.hdri_previews
        
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            box = layout.box()
            box.label(text="No HDRI loaded", icon='INFO')
            box.operator("hdri_editor.load_hdri", text="Load HDRI File", icon='FILEBROWSER')
            return
            
        img = bpy.data.images[current_hdri]
        
        # HDRI Image Display
        display_box = layout.box()
        display_box.label(text=f"Editing: {img.name}", icon='IMAGE_DATA')
        
        # Image info
        info_row = display_box.row()
        info_row.label(text=f"Size: {img.size[0]}x{img.size[1]}")
        info_row.label(text=f"Pixels: {len(img.pixels) if img.pixels else 0}")
        
        # HDRI Image Display
        col = display_box.column(align=True)
        
        # Show image properties and status
        status_row = col.row(align=True)
        status_row.label(text=f"Data: {'✓' if img.has_data else '✗'}")
        status_row.label(text=f"Pixels: {len(img.pixels) if img.pixels else 0}")
        
        # Try different display methods
        if img.has_data and len(img.pixels) > 0:
            # Method 1: Create a proper image display area with aspect ratio
            try:
                image_col = col.column(align=True)
                
                # Calculate aspect ratio and scale accordingly
                img_width, img_height = img.size[0], img.size[1]
                aspect_ratio = img_height / img_width if img_width > 0 else 1.0
                
                # Get user scale preference (default to 1.0 if not set)
                user_scale = getattr(scene, 'hdri_preview_scale', 1.0)
                
                # Base scale for width, adjust height based on aspect ratio and user preference
                base_scale = 5 * user_scale
                height_scale = max(1.0, min(12.0, base_scale * aspect_ratio))  # Clamp between 1 and 12
                
                image_col.scale_y = height_scale
                
                # Force preview generation if needed
                if not hasattr(img.preview, 'icon_id') or img.preview.icon_id == 0:
                    img.preview_ensure()
                
                # Create image display box
                image_box = image_col.box()
                info_row = image_box.row()
                info_row.label(text="HDRI Preview:", icon='IMAGE_DATA')
                info_row.label(text=f"Ratio: {aspect_ratio:.2f}", icon='NONE')
                
                # Method A: Try to use image selector template with proper sizing
                try:
                    scene.hdri_editor_current_image = img
                    
                    # Create properly sized image area
                    img_area = image_box.column(align=True)
                    
                    # Adjust display height based on aspect ratio
                    display_height = max(2.0, min(6.0, aspect_ratio * 3.0))
                    img_area.scale_y = display_height
                    
                    # Display the image
                    img_area.template_image(scene, "hdri_editor_current_image", compact=False)
                    
                    # Add size info below
                    size_row = image_box.row()
                    size_row.scale_y = 0.7
                    size_row.label(text=f"{img_width} × {img_height} px")
                    
                except:
                    # Method B: Use icon preview with proper sizing
                    try:
                        preview_area = image_box.column(align=True)
                        preview_area.scale_y = height_scale * 0.8  # Slightly smaller than container
                        
                        if img.preview.icon_id > 0:
                            # Calculate icon scale based on aspect ratio
                            icon_scale = max(4.0, min(10.0, 6.0 * (1.0 + aspect_ratio * 0.5)))
                            preview_area.template_icon(icon_value=img.preview.icon_id, scale=icon_scale)
                        else:
                            preview_area.label(text="Generating preview...", icon='TIME')
                            
                        # Add size info
                        size_row = image_box.row()
                        size_row.scale_y = 0.6
                        size_row.label(text=f"{img_width} × {img_height} px")
                        
                    except:
                        # Method C: Simple text info
                        info_box = image_box.box()
                        info_box.label(text=f"✓ {img.name}", icon='CHECKMARK')
                        info_box.label(text=f"Size: {img_width} × {img_height} px")
                        info_box.operator("hdri_2d_simple.show_in_editor", 
                                        text="Open in Image Editor", 
                                        icon='WINDOW')
                
            except Exception as e:
                col.label(text="Display error:")
                col.label(text=str(e)[:50])
        else:
            # No data loaded
            warning_box = col.box()
            warning_box.alert = True
            warning_box.label(text="⚠ Image not in memory", icon='ERROR')
            
            reload_row = warning_box.row(align=True)
            reload_row.operator("hdri_2d_simple.reload_image", text="Force Reload", icon='FILE_REFRESH')
            reload_row.operator("hdri_2d_simple.show_in_editor", text="Open in Image Editor", icon='IMAGE_DATA')
        
        # Preview size controls
        size_row = col.row(align=True)
        size_row.scale_y = 0.6
        size_row.label(text="Preview Size:", icon='FULLSCREEN_ENTER')
        
        # Add preview size property if not exists
        if not hasattr(scene, 'hdri_preview_scale'):
            scene.hdri_preview_scale = 1.0
            
        size_row.prop(scene, "hdri_preview_scale", text="Scale", slider=True)
        
        # Display controls
        controls_row = col.row(align=True)
        controls_row.scale_y = 0.8
        controls_row.operator("hdri_2d_simple.refresh_display", text="Refresh", icon='FILE_REFRESH')
        controls_row.operator("hdri_2d_simple.pack_image", text="Pack", icon='PACKAGE')
        controls_row.operator("hdri_2d_simple.view_properties", text="Properties", icon='PROPERTIES')
        
        # Debug controls
        debug_row = col.row()
        debug_row.scale_y = 0.7
        debug_row.operator("hdri_2d_simple.debug_image", text="🔍 Debug Image", icon='CONSOLE')
        
        # KeyShot-style HDRI Editing Tools
        tools_box = layout.box()
        tools_box.label(text="KeyShot-style Editing:", icon='TOOL_SETTINGS')
        
        # Light Generation Tools  
        light_row = tools_box.row(align=True)
        light_row.operator("hdri_2d_simple.add_light", text="Add Light Spot", icon='LIGHT_SUN')
        light_row.operator("hdri_2d_simple.add_sun", text="Add Sun Disk", icon='LIGHT')
        
        # Image editing tools
        edit_row = tools_box.row(align=True) 
        edit_row.operator("hdri_2d_simple.generate_sky", text="Generate Sky", icon='COLOR')
        edit_row.operator("hdri_2d_simple.create_black", text="Clear Black", icon='X')
        
        # Export options
        export_box = layout.box()
        export_box.label(text="Export:", icon='EXPORT')
        
        export_row = export_box.row(align=True)
        export_row.operator("hdri_2d_simple.save_hdri", text="Save HDRI", icon='FILE_IMAGE')

class HDRI_2D_SIMPLE_OT_add_light(Operator):
    """Add a bright light spot to HDRI"""
    bl_idname = "hdri_2d_simple.add_light"
    bl_label = "Add Light Spot"
    bl_description = "Add a bright light spot to the HDRI at center"

    def execute(self, context):
        scene = context.scene
        
        # Get current HDRI
        if not hasattr(scene, 'hdri_editor') or not hasattr(scene.hdri_editor, 'hdri_previews'):
            self.report({'WARNING'}, "No HDRI system found")
            return {'CANCELLED'}
            
        current_hdri = scene.hdri_editor.hdri_previews
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        # Add light at center (simplified version)
        self.add_simple_light(img)
        
        self.report({'INFO'}, f"Added light spot to {img.name}")
        return {'FINISHED'}

    def add_simple_light(self, img):
        """Add a simple bright spot to the center of HDRI"""
        if not img or not img.pixels:
            return
            
        width, height = img.size
        if width == 0 or height == 0:
            return
            
        pixels = list(img.pixels)
        
        # Add bright spot at center
        center_x = width // 2
        center_y = height // 2
        light_radius = min(width, height) // 20  # 5% of smallest dimension
        
        for y in range(max(0, center_y - light_radius), min(height, center_y + light_radius)):
            for x in range(max(0, center_x - light_radius), min(width, center_x + light_radius)):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                
                if distance <= light_radius:
                    # Calculate intensity falloff
                    intensity = 5.0 * (1.0 - distance / light_radius)
                    
                    pixel_index = (y * width + x) * 4
                    if pixel_index < len(pixels) - 3:
                        # Add white light (additive)
                        pixels[pixel_index] = min(pixels[pixel_index] + intensity, 50.0)      # R
                        pixels[pixel_index + 1] = min(pixels[pixel_index + 1] + intensity, 50.0)  # G
                        pixels[pixel_index + 2] = min(pixels[pixel_index + 2] + intensity, 50.0)  # B
                        # Alpha unchanged
        
        # Update image
        img.pixels = pixels
        img.update()

class HDRI_2D_SIMPLE_OT_add_sun(Operator):
    """Add a sun disk to HDRI"""
    bl_idname = "hdri_2d_simple.add_sun"
    bl_label = "Add Sun Disk"
    bl_description = "Add a sun disk at upper right"

    def execute(self, context):
        scene = context.scene
        
        current_hdri = scene.hdri_editor.hdri_previews
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        self.add_simple_sun(img)
        
        self.report({'INFO'}, f"Added sun disk to {img.name}")
        return {'FINISHED'}

    def add_simple_sun(self, img):
        """Add a simple sun disk"""
        if not img or not img.pixels:
            return
            
        width, height = img.size
        if width == 0 or height == 0:
            return
            
        pixels = list(img.pixels)
        
        # Sun position (upper right)
        sun_x = int(width * 0.75)
        sun_y = int(height * 0.7)
        sun_radius = min(width, height) // 50  # Smaller than light spot
        
        for y in range(max(0, sun_y - sun_radius * 2), min(height, sun_y + sun_radius * 2)):
            for x in range(max(0, sun_x - sun_radius * 2), min(width, sun_x + sun_radius * 2)):
                distance = ((x - sun_x) ** 2 + (y - sun_y) ** 2) ** 0.5
                
                pixel_index = (y * width + x) * 4
                
                if pixel_index < len(pixels) - 3:
                    if distance <= sun_radius:
                        # Core sun (bright white/yellow)
                        pixels[pixel_index] = min(pixels[pixel_index] + 20.0, 100.0)      # R
                        pixels[pixel_index + 1] = min(pixels[pixel_index + 1] + 19.0, 100.0)  # G
                        pixels[pixel_index + 2] = min(pixels[pixel_index + 2] + 17.0, 100.0)  # B
                    elif distance <= sun_radius * 2:
                        # Corona/glow
                        glow_intensity = 5.0 * (1.0 - (distance - sun_radius) / sun_radius)
                        pixels[pixel_index] = min(pixels[pixel_index] + glow_intensity, 100.0)
                        pixels[pixel_index + 1] = min(pixels[pixel_index + 1] + glow_intensity * 0.95, 100.0)
                        pixels[pixel_index + 2] = min(pixels[pixel_index + 2] + glow_intensity * 0.85, 100.0)
        
        img.pixels = pixels
        img.update()

class HDRI_2D_SIMPLE_OT_generate_sky(Operator):
    """Generate simple sky gradient"""
    bl_idname = "hdri_2d_simple.generate_sky"
    bl_label = "Generate Sky"
    bl_description = "Generate a simple sky gradient"

    def execute(self, context):
        scene = context.scene
        
        current_hdri = scene.hdri_editor.hdri_previews
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        self.generate_simple_sky(img)
        
        self.report({'INFO'}, f"Generated sky gradient in {img.name}")
        return {'FINISHED'}

    def generate_simple_sky(self, img):
        """Generate a simple sky gradient"""
        if not img:
            return
            
        width, height = img.size
        if width == 0 or height == 0:
            return
            
        pixels = [0.0] * (width * height * 4)
        
        # Sky colors
        horizon_color = (0.8, 0.9, 1.0)  # Light blue
        zenith_color = (0.2, 0.4, 0.8)   # Dark blue
        
        for y in range(height):
            # V coordinate (0 at bottom, 1 at top)
            v = y / height
            
            # Interpolate colors
            r = horizon_color[0] + (zenith_color[0] - horizon_color[0]) * v
            g = horizon_color[1] + (zenith_color[1] - horizon_color[1]) * v
            b = horizon_color[2] + (zenith_color[2] - horizon_color[2]) * v
            
            for x in range(width):
                pixel_index = (y * width + x) * 4
                pixels[pixel_index] = r
                pixels[pixel_index + 1] = g
                pixels[pixel_index + 2] = b
                pixels[pixel_index + 3] = 1.0
        
        img.pixels = pixels
        img.update()

class HDRI_2D_SIMPLE_OT_create_black(Operator):
    """Create black HDRI"""
    bl_idname = "hdri_2d_simple.create_black"
    bl_label = "Clear to Black"
    bl_description = "Clear HDRI to black"

    def execute(self, context):
        scene = context.scene
        
        current_hdri = scene.hdri_editor.hdri_previews
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            # Create new black HDRI
            img = bpy.data.images.new("Black_HDRI", width=2048, height=1024)
            scene.hdri_editor.hdri_previews = img.name
        else:
            img = bpy.data.images[current_hdri]
            
        # Clear to black
        if img:
            width, height = img.size
            black_pixels = [0.0, 0.0, 0.0, 1.0] * (width * height)
            img.pixels = black_pixels
            img.update()
        
        self.report({'INFO'}, "Cleared HDRI to black")
        return {'FINISHED'}

class HDRI_2D_SIMPLE_OT_reload_image(Operator):
    """Reload the current HDRI image"""
    bl_idname = "hdri_2d_simple.reload_image"
    bl_label = "Reload Image"
    bl_description = "Reload the current HDRI image into memory"

    def execute(self, context):
        scene = context.scene
        
        current_hdri = scene.hdri_editor.hdri_previews
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI to reload")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        try:
            # Force reload the image
            img.reload()
            
            # If still no data, try to pack
            if not img.has_data:
                img.pack()
            
            # Force update
            img.update()
            
            # Redraw all areas
            for area in context.screen.areas:
                area.tag_redraw()
                
            self.report({'INFO'}, f"Reloaded {img.name}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to reload: {e}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

class HDRI_2D_SIMPLE_OT_show_in_editor(Operator):
    """Show HDRI in Image Editor"""
    bl_idname = "hdri_2d_simple.show_in_editor"
    bl_label = "Show in Image Editor"
    bl_description = "Open current HDRI in Blender's Image Editor"

    def execute(self, context):
        scene = context.scene
        current_hdri = scene.hdri_editor.hdri_previews
        
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI to show")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        # Try to find or create an image editor area
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = img
                        area.tag_redraw()
                        self.report({'INFO'}, f"Opened {img.name} in Image Editor")
                        return {'FINISHED'}
        
        self.report({'INFO'}, "No Image Editor area found. Switch to Image Editor workspace.")
        return {'FINISHED'}

class HDRI_2D_SIMPLE_OT_pack_image(Operator):
    """Pack HDRI image"""
    bl_idname = "hdri_2d_simple.pack_image"
    bl_label = "Pack Image"
    bl_description = "Pack HDRI image into blend file"

    def execute(self, context):
        scene = context.scene
        current_hdri = scene.hdri_editor.hdri_previews
        
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI to pack")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        try:
            if img.packed_file is None:
                img.pack()
                self.report({'INFO'}, f"Packed {img.name}")
            else:
                self.report({'INFO'}, f"{img.name} is already packed")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to pack: {e}")
            
        return {'FINISHED'}

class HDRI_2D_SIMPLE_OT_view_properties(Operator):
    """View HDRI properties"""
    bl_idname = "hdri_2d_simple.view_properties"
    bl_label = "View Properties"
    bl_description = "Show detailed HDRI properties"

    def execute(self, context):
        scene = context.scene
        current_hdri = scene.hdri_editor.hdri_previews
        
        if current_hdri == 'NONE' or current_hdri not in bpy.data.images:
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        # Show properties in info report
        props = [
            f"Name: {img.name}",
            f"Size: {img.size[0]}x{img.size[1]}",
            f"Channels: {img.channels}",
            f"Has Data: {img.has_data}",
            f"File Format: {img.file_format}",
            f"Colorspace: {img.colorspace_settings.name}",
            f"Packed: {'Yes' if img.packed_file else 'No'}",
        ]
        
        for prop in props:
            self.report({'INFO'}, prop)
            
        return {'FINISHED'}

class HDRI_2D_SIMPLE_OT_debug_image(Operator):
    """Debug current HDRI image"""
    bl_idname = "hdri_2d_simple.debug_image"
    bl_label = "Debug Image"
    bl_description = "Debug current HDRI image loading issues"

    def execute(self, context):
        scene = context.scene
        
        # Check hdri_editor system
        if not hasattr(scene, 'hdri_editor'):
            self.report({'ERROR'}, "HDRI editor system not found")
            return {'CANCELLED'}
            
        if not hasattr(scene.hdri_editor, 'hdri_previews'):
            self.report({'ERROR'}, "HDRI previews property not found")
            return {'CANCELLED'}
            
        current_hdri = scene.hdri_editor.hdri_previews
        self.report({'INFO'}, f"Current HDRI reference: '{current_hdri}'")
        
        if current_hdri == 'NONE':
            self.report({'INFO'}, "No HDRI selected")
            return {'FINISHED'}
            
        if current_hdri not in bpy.data.images:
            self.report({'ERROR'}, f"Image '{current_hdri}' not found in bpy.data.images")
            self.report({'INFO'}, f"Available images: {list(bpy.data.images.keys())}")
            return {'CANCELLED'}
            
        img = bpy.data.images[current_hdri]
        
        # Debug image properties
        debug_info = [
            f"Image name: {img.name}",
            f"Image type: {type(img)}",
            f"Has data: {img.has_data}",
            f"Size: {img.size}",
            f"Channels: {img.channels}",
            f"Filepath: {img.filepath}",
            f"Source: {img.source}",
            f"Packed: {'Yes' if img.packed_file else 'No'}",
            f"Users: {img.users}",
            f"Colorspace: {img.colorspace_settings.name}",
        ]
        
        if img.pixels:
            debug_info.append(f"Pixels length: {len(img.pixels)}")
            debug_info.append(f"First few pixels: {list(img.pixels[:12])}")
        else:
            debug_info.append("Pixels: None or empty")
            
        for info in debug_info:
            self.report({'INFO'}, info)
            
        return {'FINISHED'}

class HDRI_2D_SIMPLE_OT_refresh_display(Operator):
    """Refresh HDRI display and regenerate preview"""
    bl_idname = "hdri_2d_simple.refresh_display"
    bl_label = "Refresh Display"
    bl_description = "Force refresh HDRI display and regenerate preview"
    
    def execute(self, context):
        scene = context.scene
        
        if not hasattr(scene, 'hdri_editor') or not hasattr(scene.hdri_editor, 'hdri_previews'):
            self.report({'WARNING'}, "No HDRI loaded")
            return {'CANCELLED'}
        
        hdri_ref = scene.hdri_editor.hdri_previews
        if hdri_ref == 'NONE' or hdri_ref not in bpy.data.images:
            self.report({'WARNING'}, "No valid HDRI image")
            return {'CANCELLED'}
        
        img = bpy.data.images[hdri_ref]
        
        # Force reload and preview generation
        try:
            img.reload()
            img.preview_ensure()
            
            # Set as current image
            scene.hdri_editor_current_image = img
            
            # Force UI refresh
            for area in context.screen.areas:
                area.tag_redraw()
            
            self.report({'INFO'}, f"Refreshed display for {img.name}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Refresh failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class HDRI_2D_SIMPLE_OT_save_hdri(Operator):
    """Save HDRI"""
    bl_idname = "hdri_2d_simple.save_hdri"
    bl_label = "Save HDRI"
    bl_description = "Save the HDRI to file"

    def execute(self, context):
        # For now, just report - full save functionality would go here
        self.report({'INFO'}, "Save HDRI (feature in development)")
        return {'FINISHED'}

# Classes for registration
classes = (
    HDRI_EDITOR_PT_hdri_2d_simple,
    HDRI_2D_SIMPLE_OT_add_light,
    HDRI_2D_SIMPLE_OT_add_sun,
    HDRI_2D_SIMPLE_OT_generate_sky,
    HDRI_2D_SIMPLE_OT_create_black,
    HDRI_2D_SIMPLE_OT_reload_image,
    HDRI_2D_SIMPLE_OT_show_in_editor,
    HDRI_2D_SIMPLE_OT_pack_image,
    HDRI_2D_SIMPLE_OT_view_properties,
    HDRI_2D_SIMPLE_OT_debug_image,
    HDRI_2D_SIMPLE_OT_refresh_display,
    HDRI_2D_SIMPLE_OT_save_hdri,
)

def register():
    """Register simple 2D HDRI editor classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add scene properties for HDRI editing
    bpy.types.Scene.hdri_editor_current_image = bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Current HDRI Image",
        description="Currently loaded HDRI image for editing"
    )
    
    bpy.types.Scene.hdri_preview_scale = bpy.props.FloatProperty(
        name="Preview Scale",
        description="Scale factor for HDRI preview size",
        default=1.0,
        min=0.2,
        max=3.0,
        step=0.1,
        update=lambda self, context: context.area.tag_redraw() if context.area else None
    )
    print("HDRI Editor: Registered simple 2D HDRI editor")

def unregister():
    """Unregister simple 2D HDRI editor classes"""
    # Remove scene properties
    if hasattr(bpy.types.Scene, 'hdri_editor_current_image'):
        del bpy.types.Scene.hdri_editor_current_image
    if hasattr(bpy.types.Scene, 'hdri_preview_scale'):
        del bpy.types.Scene.hdri_preview_scale
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("HDRI Editor: Unregistered simple 2D HDRI editor")