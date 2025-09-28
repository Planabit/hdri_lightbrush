# HDRI Light Studio - KeyShot-Style HDRI Editor for Blender

**Professional 2D HDRI painting system with real-time interactive editing capabilities**

> 🎨 **Goal**: Create a KeyShot-like HDRI editing experience directly within Blender panels
> 
> 🖱️ **Features**: Real-time mouse painting + shape-based light placement tools
> 
> �️ **Lighting**: Variable intensity and color temperature light source painting

## ✨ Key Features

### 🎯 Core Functionality
- **Real-time 2D Canvas**: Interactive HDRI painting with instant feedback
- **Empty Canvas Creation**: Generate 2K (2048x1024) and 4K (4096x2048) HDRI canvases
- **Custom Canvas Sizes**: Create canvases with user-defined dimensions
- **HDRI Loading**: Load existing HDRI files (.exr, .hdr, .jpg, .png)
- **Panel-embedded Display**: View and edit HDRI directly within Blender panels

### 🔥 KeyShot-Inspired Tools
- **Interactive Light Placement**: Click and drag light positioning
- **Temperature Control**: Kelvin-based color temperature (1000K-40000K)
- **Brush System**: Configurable size, intensity, and falloff controls
- **Shape Library**: Circle, square, and rectangle light placement tools
- **Modal Painting**: Real-time mouse-based light painting

### 🏗️ Technical Architecture  
- **Panel-embedded Canvas**: Integrated directly into Blender's UI system
- **Template Image Display**: Professional HDRI viewing with editing capabilities
- **Modular Design**: Clean separation of rendering, properties, and UI
- **Automated Installation**: One-click installer for easy setup
- **Blender 4.2+ Ready**: Modern API compatibility with future-proofing

## � Project Structure

```
hdri_light_studio/                    # Main addon directory
├── __init__.py                       # Addon registration & metadata
├── properties/                       # Property group definitions
│   └── __init__.py                   # Canvas, light, and tool properties  
├── operators/                        # Interactive operators
│   └── __init__.py                   # Modal painting and shape placement
├── canvas/                           # GPU-based rendering system
│   └── __init__.py                   # HDRICanvas class with paint methods
├── ui/                              # User interface panels
│   └── __init__.py                   # Main panel with tool controls
├── utils/                           # Utility functions
│   └── __init__.py                   # Color conversion, file handling
└── archive/                         # Previous implementation attempts
    ├── hdri_utils.py        # HDRI kezelés
    └── color_utils.py       # Szín számítások
```

## 🚀 Installation / Telepítés

### 🎯 Quick Install / Gyors Telepítés
1. **Automated Installer** / Automatikus telepítő:
   ```bash
   cd tools
   python install_hdri_light_studio.py
   ```
   Or run / Vagy futtasd: `quick_install_hdri_light_studio.bat`

2. **Manual Installation** / Kézi telepítés:
   - Open Blender / Nyisd meg a Blendert
   - Go to `Edit > Preferences > Add-ons`
   - Click `Install from Disk` / Kattints az `Install from Disk`-re
   - Select the `hdri_light_studio` folder / Válaszd ki a `hdri_light_studio` mappát
   - Enable the addon / Engedélyezd az addont

3. **Access the Panel** / Panel elérése:
   - `3D Viewport > Sidebar (N) > HDRI Studio` tab

## 🎨 Usage / Használat

### Canvas Creation / Canvas Létrehozás
- **Quick Presets**: `2K` (2048x1024) or `4K` (4096x2048) buttons
- **Custom Size**: Set width/height and click `New`
- **Load HDRI**: Import existing HDRI files

### Light Painting / Fény Festés
- **Brush Tool**: Select brush and click `Start Painting`
- **Shape Tools**: Place circle, square, or rectangle lights
- **Temperature Control**: Set Kelvin temperature (1000K-40000K)
- **Intensity**: Control light brightness and falloff

## � Technical Requirements / Technikai Követelmények

- **Blender 4.2+** (recommended / ajánlott)
- **Python 3.11+**
- **NumPy** (automatically installed / automatikusan települ)
- **Windows/macOS/Linux** support

## 📝 Development Status / Fejlesztési Állapot

### ✅ Completed Features / Kész Funkciók
- [x] Modular addon architecture
- [x] Canvas creation (2K/4K/custom)
- [x] HDRI loading and display
- [x] Panel-embedded UI
- [x] Modal painting operators
- [x] Automated installer
- [x] Temperature-based color system

### 🔄 In Progress / Fejlesztés Alatt
- [ ] Real-time pixel painting
- [ ] Advanced brush system
- [ ] Shape-based light placement
- [ ] Undo/Redo functionality

### 📋 Planned Features / Tervezett Funkciók
- [ ] KeyShot export compatibility
- [ ] Advanced shape library
- [ ] Gradient light tools
- [ ] Real-time preview rendering

## 🐛 Troubleshooting / Hibaelhárítás

### "Source code string cannot contain null bytes" Error
**Problem**: File corruption during development can introduce null bytes.

**Solution**: 
```bash
# Check for null bytes
[System.IO.File]::ReadAllBytes("file.py") | Where-Object { $_ -eq 0 } | Measure-Object

# Reinstall clean version
python tools/install_hdri_light_studio.py
```

### Addon Not Loading in Blender
1. **Check Blender version**: Requires Blender 4.2+
2. **Clear Blender cache**: Restart Blender completely
3. **Manual installation**: Use Blender's "Install from Disk" feature
4. **Check console**: Look for Python errors in Blender's console

### Canvas Not Displaying
- Ensure addon is **enabled** in preferences
- Try creating a **new canvas** (2K/4K buttons)
- Check that `Show Canvas` is **enabled** in Advanced panel 
- HD preview display with navigation arrows
- Professional UI layout matching sample addon pattern
- Support for HDR and EXR file formats
- template_icon_view implementation for large image display

## Support

This addon was created to provide a clean, professional HDRI editing interface within Blender.

## License
MIT
