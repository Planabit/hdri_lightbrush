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
from bpy.props import EnumProperty
from bpy.types import Operator

from ...exaconv import get_sckprop, get_ndprop
from ...exaproduct import Exa
from ...ops_and_fcs.node_tree_utils import store_color_ramps_props
from ...utility.utility_4 import get_active_socket


class HDRIMAKER_OT_assign_color_ramp(Operator):
    bl_idname = Exa.ops_name + "assign_color_ramp"
    bl_label = "Assign Color Ramp"
    bl_options = {'INTERNAL', 'UNDO'}

    node_tree = None
    mat = None
    options: EnumProperty(items=(("SET", "Set", ""), ("REMOVE", "Remove", "")), default="SET")

    @classmethod
    def description(cls, context, properties):
        if properties.options == "SET":
            desc = "Set active Color Ramp node to the active Socket"
        elif properties.options == "REMOVE":
            desc = "Remove active Color Ramp node from the active Socket"
        else:
            desc = "Unknown"
        return desc

    def invoke(self, context, event):
        ob = context.object
        if not ob:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

        mat = ob.active_material
        if not mat:
            self.report({'ERROR'}, "No material selected")
            return {'CANCELLED'}

        node_tree = context.space_data.edit_tree
        if not node_tree:
            self.report({'ERROR'}, "No node tree found")
            return {'CANCELLED'}

        self.node_tree = node_tree

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Select the Color Ramp node and press OK")

    def execute(self, context):

        node_tree = self.node_tree

        active_socket, active_index = get_active_socket(node_tree, input_output='INPUT')
        if not active_socket:
            self.report({'ERROR'}, "No active socket found")
            return {'CANCELLED'}

        sckProp = get_sckprop(active_socket)

        if self.options == 'REMOVE':
            # Find Node color ramp with the same name of the socket
            node = next((n for n in node_tree.nodes if get_ndprop(n).color_ramp_id_name == sckProp.api_color_ramp),
                        None)
            if node:
                get_ndprop(node).color_ramp_id_name = ""
            sckProp.api_color_ramp = ""
            active_socket.hide_value = False
            self.report({'INFO'}, "Color Ramp node removed from the active socket")
            return {'FINISHED'}

        active_node = node_tree.nodes.active
        if not active_node:
            self.report({'ERROR'}, "No active node found")
            return {'CANCELLED'}

        if active_node.type != "VALTORGB":
            self.report({'ERROR'}, "Active node is not a Color Ramp!")
            return {'CANCELLED'}

        color_ramp_node = active_node

        # Assegnamo un nome univoco alla proprietà del nodo "color_ramp_id_name" che sarà il nome del nodo stesso, in modo
        # che se il nome del nodo dovesse cambiare, la proprietà del nodo non cambierà fino al prossimo assegnamento del nome

        ndProp = get_ndprop(color_ramp_node)

        if self.options == 'SET':
            ndProp.color_ramp_id_name = color_ramp_node.name
            sckProp.api_color_ramp = color_ramp_node.name
            active_socket.hide_value = True
            store_color_ramps_props(node_tree.nodes)
            self.report({'INFO'}, "Color Ramp node assigned to the active socket")
            return {'FINISHED'}

        return {'FINISHED'}
