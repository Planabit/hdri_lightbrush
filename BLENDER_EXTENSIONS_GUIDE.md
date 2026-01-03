# Blender Extensions Submission Guide

## Checklist before submission

### ✅ Required Files
- [x] `hdri_lightbrush/__init__.py` with proper `bl_info`
- [x] `LICENSE` file (MIT)
- [x] `README.md` with documentation
- [x] All Python files properly formatted

### ✅ bl_info Requirements
```python
bl_info = {
    "name": "HDRI LightBrush",
    "author": "Tamas Laszlo (planabit@gmail.com)",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > HDRI LightBrush",
    "description": "HDRI editor with real-time 3D painting on sphere preview",
    "category": "Lighting",
    "doc_url": "https://github.com/Planabit/hdri_lightbrush",
    "tracker_url": "https://github.com/Planabit/hdri_lightbrush/issues",
    "support": "COMMUNITY",
}
```

### ✅ Package Structure
```
hdri_lightbrush_1.0.0.zip
└── hdri_lightbrush/
    ├── __init__.py
    ├── operators.py
    ├── properties.py
    ├── ui.py
    ├── utils.py
    ├── continuous_paint_handler.py
    ├── hdri_save.py
    ├── simple_paint.py
    ├── sphere_tools.py
    ├── world_operators.py
    ├── world_properties.py
    └── geometry/
        ├── __init__.py
        └── geometry_factory.py
```

## Submission Steps

### 1. Create Account
- Go to [extensions.blender.org](https://extensions.blender.org/)
- Sign in with Blender ID
- Complete profile

### 2. Prepare Package
```bash
# Build the addon
python tools/build_and_install_hdri_lightbrush.py

# Package is created in: dist/hdri_lightbrush_1.0.0.zip
```

### 3. Fill Extension Form

**Basic Info:**
- Name: `HDRI LightBrush`
- Tagline: `Professional HDRI environment editor - Paint on world sphere for precise studio lighting`
- Category: `Lighting`
- Tags: `hdri`, `lighting`, `environment`, `studio`, `painting`

**Description:**
```markdown
Professional HDRI environment lighting editor. Paint directly on the inner surface of a world-representing sphere for unprecedented precision in lighting control.

## Perfect For
- Creating custom studio lighting setups from scratch
- Fine-tuning existing HDRI environments  
- Precise control over individual light sources and highlights
- Professional product visualization and rendering workflows

## Key Features
- 🎨 Direct 3D painting on sphere inner surface (world representation)
- ⚡ Real-time environment updates with live preview
- 🖌️ Full Blender brush system integration
- 📐 2K/4K canvas support with custom resolutions
- 💾 Professional HDRI export (.exr, .hdr, .jpg, .png)
- 🔄 Intuitive 3-step workflow: Canvas → Sphere → World

## Use Cases
- Product photography lighting simulation
- Architectural visualization
- Character/vehicle studio renders
- Custom environment map creation
- HDRI touch-up and enhancement

## Quick Start
1. Open 3D Viewport sidebar (N key)
2. Go to "HDRI LightBrush" tab
3. Click "New Canvas" (2K or 4K)
4. Start painting with your favorite brushes!

## Support
Free and open-source (MIT License)
- GitHub: [github.com/Planabit/hdri_lightbrush](https://github.com/Planabit/hdri_lightbrush)
- Support: [ko-fi.com/tamaslaszlo](https://ko-fi.com/tamaslaszlo)
```

**Media:**
- Upload 2-5 screenshots showing:
  1. Main UI panel
  2. Sphere preview with painted HDRI
  3. 2D canvas editor
  4. Final render result
- Optional: Add video tutorial link

**Links:**
- Website: `https://github.com/Planabit/hdri_lightbrush`
- Documentation: `https://github.com/Planabit/hdri_lightbrush#readme`
- Issue Tracker: `https://github.com/Planabit/hdri_lightbrush/issues`
- Support: `https://ko-fi.com/tamaslaszlo` (optional)

### 4. Upload Package
- Upload `dist/hdri_lightbrush_1.0.0.zip`
- Wait for validation (usually 1-2 days)
- Address any review feedback

### 5. After Approval
- Extension will be listed on extensions.blender.org
- Users can install via Blender 4.2+ Extensions menu
- You'll receive notifications for reviews and issues

## Updating the Extension

When releasing a new version:

1. Update version in `__init__.py`:
```python
"version": (1, 1, 0),  # Increment version
```

2. Build new package:
```bash
python tools/build_and_install_hdri_lightbrush.py
```

3. Upload new version to extensions.blender.org

4. Create GitHub release tag:
```bash
git tag -a v1.1.0 -m "Version 1.1.0"
git push origin v1.1.0
```

## Tips for Success

- ✅ Clear, concise description
- ✅ High-quality screenshots/videos
- ✅ Active GitHub repository
- ✅ Responsive to user feedback
- ✅ Regular updates
- ⚠️ Avoid over-promotion in description
- ⚠️ Don't promise paid features in free version

## Monetization

Blender Extensions allows optional donation links:
- Add in extension metadata (support URL)
- Include in README
- Add Support panel in addon UI (already implemented)
- Be transparent about being free & open-source
