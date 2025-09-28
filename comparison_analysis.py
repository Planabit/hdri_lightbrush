"""
Összehasonlítás: Sample Addon vs HDRI Editor implementáció

SAMPLE ADDON (ui_interfaces/draw_functions.py):
===============================================

previewRow.scale_y = addon_prefs.icons_preview_size                    # Dinamikus méretezés
left_row.scale_y = addon_prefs.icons_preview_size * 6                  # Nyilak 6x nagyobbak
right_row.scale_y = addon_prefs.icons_preview_size * 6                 # Nyilak 6x nagyobbak

previewRow.template_icon_view(wima(), wm_main_preview(), 
                             scale_popup=mat_preview_size,              # Popup méret: addon_prefs.icons_popup_size * 5 (VIEW_3D-ben)
                             show_labels=True if addon_prefs.show_labels else False)

HDRI EDITOR (javítás után):
==========================

preview_row.scale_y = addon_prefs.icons_preview_size                   # ✅ UGYANAZ
left_row.scale_y = addon_prefs.icons_preview_size * 6                  # ✅ UGYANAZ  
right_row.scale_y = addon_prefs.icons_preview_size * 6                 # ✅ UGYANAZ

preview_row.template_icon_view(hdri_properties, "hdri_preview_enum",
                              scale_popup=popup_size,                   # ✅ UGYANAZ (addon_prefs.icons_popup_size * 5)
                              show_labels=addon_prefs.show_labels)      # ✅ UGYANAZ

KULCSFONTOSSÁGÚ JAVÍTÁSOK:
=========================

❌ RÉGI (hibás):
- preview_row.scale_y = 8.0                    # Fix érték
- template_icon_view(..., scale=8.0, ...)     # Dupla méretezés!

✅ ÚJ (helyes):  
- preview_row.scale_y = addon_prefs.icons_preview_size  # Dinamikus (default: 1.5)
- template_icon_view(...) - nincs scale paraméter      # Csak scale_popup

PREFERENCIÁK:
============
- icons_preview_size: 1.5 (default, min: 0.5, max: 3.0)
- icons_popup_size: 1.5 (default, min: 0.5, max: 3.0)  
- show_labels: True (default)

A preview ablak mérete most már dinamikusan igazodik a preferenciákhoz,
pontosan úgy, mint a sample addonban!
"""

print("HDRI Editor vs Sample Addon - Implementáció összehasonlítás")
print("=" * 60)
print(__doc__)