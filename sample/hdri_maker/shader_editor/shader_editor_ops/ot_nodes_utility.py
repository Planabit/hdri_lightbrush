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
import ntpath

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from ...bpy_data_libraries_load.data_lib_loads import load_libraries_node_group
from ...exaconv import get_ngprop, get_scnprop, get_sckprop, get_ndprop
from ...exaproduct import Exa
from ...ops_and_fcs.create_tools import create_node_utility
from ...ops_and_fcs.material_utility import force_driver_nodes
from ...ops_and_fcs.purge import purge_unused_inputs
from ...utility.text_utils import draw_info
from ...utility.utility import join_multiple_group_inputs
from ...utility.utility_4 import get_ng_inputs
from ...utility.utility_dependencies import align_node_xy


class HDRIMAKER_OT_NodesUtility(Operator):
    bl_idname = Exa.ops_name + "nodesutility"
    bl_label = "Nodes Utility"
    bl_options = {'INTERNAL', 'UNDO'}

    options: bpy.props.StringProperty()
    node_groups: bpy.props.StringProperty()
    group_inputs_idx: bpy.props.IntProperty()
    mat: bpy.props.StringProperty()
    tag: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        options = properties.options
        if options == 'IMPORT_GROUP':
            desc = "Import this node, directly into this graph of nodes (Node Tree)"
        elif options == 'EXPLODE_GROUPS':
            desc = "Explode all selected groups"
        elif options == 'JOIN_NODE_INPUTS':
            desc = "Merge all nodes of the input type group into a single input node (Automatically connect all sockets)"
        elif options == 'RESIZE':
            desc = "Based on the active node, makes the others (Selected) with the same size"
        elif options == 'ALIGN_Y':
            desc = "Vertical align selected nodes"
        elif options == 'ALIGN_X':
            desc = "Align the selected nodes horizontally"
        elif options == 'REMOVE_UNUSED_INPUTS':
            desc = "Remove unused inputs from the context group"
        return desc

    def execute(self, context):

        scn = context.scene
        scnProp = get_scnprop(scn)

        if Exa.product == 'EXTREME_PBR':
            ob = context.object
            if ob:
                mat = ob.active_material
            else:
                return {'FINISHED'}

        elif Exa.product == 'HDRI_MAKER':
            mat = scn.world

        if self.options == 'IMPORT_GROUP':
            data_group_name = ntpath.basename(scnProp.node_utils_list)[:-6]
            node_name = data_group_name.replace("X_PBR_Utility_", "").replace("_", " ")
            node_tree = context.space_data.edit_tree
            node = create_node_utility(node_tree.nodes, None, None, node_name, node_name, "ShaderNodeGroup", None,
                                       150, False)
            path = scnProp.node_utils_list
            group = load_libraries_node_group(path, data_group_name, data_group_name)
            ngProp = get_ngprop(group)
            ngProp.group_id_name = data_group_name

            node.node_tree = group
            ndProp = get_ndprop(node)
            ndProp.group_filename = ntpath.basename(scnProp.node_utils_list)

            for n in node_tree.nodes:
                n.select = True if n == node else False

            node_tree.nodes.active = node
            node.show_options = False
            force_driver_nodes(mat)

            return bpy.ops.transform.translate('INVOKE_DEFAULT')

        if self.options == 'EXPLODE_GROUPS':

            nodes = context.space_data.edit_tree.nodes
            selected_nodes = [n for n in nodes if n.select if n.type == 'GROUP' if n.node_tree]
            for n in selected_nodes:
                nodes.active = n
                bpy.ops.node.group_ungroup()

        elif self.options == 'JOIN_NODE_INPUTS':
            node_tree = context.space_data.edit_tree
            if node_tree != mat.node_tree:
                join_multiple_group_inputs(node_tree)
            else:
                text = "To remove unused sockets inputs, you need to be inside at the Group"
                draw_info(text, "Info", 'INFO')

        elif self.options == 'RESIZE':
            nodes = context.space_data.edit_tree.nodes
            node_master = nodes.active
            selected_nodes = [n for n in nodes if n.select]
            if node_master:
                size = node_master.width
            elif selected_nodes:
                size = selected_nodes[0].width
            else:
                return {'CANCELLED'}

            for n in selected_nodes:
                n.width = size

        elif self.options == 'ALIGN_Y':
            node_tree = context.space_data.edit_tree
            nodes = node_tree.nodes
            selected_nodes = [n for n in nodes if n.select]

            ordered_nodes = align_node_xy(node_tree, selected_nodes, direction='Y', margin=scnProp.node_margin)

            # center_relative_nodes(node_tree, ordered_nodes,
            #                       next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None), direction='Y',
            #                       align_relative=False)
        elif self.options == 'REMOVE_UNUSED_INPUTS':
            node_tree = context.space_data.edit_tree
            if node_tree != mat.node_tree:
                purge_unused_inputs(node_tree)
            else:
                text = "To remove unused sockets inputs, you need to be inside at the Group"
                draw_info(text, "Info", 'INFO')

        return {'FINISHED'}


