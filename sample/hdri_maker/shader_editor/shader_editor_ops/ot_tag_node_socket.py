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

from ...exaconv import get_sckprop, get_ndprop
from ...exaproduct import Exa
from ...utility.utility import safety_eval


class HDRIMAKER_OT_tag_node_socket(Operator):
    bl_idname = Exa.ops_name+"tag_node_socket"
    bl_label = "Tag Panel"
    bl_options = {'INTERNAL', 'UNDO'}

    options: bpy.props.StringProperty()
    tag: bpy.props.StringProperty()

    repr_socket: bpy.props.StringProperty()


    @classmethod
    def description(cls, context, properties):
        return properties.options

    def execute(self, context):

        if self.options == 'TAG_SOCKET':
            socket = safety_eval(self.repr_socket)
            sckProp = get_sckprop(socket)
            sckProp.tag_socket = self.tag

        if self.options == 'TAG_NODE':
            node_tree = context.space_data.edit_tree
            nodes = [n for n in node_tree.nodes if n.select]
            for n in nodes:
                ndProp = get_ndprop(n)
                ndProp.node_tag = self.tag

        return {'FINISHED'}
