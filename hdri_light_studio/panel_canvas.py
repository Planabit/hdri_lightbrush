"""
Panel Canvas Renderer - Direct panel drawing approach
Uses panel custom drawing without external draw handlers
"""

import bpy
import bgl
import gpu
from bpy.types import Panel
import numpy as np
from .operators import canvas_renderer

class HDRI_PT_canvas_panel(Panel):
    """Dedicated panel for canvas display with custom drawing"""
    bl_label = "HDRI Canvas"
    bl_idname = "HDRI_PT_canvas_panel" 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HDRI Studio"
    bl_parent_id = "HDRI_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        """Only show if canvas is active"""
        return context.scene.hdri_studio.canvas_active
    
    def draw(self, context):
        layout = self.layout
        
        # Canvas display box
        canvas_box = layout.box()
        canvas_box.label(text="Canvas View", icon='IMAGE_DATA')
        
        # Create fixed size area for canvas
        col = canvas_box.column()
        
        # Multiple separators to create space for drawing
        for i in range(8):
            col.separator()
        
        # Try to draw canvas using immediate mode
        self.draw_canvas_immediate(context, col)
    
    def draw_canvas_immediate(self, context, layout):
        """Draw canvas using immediate OpenGL calls"""
        global canvas_renderer
        
        if not canvas_renderer or not canvas_renderer.is_initialized:
            # Show placeholder
            placeholder = layout.box()
            placeholder.label(text="Canvas not initialized", icon='ERROR')
            return
        
        try:
            # Get region info for drawing area calculation
            region = context.region
            
            if not region:
                layout.label(text="No region info", icon='ERROR')
                return
            
            # Calculate canvas area (approximate panel position)
            canvas_width = 200
            canvas_height = 200
            canvas_x = 20
            canvas_y = region.height // 2
            
            # Create a large separator to ensure space
            spacer = layout.column()
            spacer.scale_y = 15
            spacer.separator()
            
            # Draw immediately during panel draw
            self.draw_canvas_now(canvas_x, canvas_y, canvas_width, canvas_height)
            
        except Exception as e:
            error_box = layout.box()
            error_box.label(text=f"Canvas error: {str(e)[:30]}", icon='ERROR')
            print(f"Canvas draw error: {e}")
    
    def draw_canvas_now(self, x, y, width, height):
        """Draw canvas immediately using bgl"""
        try:
            # Enable OpenGL state
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
            
            # Draw canvas background
            bgl.glColor4f(0.8, 0.8, 0.9, 1.0)  # Light blue-gray
            bgl.glBegin(bgl.GL_TRIANGLE_FAN)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x + width, y) 
            bgl.glVertex2f(x + width, y + height)
            bgl.glVertex2f(x, y + height)
            bgl.glEnd()
            
            # Draw canvas border
            bgl.glColor4f(0.2, 0.2, 0.3, 1.0)  # Dark border
            bgl.glLineWidth(2.0)
            bgl.glBegin(bgl.GL_LINE_LOOP)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x + width, y)
            bgl.glVertex2f(x + width, y + height) 
            bgl.glVertex2f(x, y + height)
            bgl.glEnd()
            
            # Draw simple grid
            bgl.glColor4f(0.6, 0.6, 0.7, 0.5)
            bgl.glLineWidth(1.0)
            bgl.glBegin(bgl.GL_LINES)
            
            # Vertical grid lines
            grid_step = 25
            for i in range(grid_step, width, grid_step):
                bgl.glVertex2f(x + i, y)
                bgl.glVertex2f(x + i, y + height)
            
            # Horizontal grid lines
            for i in range(grid_step, height, grid_step):
                bgl.glVertex2f(x, y + i)
                bgl.glVertex2f(x + width, y + i)
                
            bgl.glEnd()
            
            # Draw paint marks if available
            if hasattr(canvas_renderer, 'paint_marks'):
                bgl.glColor4f(1.0, 0.8, 0.2, 0.8)  # Yellow paint marks
                for mark in canvas_renderer.paint_marks[-20:]:  # Last 20 marks
                    mark_x = x + (mark['x'] / canvas_renderer.width) * width
                    mark_y = y + (mark['y'] / canvas_renderer.height) * height
                    mark_size = max(3, mark['size'] / 10)
                    
                    # Draw circle for paint mark
                    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
                    bgl.glVertex2f(mark_x, mark_y)
                    for angle in range(0, 361, 30):
                        rad = angle * 3.14159 / 180
                        px = mark_x + mark_size * np.cos(rad)
                        py = mark_y + mark_size * np.sin(rad)
                        bgl.glVertex2f(px, py)
                    bgl.glEnd()
            
            # Status text
            bgl.glColor4f(0.1, 0.1, 0.1, 1.0)
            
            # Reset OpenGL state
            bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
            bgl.glLineWidth(1.0)
            bgl.glDisable(bgl.GL_BLEND)
            
        except Exception as e:
            print(f"Immediate canvas draw failed: {e}")

def register():
    bpy.utils.register_class(HDRI_PT_canvas_panel)
    print("Panel canvas renderer registered")

def unregister():
    bpy.utils.unregister_class(HDRI_PT_canvas_panel)
    print("Panel canvas renderer unregistered")