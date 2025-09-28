"""
Utility functions for HDRI Light Studio
Color temperature and other helper functions
"""

import numpy as np
import mathutils

def kelvin_to_rgb(kelvin):
    """
    Convert Kelvin color temperature to RGB values
    Based on Tanner Helland's algorithm
    
    Args:
        kelvin: Temperature in Kelvin (1000-40000)
        
    Returns:
        tuple: (r, g, b) values in 0-1 range
    """
    
    # Clamp temperature to valid range
    kelvin = max(1000, min(40000, kelvin))
    
    # Calculate temperature / 100
    temp = kelvin / 100.0
    
    # Calculate red
    if temp <= 66:
        red = 255
    else:
        red = temp - 60
        red = 329.698727446 * (red ** -0.1332047592)
        red = max(0, min(255, red))
    
    # Calculate green
    if temp <= 66:
        green = temp
        green = 99.4708025861 * np.log(green) - 161.1195681661
    else:
        green = temp - 60
        green = 288.1221695283 * (green ** -0.0755148492)
    green = max(0, min(255, green))
    
    # Calculate blue
    if temp >= 66:
        blue = 255
    elif temp <= 19:
        blue = 0
    else:
        blue = temp - 10
        blue = 138.5177312231 * np.log(blue) - 305.0447927307
        blue = max(0, min(255, blue))
    
    # Convert to 0-1 range
    return (red / 255.0, green / 255.0, blue / 255.0)

def rgb_to_kelvin(r, g, b):
    """
    Approximate conversion from RGB to Kelvin temperature
    
    Args:
        r, g, b: RGB values in 0-1 range
        
    Returns:
        int: Approximate temperature in Kelvin
    """
    
    # Simple approximation based on color balance
    if r >= g >= b:  # Warm colors
        ratio = b / r if r > 0 else 0
        return int(6500 - (ratio * 3500))  # 3000K to 6500K
    elif b >= g >= r:  # Cool colors
        ratio = r / b if b > 0 else 0
        return int(6500 + ((1 - ratio) * 13500))  # 6500K to 20000K
    else:  # Mixed colors, default to daylight
        return 6500

