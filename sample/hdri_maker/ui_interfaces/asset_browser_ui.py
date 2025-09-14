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


# Create panel into asset browser:

class HDRIMAKER_PT_AssetBrowser(bpy.types.Panel):
    bl_label = "Materials"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'UI'
    bl_category = "HDRi Maker"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        mat_lib = context.preferences.addons['material_library'].preferences
        if mat_lib.material_library_path:
            layout.label(text=mat_lib.material_library_path)
        else:
            layout.label(text="No path set")

        layout.operator('material_library.create_json_material_library_register')

        layout.separator()

        layout.prop(mat_lib, 'material_library_path')
