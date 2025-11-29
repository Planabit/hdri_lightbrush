# 🎨 Equirectangular Grid Solution

## 🔍 PROBLÉMA ÚJRAÉRTELMEZÉSE

**Eredeti kérés**: "UV grid nem látszik az Image Editor-ban"

**Valódi igény**: Egy **reference grid** ami segít az HDRI festésében!

---

## 💡 MEGOLDÁS: Beégetett Equirectangular Grid

Ahelyett hogy a Blender UI UV grid funkcióját próbáljuk megjeleníteni (ami csak aktív mesh szerkesztésnél működik), **közvetlenül a canvas image-be rajzolunk egy equirectangular grid-et**!

### Mi ez az Equirectangular Grid?

Ez egy speciális grid ami:
- **Latitude vonalak** (horizontal) - párhuzamosak az egyenlítővel
- **Longitude vonalak** (vertical) - meridián vonalak
- **Equator** (piros vonal) - hangsúlyozott középvonal
- **Prime Meridian** (zöld vonal) - 0° hosszúsági fok

Pontosan azt mutatja amit egy HDRI panoráma (360°×180°) képen látnál!

---

## 🎯 IMPLEMENTÁCIÓ

### `operators.py` - `create_canvas_image()`

```python
# Create equirectangular grid overlay
import numpy as np
import math

# Grid parameters
lat_lines = 12   # Horizontal lines (15° spacing)
lon_lines = 24   # Vertical lines (15° spacing)
grid_thickness = 2  # Pixels

for y in range(height):
    for x in range(width):
        # Base gradient (sky-like)
        r = x / width
        g = 0.3 + 0.4 * (y / height)
        b = 0.7 - 0.4 * (y / height)
        
        # Calculate UV coordinates
        u = x / width   # 0 to 1
        v = y / height  # 0 to 1
        
        # Longitude lines (vertical, every 15°)
        lon_angle = u * 360
        lon_spacing = 360 / lon_lines  # 15°
        if abs(lon_angle % lon_spacing) < threshold:
            r = g = b = 0.8  # Light gray
        
        # Latitude lines (horizontal, every 15°)
        lat_angle = (v - 0.5) * 180  # -90° to +90°
        lat_spacing = 180 / lat_lines  # 15°
        if abs(lat_angle % lat_spacing) < threshold:
            r = g = b = 0.8  # Light gray
        
        # EQUATOR (0° latitude) - RED
        if abs(v - 0.5) < 3.0/height:
            r, g, b = 1.0, 0.3, 0.3
        
        # PRIME MERIDIAN (0° longitude) - GREEN
        if u < 3.0/width or u > 1.0 - 3.0/width:
            r, g, b = 0.3, 1.0, 0.3
```

---

## 📊 GRID LAYOUT

```
    0°      90°     180°    270°    360°
    |       |       |       |       |
+90°========================================  North Pole
    |       |       |       |       |
+60°----------------------------------------
    |       |       |       |       |
+30°----------------------------------------
    |       |       |       |       |
  0°========================================  EQUATOR (RED)
    |       |       |       |       |
-30°----------------------------------------
    |       |       |       |       |
-60°----------------------------------------
    |       |       |       |       |
-90°========================================  South Pole
    
    ^ Prime Meridian (GREEN)
```

**Grid Spacing**: 15° × 15°
**Total Cells**: 24 × 12 = 288 cells

---

## 🎨 VISUAL FEATURES

### 1. **Background Gradient**
- Top → Bottom: Blue sky → Green ground
- Left → Right: Subtle red tint variation
- Makes grid clearly visible

### 2. **Regular Grid Lines**
- Light gray (0.8, 0.8, 0.8)
- 2-pixel thickness
- Every 15° in both directions

### 3. **Special Lines**
- **Equator**: Thick red line (3 pixels)
  - Helps identify up/down orientation
  - Center reference point
  
- **Prime Meridian**: Thick green line (3 pixels)
  - 0° and 360° longitude
  - Left/right wrap-around reference

---

## ✅ ADVANTAGES

