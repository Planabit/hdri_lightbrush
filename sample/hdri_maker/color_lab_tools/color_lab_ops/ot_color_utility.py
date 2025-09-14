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
from bpy.props import StringProperty, IntProperty
from bpy.types import Operator

from ...exaproduct import Exa
from ...utility.utility import sub_nodes


class HDRIMAKER_OT_ColorUtility(Operator):
    """Swap colors between 2 consecutive Floatvectorproperty"""
    bl_idname = Exa.ops_name+"colorutility"
    bl_label = "Color Utility"
    bl_options = {'INTERNAL', 'UNDO'}

    options: StringProperty()
    mat: StringProperty()
    node: StringProperty()
    node_groups: StringProperty()
    group_inputs_idx: IntProperty()
    id_data_string: StringProperty()

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'FLIP':
            desc = "Replace color A with color B and color B with color A"
        elif properties.options == 'ASSIGN_NEXT':
            desc = "Assign color A to color B as well"
        return desc

    def execute(self, context):


        mat = bpy.data.materials[self.mat]
        # group_node = mat.node_tree.nodes[self.node]

        group_node = None
        for n in mat.node_tree.nodes:
            if n.type != 'GROUP':
                continue
            if not n.node_tree:
                continue
            for subnode in sub_nodes(n):
                if subnode.name != self.node:
                    continue
                if not subnode.node_tree:
                    continue
                if subnode.node_tree.name == self.node_groups:
                    if str(subnode.id_data) == self.id_data_string:
                        group_node = subnode

        col_1 = group_node.inputs[self.group_inputs_idx]
        col_2 = group_node.inputs[self.group_inputs_idx + 1]

        rgb_1 = list(col_1.default_value)
        rgb_2 = list(col_2.default_value)

        if self.options == 'FLIP':
            col_1.default_value = rgb_2
            col_2.default_value = rgb_1
        if self.options == 'ASSIGN_NEXT':
            col_2.default_value = rgb_1

        return {'FINISHED'}
