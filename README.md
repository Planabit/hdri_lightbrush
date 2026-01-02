# HDRI Light Studio v1.0.0

**3D HDRI painting addon for Blender with real-time sphere preview**

## Features

- **3D Paint on Sphere**: Paint directly on a preview sphere in the 3D viewport
- **Real-time Preview**: See HDRI changes instantly on the sphere surface  
- **Blender Brush Integration**: Uses native Blender brushes (radius, strength, falloff)
- **Spacing-based Painting**: Matches Blender's native paint behavior
- **Stroke Buffer**: No paint accumulation within strokes
- **World Background**: Apply painted HDRI as world environment

## Requirements

- Blender 4.2+
- Python 3.11+ (bundled with Blender)

## Installation

1. Download `hdri_light_studio_1.0.0.zip` from `dist/` folder
2. Open Blender → Edit → Preferences → Add-ons
3. Click "Install from Disk" and select the zip file
4. Enable "HDRI Light Studio" addon

## Quick Start

1. Open 3D Viewport, press N to show sidebar
2. Go to "HDRI Studio" tab
3. Click "New Canvas" to create 2K or 4K HDRI
4. Click "Add Sphere" to create preview sphere
5. Paint on the sphere with left mouse button
6. Configure brush in Image Editor sidebar (Radius, Strength, Hardness)
7. Click "Set Background" to apply to world

## Modules

```
hdri_light_studio/
├── __init__.py              # Addon registration
├── properties.py            # Canvas properties
├── operators.py             # Canvas operators  
├── ui.py                    # Main panel
├── continuous_paint_handler.py  # 3D painting system
├── sphere_tools.py          # Sphere creation/material
├── simple_paint.py          # 2D painting setup
├── hdri_save.py             # Load/save HDRI
├── world_properties.py      # World settings
├── world_operators.py       # World operators
├── utils.py                 # Color utilities
└── geometry/                # Sphere geometry
```

## Workflow

1. **Create Canvas** → Empty HDRI image (2K/4K)
2. **Add Sphere** → Transparent preview sphere around camera
3. **Paint** → Click and drag on sphere to paint lights
4. **Set World** → Apply HDRI as scene background

## Build

```bash
python tools/build_and_install_hdri_light_studio.py
```

Output: `dist/hdri_light_studio_1.0.0.zip`

## License

MIT

### Light Painting / Fény Festés
- **Brush Tool**: Select brush and click `Start Painting`
- **Shape Tools**: Place circle, square, or rectangle lights
- **Temperature Control**: Set Kelvin temperature (1000K-40000K)
- **Intensity**: Control light brightness and falloff

## � Technical Requirements / Technikai KövetelményekMIT
