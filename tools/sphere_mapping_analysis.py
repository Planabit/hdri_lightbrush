"""
Test to verify sphere material uses same mapping as Blender Environment Texture
"""

import bpy
import math
from mathutils import Vector

print("\n" + "="*70)
print("SPHERE MATERIAL MAPPING ANALYSIS")
print("="*70)

# Get sphere
sphere = bpy.data.objects.get("HDRI_Preview_Sphere")
if not sphere:
    print("ERROR: No sphere found!")
else:
    print(f"\nSphere: {sphere.name}")
    print(f"  Location: {sphere.location}")
    print(f"  Scale: {sphere.scale}")
    print(f"  Bounds: {sphere.dimensions}")
    
    # Check material
    if sphere.data.materials:
        mat = sphere.data.materials[0]
        print(f"\nMaterial: {mat.name}")
        print(f"  Blend method: {mat.blend_method}")
        print(f"  Use nodes: {mat.use_nodes}")
        
        if mat.use_nodes:
            print("\nNodes:")
            for node in mat.node_tree.nodes:
                print(f"  - {node.type}: {node.name}")
                if node.type == 'TEX_ENVIRONMENT':
                    print(f"      Projection: {node.projection}")
                    if node.image:
                        print(f"      Image: {node.image.name}")
                if node.type == 'TEX_COORD':
                    print(f"      Object: {node.object}")
            
            print("\nLinks:")
            for link in mat.node_tree.links:
                print(f"  {link.from_node.name}.{link.from_socket.name} -> {link.to_node.name}.{link.to_socket.name}")

print("\n" + "="*70)
print("UV COORDINATE COMPARISON")
print("="*70)
print("""
Issue: TexCoord.Generated uses object bounding box coordinates.
       For a sphere at origin with radius 5, the Generated coordinates
       will be based on -5 to +5 range, which the Environment Texture
       then interprets.

       The Environment Texture EQUIRECTANGULAR expects a DIRECTION vector,
       not a position! It normalizes the input internally.

       So for a vertex at position (5, 0, 0):
       - Generated gives: (0.5, 0.5, 0.5) - normalized to bounding box
       - Environment Texture treats this as direction (0.5, 0.5, 0.5) 
       - After normalization: (0.577, 0.577, 0.577) - NOT what we want!

       The paint handler calculates direction from sphere center to hit point,
       then uses Blender's EQUIRECTANGULAR formula.

SOLUTION OPTIONS:
1. Use TexCoord.Object (local position) and normalize it
2. Use math to calculate direction from position
3. Use TexCoord.Normal or TexCoord.Reflection

Let's check what TexCoord.Generated actually does:
""")

# Test what Generated output gives for a sphere
# We need to use a driver or script to access this
print("\n" + "="*70)
print("RECOMMENDED FIX")
print("="*70)
print("""
For sphere interior viewing with EQUIRECTANGULAR mapping:

OPTION A - Use normal direction (simplest):
  TexCoord.Normal -> Environment Texture
  
  Normal output gives the surface normal direction which for a sphere
  at the origin IS the direction from center to surface!
  
OPTION B - Use Object coordinate (requires normalization):
  TexCoord.Object -> Vector Math (Normalize) -> Environment Texture
  
OPTION C - Use Generated with scale compensation:
  If sphere has default scale, Generated should work for UV mapping
  but NOT for equirectangular direction!
  
The sample dome uses complex math because it's a CUBE, not a sphere.
For an actual sphere, we can use Normal directly!
""")
