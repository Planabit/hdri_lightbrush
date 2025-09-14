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

from ..draw_functions import draw_panel_sliders_group
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...ops_and_fcs.node_tree_utils import node_tree_statistics
from ...utility.utility import retrieve_nodes, data_from_string
from ...utility.utility import wima, get_addon_preferences



class HDRIMAKER_OT_EasyPanelOps(Operator):
    """ """
    bl_idname = Exa.ops_name+"easypanelops"
    bl_label = "Easy Panel"
    bl_options = {'INTERNAL'}

    options: StringProperty(description="Choose What the operator has to do")
    node_groups: StringProperty(description="Specify the name of the node_groups")
    group_inputs_idx: IntProperty(description="Input of the node_group, use Int and spec the node_group")
    group_outputs_idx: IntProperty(description="Output of the node_group, use Int and spec the node_group")
    icon: StringProperty()
    tag: StringProperty()
    id_data_name: StringProperty()
    id_data_string: StringProperty()
    node: StringProperty()
    mat_info_json = None

    @classmethod
    def description(cls, context, properties):
        desc = ""
        options = properties.options
        if options == 'SHOW_PANEL_PREVIEW':
            desc = "Show a preview of how this Node panel will look"
        elif options == 'SHADER_MAKER':
            desc = "Add and Manage the textures of this map"
        elif options == 'SHOW_STATS':
            desc = "Show Node Tree Stats"
        return desc

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        if self.options == 'SHOW_PANEL_PREVIEW':
            width = 300
        else:
            width = 500
        return wima().invoke_props_dialog(self, width=width)

    def draw(self, context):

        options = self.options
        layout = self.layout
        layout = layout.column(align=True)
        scn = context.scene
        scnProp = get_scnprop(scn)

        if options == 'SHOW_STATS':
            id_data = data_from_string(self.id_data_string)
            data_item = id_data[self.id_data_name]

            full_nodes, groups, images, univoque_mute_images, univoque_groups = node_tree_statistics(data_item)

            box = layout.box()
            col = box.column(align=False)
            row = col.row()
            row.label(text="Nodes: " + str(len(full_nodes)))
            row.label(text="Node Groups: " + str(len(groups)))
            row.label(text="Univoque Node Groups: " + str(len(univoque_groups)))

            row = col.row()
            row.label(text="Images Node: " + str(len(images)))
            if len(images) != len(set(images)):
                row.label(text="Univoque Data Images: " + str(len(set(images))))
            row.label(text="Univoque Mute images: " + str(len(set(univoque_mute_images))))

        if options == 'SHOW_PANEL_PREVIEW':
            id_data = data_from_string(self.id_data_string)
            item = id_data[self.id_data_name]

            col = layout.column(align=True)
            # Il nodo sarà sempre quello selezionato, poichè è solo per il preview nel
            # Contesto dello Shader Editor
            node_tree = context.space_data.edit_tree
            retrieve = retrieve_nodes(item.node_tree)

            node = next((n for n in retrieve if n.type == 'GROUP' if n.id_data.nodes.active == n if n.node_tree if
                         n.node_tree == node_tree), None)
            draw_panel_sliders_group(item, col, node)
            col.separator()
