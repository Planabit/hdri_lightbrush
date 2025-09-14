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

from bpy.props import StringProperty, IntProperty
from bpy.types import Operator

from ...exaconv import get_sckprop
from ...exaproduct import Exa
from ...utility.utility import safety_eval


class HDRIMAKER_OT_icon_button(Operator):
    bl_idname = Exa.ops_name+"icon_button"
    bl_label = "Icon Button"
    bl_options = {'INTERNAL', 'UNDO'}

    options: StringProperty()
    repr_socket: StringProperty()
    socket_enum_idx: IntProperty()
    icon: StringProperty()


    @classmethod
    def description(cls, context, properties):
        if properties.options == 'ICON_TRUE':
            desc = "Choose the icon for when the button is True"
        elif properties.options == 'ICON_FALSE':
            desc = "Choose the icon for when the button is False"
        elif properties.options == 'REMOVE_ICON_TRUE':
            desc = "Remove the icon for the button True"
        elif properties.options == 'REMOVE_ICON_FALSE':
            desc = "Remove the icon for the button False"
        elif properties.options == 'ADD_ICON_TO_ENUM_SOCKET':
            desc = "Choose the icon for this Enum Property"
        elif properties.options == 'REMOVE_ICON_FROM_ENUM_SOCKET':
            desc = "Remove icon From this Enum Property"
        return desc

    def execute(self, context):

        socket = safety_eval(self.repr_socket)
        sckProp = get_sckprop(socket)

        if self.options in ['ICON_TRUE', 'ICON_FALSE']:
            if self.options == 'ICON_TRUE':
                sckProp.api_icon_true = self.icon
            elif self.options == 'ICON_FALSE':
                sckProp.api_icon_false = self.icon

        elif self.options == 'REMOVE_ICON_FALSE':
            sckProp.api_icon_false = ""
        elif self.options == 'REMOVE_ICON_TRUE':
            sckProp.api_icon_true = ""

        elif self.options == 'ADD_ICON_TO_ENUM_SOCKET':
            sckProp.api_collection_idx[self.socket_enum_idx].icon = self.icon

        elif self.options == 'REMOVE_ICON_FROM_ENUM_SOCKET':
            sckProp.api_collection_idx[self.socket_enum_idx].icon = 'NONE'

        return {'FINISHED'}
