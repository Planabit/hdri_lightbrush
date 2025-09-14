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
from bpy.types import PropertyGroup

from ...utility.utility_4 import get_ng_inputs
from ...exaconv import get_sckprop
from ...ops_and_fcs.socket_utility import change_socket_type
from ...utility.utility import retrieve_nodes, has_nodetree


class HdriMakerEnumSocketInt(PropertyGroup):
    idx: StringProperty(default='0')
    name: StringProperty(default="Insert Name")
    description: StringProperty(default="Insert Descriptions")
    icon: StringProperty(default='NONE')


procedural_texture = []


def get_socket_input_from_self(self, context):
    node_tree = self.id_data
    for idx, input in enumerate(get_ng_inputs(node_tree)):
        ndProp = get_sckprop(input)
        ndProp.self_id_idx = idx

    socket = None
    for idx, input in enumerate(get_ng_inputs(node_tree)):
        if get_sckprop(input).self_id_idx == self.self_id_idx:
            socket = input
            socket_idx = idx

    return {'node_tree': node_tree, 'current_socket': socket, 'socket_idx': socket_idx}



# def enum_int_socket(self, context):
#     if not self.enum_socket_reset:
#         return self.enum_socket_items
#     self.enum_socket_items.clear()
#     for idx, props in enumerate(self.api_collection_idx):
#         self.enum_socket_items.append((props.idx, props.name, props.description, props.icon, idx))
#
#     self.enum_socket_reset.clear()
#
#     return self.enum_socket_items

class EnumSocketStore:
    # Per evitare l'enum piu e piu volte
    to_popolate = True


def enum_int_socket(self, context):
    # Tutto sto casino, perchè le liste possono essere multiple,
    # e non si riesce a salvarle in un altra proprietà sckProp (Self)
    reset_mem_list_str = str(self).split()[-1] + "_reset"
    if not hasattr(EnumSocketStore, reset_mem_list_str):
        setattr(EnumSocketStore, reset_mem_list_str, True)

    reset_mem_list = getattr(EnumSocketStore, reset_mem_list_str)

    mem_id = str(self).split()[-1]
    if not hasattr(EnumSocketStore, mem_id):
        setattr(EnumSocketStore, mem_id, [])

    item_list = getattr(EnumSocketStore, mem_id)

    if reset_mem_list == False:
        return item_list

    item_list.clear()
    for idx, props in enumerate(self.api_collection_idx):
        item_list.append((props.idx, props.name, props.description, props.icon, idx))

    # aspe a cancellare , trovala nell' operatore che assegna i socket

    setattr(EnumSocketStore, reset_mem_list_str, False)

    return item_list


def update_enum_item_to_socket_idx(self, context):
    self_list = get_socket_input_from_self(self, context)
    node_tree = self_list.get('node_tree')
    current_socket = self_list.get('current_socket')
    socket_idx = self_list.get('socket_idx')

    mat = context.object.active_material

    node_list = retrieve_nodes(mat.node_tree)
    for n in node_list:
        if has_nodetree(n):
            if n.node_tree == node_tree:
                n.inputs[int(socket_idx)].default_value = int(self.api_enum_items)


def update_api_enum(self, context):
    self_list = get_socket_input_from_self(self, context)

    node_tree = self_list.get('node_tree')
    current_socket = self_list.get('current_socket')
    socket_idx = self_list.get('socket_idx')

    nodes = node_tree.nodes

    if current_socket.type == 'INT':
        return

    group_input_node = None
    for n in nodes:
        if n.type == 'GROUP_INPUT':
            if n.outputs[socket_idx].is_linked:
                group_input_node = n

    # to_socket = group_input_node.outputs[socket_idx].links[0].to_socket ???

    new_socket = change_socket_type(current_socket, 'NodeSocketInt')
    new_socket.min_value = 0
    new_socket.max_value = 3

    socketProp = get_sckprop(new_socket)
    if not socketProp.is_api_enum:
        socketProp.is_api_enum = True


def enum_procedural_texture(self, context):
    global procedural_texture
    if procedural_texture:
        return procedural_texture

    nodes = [node for node in bpy.types.ShaderNode.__subclasses__() if 'ShaderNodeTex' in node.bl_rna.identifier]
    tex_node_procedural = []
    for idx, node in enumerate(nodes):
        procedural_texture.append((node.bl_rna.identifier, node.bl_rna.name, "", idx))

    return procedural_texture

def update_api_bool_description(self, context):
    self_list = get_socket_input_from_self(self, context)
    node_tree = self_list.get('node_tree')
    current_socket = self_list.get('current_socket')
    socket_idx = self_list.get('socket_idx')

    tooltip = self.api_bool_description

    if hasattr(current_socket, 'description'):
        current_socket.description = tooltip