class HDRIMAKER_OT_StoreNodesAttributes(Operator):
    """Store the nodes attributes"""

    bl_idname = Exa.ops_name + "store_nodes_attributes"
    bl_label = "Store Nodes Attributes"
    bl_options = {'INTERNAL'}

    confirm: EnumProperty(default='NO', items=(('YES', "Yes", ""), ('NO', "No", "")))
    options: EnumProperty(default='STORE', items=(('STORE', "Store", ""), ('RESTORE', "Restore", "")))
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Are you sure you want to store the nodes attributes?")
        col.label(text="This action will overwrite the previous stored attributes!")
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(self, 'confirm', expand=True)

    def invoke(self, context, event):
        self.confirm = 'NO'
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.options == 'STORE':
            from ...utility.nodes_compatibility import store_node_attributes_into_node_tree
            node_tree = context.space_data.edit_tree
            store_node_attributes_into_node_tree(node_tree)

        return {'FINISHED'}

class HDRIMAKER_OT_CopyNodeDescriptionToClipboard(Operator):
    """Copy the node description to clipboard"""

    bl_idname = Exa.ops_name + "copy_desc_to_clipboard"
    bl_label = "Copy Node Description to Clipboard"
    bl_options = {'INTERNAL'}

    exclude_list: StringProperty(default="")


    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Insert the numbers of the sockets you want to exclude")
        col.label(text="separated by comma (,)")
        col.prop(self, 'exclude_list', text="Exclude List")
        col.separator

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        exclude_list = self.exclude_list.split(',')

        print("exclude_list", exclude_list)
        # Transform the list of strings into a list of integers
        if exclude_list != ['']:
            exclude_list = [int(i) for i in exclude_list]
        else:
            exclude_list = []

        descriptions = {}
        node_tree = context.space_data.edit_tree

        ngProp = get_ngprop(node_tree)

        ng_description = ngProp.ng_description

        body = node_tree.name+" (Node Group)\n"
        # Need to put - under the title, with the same number of characters
        body += "-" * len(node_tree.name+" (Node Group)") + "\n\n"
        body += "\n\n"
        body += ng_description + "\n\n"
        body += "Inputs:\n\n"

        user_idx = 0
        for idx, ng_input in enumerate(get_ng_inputs(node_tree)):

            if idx in exclude_list:
                continue

            user_idx += 1

            sckProp = get_sckprop(ng_input)
            input_type = ""
            if sckProp.api_boolean:
                input_type = " (Button)"
            else:
                input_type = " (" + ng_input.type.title() + ")"


            if sckProp.api_top_label_text != '':
                body += "**"+sckProp.api_top_label_text+"**\n"
                body += "\n"

            body += str(user_idx) + ". **" + ng_input.name + " " + input_type + "**\n"
            body += "\n"
            body += " - " + sckProp.api_bool_description + "\n"
            body += "\n"

        # Copy to clipboard
        bpy.context.window_manager.clipboard = body

        return {'FINISHED'}
