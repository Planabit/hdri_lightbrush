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
from bpy.types import Operator

from ...exaproduct import Exa
from ...ops_and_fcs.create_tools import create_node_utility
from ...utility.utility import get_all_blender_shadernodes
from ...utility.utility_4 import get_ng_inputs


# Create button operator in the shader node editor


class HDRIMAKER_OT_CreateShaderNodesProperties(Operator):
    """UNUSED FOR NOW"""

    bl_idname = Exa.ops_name + "create_shader_nodes_properties"
    bl_label = "Create Shader Nodes Info"
    bl_description = "Create shader nodes info"
    bl_options = {'REGISTER', 'UNDO'}

    loc_x = 0
    loc_y = 0

    @classmethod
    def poll(self, context):
        # Return true if the area is the shader editor
        return context.area.type == 'NODE_EDITOR' and context.space_data.node_tree

    def execute(self, context):

        # Get node_tree from the active node editor
        node_tree = context.space_data.node_tree
        nodes = node_tree.nodes

        shader_nodes_list = get_all_blender_shadernodes()
        for n in nodes:
            n.select = False

        nodes_dict = {}
        for node_idx, (nodeType, label) in enumerate(shader_nodes_list):
            context_node_dict = {"nodeName": label, "nodeType": nodeType}

            node = create_node_utility(nodes, loc_x=0, loc_y=0, nodeType=nodeType, label=label)
            nodes.active = node
            node.select = True
            bpy.ops.node.group_make()
            node.select = False
            # Now by default we are inside the new group created,
            node_group = context.space_data.edit_tree
            node_group.name = label

            inputs_dict = {}
            for inp_idx, inp in enumerate(get_ng_inputs(node_group)):
                if hasattr(inp, "default_value") and hasattr(inp, "min_value") and hasattr(inp, "max_value"):
                    name = inp.name

                    bl_socket_idname = inp.bl_socket_idname
                    min_value = inp.min_value
                    max_value = inp.max_value
                    default_value = inp.default_value[:] if inp.type == 'VECTOR' else inp.default_value

                    inputs_dict[inp_idx] = {"name": name, "bl_socket_idname": bl_socket_idname,
                                            "min_value": min_value,
                                            "max_value": max_value, "default_value": default_value}

            nodes_dict[nodeType] = context_node_dict
            context_node_dict["inputs"] = inputs_dict

            context.space_data.node_tree = node_tree

            node_group_node = next((n for n in nodes if hasattr(n, 'node_tree') if n.node_tree == node_group), None)
            nodes.remove(node_group_node)
            bpy.data.node_groups.remove(node_group)

        # Now we have to create a json file with all the info

        # save_path = os.path.join(risorse_lib(), "Files", "shader_nodes_properties.json")
        # save_json(save_path, nodes_dict)

        return {'FINISHED'}
