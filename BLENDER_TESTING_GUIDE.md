# HDRI Light Studio - Blender Testing Guide

## 🎯 Quick Setup Steps

### 1. Open Blender
- Start Blender 4.2+ 
- Delete the default cube (optional)

### 2. Enable the Addon
- Go to `Edit > Preferences > Add-ons`
- Search for "HDRI Light Studio"  
- Check the checkbox to enable it
- Click "Save Preferences"

### 3. Find the Panel
- In 3D Viewport, press `N` to open Sidebar
- Look for "HDRI Studio" tab
- Click on it to see the panel

## 🔧 Expected Panel Layout

```
HDRI Studio Tab
├── KeyShot-style HDRI Editor
├── Canvas
│   ├── [2K] [4K] (preset buttons)
│   ├── W: 2048  H: 1024 (size controls)
│   └── [New] [Load] [Clear] (operations)
├── Tools
│   ├── Tool: Brush/Shape dropdown
│   └── [Start Painting] or shape buttons
├── Light Properties
│   ├── Size: 50.0
│   ├── Intensity: 1.0
│   ├── Softness: 0.5
│   ├── ☑ Use Temperature
│   └── Temperature: 6500K
└── Canvas Display
    └── Shows active HDRI if created
```

## 🧪 Test Canvas Creation

1. Click the **2K** button
2. You should see:
   - Info message: "Created 2K canvas (2048x1024)"
   - Active image name appears
   - Canvas Display section shows the image

## 🐛 Troubleshooting

### Panel Not Visible
- Check if addon is **enabled** in Preferences
- Look in **all tabs** in the Sidebar (sometimes tabs get rearranged)
- Try **restarting Blender** completely
- Check Blender **Console** for error messages

### Buttons Don't Work
- Check Blender Console for Python errors
- Verify all addon files were copied correctly
- Try **disabling and re-enabling** the addon

### Canvas Not Created
- Check if `bpy.data.images` contains new images after clicking 2K/4K
- Verify `utils.create_default_hdri` function exists
- Check Scene properties: `bpy.context.scene.hdrils_props`

## 📋 Diagnostic Script

If the panel doesn't appear, copy this into Blender's Text Editor and run it:

```python
import bpy
import addon_utils

# Check if addon exists
for mod in addon_utils.modules():
    if hasattr(mod, 'bl_info') and 'hdri' in mod.bl_info.get('name', '').lower():
        print(f"Found: {mod.bl_info['name']}")
        print(f"Enabled: {addon_utils.check(mod.__name__)[1]}")

# Check scene properties
if hasattr(bpy.context.scene, 'hdrils_props'):
    print("✅ Scene properties OK")
else:
    print("❌ Scene properties missing")

# Check panels
for cls in bpy.types.Panel.__subclasses__():
    if hasattr(cls, 'bl_idname') and 'HDRILS' in cls.bl_idname:
        print(f"✅ Panel: {cls.bl_label}")
```

## 💡 Success Indicators

✅ Panel appears in Sidebar under "HDRI Studio" tab
✅ Clicking 2K creates a new image in Blender
✅ Canvas Display shows the created image
✅ All buttons are clickable and show info messages

---

**Need help?** Check the Blender Console (Window > Toggle System Console) for error messages.