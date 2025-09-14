#  #
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version
#   of the License, or (at your option) any later version.
#  #
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#  #
#  Copyright 2024(C) Andrea Donati

import bpy

from ..functions import check_shader_area_ok
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...library_manager.k_size_enum import get_k_size_list
from ...library_manager.main_pcoll_attributes import get_winman_main_preview, wm_main_preview
from ...library_manager.textures_pcoll_attributes import wm_texture_preview, get_winman_texture_preview
from ...utility.utility import get_addon_preferences, wima, get_filename_from_path


class HDRIMAKER_PT_TextureBrowser(bpy.types.Panel):
    bl_label = "Texture Browser"
    # bl_idname = "HDRIMAKER_PT_TextureBrowser"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HDRi Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return check_shader_area_ok(context)

    def draw(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        addon_prefs = get_addon_preferences()
        preview_mat_name = get_winman_main_preview()

        layout = self.layout
        col = layout.column(align=True)

        col.prop(scnProp, 'libraries_selector', text="Library")
        col.prop(scnProp, 'up_category', text="Category")

        box = col.box()
        colBox = box.column(align=True)
        colBox.operator(Exa.ops_name + "searchmaterials", text=preview_mat_name, emboss=False, icon='VIEWZOOM')
        k_size_list = get_k_size_list()
        if scnProp.k_size != 'NONE' and len(k_size_list['list']) > 1:
            kRow = colBox.row()
            kRow.prop(scnProp, 'k_size', expand=True)

        row_col_1 = col.row(align=True)
        col_1 = row_col_1.column(align=True)

        col_1.template_icon_view(wima(), wm_main_preview(), scale_popup=5, scale=6,
                                 show_labels=True if addon_prefs.show_labels else False)

        split = col_1.split(align=True)
        split_1 = split.column(align=True)
        split_1.operator(Exa.ops_name + "scrollmaterial", text="",
                         icon='TRIA_LEFT').options = 'LEFT'
        split_2 = split.column(align=True)
        split_2.operator(Exa.ops_name + "scrollmaterial", text="",
                         icon='TRIA_RIGHT').options = 'RIGHT'

        col_2 = row_col_1.column(align=True)
        col_2.operator(Exa.ops_name + "scrollmaterial", text="",
                       icon='TRIA_UP').options = 'UP'
        col_2.operator(Exa.ops_name + "scrollmaterial", text="",
                       icon='TRIA_DOWN').options = 'DOWN'

        col_3 = row_col_1.column(align=True)
        col_3.template_icon_view(wima(), wm_texture_preview(), show_labels=True, scale=6, scale_popup=6)
        split = col_3.split(align=True)
        split_1 = split.column(align=True)
        split_1.operator(Exa.ops_name + "scrollmaterial", text="",
                         icon='TRIA_LEFT').options = 'TEXTURE_LEFT'
        split_2 = split.column(align=True)
        split_2.operator(Exa.ops_name + "scrollmaterial", text="",
                         icon='TRIA_RIGHT').options = 'TEXTURE_RIGHT'

        box = col.box()
        colBox = box.column(align=True)
        filePath = get_winman_texture_preview()
        texture_name = get_filename_from_path(filePath)
        row = colBox.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=texture_name)

        row = col.row(align=True)
        row.scale_y = 2

        add = row.operator(Exa.ops_name + "importtexture", text="Add Texture", icon="ADD")
        add.options = "ADD_TEXTURE"

        replace = row.operator(Exa.ops_name + "importtexture", text="Replace Texture", icon="FILE_REFRESH")
        replace.options = "REPLACE_TEXTURE"


