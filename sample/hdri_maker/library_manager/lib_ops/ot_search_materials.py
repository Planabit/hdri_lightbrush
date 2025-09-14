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
import os

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ..categories_enum import get_mats_categories
from ..get_library_utils import current_lib, risorse_lib
from ..main_pcoll_attributes import set_winman_main_preview
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...utility.text_utils import draw_info
from ...utility.utility import wima

def search_cat_materials(self, context):
    cls = HDRIMAKER_OT_SearchMaterials

    scn = context.scene
    scnProp = get_scnprop(scn)

    if scnProp.libraries_selector == cls.last_materials_switch:
        return cls.search_mat_list
    else:
        print("search_cat_materials - update")
        cls.search_mat_list.clear()


    cls.last_materials_switch = scnProp.libraries_selector

    mats_categories = get_mats_categories()

    special_categories = ['Tools']

    mat_list = []
    for idx, (folder, t, d, i, identifier) in enumerate(mats_categories["categories"]):
        choose_dir = os.path.join(current_lib() if folder not in special_categories else risorse_lib(), folder)
        for fn in os.listdir(choose_dir):
            folder_path = os.path.join(choose_dir, fn)
            if os.path.isdir(folder_path) and not fn.startswith("."):
                if not mats_categories["tagged"] or fn in mats_categories["tagged"]:  # Condizione sotto tag
                    mat_list.append((str(idx) + "'SpLiT'" + fn))

    mat_list.sort()
    maximum = 0
    for idx, item in enumerate(mat_list):
        if len(item) > maximum:
            maximum = len(item)
        cls.search_mat_list.append((item, item.split("'SpLiT'")[1], "", idx))

    return cls.search_mat_list


class HDRIMAKER_OT_SearchMaterials(Operator):
    bl_idname = Exa.ops_name+"searchmaterials"
    bl_label = "Search:"
    bl_property = "search_mat"
    bl_options = {'INTERNAL'}

    search_mat: EnumProperty(name="search_mat", description="", items=search_cat_materials)
    search_mat_list = []
    last_materials_switch = None

    @classmethod
    def description(cls, context, properties):
        return "Search material from current library"

    def execute(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        mats_categories = get_mats_categories()

        cat_index = int(self.search_mat.split("'SpLiT'")[0])
        mat_name = self.search_mat.split("'SpLiT'")[1]
        sub_text_cat = sub_text_mat = ""
        try:
            scnProp.up_category = mats_categories["categories"][cat_index][0]
        except:
            sub_text_cat = " the category " + mats_categories["categories"][cat_index][0]

        try:
            set_winman_main_preview(mat_name)
        except:
            sub_text_mat = " the material " + mat_name

        if sub_text_cat or sub_text_mat:
            text = "I could not find"
            if sub_text_cat: text += sub_text_cat
            if sub_text_mat: text += sub_text_mat
            draw_info(text, "Info", 'INFO')
        return {'FINISHED'}

    def invoke(self, context, event):
        wima().invoke_search_popup(self)
        return {'FINISHED'}
