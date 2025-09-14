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
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from ...exaconv import get_ngprop
from ...exaproduct import Exa
from ...utility.utility import safety_eval
from ...utility.utility_4 import ng_move_socket, get_socket_index, set_active_socket


class HDRIMAKER_OT_move_socket(Operator):
    bl_idname = Exa.ops_name+"move_socket"
    bl_label = "Move Socket"
    bl_options = {'INTERNAL', 'UNDO'}

    direction: EnumProperty(
        name="Direction",
        items=(
            ('UP', "Up", "Move socket Up"),
            ('DOWN', "Down", "Move socket Down"),
        ),
        default='UP',
    )
    repr_socket: StringProperty()

    @classmethod
    def description(cls, context, properties):
        if properties.direction == 'UP':
            desc = 'Move socket Up, This will affect the group node. Be careful if you have put a property of type "Hide" with the numbers of the properties to be hidden. These could change their position, therefore their number!'
        elif properties.direction == 'DOWN':
            desc = 'Move socket Down, This will affect the group node. Be careful if you have put a property of type "Hide" with the numbers of the properties to be hidden. These could change their position, therefore their number!'
        return desc

    def execute(self, context):

        socket = safety_eval(self.repr_socket)
        node_group = socket.id_data

        ngProp = get_ngprop(node_group)

        # ngProp.ng_util['last_active_socket'] = socket_idx #ngProp.last_active_socket = socket_idx
        if self.direction == 'UP':
            socket_idx = get_socket_index(socket, get_real_index=True)
            ng_move_socket(socket, socket_idx - 1)
            ngProp.ng_util['last_active_socket'] = socket_idx - 1
            set_active_socket(socket)
            socket_idx = get_socket_index(socket, get_real_index=True)


        if self.direction == 'DOWN':
            socket_idx = get_socket_index(socket, get_real_index=True)
            ng_move_socket(socket, socket_idx + 2)
            ngProp.ng_util['last_active_socket'] = socket_idx + 2
            set_active_socket(socket)
            socket_idx = get_socket_index(socket, get_real_index=True)

        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}
