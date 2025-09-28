"""
Simple Canvas Renderer - Fallback implementation without GPU textures
Uses basic bgl drawing for compatibility
"""

import bpy
import bgl
import numpy as np
from mathutils import Vector

class SimpleCanvasRenderer:
    """
    Simple canvas renderer using basic bgl calls
    Fallback when GPU texture approach fails
    """
    
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        self.canvas_data = None
        self.is_initialized = False
        
        # Initialize simple canvas
        self.initialize_simple_canvas()
    
    def initialize_simple_canvas(self):
        """Initialize simple canvas without GPU textures"""
        try:
            # Create simple canvas data
            self.canvas_data = np.ones((self.height, self.width, 4), dtype=np.float32)
            self.canvas_data[:, :, 0:3] = 0.7  # Light gray background
            self.canvas_data[:, :, 3] = 1.0    # Full alpha
            
            self.is_initialized = True
            print(f"Simple canvas renderer initialized: {self.width}x{self.height}")
            
        except Exception as e:
            print(f"Simple canvas initialization failed: {e}")
            self.is_initialized = False
    
    def render_canvas(self, x, y, width, height):
        """
        Render canvas using simple bgl rectangle drawing
        """
        if not self.is_initialized:
            return
            
        try:
            # Enable blending
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
            
            # Draw background rectangle
            bgl.glColor4f(0.7, 0.7, 0.7, 1.0)  # Light gray
            bgl.glBegin(bgl.GL_TRIANGLE_FAN)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x + width, y)
            bgl.glVertex2f(x + width, y + height)
            bgl.glVertex2f(x, y + height)
            bgl.glEnd()
            
            # Draw border
            bgl.glColor4f(0.3, 0.3, 0.3, 1.0)  # Dark gray border
            bgl.glBegin(bgl.GL_LINE_LOOP)
            bgl.glVertex2f(x, y)
            bgl.glVertex2f(x + width, y)
            bgl.glVertex2f(x + width, y + height)
            bgl.glVertex2f(x, y + height)
            bgl.glEnd()
            
            # Draw simple grid
            bgl.glColor4f(0.5, 0.5, 0.5, 0.3)
            grid_size = 20
            bgl.glBegin(bgl.GL_LINES)
            
            # Vertical lines
            for i in range(0, width, grid_size):
                bgl.glVertex2f(x + i, y)
                bgl.glVertex2f(x + i, y + height)
            
            # Horizontal lines    
            for i in range(0, height, grid_size):
                bgl.glVertex2f(x, y + i)
                bgl.glVertex2f(x + width, y + i)
                
            bgl.glEnd()
            
            # Reset color
            bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
            bgl.glDisable(bgl.GL_BLEND)
            
        except Exception as e:
            print(f"Simple canvas render failed: {e}")
    
    def paint_at_position(self, x, y, brush_size=50, intensity=1.0, color=(1.0, 1.0, 1.0)):
        """
        Paint at specified canvas coordinates (simplified)
        """
        try:
            if self.canvas_data is None:
                return
                
            # Paint directly on canvas data
            canvas_x = int(x)
            canvas_y = int(y)
            
            # Ensure coordinates are within bounds
            canvas_x = max(0, min(canvas_x, self.width - 1))
            canvas_y = max(0, min(canvas_y, self.height - 1))
            
            # Paint circular brush
            radius = max(1, brush_size // 2)
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px = canvas_x + dx
                    py = canvas_y + dy
                    
                    if (0 <= px < self.width and 0 <= py < self.height):
                        distance = np.sqrt(dx*dx + dy*dy)
                        if distance <= radius:
                            # Soft falloff
                            falloff = max(0, 1.0 - (distance / radius)) if radius > 0 else 1.0
                            alpha = intensity * falloff
                            
                            # Blend colors
                            self.canvas_data[py, px, 0] = (1 - alpha) * self.canvas_data[py, px, 0] + alpha * color[0]
                            self.canvas_data[py, px, 1] = (1 - alpha) * self.canvas_data[py, px, 1] + alpha * color[1] 
                            self.canvas_data[py, px, 2] = (1 - alpha) * self.canvas_data[py, px, 2] + alpha * color[2]
            
        except Exception as e:
            print(f"Simple paint failed: {e}")
    
    def update_canvas_data(self):
        """Update canvas data (no-op for simple renderer)"""
        pass
    
    def cleanup(self):
        """Clean up resources"""
        self.canvas_data = None
        self.is_initialized = False
        if hasattr(self, 'paint_marks'):
            self.paint_marks.clear()

def register():
    print("Simple canvas renderer module registered")

def unregister():
    print("Simple canvas renderer module unregistered")