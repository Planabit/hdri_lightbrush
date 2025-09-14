#   #
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version
#    of the License, or (at your option) any later version.
#   #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#   #
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software Foundation,
#    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#   #
#   Copyright 2024(C) Andrea Donati
import bpy

from .utility_4 import new_ng_socket
from ..exaconv import get_ndprop
from ..utility.utility import copy_attributes


def get_links_dict(node_tree):
    """Return a dictionary with the links of the node tree, example of return:
    {'0': { 'from_node_name': 'NodeName', 'from_socket_index': 0, 'to_node_name': 'NodeName', 'to_socket_index': 0 }   }"""

    links_dict = {}
    links = node_tree.links
    for idx, l in enumerate(links):
        from_socket_index = list(l.from_node.outputs).index(l.from_socket)
        to_socket_index = list(l.to_node.inputs).index(l.to_socket)

        links_dict[idx] = {"from_node_name": l.from_node.name,
                           "from_socket_index": from_socket_index,
                           "to_node_name": l.to_node.name,
                           "to_socket_index": to_socket_index}

    return links_dict


def copy_node_tree(from_node_tree, to_node_tree):
    """Copy the node tree from one node tree to another, this function copy the entire node tree, with they nodes, and links"""

    old_links = get_links_dict(from_node_tree)

    for old_node in from_node_tree.nodes:
        for idx, i in enumerate(old_node.inputs):
            if not i.is_linked:
                continue
        new_node = to_node_tree.nodes.new(old_node.bl_idname)

        # In this case, if the node is a ColorRamp, we need to create/copy the elements of the color ramp
        if old_node.type == 'VALTORGB':
            copy_color_ramp_elements(old_node, new_node)

        copy_attributes(get_ndprop(old_node), get_ndprop(new_node))
        copy_attributes(old_node, new_node)

        if old_node.type in ['REROUTE']:
            continue

        for idx, i in enumerate(old_node.inputs):
            if not hasattr(i, 'default_value'):
                continue
            new_node.inputs[idx].default_value = i.default_value

    for key, link in old_links.items():
        from_socket = to_node_tree.nodes[link["from_node_name"]].outputs[link["from_socket_index"]]
        to_socket = to_node_tree.nodes[link["to_node_name"]].inputs[link["to_socket_index"]]
        to_node_tree.links.new(from_socket, to_socket)


def copy_color_ramp_elements(from_cr, to_cr):
    """Copy color ramp elements from from_ct to to_cr"""
    # Note: the color ramp elements need to be having at least one element.
    # for element in to_cr.color_ramp.elements:
    #     to_cr.color_ramp.elements.remove(element)
    from_elements = from_cr.color_ramp.elements
    to_elements = to_cr.color_ramp.elements

    # Remove all elements except the first one from the Color Ramp node to be a copy of the Color Ramp node from
    for idx, element in enumerate(to_elements):
        if idx == 0:
            continue
        to_elements.remove(element)

    # Now we have to create the same number of elements of the Color Ramp node from, to the Color Ramp node to
    for idx, element in enumerate(from_elements):
        if idx == 0:
            continue
        to_elements.new(position=element.position)

    # Now we can copy the color and alpha values to the Color Ramp node to, because the elements are in the same order:
    for idx, element in enumerate(from_elements):
        to_elements[idx].color = element.color
        to_elements[idx].alpha = element.alpha


def create_group_from_node_tree(id_data):

    node_tree = id_data.node_tree
    node_group = bpy.data.node_groups.new(id_data.name, 'ShaderNodeTree')
    copy_node_tree(node_tree, node_group)
    node_group.name = id_data.name

    links = node_group.links
    nodes = node_group.nodes

    # Get the node output from the node group, because it is a copy of the node_tree, the node output is not the same
    # ('OUTPUT_WORLD' or 'OUTPUT_MATERIAL') is because the user can for an error create a world with a material node output

    output_node = next((n for n in nodes if n.type == ('OUTPUT_WORLD' or 'OUTPUT_MATERIAL') if n.inputs[0].is_linked),
                       None)

    if not output_node:
        return {}

    if not output_node.inputs[0].is_linked:
        return {}

    background_node = output_node.inputs[0].links[0].from_node
    nodes.remove(output_node)

    # Create node_tree node input:
    nodes_input = nodes.new('NodeGroupInput')
    # Create node_tree node output:
    nodes_output = nodes.new('NodeGroupOutput')

    shader_output = new_ng_socket(node_group, socket_type="NodeSocketShader", socket_name="Shader", in_out='OUTPUT')
    links.new(background_node.outputs[0], nodes_output.inputs[0])

    return {'node_group': node_group, 'nodes_input': nodes_input, 'nodes_output': nodes_output}
