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
from bpy.props import StringProperty
from bpy.types import Operator

from ..color_lab_ui import colorlab_panel
from ...exaconv import get_sckprop, get_objprop
from ...exaproduct import Exa
from ...utility.utility import wima, safety_eval


class HDRIMAKER_OT_color_lab(Operator):
    """Color Lab Menu"""

    bl_idname = Exa.ops_name+"color_lab"
    bl_label = "Color Lab"
    bl_options = {'INTERNAL', 'UNDO'}

    options: StringProperty()

    repr_socket: StringProperty()
    repr_n_socket: StringProperty()

    def execute(self, context):
        scn = context.scene
        colabProp = scn.hdri_maker_colorlab_scene_prop

        if self.options == 'ASSIGN_TO_SOCKET':
            n_input = safety_eval(self.repr_n_socket)
            n_input.default_value = colabProp.color_lab_example

        elif self.options == 'ASSIGN_TO_PAINT':
            socket = safety_eval(self.repr_socket)
            sckProp = get_sckprop(socket)
            sckProp.rgb_paint = colabProp.color_lab_example

        elif self.options == 'LIGHT_STUDIO':
            light_holder = [o for o in scn.objects if get_objprop(o).object_id_name == 'LIGHT_HOLDER']
            for o in light_holder:

                o.data.color = colabProp.color_lab_example[0:3]

        return {'FINISHED'}

    def invoke(self, context, event):

        return wima().invoke_props_dialog(self, width=400)

    def draw(self, context):
        colorlab_panel(self, context)
