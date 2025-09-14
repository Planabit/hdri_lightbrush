#   #
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version
#    of the License, or (at your option) any later version.
#   #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#   #
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software Foundation,
#    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#   #
#   Copyright 2024(C) Andrea Donati
import bpy

class ScnVar:
    empty_type_list = []
    light_types = []
    color_space = []


def enum_light_type(self, context):
    if ScnVar.light_types:
        return ScnVar.light_types

    for idx, key in  enumerate(bpy.types.Light.bl_rna.properties['type'].enum_items.keys()):
        if 'sun' in key.lower():
            continue
        ScnVar.light_types.append((key, key.replace("_", "").title(), ""))

    return ScnVar.light_types


def enum_empty_types(self, context):
    if ScnVar.empty_type_list:
        return ScnVar.empty_type_list

    for idx, key in  enumerate(bpy.types.Object.bl_rna.properties['empty_display_type'].enum_items.keys()):
        ScnVar.empty_type_list.append((key, key.replace("_", "").title(), ""))  # , eType, idx))

    return ScnVar.empty_type_list


def enum_material_shadow_method_items(self, context):
    # Return a list of items for the material shadow method
    shadow_method_items = []
    for key in bpy.types.Material.bl_rna.properties['shadow_method'].enum_items_static.keys():
        name = bpy.types.Material.bl_rna.properties['shadow_method'].enum_items[key].name
        description = bpy.types.Material.bl_rna.properties['shadow_method'].enum_items[key].description
        shadow_method_items.append((key, name, description))

    return shadow_method_items


def enum_material_blend_method_items(self, context):
    # Return a list of items for the material blend method
    blend_method_items = []
    for key in bpy.types.Material.bl_rna.properties['blend_method'].enum_items_static.keys():
        name = bpy.types.Material.bl_rna.properties['blend_method'].enum_items[key].name
        description = bpy.types.Material.bl_rna.properties['blend_method'].enum_items[key].description
        blend_method_items.append((key, name, description))
    return blend_method_items


def get_blender_icons():
    """Return the original blender icons"""
    icons = [icon_name for icon_name in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()
             if icon_name != "BRUSH_PAINT"]

    return icons

def enum_blender_colorspace(self, context):
    """Return the original blender colorspace"""
    if ScnVar.color_space:
        return ScnVar.color_space

    for key in bpy.types.Image.bl_rna.properties['colorspace_settings'].fixed_type.properties['name'].enum_items.keys():
        ScnVar.color_space.append((key, key, ""))

    # Searching for the key ("Linear", "Linear", "") if it exists, it will be the first element
    if ("Linear", "Linear", "") in ScnVar.color_space:
        ScnVar.color_space.insert(0, ScnVar.color_space.pop(ScnVar.color_space.index(("Linear", "Linear", ""))))

    return ScnVar.color_space

