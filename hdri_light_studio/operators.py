"""
Operators Module
Canvas and painting operators for HDRI Light Studio
"""

import bpy
from bpy.types import Operator
import numpy as np
from .canvas_renderer import HDRICanvasRenderer
from .simple_canvas import SimpleCanvasRenderer
from .utils import kelvin_to_rgb

# Global canvas renderer instance
canvas_renderer = None

def update_world_hdri(context):
    """Update world material with current canvas image"""
    try:
        # Get or create world material
        world = context.scene.world
        if not world:
            world = bpy.data.worlds.new("HDRI_World")
            context.scene.world = world
            
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Add Environment Texture node
        env_tex = nodes.new(type='ShaderNodeTexEnvironment')
        env_tex.location = (-300, 300)
        
        # Add Background node
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (0, 300)
        
        # Add World Output node
        world_output = nodes.new(type='ShaderNodeOutputWorld')
        world_output.location = (300, 300)
        
        # Link nodes
        links.new(env_tex.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], world_output.inputs['Surface'])
        
        # Set canvas image to Environment Texture
        if "HDRI_Canvas" in bpy.data.images:
            env_tex.image = bpy.data.images["HDRI_Canvas"]
            
        # Force viewport update
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        area.tag_redraw()
                        
        print("World HDRI updated")
        
    except Exception as e:
        print(f"World HDRI update failed: {e}")
        import traceback
        traceback.print_exc()

