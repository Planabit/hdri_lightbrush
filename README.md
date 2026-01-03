<div align="center">
  <img src="hdri_lightbrush/img/HDRI lightbrush.png" alt="HDRI LightBrush Logo" width="400"/>
  
  # HDRI LightBrush v1.0.0
  
  **Professional HDRI environment lighting editor for Blender**
  
  Paint directly on the inner surface of a world-representing sphere in 3D viewport for precise lighting control. Perfect for creating and fine-tuning studio lighting setups.
</div>

## Features

### Core Concept
HDRI LightBrush revolutionizes environment lighting workflow by allowing you to **paint directly on the inner surface of a sphere that represents your world environment**. This intuitive approach provides unprecedented precision for creating and fine-tuning studio lighting setups.

### Key Features
- **Direct 3D Painting**: Paint on the world-representing sphere's inner surface in real-time
- **Precision Lighting Control**: Fine-tune individual light sources and highlights with pixel-perfect accuracy
- **Studio Lighting Workflow**: Create professional studio setups from scratch or modify existing HDRIs
- **Real-time Preview**: See environment changes instantly reflected on the sphere surface
- **Blender Brush Integration**: Full support for native Blender brushes (radius, strength, falloff, spacing)
- **World Environment Sync**: Apply painted HDRI directly as world background

## Technical Capabilities
- **Canvas Creation**: Generate 2K (2048x1024) and 4K (4096x2048) HDRI canvases
- **Custom Resolutions**: Create canvases with user-defined dimensions
- **HDRI Loading**: Import existing HDRI files (.exr, .hdr, .jpg, .png) for editing
- **Professional Export**: Save edited HDRIs in industry-standard formats
- **Integrated Workflow**: Edit HDRI directly within Blender panels alongside your 3D scene

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
- **Patreon**: [patreon.com/TamasLaszlo](https://patreon.com/TamasLaszlo) - Monthly support & early access

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


