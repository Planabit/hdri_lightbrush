
import bpy
import sys

def test_hdri_light_studio():
    """Test HDRI Light Studio addon functionality"""
    
    print("\n=== HDRI Light Studio Test ===")
    
    try:
        # Check if addon is available
        import hdri_light_studio
        print("✅ Addon import successful")
        
        # Check if properties are registered
        scene = bpy.context.scene
        if hasattr(scene, 'hdri_studio'):
            props = scene.hdri_studio
            print("✅ Properties registered")
            
            # Test property access
            print(f"📏 Default canvas size: {props.canvas_size}")
            print(f"🎨 Default tool: {props.current_tool}")
            print(f"🌡️  Default temperature: {props.color_temperature}K")
            
        else:
            print("❌ Properties not registered")
            return False
        
        # Check if operators are available
        operators_to_check = [
            "hdri_studio.create_canvas",
            "hdri_studio.clear_canvas", 
            "hdri_studio.paint_canvas",
            "hdri_studio.add_light",
            "hdri_studio.interactive_light"
        ]
        
        for op_id in operators_to_check:
            if hasattr(bpy.ops, op_id.split('.')[0]) and hasattr(getattr(bpy.ops, op_id.split('.')[0]), op_id.split('.')[1]):
                print(f"✅ Operator available: {op_id}")
            else:
                print(f"❌ Operator missing: {op_id}")
                return False
        
        # Check utils functions
        from hdri_light_studio.utils import kelvin_to_rgb, create_light_shape
        
        # Test Kelvin conversion
        test_rgb = kelvin_to_rgb(6500)
        print(f"🌡️  6500K → RGB: {test_rgb}")
        
        # Test light shape creation
        coords_x, coords_y, values = create_light_shape('CIRCLE', 50, 100, 100, 1.0, (1.0, 0.8, 0.6))
        print(f"💡 Light shape created: {len(coords_x)} pixels")
        
        print("\n🎉 All tests passed! HDRI Light Studio is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hdri_light_studio()
    sys.exit(0 if success else 1)
