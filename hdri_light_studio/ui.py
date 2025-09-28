"""
UI Module
Panel with GPU-based HDRI canvas display using custom draw handler
"""

import bpy
import gpu
import bgl
from bpy.types import Panel
from .operators import canvas_renderer

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
        
        # Canvas controls
        box = layout.box()
        box.label(text="Canvas", icon='IMAGE_DATA')
        
        row = box.row()
        row.prop(props, "canvas_size")
        
        row = box.row()
        if not props.canvas_active:
            row.operator("hdri_studio.create_canvas", icon='ADD')
        else:
            row.operator("hdri_studio.clear_canvas", icon='X')
        
        # Painting Instructions
        if props.canvas_active:
            instructions_box = layout.box()
            instructions_box.label(text="🎨 How to Paint:", icon='HELP')
            
            inst_col = instructions_box.column()
            inst_col.scale_y = 0.8
            
            inst_col.label(text="1. Click '✨ Ready to Paint' above")
            inst_col.label(text="2. Go to Image Editor panel (right side)")
            inst_col.label(text="3. Use brush tools or press 'B' for brush")
            inst_col.label(text="4. Paint directly on the image!")
            
            inst_col.separator()
            inst_col.label(text="💡 Pro Tips:")
            inst_col.label(text="• Switch to 'Texture Paint' workspace")
            inst_col.label(text="• Use 'F' to adjust brush size")
            inst_col.label(text="• Changes appear in 3D viewport instantly")
        
        # World Preview section
        if props.canvas_active:
            world_box = layout.box()
            world_box.label(text="World Preview", icon='WORLD')
            
            # Show current world shading mode
            world_info = world_box.column()
            world_info.scale_y = 0.8
            
            if context.scene.world and context.scene.world.use_nodes:
                world_info.label(text="✅ World HDRI Active", icon='CHECKMARK')
                
                # Quick shading mode controls
                shading_row = world_box.row(align=True)
                shading_row.label(text="View Mode:")
                
                # Check current viewport shading
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                if space.shading.type == 'MATERIAL':
                                    shading_row.label(text="Material ✅", icon='SHADING_RENDERED')
                                else:
                                    shading_button = shading_row.operator("wm.context_set_enum", text="Enable Material View")
                                    shading_button.data_path = "space_data.shading.type"
                                    shading_button.value = 'MATERIAL'
                                break
                        break
            else:
                world_info.label(text="❌ World HDRI Inactive", icon='ERROR')
            

        
        # Canvas display area (this is where we'll draw the GPU canvas)
        if props.canvas_active and canvas_renderer and canvas_renderer.is_initialized:
            canvas_box = layout.box()
            canvas_box.label(text="Canvas Display")
            
            # Create a custom canvas area
            canvas_area = canvas_box.column()
            canvas_area.scale_y = 10  # Make it bigger
            canvas_area.separator()
            
            # This is where we would draw the canvas using custom GPU drawing
            # We'll use a custom draw handler for this
            
        # Tool palette
        if props.canvas_active:
            tool_box = layout.box()
            tool_box.label(text="Tools", icon='TOOL_SETTINGS')
            
            row = tool_box.row()
            row.prop(props, "current_tool", expand=True)
            
            if props.current_tool == 'PAINT':
                # Paint tool settings
                paint_box = tool_box.box()
                paint_box.label(text="Paint Settings")
                
                paint_box.prop(props, "brush_size")
                paint_box.prop(props, "brush_intensity")
                
                # Color settings
                color_row = paint_box.row()
                color_row.prop(props, "use_temperature")
                
                if props.use_temperature:
                    paint_box.prop(props, "color_temperature")
                else:
                    paint_box.prop(props, "brush_color")
                
                # Paint modes
                paint_mode_box = paint_box.box()
                paint_mode_box.label(text="🎨 Paint Methods:", icon='BRUSH_DATA')
                
                # Method 1: Simple Paint Setup (EASIEST)
                simple_row = paint_mode_box.row()
                simple_row.scale_y = 1.3
                simple_row.operator("hdri_studio.simple_paint_setup", text="✨ Ready to Paint", icon='TPAINT_HLT')
                
                help_row = paint_mode_box.row()
                help_row.scale_y = 0.7
                help_row.label(text="↳ Use Image Editor paint tools or Texture Paint workspace")
                
                paint_mode_box.separator()
                
                # Method 2: Advanced texture paint (for mesh painting)
                advanced_row = paint_mode_box.row()
                advanced_row.scale_y = 0.9  
                advanced_row.operator("hdri_studio.setup_texture_paint", text="🔧 Mesh Paint Setup", icon='MESH_PLANE')
                
                # Method 3: Modal painting (backup)
                modal_row = paint_mode_box.row()
                modal_row.scale_y = 0.8
                modal_row.operator("hdri_studio.paint_canvas", text="📍 Modal Paint (3D View)", icon='BRUSH_DATA')
                
            elif props.current_tool == 'LIGHT':
                # Light tool settings
                light_box = tool_box.box()
                light_box.label(text="Light Settings")
                
                light_box.prop(props, "light_shape")
                light_box.prop(props, "light_size")
                light_box.prop(props, "light_intensity")
                
                # Color settings for lights
                color_row = light_box.row()
                color_row.prop(props, "use_temperature")
                
                if props.use_temperature:
                    temp_row = light_box.row()
                    temp_row.prop(props, "color_temperature")
                    # Show temperature color preview
                    from .utils import kelvin_to_rgb
                    temp_color = kelvin_to_rgb(props.color_temperature)
                    temp_preview = temp_row.row()
                    temp_preview.scale_x = 0.3
                    temp_preview.prop(props, "brush_color", text="")  # Preview color
                    
                else:
                    light_box.prop(props, "brush_color")
                
                # Light placement buttons
                light_buttons = light_box.row(align=True)
                light_buttons.operator("hdri_studio.add_light", text="Add Center", icon='LIGHT_SUN')
                light_buttons.operator("hdri_studio.interactive_light", text="Click to Place", icon='CURSOR')

