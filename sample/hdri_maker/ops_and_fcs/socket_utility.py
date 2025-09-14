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
from ..exaconv import get_ngprop
from ..utility.dictionaries import socket_types, socket_forbidden
from ..utility.utility import get_addon_preferences, hide_unide_unused_sockets
from ..utility.utility_4 import get_socket_index, is_ng_input, is_ng_output, set_active_socket, new_ng_socket, \
    ng_move_socket, remove_ng_socket


def hide_unide_sockets(mat):
    addon_prefs = get_addon_preferences()
    for node in mat.node_tree.nodes:
        bool = False if addon_prefs.show_sockets else True
        hide_unide_unused_sockets(node, bool)
        if node.type == "GROUP" and node.node_tree and get_ngprop(node.node_tree).self_tag:
            node.show_options = True if addon_prefs.show_options else False


def change_socket_type(socket, socket_type):
    # Funzione che sostituisce il socket vecchio con quello scelto Itera a tutti i nodi Input e Output del gruppo

    node_tree = socket.id_data
    nodes = node_tree.nodes
    links = node_tree.links

    socket_idx = get_socket_index(socket)

    inputs_nodes = [n for n in node_tree.nodes if n.type == "GROUP_INPUT"]
    output_nodes = [n for n in node_tree.nodes if n.type == "GROUP_OUTPUT"]

    link_list = []

    if is_ng_input(socket):
        new_socket = new_ng_socket(node_tree, socket_type=socket_type, socket_name=socket.name, in_out="INPUT")
        for node in inputs_nodes:
            output = node.outputs[socket_idx]
            if output.is_linked:
                for link in output.links:
                    to_idx = get_socket_index(link.to_socket)
                    link_list.append((node, socket_idx, link.to_node, to_idx))

        ng_move_socket(new_socket, socket_idx)

    if is_ng_output(socket):
        new_socket = new_ng_socket(node_tree, socket_type=socket_type, socket_name=socket.name, in_out="OUTPUT")
        for node in output_nodes:
            input = node.inputs[socket_idx]
            if input.is_linked:
                for link in input.links:
                    from_idx = get_socket_index(link.from_socket)
                    link_list.append((link.from_node, from_idx, node, socket_idx))


        ng_move_socket(new_socket, socket_idx)


    for link in link_list:
        from_node = link[0]
        from_idx = link[1]
        to_node = link[2]
        to_idx = link[3]
        links.new(from_node.outputs[from_idx], to_node.inputs[to_idx])


    remove_ng_socket(socket)
    set_active_socket(new_socket)

    return new_socket


def enum_socket_type(self, context):
    list = []
    for idx, item in enumerate(socket_types()):
        if item not in socket_forbidden():
            name = item.replace("NodeSocket", "")
            list.append((item, name, "", idx))

    return list
