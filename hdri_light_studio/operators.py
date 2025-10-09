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
        try:
            # Check if HDRI_Canvas exists
            if "HDRI_Canvas" not in bpy.data.images:
                self.report({'ERROR'}, "No HDRI canvas found")
                return {'CANCELLED'}
            
            canvas_image = bpy.data.images["HDRI_Canvas"]
            
            # Get canvas dimensions
            width = canvas_image.size[0]
            height = canvas_image.size[1]
            
            # Create white pixels (RGBA)
            white_pixels = [1.0, 1.0, 1.0, 1.0] * (width * height)
            
            # Clear canvas to white
            canvas_image.pixels[:] = white_pixels
            canvas_image.update()
            
            # Update world HDRI if function exists
            try:
                update_world_hdri(context)
            except:
                pass  # update_world_hdri might not exist
            
            # Mark canvas as still active
            props = context.scene.hdri_studio
            props.canvas_active = True
            
            # Redraw areas
            for area in context.screen.areas:
                area.tag_redraw()
                    
            self.report({'INFO'}, "Canvas cleared to white")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Clear canvas failed: {e}")
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













# Operator classes list
classes = [
    HDRI_OT_create_canvas,
    HDRI_OT_clear_canvas,
    HDRI_OT_add_light,
]

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