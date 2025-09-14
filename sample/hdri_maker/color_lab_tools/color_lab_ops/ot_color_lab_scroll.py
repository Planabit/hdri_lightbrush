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
from bpy.types import Operator

from ..colorlab_func import get_color_lab_items
from ...exaproduct import Exa


class HDRIMAKER_OT_ColorLabScroll(Operator):
    """Scroll Colors"""

    bl_idname = Exa.ops_name+"colorlabscroll"
    bl_label = "Previous color"
    bl_options = {'INTERNAL', 'UNDO'}

    options: bpy.props.StringProperty()
    destination: bpy.props.StringProperty()

    def execute(self, context):

        colabProp = context.scene.hdri_maker_colorlab_scene_prop

        colors_list = get_color_lab_items('color_list')

        current_idx = next((i[3] for i in colors_list if i[0] == colabProp.color_lab_name), None)

        if self.options == 'PREVIUOS':
            previous_color = next((i[0] for i in colors_list if i[3] == current_idx - 1), None)
            if previous_color: colabProp.color_lab_name = previous_color

        if self.options == 'NEXT':
            next_color = next((i[0] for i in colors_list if i[3] == current_idx + 1), None)
            if next_color: colabProp.color_lab_name = next_color

        return {'FINISHED'}
