import os
from pathlib import Path

addon_dir = Path(r"C:\Users\plana\AppData\Roaming\Blender Foundation\Blender\4.2\scripts\addons\hdri_light_studio")

print("="*70)
print("CHECKING BLENDER ADDON FILES")
print("="*70)
print(f"\nAddon directory: {addon_dir}")
print(f"Exists: {addon_dir.exists()}\n")

if addon_dir.exists():
    # List all Python files
    print("Python files:")
    for py_file in sorted(addon_dir.glob("*.py")):
        size = py_file.stat().st_size
        print(f"  {py_file.name:40s} {size:>8,} bytes")
    
    # Check ui.py specifically
    ui_file = addon_dir / "ui.py"
    print(f"\n{'='*70}")
    print("CHECKING ui.py FOR DEBUG SECTION")
    print("="*70)
    
    if ui_file.exists():
        content = ui_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        print(f"File size: {len(content):,} characters")
        print(f"Lines: {len(lines)}")
        
        # Search for debug-related lines
        print(f"\nSearching for debug-related code:")
        found_debug = False
        for i, line in enumerate(lines, 1):
            if any(marker in line for marker in ['draw_debug_points', 'Debug UV Tracking', 'start_debug_tracking']):
                found_debug = True
                print(f"  Line {i:3d}: {line.strip()}")
        
        if found_debug:
            print(f"\n✅ DEBUG SECTION FOUND!")
        else:
            print(f"\n❌ NO DEBUG SECTION FOUND!")
            print(f"\nShowing last 30 lines of ui.py:")
            for i, line in enumerate(lines[-30:], len(lines)-29):
                print(f"  {i:3d}: {line}")
    else:
        print(f"❌ ui.py NOT FOUND!")
else:
    print("❌ ADDON DIRECTORY NOT FOUND!")
    print(f"\nSearching for addon in addons directory...")
    addons_dir = addon_dir.parent
    if addons_dir.exists():
        print(f"Addons directory exists: {addons_dir}")
        print(f"Contents:")
        for item in addons_dir.iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}")

print("\n" + "="*70)