class HDRI_OT_create_canvas(Operator):
    """Create new HDRI canvas"""
    bl_idname = "hdri_studio.create_canvas"
    bl_label = "Create Canvas"
    bl_description = "Create a new HDRI canvas for editing"
    
    def execute(self, context):
        global canvas_renderer
        
        try:
            props = context.scene.hdri_studio
            
            # Set proper canvas dimensions - 2K = 2048x1024, 4K = 4096x2048
            if props.canvas_size == '2K':
                width = 2048
                height = 1024
            else:  # 4K
                width = 4096
                height = 2048
                
            print(f"Creating canvas: {width}x{height}")
            
            # Clean up existing canvas
            if canvas_renderer:
                try:
                    canvas_renderer.cleanup()
                except:
                    pass
                canvas_renderer = None
            
            # Try advanced canvas renderer first
            try:
                canvas_renderer = HDRICanvasRenderer(width, height)
                if canvas_renderer.is_initialized:
                    props.canvas_active = True
                    self.report({'INFO'}, f"Advanced canvas created: {width}x{height}")
                    print(f"Advanced canvas successfully created: {width}x{height}")
                else:
                    raise Exception("Advanced renderer failed")
            except Exception as advanced_error:
                print(f"Advanced canvas failed: {advanced_error}")
                
                # Fallback to simple renderer
                try:
                    canvas_renderer = SimpleCanvasRenderer(width, height)
                    if canvas_renderer.is_initialized:
                        props.canvas_active = True
                        self.report({'INFO'}, f"Simple canvas created: {width}x{height}")
                        print(f"Simple canvas successfully created: {width}x{height}")
                    else:
                        raise Exception("Simple renderer also failed")
                except Exception as simple_error:
                    self.report({'ERROR'}, f"All canvas creation methods failed: {simple_error}")
                    print(f"Both canvas creation methods failed: {simple_error}")
                    return {'FINISHED'}
            
            # Split viewport and show canvas
            self.setup_canvas_viewport(context)
            
            # Set up world HDRI for real-time preview
            update_world_hdri(context)
            
            # Redraw UI
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
                    
        except Exception as e:
            self.report({'ERROR'}, f"Canvas creation error: {str(e)}")
            print(f"Canvas creation exception: {e}")
            import traceback
            traceback.print_exc()
            
        return {'FINISHED'}
    
    def setup_canvas_viewport(self, context):
        """Split 3D viewport and setup canvas display"""
        try:
            # Find the active 3D viewport area
            view3d_area = None
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    view3d_area = area
                    break
            
            if not view3d_area:
                print("No 3D viewport found for splitting")
                return
            
            # Count 3D viewports before split
            view3d_count_before = len([area for area in context.screen.areas if area.type == 'VIEW_3D'])
            print(f"3D Viewports before split: {view3d_count_before}")
            
            # Split the area vertically
            with context.temp_override(area=view3d_area):
                bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
            
            # Find the newly created 3D viewport (should be rightmost)
            view3d_areas = [area for area in context.screen.areas if area.type == 'VIEW_3D']
            view3d_count_after = len(view3d_areas)
            print(f"3D Viewports after split: {view3d_count_after}")
            
            if view3d_count_after > view3d_count_before:
                # Sort by X position and get the rightmost
                view3d_areas.sort(key=lambda a: a.x)
                rightmost_area = view3d_areas[-1]  # Rightmost 3D viewport
                print(f"Found rightmost 3D viewport at x={rightmost_area.x}")
            else:
                print("Split failed or no new viewport created")
                return
            
            if rightmost_area:
                print(f"Converting area at x={rightmost_area.x} to Image Editor")
                
                # Change the right area to Image Editor - FORCE it
                rightmost_area.type = 'IMAGE_EDITOR'
                
                # Wait a moment for the area to update
                import time
                time.sleep(0.1)
                
                # Force area redraw
                rightmost_area.tag_redraw()
                
                # Ensure it's set to image editor mode
                image_space = None
                for space in rightmost_area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.mode = 'VIEW'
                        space.show_gizmo = False
                        image_space = space
                        print("Image editor space configured")
                        break
                
                if image_space:
                    # Create and display canvas image
                    self.create_canvas_image(context, rightmost_area)
                else:
                    print("Failed to find image editor space")
                
                print("Viewport split completed")
            
        except Exception as e:
            print(f"Viewport setup failed: {e}")
    
    def create_canvas_image(self, context, image_area):
        """Create Blender image for canvas display"""
        try:
            # Always create a simple test image first
            image_name = "HDRI_Canvas"
            
            # Remove existing image if present
            if image_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[image_name])
            
            # Create test image with simple dimensions
            width, height = 1024, 512
            canvas_image = bpy.data.images.new(image_name, width, height, alpha=True)
            
            # Create simple test pattern
            import numpy as np
            pixels = np.zeros((height, width, 4), dtype=np.float32)
            
            # Create gradient + checkerboard
            for y in range(height):
                for x in range(width):
                    # Basic gradient
                    r = x / width
                    g = y / height
                    b = 0.5
                    
                    # Add checkerboard
                    if (x // 50 + y // 50) % 2 == 0:
                        r *= 0.7
                        g *= 0.7
                        b *= 0.7
                    
                    pixels[y, x] = [r, g, b, 1.0]
            
            # Set pixels
            canvas_image.pixels[:] = pixels.flatten()
            canvas_image.update()
            
            # Set the image in ALL image editors
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    for space in area.spaces:
                        if space.type == 'IMAGE_EDITOR':
                            space.image = canvas_image
                            space.mode = 'VIEW'
                            area.tag_redraw()
                            print(f"Image set in Image Editor at x={area.x}")
            
            print(f"Canvas image created: {width}x{height}")
            
        except Exception as e:
            print(f"Canvas image creation failed: {e}")
            import traceback
            traceback.print_exc()

class HDRI_OT_clear_canvas(Operator):
    """Clear HDRI canvas"""
    bl_idname = "hdri_studio.clear_canvas"
    bl_label = "Clear Canvas"
    bl_description = "Clear the current canvas"
    
    def execute(self, context):
        global canvas_renderer
        
        if canvas_renderer and canvas_renderer.is_initialized:
            # Reset canvas to white
            canvas_renderer.canvas_data.fill(1.0)
            canvas_renderer.canvas_data[:, :, 3] = 1.0  # Alpha
            canvas_renderer.update_canvas_data()
            
            # Update canvas image and world HDRI
            try:
                if "HDRI_Canvas" in bpy.data.images:
                    canvas_image = bpy.data.images["HDRI_Canvas"]
                    height, width = canvas_renderer.canvas_data.shape[:2]
                    pixels = canvas_renderer.canvas_data.reshape(height * width * 4)
                    canvas_image.pixels[:] = pixels
                    canvas_image.update()
                
                # Update world HDRI
                update_world_hdri(context)
                
            except Exception as e:
                print(f"Canvas clear update failed: {e}")
            
            # Redraw UI
            for area in context.screen.areas:
                area.tag_redraw()
                    
            self.report({'INFO'}, "Canvas cleared")
        else:
            self.report({'ERROR'}, "No active canvas")
            
        return {'FINISHED'}

class HDRI_OT_paint_canvas(Operator):
    """Paint on HDRI canvas - Modal operator for interactive painting"""
    bl_idname = "hdri_studio.paint_canvas" 
    bl_label = "Paint Canvas"
    bl_description = "Paint on the canvas with mouse"
    
    def __init__(self):
        self.drawing = False
        self.mouse_pos = (0, 0)
    
    def convert_mouse_to_canvas(self, context, mouse_x, mouse_y):
        """Convert mouse coordinates to canvas coordinates"""
        try:
            # For Image Editor, we need to find the image space coordinates
            for area in context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    for space in area.spaces:
                        if space.type == 'IMAGE_EDITOR' and space.image:
                            # Simple mapping: mouse region to canvas size
                            region_width = area.width
                            region_height = area.height
                            
                            if region_width > 0 and region_height > 0:
                                # Normalize mouse position (0-1)
                                norm_x = mouse_x / region_width
                                norm_y = mouse_y / region_height
                                
                                # Map to canvas size
                                canvas_x = int(norm_x * canvas_renderer.width)
                                canvas_y = int((1.0 - norm_y) * canvas_renderer.height)  # Flip Y
                                
                                return canvas_x, canvas_y
            
            # Fallback: use mouse coordinates directly (scaled)
            scale_factor = 0.5  # Adjust as needed
            return int(mouse_x * scale_factor), int(mouse_y * scale_factor)
            
        except Exception as e:
            print(f"Mouse coordinate conversion failed: {e}")
            return int(mouse_x), int(mouse_y)
    
    def update_canvas_and_world(self, context):
        """Update canvas image and world HDRI in real-time"""
        try:
            # Update canvas image in Blender
            if "HDRI_Canvas" in bpy.data.images:
                canvas_image = bpy.data.images["HDRI_Canvas"]
                if canvas_renderer and hasattr(canvas_renderer, 'canvas_data'):
                    # Check dimensions match
                    height, width = canvas_renderer.canvas_data.shape[:2]
                    image_width, image_height = canvas_image.size
                    
                    if width == image_width and height == image_height:
                        # Convert canvas data to flat pixel array
                        try:
                            pixels = canvas_renderer.canvas_data.reshape(height * width * 4)
                            
                            # Ensure pixel array length matches image
                            expected_length = image_width * image_height * 4
                            if len(pixels) == expected_length:
                                # Create a new pixel list to avoid re-sizing issues
                                new_pixels = list(pixels)
                                canvas_image.pixels[:] = new_pixels
                                canvas_image.update()
                                print(f"Canvas updated: {width}x{height}")
                            else:
                                print(f"Pixel array size mismatch: {len(pixels)} vs expected {expected_length}")
                                
                        except Exception as reshape_error:
                            print(f"Canvas reshape error: {reshape_error}")
                    else:
                        print(f"Canvas size mismatch: canvas={width}x{height}, image={image_width}x{image_height}")
            
            # Update world HDRI
            update_world_hdri(context)
            
            # Force viewport redraw
            for area in context.screen.areas:
                area.tag_redraw()
                
        except Exception as e:
            print(f"Canvas/World update failed: {e}")
    
    def modal(self, context, event):
        global canvas_renderer
        
        if not canvas_renderer or not canvas_renderer.is_initialized:
            return {'CANCELLED'}
            
        props = context.scene.hdri_studio
        
        if event.type == 'MOUSEMOVE':
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            
            if self.drawing:
                # Paint at current mouse position
                if props.use_temperature:
                    color = kelvin_to_rgb(props.color_temperature)
                else:
                    color = props.brush_color
                
                # Convert mouse coordinates to canvas coordinates
                canvas_x, canvas_y = self.convert_mouse_to_canvas(context, self.mouse_pos[0], self.mouse_pos[1])
                
                print(f"Painting at mouse=({self.mouse_pos[0]}, {self.mouse_pos[1]}) -> canvas=({canvas_x}, {canvas_y})")
                    
                canvas_renderer.paint_at_position(
                    canvas_x, 
                    canvas_y,
                    props.brush_size,
                    props.brush_intensity,
                    color
                )
                
                # Update canvas image and world HDRI in real-time
                self.update_canvas_and_world(context)
                
        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.drawing = True
                # Start painting
                if props.use_temperature:
                    color = kelvin_to_rgb(props.color_temperature)
                else:
                    color = props.brush_color
                
                # Convert mouse coordinates to canvas coordinates
                canvas_x, canvas_y = self.convert_mouse_to_canvas(context, self.mouse_pos[0], self.mouse_pos[1])
                    
                canvas_renderer.paint_at_position(
                    canvas_x,
                    canvas_y, 
                    props.brush_size,
                    props.brush_intensity,
                    color
                )
                self.update_canvas_and_world(context)
                
            elif event.value == 'RELEASE':
                self.drawing = False
                
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Exit painting mode
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be 3D View")
            return {'CANCELLED'}

class HDRI_OT_add_light(Operator):
    """Add light source to canvas"""
    bl_idname = "hdri_studio.add_light"
    bl_label = "Add Light"
    bl_description = "Add a light source to the canvas"
    
    def execute(self, context):
        global canvas_renderer
        
        if not canvas_renderer or not canvas_renderer.is_initialized:
            self.report({'ERROR'}, "No active canvas")
            return {'CANCELLED'}
            
        props = context.scene.hdri_studio
        
        # Get light color (temperature or RGB)
        if props.use_temperature:
            light_color = kelvin_to_rgb(props.color_temperature)
        else:
            light_color = props.brush_color[:3]  # RGB only
        
        # Add light at center of canvas
        center_x = canvas_renderer.width // 2
        center_y = canvas_renderer.height // 2
        
        # Use shape-based light placement
        from .utils import create_light_shape
        
        coords_x, coords_y, values = create_light_shape(
            props.light_shape,
            int(props.light_size),
            center_x,
            center_y,
            props.light_intensity,
            light_color
        )
        
        # Paint the light shape
        for i in range(len(coords_x)):
            x, y = coords_x[i], coords_y[i]
            if 0 <= x < canvas_renderer.width and 0 <= y < canvas_renderer.height:
                # Apply color to canvas
                color_value = values[i]
                canvas_renderer.paint_at_position(
                    x, y, 1, 1.0, color_value[:3]  # Single pixel, full intensity
                )
        
        # Update canvas image and world HDRI
        try:
            if "HDRI_Canvas" in bpy.data.images:
                canvas_image = bpy.data.images["HDRI_Canvas"]
                if hasattr(canvas_renderer, 'canvas_data'):
                    height, width = canvas_renderer.canvas_data.shape[:2]
                    pixels = canvas_renderer.canvas_data.reshape(height * width * 4)
                    canvas_image.pixels[:] = pixels
                    canvas_image.update()
            
            # Update world HDRI
            update_world_hdri(context)
            
        except Exception as e:
            print(f"Light addition update failed: {e}")
        
        # Redraw all areas
        for area in context.screen.areas:
            area.tag_redraw()
                
        self.report({'INFO'}, f"Added {props.light_shape.lower()} light")
        return {'FINISHED'}

class HDRI_OT_interactive_light(Operator):
    """Interactive light placement with mouse"""
    bl_idname = "hdri_studio.interactive_light"
    bl_label = "Interactive Light"
    bl_description = "Click to place lights interactively"
    
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.light_preview = False
    
    def modal(self, context, event):
        global canvas_renderer
        
        if not canvas_renderer or not canvas_renderer.is_initialized:
            return {'CANCELLED'}
            
        props = context.scene.hdri_studio
        
        if event.type == 'MOUSEMOVE':
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            # TODO: Show light preview at mouse position
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Place light at mouse position
            
            # Get light color (temperature or RGB)
            if props.use_temperature:
                light_color = kelvin_to_rgb(props.color_temperature)
            else:
                light_color = props.brush_color[:3]
            
            # Convert mouse position to canvas coordinates
            # This needs to be implemented based on Image Editor space
            mouse_x = self.mouse_pos[0]
            mouse_y = self.mouse_pos[1]
            
            # Create and place light shape
            from .utils import create_light_shape
            
            coords_x, coords_y, values = create_light_shape(
                props.light_shape,
                int(props.light_size),
                mouse_x,
                mouse_y,
                props.light_intensity,
                light_color
            )
            
            # Paint the light shape
            for i in range(len(coords_x)):
                x, y = coords_x[i], coords_y[i]
                if 0 <= x < canvas_renderer.width and 0 <= y < canvas_renderer.height:
                    color_value = values[i]
                    canvas_renderer.paint_at_position(
                        x, y, 1, 1.0, color_value[:3]
                    )
            
            # Update canvas and world
            try:
                if "HDRI_Canvas" in bpy.data.images:
                    canvas_image = bpy.data.images["HDRI_Canvas"]
                    if hasattr(canvas_renderer, 'canvas_data'):
                        height, width = canvas_renderer.canvas_data.shape[:2]
                        pixels = canvas_renderer.canvas_data.reshape(height * width * 4)
                        canvas_image.pixels[:] = pixels
                        canvas_image.update()
                
                update_world_hdri(context)
                
            except Exception as e:
                print(f"Interactive light update failed: {e}")
            
            # Redraw areas
            for area in context.screen.areas:
                area.tag_redraw()
                
            self.report({'INFO'}, f"Placed {props.light_shape.lower()} light")
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
            
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if context.area.type in {'VIEW_3D', 'IMAGE_EDITOR'}:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be 3D View or Image Editor")
            return {'CANCELLED'}











# Operator classes list
classes = [
    HDRI_OT_create_canvas,
    HDRI_OT_clear_canvas,
    HDRI_OT_paint_canvas,
    HDRI_OT_add_light,
    HDRI_OT_interactive_light,
]

# Import image paint operators
from . import image_paint

def register():
    """Register operator classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("Operators module registered")

def unregister():
    """Unregister operator classes and cleanup"""
    global canvas_renderer
    
    # Clean up canvas renderer
    if canvas_renderer:
        canvas_renderer.cleanup()
        canvas_renderer = None
        
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Operators module unregistered")