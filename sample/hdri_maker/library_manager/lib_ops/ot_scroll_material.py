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
from bpy.props import StringProperty
from bpy.types import Operator

from ..categories_enum import get_mats_categories
from ..k_size_enum import set_k_size
from ..main_pcoll import enum_material_previews
from ..main_pcoll_attributes import get_winman_main_preview, set_winman_main_preview
from ..textures_pcoll import enum_material_textures
from ..textures_pcoll_attributes import get_winman_texture_preview, set_winman_texture_preview
from ...exaconv import get_scnprop
from ...exaproduct import Exa


class HDRIMAKER_OT_ScrollMaterial(Operator):
    bl_idname = Exa.ops_name+"scrollmaterial"
    bl_label = "Smart Arrows"
    bl_options = {'INTERNAL'}

    options: StringProperty()

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if 'UP' == properties.options:
            desc = "Scroll the categories towards the beginning"
        elif 'DOWN' == properties.options:
            desc = "Scroll through the categories towards the end"
        elif 'LEFT' == properties.options:
            desc = "Scroll the materials towards the beginning"
        elif 'RIGHT' == properties.options:
            desc = "Scroll the materials towards the end"
        elif 'TEXTURE_LEFT' == properties.options:
            desc = "Scroll the image towards the beginning"
        elif 'TEXTURE_RIGHT' == properties.options:
            desc = "Scroll the image towards the end"
        return desc

    def execute(self, context):

        scn = context.scene
        scnProp = get_scnprop(scn)

        mats_categories = get_mats_categories()
        context_preview = get_winman_main_preview()

        if self.options in ['UP', 'DOWN']:
            category_index = next(
                (idx for idx, cat in enumerate(mats_categories["categories"]) if scnProp.up_category == cat[0]), 0)
            if self.options == 'UP':
                if scnProp.up_category != mats_categories["categories"][0][0]:
                    scnProp.up_category = mats_categories["categories"][category_index - 1][0]

            elif self.options == 'DOWN':
                if scnProp.up_category != mats_categories["categories"][-1][0]:
                    scnProp.up_category = mats_categories["categories"][category_index + 1][0]

            set_k_size(scnProp, context)

        elif self.options in ['LEFT', 'RIGHT']:
            preview_image_list = [(N, idx) for (N, n, d, id_n, idx) in enum_material_previews(self, context)]
            current_idx = next((idx for (N, idx) in preview_image_list if N == context_preview), None)

            if self.options == 'LEFT':
                if context_preview != preview_image_list[0][0]:
                    left = next((N for (N, idx) in preview_image_list if idx == (current_idx - 1)), None)
                    if left:
                        set_winman_main_preview(left)

            elif self.options == 'RIGHT':
                if context_preview != preview_image_list[0][-1]:
                    right = next((N for (N, idx) in preview_image_list if idx == (current_idx + 1)), None)
                    if right:
                        set_winman_main_preview(right)

        elif self.options in ['TEXTURE_LEFT', 'TEXTURE_RIGHT']:

            context_preview = get_winman_texture_preview()
            preview_image_list = enum_material_textures(self, context)

            current_idx = next((idx for (P, N, D, I, idx) in preview_image_list if P == context_preview), None)


            if self.options == 'TEXTURE_LEFT':
                if context_preview != preview_image_list[0][0]:
                    left = next((P for (P, N, D, I, idx) in preview_image_list if idx == (current_idx - 1)), None)
                    if left:
                        set_winman_texture_preview(left)

            elif self.options == 'TEXTURE_RIGHT':
                if context_preview != preview_image_list[0][-1]:
                    right = next((P for (P, N, D, I, idx) in preview_image_list if idx == (current_idx + 1)), None)
                    if right:
                        set_winman_texture_preview(right)

        return {'FINISHED'}
