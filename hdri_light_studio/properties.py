"""
Properties Module
Scene and tool properties for HDRI Light Studio
"""

import bpy
from bpy.props import (
    EnumProperty, FloatProperty, IntProperty, 
    BoolProperty, FloatVectorProperty, StringProperty, PointerProperty
)
from bpy.types import PropertyGroup

class HDRIStudioProperties(PropertyGroup):
    """Main property group for HDRI Studio settings"""
    
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
    
    # Paint tool properties
    brush_size: IntProperty(
        name="Brush Size",
        description="Size of the paint brush",
        default=50,
        min=1,
        max=200
    )
    
    brush_intensity: FloatProperty(
        name="Intensity", 
        description="Paint intensity/opacity",
        default=1.0,
        min=0.0,
        max=2.0
    )
    
    brush_color: FloatVectorProperty(
        name="Brush Color",
        description="RGB color for painting",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        size=3
    )
    
    # Color temperature properties
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
    
    light_intensity: FloatProperty(
        name="Light Intensity",
        description="Intensity of the light source", 
        default=1.0,
        min=0.0,
        max=10.0
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
    print("Properties module registered")

def unregister():
    """Unregister property classes"""
    bpy.utils.unregister_class(HDRIStudioProperties)
    print("Properties module unregistered")