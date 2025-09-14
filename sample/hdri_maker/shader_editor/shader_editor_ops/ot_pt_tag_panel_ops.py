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

from ...dictionaries.dictionaries import node_tag
from ...exaconv import get_ndprop, get_sckprop
from ...exaproduct import Exa
from ...utility.utility import wima, safety_eval


class HDRIMAKER_OT_tag_panel_utils(Operator):

    bl_idname = Exa.ops_name+"tag_panel_utils"
    bl_label = "Tag Panel"
    bl_options = {'INTERNAL', 'UNDO'}

    options: bpy.props.StringProperty()
    tag: bpy.props.StringProperty()

    repr_socket: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        options = properties.options
        desc = ""
        if options == 'TAG_SOCKET':
            desc = "Tag For the socket"
        elif options == 'TAG_NODE':
            desc = "Tags for texture nodes. Useful for handling PBR type materials, Extreme PBR tools will recognize and manage this also to switch to Uv Mapping, Box Mapping Etc."
        return desc

    def invoke(self, context, event):
        return wima().invoke_props_dialog(self, width=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):

        layout = self.layout

        ob = context.object

        def draw_tag_buttons(tag_type, socket, node_tree):
            col = layout.column(align=True)
            row = col.row(align=True)
            # ???tag_list = node_tag if options == 'TAG_NODE' else node_tag_util
            for idx, tag in enumerate(node_tag()):
                if idx % 4 == 0: row = col.row(align=True)

                if tag_type == 'TAG_NODE':
                    ndProp = get_ndprop(node_tree.nodes.active)
                    depresStat = True if ndProp.node_tag == tag else False
                    nodes_utility = row.operator(Exa.ops_name+"tag_node_socket", text=tag.replace("X_PBR_", ""),
                                                depress=depresStat)
                    nodes_utility.options = tag_type
                    nodes_utility.tag = tag

                elif tag_type == 'TAG_SOCKET':
                    sckProp = get_sckprop(socket)
                    depresStat = True if sckProp.tag_socket == tag else False
                    socket_manager = row.operator(Exa.ops_name+"tag_node_socket", text=tag, depress=depresStat)
                    socket_manager.options = tag_type
                    socket_manager.tag = tag
                    socket_manager.repr_socket = repr(socket)


        if self.options == 'TAG_NODE':

            node_tree = context.space_data.edit_tree
            if not node_tree.nodes.active:
                layout.label(text="No node selected", icon='INFO')
                return

            draw_tag_buttons('TAG_NODE', None, node_tree)

        elif self.options == 'TAG_SOCKET':
            socket = safety_eval(self.repr_socket)
            node_tree = socket.id_data
            draw_tag_buttons('TAG_SOCKET', socket, node_tree)
