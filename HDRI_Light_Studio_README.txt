================================================================================
  🎨 HDRI Light Studio v1.1 - Blender Addon
================================================================================

Professional 360° HDRI painting and editing tool for Blender 4.2+

✨ FEATURES:
-----------
✅ 360° Sphere Preview - Full spherical HDRI preview with scaling
✅ Real-time Texture Painting - GPU accelerated, ZERO lag
✅ Calibrated UV Mapping - <65px accuracy for precise painting
✅ UV Grid Overlay - Visual grid in image editor for alignment
✅ Multiple Canvas Sizes - 2K, 4K, 8K support
✅ Native Blender Tools - Full access to all Blender brushes
✅ Complete Save/Load System - Quick Save, Save As, and Load HDRI
✅ Sphere Scaling - Real-time preview size adjustment
✅ World Background Integration - Direct world shader setup

📦 INSTALLATION:
----------------
1. Open Blender (4.2 or newer)
2. Go to: Edit → Preferences → Add-ons
3. Click "Install..." button (top right)
4. Navigate to and select: HDRI_Light_Studio_v1.0.zip
5. Click "Install Add-on"
6. Enable the addon by checking the checkbox
7. Save Preferences (bottom left)

🎯 QUICK START:
---------------
1. Open 3D Viewport
2. Press 'N' to show sidebar
3. Find 'HDRI Studio' tab
4. Click "Create Canvas" (2K recommended for testing)
5. Click "Add Preview Sphere"
6. Start painting! (Automatic Texture Paint mode)

🖌️ PAINTING:
-------------
- LEFT MOUSE: Paint directly on sphere
- F: Adjust brush size (drag mouse)
- Shift+F: Adjust brush strength (drag mouse)
- X: Pick color from sphere
- Ctrl+Z: Undo
- All standard Blender brush settings work!

💾 WORKFLOW:
------------
1. Create Canvas → Choose size (2K/4K/8K)
2. Add Preview Sphere → Automatic paint mode
3. Adjust Sphere Size → Use scale slider for comfort
4. Paint your HDRI → Real-time preview with UV grid
5. Quick Save → Save progress instantly
6. Save As → Export with custom name/location
7. Load HDRI → Continue previous work or import existing HDRI

🎛️ UI CONTROLS:
----------------
MAIN PANEL:
- Canvas Size: Select 2K, 4K, or 8K resolution
- Create Canvas: Initialize new HDRI canvas
- Load HDRI: Import existing .exr or .hdr files
- Quick Save: Save to default location
- Save As: Choose custom save location
- Clear: Reset canvas to blank
- Load Different: Switch to another HDRI file

PREVIEW SPHERE PANEL:
- Type: Choose Sphere (360°) or Hemisphere (180°)
- Add Preview Sphere: Create sphere for painting
- Scale Slider: Adjust sphere size (0.1 - 10.0)
- Remove Sphere: Delete preview geometry

IMAGE EDITOR:
- UV Grid Overlay: Automatic grid for alignment
- Standard zoom/pan controls
- Real-time paint preview

⚙️ TECHNICAL DETAILS:
---------------------
- Calibrated UV Mapping: <65px accuracy
- GPU Accelerated Painting: 60+ FPS
- Native Texture Paint Mode: Zero blocking
- Supports: Full Sphere & Hemisphere geometry
- Canvas Formats: 2048x1024, 4096x2048, 8192x4096

🐛 TROUBLESHOOTING:
-------------------
Q: Addon not showing in sidebar?
A: Press 'N' in 3D Viewport, check 'HDRI Studio' tab

Q: Can't paint on sphere?
A: Make sure you're in Texture Paint mode (auto-enabled when adding sphere)

Q: Painting in wrong location?
A: This shouldn't happen - UV mapping is calibrated!
   If it does, report it as a bug.

Q: Lag when painting?
A: Try smaller canvas (2K instead of 4K)
   Close other Blender windows

📧 SUPPORT:
-----------
For questions, bug reports, or feature requests:
- Check the GitHub repository
- Open an issue with detailed description
- Include Blender version and steps to reproduce

🎓 TIPS:
--------
💡 Start with 2K canvas for fast iteration
💡 Use UV grid overlay for precise alignment
💡 Adjust sphere scale for comfortable painting distance
💡 Use symmetry painting (X/Y/Z) for quick results
💡 Save As different versions to experiment
💡 Load existing HDRIs and paint over them
💡 Combine with Blender's procedural textures
💡 Export as .exr for best quality (32-bit)
💡 Use "Quick Save" often to avoid losing work
💡 Larger canvas = more detail but slower painting

📜 LICENSE:
-----------
HDRI Light Studio v1.1
Copyright © 2025

This addon is provided as-is for educational and commercial use.

================================================================================
  Enjoy creating beautiful HDRIs! 🌟
================================================================================
