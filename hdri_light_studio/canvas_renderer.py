"""
Canvas Renderer Module
GPU-based texture rendering using bgl + triangle fan for inline panel display
"""

import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader
import numpy as np
from mathutils import Vector

class HDRICanvasRenderer:
    """
    GPU-based canvas renderer for inline HDRI editing in panels
    Uses bgl + triangle fan primitive for direct texture rendering
    """
    
    def __init__(self, width=2048, height=2048):
        self.width = width
        self.height = height
        self.texture = None
        self.shader = None
        self.batch = None
        self.canvas_data = None
        self.is_initialized = False
        
        # Canvas properties
        self.canvas_rect = (0, 0, 400, 400)  # Panel display size
        self.zoom = 1.0
        self.pan_offset = Vector((0, 0))
        
        # Initialize canvas
        self.initialize_canvas()
    
    def initialize_canvas(self):
        """Initialize GPU resources for canvas rendering"""
        try:
            # Create canvas data (RGBA) - simpler approach
            self.canvas_data = np.ones((self.height, self.width, 4), dtype=np.float32)
            self.canvas_data[:, :, 0:3] = 0.5  # Gray background
            self.canvas_data[:, :, 3] = 1.0    # Full alpha
            
            # Try to create GPU texture with error handling
            try:
                # Use simpler format first
                buffer = gpu.types.Buffer('FLOAT', [self.width * self.height * 4], self.canvas_data.flatten())
                self.texture = gpu.types.GPUTexture((self.width, self.height), format='RGBA32F', data=buffer)
            except Exception as tex_error:
                print(f"RGBA32F texture failed, trying RGBA8: {tex_error}")
                # Fallback to 8-bit texture
                canvas_8bit = (self.canvas_data * 255).astype(np.uint8)
                buffer = gpu.types.Buffer('UBYTE', [self.width * self.height * 4], canvas_8bit.flatten())
                self.texture = gpu.types.GPUTexture((self.width, self.height), format='RGBA8', data=buffer)
            
            # Use built-in shader instead of custom
            try:
                from gpu_extras.presets import draw_texture_2d
                self.draw_texture_2d = draw_texture_2d
                self.shader = None  # We'll use the built-in function
            except ImportError:
                # Fallback to simpler custom shader
                vertex_shader = '''
                    uniform mat4 ModelViewProjectionMatrix;
                    in vec2 pos;
                    in vec2 texCoord_in;
                    out vec2 texCoord_interp;
                    
                    void main()
                    {
                        gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
                        texCoord_interp = texCoord_in;
                    }
                '''
                
                fragment_shader = '''
                    in vec2 texCoord_interp;
                    out vec4 fragColor;
                    uniform sampler2D image;
                    
                    void main()
                    {
                        fragColor = texture(image, texCoord_interp);
                    }
                '''
                
                self.shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
                
                # Simple quad
                vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
                texcoords = [(0, 0), (1, 0), (1, 1), (0, 1)]
                indices = [(0, 1, 2), (0, 2, 3)]
                
                self.batch = batch_for_shader(
                    self.shader, 'TRIS',
                    {"pos": vertices, "texCoord_in": texcoords},
                    indices=indices
                )
            
            self.is_initialized = True
            print(f"Canvas renderer initialized: {self.width}x{self.height}")
            
        except Exception as e:
            print(f"Canvas renderer initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.is_initialized = False
    
    def update_canvas_data(self):
        """Update GPU texture with current canvas data"""
        if not self.texture or self.canvas_data is None:
            return
            
        try:
            # Create new buffer with updated data
            if hasattr(self.texture, 'format') and 'RGBA8' in str(self.texture.format):
                # 8-bit texture
                canvas_8bit = (np.clip(self.canvas_data, 0, 1) * 255).astype(np.uint8)
                buffer = gpu.types.Buffer('UBYTE', [self.width * self.height * 4], canvas_8bit.flatten())
            else:
                # Float texture
                buffer = gpu.types.Buffer('FLOAT', [self.width * self.height * 4], self.canvas_data.flatten())
            
            # Update texture - recreate if necessary
            try:
                # Try to update existing texture
                texture_name = self.texture.name if hasattr(self.texture, 'name') else 0
                if texture_name > 0:
                    bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture_name)
                    if hasattr(self.texture, 'format') and 'RGBA8' in str(self.texture.format):
                        bgl.glTexSubImage2D(bgl.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, 
                                          bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)
                    else:
                        bgl.glTexSubImage2D(bgl.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height,
                                          bgl.GL_RGBA, bgl.GL_FLOAT, buffer)
                    bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
                else:
                    raise Exception("Invalid texture name")
                    
            except Exception:
                # Fallback: recreate texture
                print("Recreating texture...")
                if hasattr(self.texture, 'format') and 'RGBA8' in str(self.texture.format):
                    self.texture = gpu.types.GPUTexture((self.width, self.height), format='RGBA8', data=buffer)
                else:
                    self.texture = gpu.types.GPUTexture((self.width, self.height), format='RGBA32F', data=buffer)
                    
        except Exception as e:
            print(f"Canvas data update failed: {e}")
            import traceback
            traceback.print_exc()
    
    def render_canvas(self, x, y, width, height):
        """
        Render canvas to specified screen coordinates using simplified approach
        """
        if not self.is_initialized or not self.texture:
            return
            
        try:
            # Use built-in draw_texture_2d if available
            if hasattr(self, 'draw_texture_2d'):
                # Calculate texture coordinates for the given area
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
                
                # Draw using built-in function
                self.draw_texture_2d(self.texture, (x, y), width, height)
                
                bgl.glDisable(bgl.GL_BLEND)
                return
            
            # Fallback to bgl triangle fan method
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
            bgl.glEnable(bgl.GL_TEXTURE_2D)
            
            # Bind texture
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.texture.name if hasattr(self.texture, 'name') else 0)
            
            # Set up viewport and matrices
            bgl.glMatrixMode(bgl.GL_PROJECTION)
            bgl.glPushMatrix()
            bgl.glLoadIdentity()
            bgl.glOrtho(0, width, 0, height, -1, 1)
            
            bgl.glMatrixMode(bgl.GL_MODELVIEW)
            bgl.glPushMatrix()
            bgl.glLoadIdentity()
            
            # Draw quad using triangle fan
            bgl.glBegin(bgl.GL_TRIANGLE_FAN)
            bgl.glTexCoord2f(0.0, 1.0); bgl.glVertex2f(0, 0)      # Bottom-left
            bgl.glTexCoord2f(1.0, 1.0); bgl.glVertex2f(width, 0)  # Bottom-right  
            bgl.glTexCoord2f(1.0, 0.0); bgl.glVertex2f(width, height) # Top-right
            bgl.glTexCoord2f(0.0, 0.0); bgl.glVertex2f(0, height) # Top-left
            bgl.glEnd()
            
            # Restore matrices
            bgl.glPopMatrix()
            bgl.glMatrixMode(bgl.GL_PROJECTION)
            bgl.glPopMatrix()
            bgl.glMatrixMode(bgl.GL_MODELVIEW)
            
            # Cleanup
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
            bgl.glDisable(bgl.GL_TEXTURE_2D)
            bgl.glDisable(bgl.GL_BLEND)
            
        except Exception as e:
            print(f"Canvas render failed: {e}")
            import traceback
            traceback.print_exc()
    
    def paint_at_position(self, x, y, brush_size=50, intensity=1.0, color=(1.0, 1.0, 1.0)):
        """
        Paint at specified canvas coordinates
        """
        if not self.is_initialized or self.canvas_data is None:
            return
            
        try:
            # Use coordinates directly (not scaled to canvas_rect)
            canvas_x = int(x)
            canvas_y = int(y)
            
            # Ensure coordinates are within bounds
            canvas_x = max(0, min(canvas_x, self.width - 1))
            canvas_y = max(0, min(canvas_y, self.height - 1))
            
            # Paint circular brush
            radius = brush_size // 2
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px = canvas_x + dx
                    py = canvas_y + dy
                    
                    if (0 <= px < self.width and 0 <= py < self.height):
                        distance = np.sqrt(dx*dx + dy*dy)
                        if distance <= radius:
                            # Soft falloff
                            falloff = max(0, 1.0 - (distance / radius))
                            alpha = intensity * falloff
                            
                            # Blend colors
                            self.canvas_data[py, px, 0] = (1 - alpha) * self.canvas_data[py, px, 0] + alpha * color[0]
                            self.canvas_data[py, px, 1] = (1 - alpha) * self.canvas_data[py, px, 1] + alpha * color[1] 
                            self.canvas_data[py, px, 2] = (1 - alpha) * self.canvas_data[py, px, 2] + alpha * color[2]
            
            # Update GPU texture
            self.update_canvas_data()
            
        except Exception as e:
            print(f"Paint operation failed: {e}")
    
    def cleanup(self):
        """Clean up GPU resources"""
        if self.texture:
            del self.texture
        if self.batch:
            del self.batch
        self.is_initialized = False

def register():
    print("Canvas renderer module registered")

def unregister():
    print("Canvas renderer module unregistered")