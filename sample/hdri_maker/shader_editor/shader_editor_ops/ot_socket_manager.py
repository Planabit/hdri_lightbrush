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

from ...custom_property_groups.socket.socket_callback import EnumSocketStore
from ...dictionaries.dictionaries import socket_colors
from ...exaconv import get_ngprop, get_sckprop
from ...exaproduct import Exa
from ...ops_and_fcs.socket_utility import change_socket_type
from ...utility.text_utils import draw_info
from ...utility.utility import remove_duplicate_consecutive, redraw_all_areas, safety_eval
from ...utility.utility_4 import get_ng_inputs, get_socket_index, remove_ng_socket


class HDRIMAKER_OT_socket_manager(Operator):
    bl_idname = Exa.ops_name + "socket_manager"
    bl_label = "Socket icon manager"
    bl_options = {'INTERNAL', 'UNDO'}

    options: bpy.props.StringProperty()
    tag: bpy.props.StringProperty()

    repr_node_group: bpy.props.StringProperty()
    repr_socket: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        options = properties.options

        if options == 'REMOVE_SOCKET':
            desc = "Remove the current socket"
        elif options == 'CHANGE_SOCKET_TYPE':
            desc = "Confirm the change of the selected socket"
        elif options in ['HIDE_LIST_MAX', 'HIDE_LIST_MIN']:
            desc = "Check and solve that everything is ok"
        elif options in ['CLOSE_SOCKETS', 'DISCLOSE_SOCKETS']:
            desc = "Close or open all sockets in the panel"
        elif options in ['RECTIFY_MUTE_NODE_LIST_FALSE', 'RECTIFY_MUTE_NODE_LIST_TRUE']:
            desc = "Check that the list is ok"
        elif options == 'SET_API_ENUM':
            desc = "Use Min and Max value as range in the enumeration of the Enum property options"
        return desc

    def execute(self, context):

        if self.options == 'REMOVE_SOCKET':
            socket = safety_eval(self.repr_socket)
            remove_ng_socket(socket)

        elif self.options == 'CHANGE_SOCKET_TYPE':
            socket = safety_eval(self.repr_socket)
            node_tree = socket.id_data
            ngProp = get_ngprop(node_tree)
            s_type = ngProp.NodeSocketType
            if socket_colors().get(s_type):
                print("Cerco di cambiare il socket, ecco il socket: ", socket)
                change_socket_type(socket, s_type)

        elif self.options in ['HIDE_LIST_MAX', 'HIDE_LIST_MIN']:
            # Serve per pulire la lista di idx dei socket da includere nell'hide
            socket = safety_eval(self.repr_socket)
            sckProp = get_sckprop(socket)
            idx = get_socket_index(socket)

            string = sckProp.api_hide_prop_if_min if self.options == 'HIDE_LIST_MIN' else sckProp.api_hide_prop_if_max
            before_min = sckProp.api_hide_prop_if_min
            before_max = sckProp.api_hide_prop_if_max

            def purge(string):
                string = ''.join([i for i in string if i.isdigit() or i == ","])
                string = remove_duplicate_consecutive(string, ",")

                if string.endswith(","): string = string[:-1]
                if string.startswith(","): string = string[1:]
                return string

            string = purge(string)

            if str(idx) in string.split(","):
                string = ''.join([i for i in string if i != str(idx)])
                string = purge(string)

            if self.options == 'HIDE_LIST_MAX': sckProp.api_hide_prop_if_max = string
            if self.options == 'HIDE_LIST_MIN': sckProp.api_hide_prop_if_min = string

            if before_min == sckProp.api_hide_prop_if_min and before_max == sckProp.api_hide_prop_if_max:
                text = "Everything is ok"
            else:
                text = "Compilation errors have been corrected"

            draw_info(text, "Info", 'INFO')

        elif self.options in ['DISCLOSE_SOCKETS', 'CLOSE_SOCKETS']:
            node_tree = safety_eval(self.repr_node_group)
            ng_inputs = get_ng_inputs(node_tree)
            for idx, input in enumerate(ng_inputs):
                sckProp = get_sckprop(input)
                sckProp.show_socket_menu = True if self.options == 'DISCLOSE_SOCKETS' else False

        elif self.options == 'SET_API_ENUM':
            socket = safety_eval(self.repr_socket)
            sckProp = get_sckprop(socket)
            socket.default_value = 1

            if socket.min_value != 1:
                text = "The Min Value must be set to 1"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if socket.max_value < 2:
                text = "The Max Value must be greater than 1"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if socket.max_value > 10:
                text = "The Max Value must be less than 10"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            real_idx_in_use = []
            for idx in range(socket.min_value, socket.max_value + 1):
                sckProp.self_id_idx = idx
                real_idx_in_use.append(idx)
                if str(idx) not in [i.idx for i in sckProp.api_collection_idx]:
                    item = sckProp.api_collection_idx.add()
                    item.idx = str(idx)

            for item in reversed(sckProp.api_collection_idx):
                if int(item.idx) not in real_idx_in_use:
                    for idx, X_item in enumerate(sckProp.api_collection_idx):
                        if X_item.idx == item.idx:
                            sckProp.api_collection_idx.remove(idx)
                            break

            mem_id = str(sckProp).split()[-1]
            enum_item = getattr(EnumSocketStore, mem_id)
            sckProp.api_enum_items = enum_item[0][0]
            mem_id_reset = mem_id + "_reset"
            setattr(EnumSocketStore, mem_id_reset, True)

        redraw_all_areas()

        # elif options in ['RECTIFY_MUTE_NODE_LIST_FALSE', 'RECTIFY_MUTE_NODE_LIST_TRUE']:
        #     # TODO: Non credo serva per il momento, serve per correggere la lista di nodi da metter in muto in base all'operatore booleano
        #     node_tree = bpy.data.node_groups[self.node_groups]
        #     ngProp = get_ngprop(node_tree)
        #     socket = node_tree.inputs[self.group_inputs_idx]
        #     sckProp = get_sckprop(socket)
        #
        #     if options == 'RECTIFY_MUTE_NODE_LIST_FALSE':
        #         text = sckProp.api_bool_mute_nodes_if_true
        #     elif options == 'RECTIFY_MUTE_NODE_LIST_TRUE':
        #         text = sckProp.api_bool_mute_nodes_if_false
        #
        #     list_of_node_name = text.split("//")
        #     for name in list_of_node_name:
        #         if node_tree.nodes.get(name):

        return {'FINISHED'}
