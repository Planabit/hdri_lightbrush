<div align="center">
  <img src="hdri_lightbrush/img/HDRI lightbrush.png" alt="HDRI LightBrush Logo" width="400"/>
  
  # HDRI LightBrush v1.0.0
  
  **3D HDRI painting addon for Blender with real-time sphere preview**
</div>

## Features

- **3D Paint on Sphere**: Paint directly on a preview sphere in the 3D viewport
- **Real-time Preview**: See HDRI changes instantly on the sphere surface  
- **Blender Brush Integration**: Uses native Blender brushes (radius, strength, falloff)
- **Spacing-based Painting**: Matches Blender's native paint behavior
- **Stroke Buffer**: No paint accumulation within strokes
- **World Background**: Apply painted HDRI as world environment

## Core Functionality
- **Real-time 2D Canvas**: Interactive HDRI painting with instant feedback
- **Empty Canvas Creation**: Generate 2K (2048x1024) and 4K (4096x2048) HDRI canvases
- **Custom Canvas Sizes**: Create canvases with user-defined dimensions
- **HDRI Loading**: Load existing HDRI files (.exr, .hdr, .jpg, .png)
- **Panel-embedded Display**: View and edit HDRI directly within Blender panels

## Requirements

- Blender 4.2+
- Python 3.11+ (bundled with Blender)

## Installation 

1. Download `hdri_lightbrush_....zip` from `dist/` folder
2. Open Blender → Edit → Preferences → Add-ons
3. Click "Install from Disk" and select the zip file
4. Enable "HDRI LightBrush" addon

## Quick Start

1. Open 3D Viewport, press N to show sidebar
2. Go to "HDRI LightBrush" tab
3. Click "New Canvas" to create 2K or 4K HDRI
4. Click "Add Sphere" to create preview sphere
5. Click "Set Background" to apply to world
6. Paint on the sphere with left mouse button
7. Configure brush in Image Editor sidebar (Radius, Strength, Hardness)

## Modules

```
hdri_lightbrush/
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
3. **Set World** → Apply HDRI as scene background
4. **Paint** → Click and drag on sphere to paint lights

## Build

```bash
python tools/build_and_install_hdri_lightbrush.py
```

Output: `dist/hdri_lightbrush_....zip`

## Support & Development

HDRI LightBrush is **free and open-source** software. If you find it useful, consider supporting development:

### ☕ Support via Donations
- **Ko-fi**: [ko-fi.com/tamaslaszlo](https://ko-fi.com/tamaslaszlo) - One-time donations
- **Patreon**: [patreon.com/planabit](https://patreon.com/planabit) - Monthly support & early access
- **GitHub Sponsors**: [github.com/sponsors/Planabit](https://github.com/sponsors/Planabit) - Support development

### 🚀 Custom Development
Need additional features or custom modifications?

- **Hourly Rate**: $50-80/hour (depending on complexity)
- **Feature Requests**: Contact via [planabit@gmail.com](mailto:planabit@gmail.com?subject=HDRI%20LightBrush%20-%20Feature%20Request)
- **Priority Support**: Available for Patreon supporters

### 📣 Roadmap & Feature Voting
- Check the [GitHub Issues](https://github.com/Planabit/hdri_lightbrush/issues) for planned features
- Vote with 👍 on features you'd like to see prioritized
- Suggest new features in [Discussions](https://github.com/Planabit/hdri_lightbrush/discussions)

## License

MIT License - See [LICENSE](LICENSE) file for details


