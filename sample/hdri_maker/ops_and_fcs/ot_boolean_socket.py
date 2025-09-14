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

from ..exaconv import get_sckprop
from ..exaproduct import Exa
from ..utility.utility import sub_nodes, safety_eval
from ..utility.utility_4 import get_ng_inputs


class HDRIMAKER_OT_boolean_socket(Operator):
    bl_idname = Exa.ops_name+"boolean_socket"
    bl_label = "Activate or deactivate"
    bl_options = {'INTERNAL', 'UNDO'}

    options: StringProperty()
    repr_node_tree: StringProperty()
    node: StringProperty()
    node_groups: StringProperty()
    group_inputs_idx: IntProperty()
    description: StringProperty()
    id_data: StringProperty()
    docs_key: StringProperty()  # Questa deve leggere la docs_key del socket (socket.extremepbr_socket_props.docs_key)

    @classmethod
    def description(cls, context, properties):

        description = properties.description
        if description == "": description = "Boolean Operator"
        return description

    def execute(self, context):

        options = self.options

        if options == 'BOOL':
            node_tree = safety_eval(self.repr_node_tree)
            # Siccome si può avere a che fare con sottogruppi, bisogna iterare con sub_nodes e trovare il nodo che contiene
            # il gruppo in cui si sta operando:

            node = []
            for n in node_tree.nodes:
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
                        if str(subnode.id_data) == self.id_data:
                            node.append(subnode)

            node = next(iter(node), None)
            # node = next((sn for n in mat.node_tree.nodes if n.type == 'GROUP' if n.node_tree for sn in
            #              sub_nodes(n) if sn.name == self.node if
            #              sn.node_tree.name == self.node_groups if str(sn.id_data) == self.id_data), None)

            n_input = node.inputs[self.group_inputs_idx]
            ng_input = get_ng_inputs(node.node_tree, index=self.group_inputs_idx)
            minim, maximum = ng_input.min_value, ng_input.max_value

            n_input.default_value = minim if n_input.default_value > minim else maximum

            # ############################################################################
            # Sezione che muta i nodi se presente in lista:
            # ############################################################################

            socket = get_ng_inputs(node.node_tree, index=self.group_inputs_idx)
            sckProp = get_sckprop(socket)

            bool_value = False if n_input.default_value == minim else True

            true_list = sckProp.api_bool_mute_nodes_if_true.split("//")
            false_list = sckProp.api_bool_mute_nodes_if_false.split("//")

            if not true_list and not false_list:
                return{'FINISHED'}

            node_names_if_true = [n for n in node.node_tree.nodes if n.name in true_list]
            node_names_if_false = [n for n in node.node_tree.nodes if n.name in false_list]

            if not node_names_if_true and not node_names_if_false:
                return{'FINISHED'}

            for n in node.node_tree.nodes:
                if bool_value is True:
                    if n in node_names_if_true:
                        n.mute = True
                    elif n in node_names_if_false:
                        n.mute = False

                elif bool_value is False:
                    if n in node_names_if_false:
                        n.mute = True
                    elif n in node_names_if_true:
                        n.mute = False

        return {'FINISHED'}