# Global draw handler
canvas_draw_handler = None

def draw_canvas_callback():
    """Custom draw callback for rendering canvas in UI"""
    global canvas_renderer
    
    if not canvas_renderer or not canvas_renderer.is_initialized:
        return
        
    # Get current context and region
    context = bpy.context
    if not context or not context.region:
        return
        
    # Get canvas area dimensions (approximate)
    region = context.region
    
    # Calculate canvas display area (adjust as needed)
    canvas_x = 20
    canvas_y = region.height // 2 - 200  
    canvas_width = region.width - 40
    canvas_height = 400
    
    # Ensure canvas fits within region
    if canvas_width <= 0 or canvas_height <= 0:
        return
        
    try:
        # Render canvas using our GPU renderer  
        canvas_renderer.render_canvas(canvas_x, canvas_y, canvas_width, canvas_height)
    except Exception as e:
        print(f"Canvas draw callback failed: {e}")

def register_draw_handler():
    """Register the custom draw handler for canvas display"""
    global canvas_draw_handler
    
    if canvas_draw_handler is None:
        canvas_draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_canvas_callback, (), 'WINDOW', 'POST_PIXEL'
        )

def unregister_draw_handler():
    """Unregister the custom draw handler"""
    global canvas_draw_handler
    
    if canvas_draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(canvas_draw_handler, 'WINDOW')
        canvas_draw_handler = None

# Panel classes list  
classes = [
    HDRI_PT_main_panel,
]

def register():
    """Register UI classes and draw handler"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register draw handler for canvas display
    register_draw_handler()
    print("UI module registered")

def unregister():
    """Unregister UI classes and draw handler"""
    # Unregister draw handler
    unregister_draw_handler()
    
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("UI module unregistered")