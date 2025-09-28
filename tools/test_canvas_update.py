"""
Simple Canvas Update Test
Test script to debug canvas painting issues
"""

import bpy
import numpy as np

def test_simple_canvas_update():
    """Test simple canvas creation and update"""
    
    print("\n=== Simple Canvas Update Test ===")
    
    try:
        # Create a simple test image
        image_name = "Test_Canvas"
        width, height = 512, 256  # Small size for testing
        
        # Remove existing if present
        if image_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[image_name])
        
        # Create new image
        test_image = bpy.data.images.new(image_name, width, height, alpha=True)
        print(f"Created image: {width}x{height}")
        
        # Create test pixel data
        print("Creating pixel data...")
        pixels = np.ones((height, width, 4), dtype=np.float32)
        
        # Add some color pattern
        for y in range(height):
            for x in range(width):
                pixels[y, x] = [
                    x / width,      # Red gradient
                    y / height,     # Green gradient
                    0.5,            # Blue constant
                    1.0             # Alpha
                ]
        
        print(f"Pixel array shape: {pixels.shape}")
        
        # Flatten and update image
        flat_pixels = pixels.reshape(height * width * 4)
        print(f"Flat pixel array length: {len(flat_pixels)}")
        print(f"Image pixel array length: {len(test_image.pixels)}")
        
        if len(flat_pixels) == len(test_image.pixels):
            test_image.pixels[:] = flat_pixels
            test_image.update()
            print("✅ Image updated successfully!")
        else:
            print(f"❌ Size mismatch: {len(flat_pixels)} vs {len(test_image.pixels)}")
            
        # Test partial update
        print("Testing partial update...")
        for i in range(100):
            x = i % width
            y = i // width
            if y < height:
                idx = (y * width + x) * 4
                if idx + 3 < len(test_image.pixels):
                    test_image.pixels[idx] = 1.0      # Red
                    test_image.pixels[idx + 1] = 0.0  # Green  
                    test_image.pixels[idx + 2] = 0.0  # Blue
                    test_image.pixels[idx + 3] = 1.0  # Alpha
        
        test_image.update()
        print("✅ Partial update successful!")
        
        # Display in Image Editor
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = test_image
                        area.tag_redraw()
                        print("✅ Image set in Image Editor")
                        break
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_canvas_update()