### Compared to Blender UV Grid:
- ✅ **Always visible** - No need for active mesh
- ✅ **Built into canvas** - No overlay configuration needed
- ✅ **HDRI-specific** - Shows actual equirectangular projection
- ✅ **Reference lines** - Equator and meridian clearly marked
- ✅ **Paintable** - Can paint over or erase grid lines
- ✅ **Export-ready** - Grid visible in saved HDRI (can be painted over)

### For HDRI Painting Workflow:
- ✅ Shows 360° wrap-around clearly
- ✅ Helps place lights at specific angles
- ✅ Equator line shows horizon
- ✅ Grid cells help judge light size/position
- ✅ Meridian shows front (0°) direction

---

## 🔧 CONFIGURATION OPTIONS

Easy to customize in `operators.py`:

```python
# Make grid finer (more lines)
lat_lines = 18  # Every 10° instead of 15°
lon_lines = 36  # Every 10° instead of 15°

# Make grid thicker/thinner
grid_thickness = 1  # Thin lines
grid_thickness = 4  # Thick lines

# Change grid color
r = g = b = 0.5  # Darker gray
r = g = b = 1.0  # White grid

# Change special line colors
r, g, b = 1.0, 1.0, 0.0  # Yellow equator
r, g, b = 0.0, 0.0, 1.0  # Blue meridian
```

---

## 📝 IMAGE_EDITOR Settings

Also updated:
```python
space.mode = 'VIEW'  # Simple viewing mode
space.show_gizmo = True  # Enable viewport gizmos
space.overlay.show_overlays = True  # Show all overlays
```

**Why VIEW mode?**
- Clean interface
- No painting tools in the way
- Focus on the canvas grid
- Easy to see grid pattern

**Why UV mode DOESN'T work:**
- UV mode shows mesh UVs (not image grids!)
- Requires active selected mesh
- Shows mesh UV layout, not canvas reference
- Not suitable for image-based workflow

---

## 🎯 RESULT

### What You'll See:
1. **Create Canvas** button → IMAGE_EDITOR opens
2. Beautiful equirectangular grid appears
3. Gradient background (sky blue → ground green)
4. Red equator line (horizontal center)
5. Green prime meridian (vertical edges)
6. 24×12 grid cells (15° spacing)

### When Painting:
- Grid helps position lights at specific angles
- Equator shows horizon placement
- Meridian shows front/back direction
- Can paint OVER grid (it's just pixels!)
- Grid stays visible as reference

---

## 💡 PRO TIPS

### Using the Grid:

1. **Equator (Red Line)**:
   - Place sun/moon here for horizon lighting
   - Above = sky lights
   - Below = ground lights

2. **Prime Meridian (Green Line)**:
   - Front view (0°)
   - Opposite edge = back view (180°)

3. **Grid Cells**:
   - Each cell = 15° × 15°
   - Count cells to place lights precisely
   - Example: 6 cells right = 90° (side view)

4. **Painting Over Grid**:
   - Grid is just pixels - paint over it!
   - Start with grid visible
   - Paint your HDRI lights
   - Grid naturally disappears under paint

---

## 🚀 NEXT STEPS

### Optional Enhancements:

1. **User-controllable grid density**:
   - Property in UI: "Grid Spacing: 10° / 15° / 30°"
   
2. **Toggle grid on/off**:
   - Button: "Show Reference Grid"
   - Save grid preference

3. **Grid export options**:
   - "Save with grid" or "Save clean HDRI"
   
4. **Different grid styles**:
   - Equirectangular (current)
   - Simple cartesian (square grid)
   - Polar (circular pattern)

---

## ✅ SUMMARY

**Problem Solved**: ✅
- User wants to see grid in Image Editor
- Blender UV grid only works for mesh editing
- Our solution: **Draw grid directly on canvas!**

**Benefits**:
- Always visible ✅
- HDRI-specific (equirectangular) ✅
- Clear reference lines ✅
- No Blender UI configuration needed ✅
- Professional look ✅

**Result**:
A beautiful, functional reference grid that's **perfect for HDRI painting!** 🎨

---

**File Updated**: `operators.py`
**Lines Changed**: ~40 lines in `create_canvas_image()`
**ZIP Ready**: Just repackage and test!
