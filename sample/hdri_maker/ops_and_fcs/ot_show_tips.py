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
#  Copyright 2021(C) Andrea Donati
from bpy.props import StringProperty
from bpy.types import Operator

from ..exaconv import get_sckprop
from ..exaproduct import Exa
from ..icons.interfaceicons import get_icon
from ..utility.text_utils import wrap_text
from ..utility.utility import safety_eval


def draw_socket_tips(self, context, string, socket, docs_key):
    def draw(self, context):
        col = self.layout.column(align=True)
        wrap_text(col, string, None, 130, None, "")
        sckProp = get_sckprop(socket)
        if docs_key:
            col.separator()
            docs = col.operator(Exa.ops_name + "docs_helper",
                                text="Extreme PBR Online Manual",
                                icon_value=get_icon("extreme_addons_32"))

            docs.docs_key = docs_key

    context.window_manager.popup_menu(draw, title="Tips", icon='URL')

class HDRIMAKER_OT_show_tips(Operator):
    bl_idname = Exa.ops_name + "show_tips"
    bl_label = "Show Value Tips"
    bl_options = {'INTERNAL'}

    repr_socket: StringProperty()

    @classmethod
    def description(cls, context, properties):
        socket = safety_eval(properties.repr_socket)
        return socket.name

    def execute(self, context):
        socket = safety_eval(self.repr_socket)
        sckProp = get_sckprop(socket)
        text = sckProp.api_bool_description
        docs_key = sckProp.docs_key
        draw_socket_tips(self, context, text, socket, docs_key)
        return {'FINISHED'}
