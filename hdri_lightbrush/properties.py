"""
Properties Module
Scene and tool properties for HDRI LightBrush
"""

import bpy
from bpy.props import (
    EnumProperty, FloatProperty, IntProperty, 
    BoolProperty, FloatVectorProperty, StringProperty, PointerProperty
)
from bpy.types import PropertyGroup


class HDRIStudioProperties(PropertyGroup):
    """Main property group for HDRI LightBrush settings"""
    
    # Canvas properties
    canvas_size: EnumProperty(
        name="Canvas Size",
        description="Size of the HDRI canvas",
        items=[
            ('2K', "2K HDRI (2048x1024)", "2048x1024 HDRI standard resolution"),
            ('4K', "4K HDRI (4096x2048)", "4096x2048 HDRI standard resolution"),
        ],
        default='2K'
    )
    
    # Current canvas instance
    canvas_active: BoolProperty(
        name="Canvas Active",
        description="Whether a canvas is currently active",
        default=False
    )
    
    # Tool properties
    current_tool: EnumProperty(
        name="Current Tool",
        description="Currently selected painting tool",
        items=[
            ('PAINT', "Paint", "Paint with brush"),
            ('LIGHT', "Add Light", "Add light source"),
        ],
        default='PAINT'
    )
    
    # Color temperature properties (optional alternative to brush color)
    use_temperature: BoolProperty(
        name="Use Temperature",
        description="Use color temperature instead of RGB",
        default=False
    )
    
    color_temperature: IntProperty(
        name="Temperature",
        description="Color temperature in Kelvin",
        default=6500,
        min=1000,
        max=40000
    )
    
    # Light tool properties  
    light_shape: EnumProperty(
        name="Light Shape",
        description="Shape of the light to add",
        items=[
            ('CIRCLE', "Circle", "Circular light"),
            ('SQUARE', "Square", "Square light"),
            ('RECTANGLE', "Rectangle", "Rectangular light"),
        ],
        default='CIRCLE'
    )
    
    light_size: FloatProperty(
        name="Light Size",
        description="Size of the light source",
        default=100.0,
        min=10.0,
        max=500.0
    )
    
    # Performance optimization for 4K-8K textures
    performance_mode: BoolProperty(
        name="Performance Mode",
        description="Enable optimizations for 4K-8K HDRI painting (reduces real-time updates)",
        default=False
    )
    
    update_rate: EnumProperty(
        name="Update Rate",
        description="How often to update 3D preview while painting",
        items=[
            ('REALTIME', "Real-time (30 FPS)", "Update every frame - smooth but slower on large textures"),
            ('FAST', "Fast (15 FPS)", "Good balance for 4K textures"),
            ('RESPONSIVE', "Responsive (10 FPS)", "Better performance for 8K textures"),
        ],
        default='FAST'
    )
    
    light_intensity: FloatProperty(
        name="Light Intensity",
        description="Intensity of the light source", 
        default=1.0,
        min=0.0,
        max=10.0
    )
    
    # ═══════════════════════════════════════════════════════
    # 3D PAINT BRUSH SETTINGS (Blender 5.0 compatibility)
    # ═══════════════════════════════════════════════════════
    paint_color: FloatVectorProperty(
        name="Paint Color",
        description="Brush color for 3D painting",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    
    paint_size: IntProperty(
        name="Brush Size",
        description="Radius of the brush in pixels",
        default=70,
        min=1,
        max=500,
        subtype='PIXEL'
    )
    
    paint_strength: FloatProperty(
        name="Strength",
        description="Brush strength/opacity",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    
    paint_hardness: FloatProperty(
        name="Hardness",
        description="Brush edge hardness (0=soft, 1=hard)",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    
    paint_blend: EnumProperty(
        name="Blend Mode",
        description="How the brush blends with existing colors",
        items=[
            ('MIX', "Mix", "Normal blend - replaces color"),
            ('ADD', "Add", "Adds color (brightens)"),
            ('MULTIPLY', "Multiply", "Multiplies colors (darkens)"),
            ('LIGHTEN', "Lighten", "Only lightens pixels"),
            ('DARKEN', "Darken", "Only darkens pixels"),
            ('ERASE', "Erase", "Erases to black"),
        ],
        default='MIX'
    )
    
    # Canvas display properties
    canvas_zoom: FloatProperty(
        name="Zoom",
        description="Canvas zoom level",
        default=1.0,
        min=0.1,
        max=5.0
    )
    
    canvas_pan_x: FloatProperty(
        name="Pan X",
        description="Canvas pan X offset",
        default=0.0
    )
    
    canvas_pan_y: FloatProperty(
        name="Pan Y", 
        description="Canvas pan Y offset",
        default=0.0
    )

def register():
    """Register property classes"""
    bpy.utils.register_class(HDRIStudioProperties)

def unregister():
    """Unregister property classes"""
    bpy.utils.unregister_class(HDRIStudioProperties)