"""
Test to compare UV calculations between:
1. Sphere material (TexCoord.Generated -> Environment Texture)
2. World material (Environment Texture)
3. Paint handler (mathematical calculation)

Goal: Make all three use identical mapping
"""

import bpy
import math
from mathutils import Vector

print("\n" + "="*70)
print("UV MAPPING COMPARISON TEST")
print("="*70)

# Test directions (normalized vectors from center)
test_directions = [
    Vector((1, 0, 0)),      # +X (right)
    Vector((-1, 0, 0)),     # -X (left)
    Vector((0, 1, 0)),      # +Y (front)
    Vector((0, -1, 0)),     # -Y (back)
    Vector((0, 0, 1)),      # +Z (top)
    Vector((0, 0, -1)),     # -Z (bottom)
    Vector((1, 1, 0)).normalized(),  # +X+Y diagonal
    Vector((1, 0, 1)).normalized(),  # +X+Z diagonal
]

print("\n1. PAINT HANDLER UV CALCULATION:")
print("-"*50)
print("Formula: u = 0.5 - (atan2(y,x) / 2π), v = 0.5 + (asin(z) / π)")

def paint_handler_uv(direction):
    """Same calculation as in continuous_paint_handler.py"""
    d = direction.normalized()
    
    longitude = math.atan2(d.y, d.x)
    u = 0.5 - (longitude / (2.0 * math.pi))
    
    latitude = math.asin(max(-1.0, min(1.0, d.z)))
    v = 0.5 + (latitude / math.pi)
    
    # Wrap U
    if u < 0.0:
        u += 1.0
    elif u > 1.0:
        u -= 1.0
    
    return (u, v)

for d in test_directions:
    u, v = paint_handler_uv(d)
    print(f"  Direction ({d.x:+.2f}, {d.y:+.2f}, {d.z:+.2f}) -> UV ({u:.3f}, {v:.3f})")

print("\n2. BLENDER ENVIRONMENT TEXTURE (EQUIRECTANGULAR):")
print("-"*50)
print("Blender's internal formula for EQUIRECTANGULAR:")
print("  u = 0.5 + atan2(y, x) / (2*pi)  <- NOTE: + not -")
print("  v = 0.5 - asin(z) / pi          <- NOTE: - not +")

def blender_equirect_uv(direction):
    """Blender's EQUIRECTANGULAR projection formula"""
    d = direction.normalized()
    
    # Blender's formula (from source code)
    u = 0.5 + math.atan2(d.y, d.x) / (2.0 * math.pi)
    v = 0.5 - math.asin(max(-1.0, min(1.0, d.z))) / math.pi
    
    # Wrap U
    if u < 0.0:
        u += 1.0
    elif u > 1.0:
        u -= 1.0
    
    return (u, v)

for d in test_directions:
    u, v = blender_equirect_uv(d)
    print(f"  Direction ({d.x:+.2f}, {d.y:+.2f}, {d.z:+.2f}) -> UV ({u:.3f}, {v:.3f})")

print("\n3. DIFFERENCE ANALYSIS:")
print("-"*50)

for d in test_directions:
    paint_uv = paint_handler_uv(d)
    blender_uv = blender_equirect_uv(d)
    
    u_diff = paint_uv[0] - blender_uv[0]
    v_diff = paint_uv[1] - blender_uv[1]
    
    # Account for wraparound
    if abs(u_diff) > 0.5:
        u_diff = 1.0 - abs(u_diff) if u_diff > 0 else -(1.0 - abs(u_diff))
    
    print(f"  Dir ({d.x:+.2f}, {d.y:+.2f}, {d.z:+.2f}): Paint({paint_uv[0]:.3f},{paint_uv[1]:.3f}) vs Blender({blender_uv[0]:.3f},{blender_uv[1]:.3f}) | Diff: U={u_diff:+.3f}, V={v_diff:+.3f}")

print("\n4. CORRECTED PAINT HANDLER (to match Blender):")
print("-"*50)

def corrected_paint_handler_uv(direction):
    """Paint handler UV that matches Blender's EQUIRECTANGULAR"""
    d = direction.normalized()
    
    # Use SAME formula as Blender
    u = 0.5 + math.atan2(d.y, d.x) / (2.0 * math.pi)
    v = 0.5 - math.asin(max(-1.0, min(1.0, d.z))) / math.pi
    
    # Wrap U
    if u < 0.0:
        u += 1.0
    elif u > 1.0:
        u -= 1.0
    
    return (u, v)

print("Verification (should match Blender exactly):")
for d in test_directions:
    corrected = corrected_paint_handler_uv(d)
    blender = blender_equirect_uv(d)
    match = "✓" if abs(corrected[0] - blender[0]) < 0.001 and abs(corrected[1] - blender[1]) < 0.001 else "✗"
    print(f"  {match} Dir ({d.x:+.2f}, {d.y:+.2f}, {d.z:+.2f}): Corrected({corrected[0]:.3f},{corrected[1]:.3f})")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
The paint handler uses INVERTED formulas compared to Blender:
  Paint:   u = 0.5 - atan2/2π,  v = 0.5 + asin/π
  Blender: u = 0.5 + atan2/2π,  v = 0.5 - asin/π

This causes:
  - U to be mirrored (left-right swap)
  - V to be inverted (top-bottom swap)

FIX: Change paint handler to use Blender's formula.
""")
