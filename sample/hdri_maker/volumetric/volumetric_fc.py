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
from ..utility.utility_ops.store_node_dimension import get_node_dimensions

volumes = []


def enum_volumetric_groups(self, context):
    """Enumerate the Volumes Node Groups into the blendfile"""

    if volumes:
        return volumes

    from ..library_manager.get_library_utils import risorse_lib
    import os

    folder_path = os.path.join(risorse_lib(), "blendfiles", "volumes")

    for idx, file in enumerate(os.listdir(folder_path)):
        if file.endswith(".blend"):
            filepath = os.path.join(folder_path, file)
            filename_clean = file.replace(".blend", "").title()
            volumes.append((filepath, filename_clean, ""))

    return volumes


def load_volumetric(self, context):
    """Load the Volumes Node Groups into the World Node Tree"""
    from ..exaconv import get_scnprop
    from ..utility.utility import get_filename_from_path
    from ..background_tools.background_fc import get_nodes_dict
    from ..bpy_data_libraries_load.data_lib_loads import load_libraries_node_group

    scn = context.scene

    scnProp = get_scnprop(scn)
    world = scn.world

    nodes_dict = get_nodes_dict(world.node_tree)
    output_world = nodes_dict.get('OUTPUT_WORLD')
    volume = nodes_dict.get('VOLUMETRIC')

    filepath = scnProp.volumetric_groups
    filename = get_filename_from_path(filepath)
    filename_clean = filename.replace('.blend', '')

    nodes = world.node_tree.nodes
    links = world.node_tree.links

    node_group = load_libraries_node_group(filepath, filename_clean, filename_clean, try_to_reuse=False)
    from ..exaconv import get_ngprop
    ngProp = get_ngprop(node_group)
    ngProp.group_id_name = 'VOLUMETRIC'
    if not volume:
        from ..ops_and_fcs.create_tools import create_node_utility
        # Location of the volume is the output_world location.x and the sum of the output_world
        # location_y = output_world.location.y - output_world.dimensions.y - 10
        location_y = output_world.location.y - get_node_dimensions(output_world)[1] - 10

        volume = create_node_utility(nodes,
                                     loc_x=output_world.location.x,
                                     loc_y=location_y,
                                     nodeName=node_group.name,
                                     nodeType='ShaderNodeGroup')

    volume.node_tree = node_group
    # Link the "Volume" output to the "Volume" input of the Output World
    links.new(volume.outputs['Volume'], output_world.inputs['Volume'])

    return volume


class MemorizeNodeGroup:
    """This is for keep the volume node_group"""
    attributes = {}
    @classmethod
    def keep_node_group_in_memory(cls, node):
        # Store node name:
        cls.attributes['node_name'] = node.name
        # Store node tree:
        cls.attributes['node_tree'] = node.node_tree
        # Store node location:
        cls.attributes['node_location'] = node.location
        # Store node width:
        cls.attributes['node_width'] = node.width
        # Store node height:
        cls.attributes['node_height'] = node.height
        # Store node Inputs Values:
        cls.attributes['node_inputs_values'] = {}
        for idx, input in enumerate(node.inputs):
            if hasattr(input, 'default_value'):
                cls.attributes['node_inputs_values'][input.name] = input.default_value

        # Store the links of the node, memorize the inputs links from the node.name and the outputs links to the node.name and their sockets names
        cls.attributes['inputs_node_links'] = {}
        cls.attributes['outputs_node_links'] = {}
        for idx, inputs in enumerate(node.inputs):
            for link in inputs.links:
                # Store the links from_node.name and from_socket.name to the socket index of the node
                cls.attributes['inputs_node_links'][link.from_node.name] = [link.from_socket.name, idx]
        for idx, outputs in enumerate(node.outputs):
            for link in outputs.links:
                # Store the links to_node.name and to_socket.name from the socket index of the node
                cls.attributes['outputs_node_links'][link.to_node.name] = [link.to_socket.name, idx]


    @classmethod
    def restore_node_group_from_memory(cls, node_tree):
        # Create a new node:
        new_node = node_tree.nodes.new(type='ShaderNodeGroup')
        # Set the node name:
        new_node.name = cls.attributes['node_name']
        # Set the node tree:
        new_node.node_tree = cls.attributes['node_tree']
        # Set the node location:
        new_node.location = cls.attributes['node_location']
        # Set the node width:
        new_node.width = cls.attributes['node_width']
        # Set the node height:
        new_node.height = cls.attributes['node_height']
        # Set the node Inputs Values:
        for idx, input in enumerate(new_node.inputs):
            if hasattr(input, 'default_value'):
                input.default_value = cls.attributes['node_inputs_values'][input.name]

        # Create the links memorized into inputs_node_links and outputs_node_links

        for node_name, link in cls.attributes['inputs_node_links'].items():
            from_socket = node_tree.nodes[node_name].outputs[link[0]]
            to_socket = new_node.inputs[link[1]]
            try:
                node_tree.links.new(from_socket, to_socket)
            except:
                print("Impossible to create the link from", from_socket, "to", to_socket, "into the node", new_node.name, "Because some names are not the same")
                pass

        for node_name, link in cls.attributes['outputs_node_links'].items():
            from_socket = new_node.outputs[link[1]]
            to_socket = node_tree.nodes[node_name].inputs[link[0]]
            try:
                node_tree.links.new(from_socket, to_socket)
            except:
                print("Impossible to create the link from", from_socket, "to", to_socket, "into the node", new_node.name, "Because some names are not the same")
                pass

        return new_node












