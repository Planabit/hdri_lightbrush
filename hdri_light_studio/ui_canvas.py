"""
UI Canvas Display - Using Blender UI elements for canvas representation
"""

import bpy
from bpy.types import Panel, UILayout
import bmesh
from .operators import canvas_renderer

class HDRI_PT_canvas_display(Panel):
    """Canvas display using UI elements"""
    bl_label = "Canvas View"
    bl_idname = "HDRI_PT_canvas_display"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI Studio"
    bl_parent_id = "HDRI_PT_main_panel"
    
    @classmethod 
    def poll(cls, context):
        return context.scene.hdri_studio.canvas_active
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.hdri_studio
        
        # Canvas info
        canvas_box = layout.box()
        canvas_box.label(text="Canvas Display", icon='IMAGE_DATA')
        
        global canvas_renderer
        if canvas_renderer and canvas_renderer.is_initialized:
            # Show canvas info
            info_row = canvas_box.row()
            info_row.label(text=f"Size: {canvas_renderer.width}x{canvas_renderer.height}")
            
            # Canvas type
            canvas_type = "Advanced GPU" if hasattr(canvas_renderer, 'texture') and canvas_renderer.texture else "Simple BGL"
            info_row.label(text=f"Type: {canvas_type}")
            
            # Create visual representation using UI elements
            self.draw_canvas_ui(canvas_box, context)
            
            # Paint marks display
            if hasattr(canvas_renderer, 'paint_marks') and canvas_renderer.paint_marks:
                marks_box = canvas_box.box()
                marks_box.label(text=f"Paint Marks: {len(canvas_renderer.paint_marks)}")
                
                # Show last few paint marks
                for i, mark in enumerate(canvas_renderer.paint_marks[-3:]):
                    mark_row = marks_box.row()
                    mark_row.scale_y = 0.8
                    mark_row.label(text=f"Mark {i+1}: ({int(mark['x'])}, {int(mark['y'])}) Size: {int(mark['size'])}")
        else:
            canvas_box.label(text="Canvas not initialized", icon='ERROR')
    
    def draw_canvas_ui(self, layout, context):
        """Draw canvas representation using UI grid"""
        
        # Create a grid of buttons to represent canvas
        canvas_grid = layout.box()
        canvas_grid.label(text="Canvas Grid (Interactive)", icon='GRID')
        
        # Create 8x8 grid of buttons
        for row in range(8):
            button_row = canvas_grid.row()
            button_row.scale_y = 0.5
            
            for col in range(8):
                # Calculate if this grid cell has paint
                has_paint = self.check_paint_at_grid(row, col, 8, 8)
                
                if has_paint:
                    button_row.operator("hdri_studio.grid_paint", text="●", emboss=True).grid_pos = f"{row},{col}"
                else:
                    button_row.operator("hdri_studio.grid_paint", text="○", emboss=False).grid_pos = f"{row},{col}"
        
        # Canvas controls
        controls = layout.row()
        controls.operator("hdri_studio.clear_canvas", text="Clear", icon='X')
        
        # Show canvas data summary
        summary = layout.box()
        summary.label(text="Canvas Summary:")
        
        global canvas_renderer
        if canvas_renderer:
            if hasattr(canvas_renderer, 'canvas_data') and canvas_renderer.canvas_data is not None:
                # Calculate some basic stats
                try:
                    import numpy as np
                    avg_brightness = float(np.mean(canvas_renderer.canvas_data[:,:,0:3]))
                    summary.label(text=f"Avg Brightness: {avg_brightness:.2f}")
                except:
                    summary.label(text="Canvas data available")
            
            if hasattr(canvas_renderer, 'paint_marks'):
                summary.label(text=f"Paint operations: {len(canvas_renderer.paint_marks) if canvas_renderer.paint_marks else 0}")
    
    def check_paint_at_grid(self, row, col, grid_rows, grid_cols):
        """Check if there's paint in this grid cell"""
        global canvas_renderer
        
        if not canvas_renderer or not hasattr(canvas_renderer, 'paint_marks'):
            return False
        
        if not canvas_renderer.paint_marks:
            return False
        
        # Calculate grid cell bounds
        cell_width = canvas_renderer.width / grid_cols
        cell_height = canvas_renderer.height / grid_rows
        
        cell_x_min = col * cell_width
        cell_x_max = (col + 1) * cell_width
        cell_y_min = row * cell_height  
        cell_y_max = (row + 1) * cell_height
        
        # Check if any paint marks fall in this cell
        for mark in canvas_renderer.paint_marks:
            mark_x = mark['x']
            mark_y = mark['y']
            
            if (cell_x_min <= mark_x <= cell_x_max and 
                cell_y_min <= mark_y <= cell_y_max):
                return True
        
        return False

class HDRI_OT_grid_paint(bpy.types.Operator):
    """Paint on grid cell"""
    bl_idname = "hdri_studio.grid_paint"
    bl_label = "Grid Paint"
    
    grid_pos: bpy.props.StringProperty()
    
    def execute(self, context):
        try:
            row, col = map(int, self.grid_pos.split(','))
            
            global canvas_renderer
            if canvas_renderer:
                # Convert grid position to canvas coordinates
                cell_width = canvas_renderer.width / 8
                cell_height = canvas_renderer.height / 8
                
                paint_x = (col + 0.5) * cell_width
                paint_y = (row + 0.5) * cell_height
                
                # Paint at this position
                props = context.scene.hdri_studio
                canvas_renderer.paint_at_position(
                    paint_x, paint_y,
                    props.brush_size,
                    props.brush_intensity,
                    props.brush_color
                )
                
                # Redraw UI
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                
                self.report({'INFO'}, f"Painted at grid ({row},{col})")
        
        except Exception as e:
            self.report({'ERROR'}, f"Grid paint failed: {e}")
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(HDRI_PT_canvas_display)
    bpy.utils.register_class(HDRI_OT_grid_paint)
    print("UI Canvas display registered")

def unregister():
    bpy.utils.unregister_class(HDRI_OT_grid_paint)
    bpy.utils.unregister_class(HDRI_PT_canvas_display)
    print("UI Canvas display unregistered")