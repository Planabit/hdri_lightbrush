"""
Rename all 'hemisphere' references to 'sphere' throughout the codebase
"""
import os
import re
from pathlib import Path

# Root directory
root_dir = Path(r"e:\Projects\HDRI_editor\hdri_light_studio")

# Replacement mappings (order matters!)
replacements = [
    # Class names
    ("HemisphereProperties", "SphereProperties"),
    ("HDRI_PT_hemisphere_panel", "HDRI_PT_sphere_panel"),
    ("HDRI_OT_hemisphere_add", "HDRI_OT_sphere_add"),
    ("HDRI_OT_hemisphere_remove", "HDRI_OT_sphere_remove"),
    ("HDRI_OT_hemisphere_paint_setup", "HDRI_OT_sphere_paint_setup"),
    
    # bl_idname values
    ("hdri_studio.hemisphere_add", "hdri_studio.sphere_add"),
    ("hdri_studio.hemisphere_remove", "hdri_studio.sphere_remove"),
    ("hdri_studio.hemisphere_paint_setup", "hdri_studio.sphere_paint_setup"),
    
    # Object names
    ('"HDRI_Hemisphere"', '"HDRI_Preview_Sphere"'),
    ("'HDRI_Hemisphere'", "'HDRI_Preview_Sphere'"),
    ('"HDRI_Hemisphere_Handler"', '"HDRI_Preview_Sphere_Handler"'),
    ("'HDRI_Hemisphere_Handler'", "'HDRI_Preview_Sphere_Handler'"),
    ('"HDRI_Hemisphere_Material"', '"HDRI_Preview_Sphere_Material"'),
    ("'HDRI_Hemisphere_Material'", "'HDRI_Preview_Sphere_Material'"),
    
    # Geometry type enum
    ("'CLOSED_HEMISPHERE'", "'HALF_SPHERE'"),
    ('"CLOSED_HEMISPHERE"', '"HALF_SPHERE"'),
    ("CLOSED_HEMISPHERE", "HALF_SPHERE"),
    ("'Closed Hemisphere'", "'Half Sphere (180°)'"),
    ("'Hemisphere with rounded bottom edge'", "'Half sphere for 180° HDRI'"),
    
    # Property names
    ("hemisphere_props", "sphere_props"),
    ("hemisphere_name", "sphere_name"),
    ("hemisphere_scale", "sphere_scale"),
    ("geometry_type", "sphere_type"),
    
    # Function names
    ("update_hemisphere_scale_callback", "update_sphere_scale_callback"),
    ("create_hemisphere_handler", "create_sphere_handler"),
    ("load_dome_as_hemisphere", "load_dome_as_sphere"),
    ("setup_hemisphere_material", "setup_sphere_material"),
    ("assign_hemisphere_to_material_coordinates", "assign_sphere_to_material_coordinates"),
    ("assign_image_to_hemisphere_material", "assign_image_to_sphere_material"),
    ("create_painting_hemisphere_material", "create_painting_sphere_material"),
    ("setup_hemisphere_collection", "setup_sphere_collection"),
    ("setup_hemisphere_parenting", "setup_sphere_parenting"),
    ("setup_hemisphere_for_painting", "setup_sphere_for_painting"),
    ("create_closed_hemisphere", "create_half_sphere"),
    
    # Variable names
    ("hemisphere_obj", "sphere_obj"),
    ("hemisphere_center", "sphere_center"),
    ("hemi_props", "sphere_props_obj"),
    ("_hemisphere", "_sphere"),
    
    # Comments and descriptions (generic)
    ("hemisphere", "sphere"),
    ("Hemisphere", "Sphere"),
    ("HEMISPHERE", "SPHERE"),
]

# Files to process
py_files = list(root_dir.rglob("*.py"))

print(f"Found {len(py_files)} Python files to process")

for py_file in py_files:
    try:
        # Read file
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Only write if changed
        if content != original_content:
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {py_file.relative_to(root_dir)}")
    
    except Exception as e:
        print(f"❌ Error processing {py_file}: {e}")

print("\n✅ Renaming complete!")
print("\nNext step: Rename file 'hemisphere_tools.py' to 'sphere_tools.py'")