def create_light_shape(shape_type, size, center_x, center_y, intensity=1.0, color=(1.0, 1.0, 1.0)):
    """
    Create light shape data for painting on canvas
    
    Args:
        shape_type: 'CIRCLE', 'SQUARE', 'RECTANGLE'
        size: Size in pixels
        center_x, center_y: Center position
        intensity: Light intensity (0-10)
        color: RGB color tuple
        
    Returns:
        tuple: (x_coords, y_coords, values) for painting
    """
    
    coords_x = []
    coords_y = []
    values = []
    
    half_size = size // 2
    
    if shape_type == 'CIRCLE':
        # Create circular light
        for y in range(-half_size, half_size + 1):
            for x in range(-half_size, half_size + 1):
                distance = np.sqrt(x*x + y*y)
                if distance <= half_size:
                    # Soft falloff
                    falloff = 1.0 - (distance / half_size)
                    falloff = falloff * falloff  # Smooth curve
                    
                    coords_x.append(center_x + x)
                    coords_y.append(center_y + y)
                    
                    # Apply intensity and color
                    final_intensity = intensity * falloff
                    values.append((
                        color[0] * final_intensity,
                        color[1] * final_intensity, 
                        color[2] * final_intensity,
                        1.0  # Alpha
                    ))
                    
    elif shape_type == 'SQUARE':
        # Create square light
        for y in range(-half_size, half_size + 1):
            for x in range(-half_size, half_size + 1):
                # Distance from center for falloff
                distance = max(abs(x), abs(y)) / half_size
                falloff = 1.0 - distance
                falloff = max(0, falloff)
                
                coords_x.append(center_x + x)
                coords_y.append(center_y + y)
                
                # Apply intensity and color
                final_intensity = intensity * falloff
                values.append((
                    color[0] * final_intensity,
                    color[1] * final_intensity,
                    color[2] * final_intensity, 
                    1.0  # Alpha
                ))
                
    elif shape_type == 'RECTANGLE':
        # Create rectangular light (2:1 aspect ratio)
        rect_width = size
        rect_height = size // 2
        
        for y in range(-rect_height//2, rect_height//2 + 1):
            for x in range(-rect_width//2, rect_width//2 + 1):
                # Distance for falloff
                x_dist = abs(x) / (rect_width//2)
                y_dist = abs(y) / (rect_height//2)
                distance = max(x_dist, y_dist)
                falloff = 1.0 - distance
                falloff = max(0, falloff)
                
                coords_x.append(center_x + x)
                coords_y.append(center_y + y)
                
                # Apply intensity and color
                final_intensity = intensity * falloff
                values.append((
                    color[0] * final_intensity,
                    color[1] * final_intensity,
                    color[2] * final_intensity,
                    1.0  # Alpha
                ))
    
    return coords_x, coords_y, values

def apply_brush_falloff(distance, brush_size, falloff_type='SMOOTH'):
    """
    Calculate brush falloff based on distance from center
    
    Args:
        distance: Distance from brush center
        brush_size: Brush radius
        falloff_type: 'SMOOTH', 'LINEAR', 'SHARP'
        
    Returns:
        float: Falloff value 0-1
    """
    
    if distance >= brush_size:
        return 0.0
        
    normalized_distance = distance / brush_size
    
    if falloff_type == 'LINEAR':
        return 1.0 - normalized_distance
    elif falloff_type == 'SHARP':
        return 1.0 if distance < brush_size * 0.5 else 0.0
    else:  # SMOOTH (default)
        return (1.0 - normalized_distance) ** 2

def blend_colors(base_color, paint_color, blend_mode='NORMAL', opacity=1.0):
    """
    Blend two colors with different blend modes
    
    Args:
        base_color: Base RGBA tuple
        paint_color: Paint RGBA tuple  
        blend_mode: 'NORMAL', 'ADD', 'MULTIPLY', 'OVERLAY'
        opacity: Blend opacity 0-1
        
    Returns:
        tuple: Blended RGBA color
    """
    
    base_r, base_g, base_b, base_a = base_color
    paint_r, paint_g, paint_b, paint_a = paint_color
    
    # Apply opacity
    paint_a *= opacity
    
    if blend_mode == 'ADD':
        result_r = min(1.0, base_r + paint_r * paint_a)
        result_g = min(1.0, base_g + paint_g * paint_a) 
        result_b = min(1.0, base_b + paint_b * paint_a)
    elif blend_mode == 'MULTIPLY':
        result_r = base_r * (1 - paint_a) + (base_r * paint_r) * paint_a
        result_g = base_g * (1 - paint_a) + (base_g * paint_g) * paint_a
        result_b = base_b * (1 - paint_a) + (base_b * paint_b) * paint_a
    elif blend_mode == 'OVERLAY':
        def overlay_blend(base, paint):
            if base < 0.5:
                return 2 * base * paint
            else:
                return 1 - 2 * (1 - base) * (1 - paint)
        
        result_r = base_r * (1 - paint_a) + overlay_blend(base_r, paint_r) * paint_a
        result_g = base_g * (1 - paint_a) + overlay_blend(base_g, paint_g) * paint_a  
        result_b = base_b * (1 - paint_a) + overlay_blend(base_b, paint_b) * paint_a
    else:  # NORMAL
        result_r = base_r * (1 - paint_a) + paint_r * paint_a
        result_g = base_g * (1 - paint_a) + paint_g * paint_a
        result_b = base_b * (1 - paint_a) + paint_b * paint_a
    
    result_a = min(1.0, base_a + paint_a)
    
    return (result_r, result_g, result_b, result_a)

def register():
    """Register utils module"""
    pass

def unregister():
    """Unregister utils module"""
    pass