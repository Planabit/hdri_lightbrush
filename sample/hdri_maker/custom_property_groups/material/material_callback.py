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
import os

import bpy

from ...bpy_data_libraries_load.data_lib_loads import load_libraries_node_group
from ...exaconv import get_ngprop
from ...exaproduct import Exa
from ...library_manager.get_library_utils import risorse_lib
from ...ops_and_fcs.create_tools import create_node_utility
from ...utility.utility import has_nodetree, get_filename_from_path, redraw_all_areas


class FcNormals:
    normals = []


def enum_fc_normals_items(self, context):
    """This function is the enum items for the fc_normals node_groups for the shadow catcher"""
    if FcNormals.normals:
        return FcNormals.normals

    FcNormals.normals.append(("NONE", "None", ""))

    domes_path = os.path.join(risorse_lib(), "blendfiles", "shadow_catcher", "sc_normals")
    for fn in os.listdir(domes_path):
        if not fn.endswith('.blend'):
            continue
        filepath = os.path.join(domes_path, fn)
        filename = fn.replace("_", "").replace(".blend", "").title()
        FcNormals.normals.append((filepath, filename, ""))

    return FcNormals.normals


def update_fc_normals_items(self, context):
    """This function is used to load the sc_normals node group or remove it with NONE"""
    material = self.id_data

    node_tree = material.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    sc_normal_node = next(
        (n for n in nodes if has_nodetree(n) if get_ngprop(n.node_tree).group_id_name == "SC_NORMAL"), None)
    sc_node = next(
        (n for n in nodes if has_nodetree(n) if get_ngprop(n.node_tree).group_id_name == "EEVEE_SHADOW_CATCHER"), None)

    if sc_normal_node:
        # Removing node and node_tree from data
        node_tree = sc_normal_node.node_tree
        nodes.remove(sc_normal_node)
        bpy.data.node_groups.remove(node_tree)

    if not sc_node:
        return

    if self.enum_fc_normals == "NONE":
        return

    path = self.enum_fc_normals
    if not os.path.isfile(path):
        return

    filename = get_filename_from_path(path)
    node_name = filename.replace(".blend", "")
    # Creating node and node_tree
    node_group = load_libraries_node_group(path, node_name, node_name, try_to_reuse=False)
    node = create_node_utility(nodes, nodeName=node_name, label=node_name, loc_x=sc_node.location.x - 200, loc_y=sc_node.location.y - 200, nodeType="ShaderNodeGroup")
    node.node_tree = node_group
    ngProp = get_ngprop(node_group)
    ngProp.group_id_name = "SC_NORMAL"

    # Linking node
    normal_out = node.outputs.get("Normal")
    normal_in = sc_node.inputs.get("Normal")
    if normal_out and normal_in:
        links.new(normal_out, normal_in)

    value_out = node.outputs.get('Value')
    value_in = sc_node.inputs.get('Roughness')
    if value_out and value_in:
        links.new(value_out, value_in)

    redraw_all_areas()