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

from ..functions import check_shader_area_ok
from ...exaconv import get_scnprop
from ...exaproduct import Exa


class HDRIMAKER_PT_NodeUtility(bpy.types.Panel):
    bl_label = "Node Utility"
    # bl_idname = "HDRIMAKER_PT_TextureBrowser"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HDRi Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return check_shader_area_ok(context)

    def draw(self, context):
        shader_type = context.space_data.shader_type
        if shader_type == 'WORLD': save_type = 'WORLDS'
        elif shader_type == 'OBJECT': save_type = 'MATERIALS'

        node_tree = context.space_data.edit_tree
        active_node = node_tree.nodes.active

        scnProp = get_scnprop(context.scene)

        col = self.layout.column(align=True)

        utilBox = col.box()
        utilCol = utilBox.column(align=True)

        # row = utilCol.row()
        # row.scale_y = 1.5
        # row.operator(Exa.ops_name+"addremovebsdf", text="Add Xpbr BSDF", icon="ADD").options = "ADD_BSDF"
        utilCol.separator()
        utilCol.operator(Exa.ops_name + "copy_desc_to_clipboard", text="Copy Node Info To Clipboard", icon="COPYDOWN")
        utilCol.separator()
        sna = utilCol.operator(Exa.ops_name + "store_nodes_attributes", text="Store Nodes Attributes", icon="NODETREE")
        sna.options = "STORE"
        utilCol.separator()

        row = utilCol.row(align=True)
        row.operator(Exa.ops_name + "tag_panel_utils", text="Node Tag Type",
                     icon='OUTLINER_DATA_GP_LAYER').options = 'TAG_NODE'

        utilCol.separator()

        # if active_node and active_node.type == 'TEX_IMAGE':
        #     row = utilCol.row(align=True)
        #     row.prop(get_ndprop(active_node), 'tag_for_mapping', text="Mapping Tag")
        utilCol.label(text="Utility Nodes:")
        row = utilCol.row(align=True)
        row.operator(Exa.ops_name + "nodesutility", text="Import:", icon="NODETREE").options = "IMPORT_GROUP"
        row.prop(scnProp, 'node_utils_list', text="")
        utilCol.separator()
        row = utilCol.row()
        row.operator(Exa.ops_name + "nodesutility", text='Purge unused group inputs',
                     icon='NODE_SEL').options = 'REMOVE_UNUSED_INPUTS'
        row.operator(Exa.ops_name + "nodesutility", text="Join Inputs Nodes into 1 node",
                     icon='NODE_SEL').options = 'JOIN_NODE_INPUTS'
        utilCol.separator()
        row = utilCol.row()
        row.operator(Exa.ops_name + "nodesutility", text="Explode Selected groups",
                     icon='NODE_INSERT_OFF').options = 'EXPLODE_GROUPS'
        row.operator(Exa.ops_name + "easypanelops", text="Stats", icon='INFO').options = 'SHOW_STATS'
        utilCol.separator()
        row = utilCol.row()
        row.operator(Exa.ops_name + "nodesutility", text="Match nodes size", icon='NODE').options = 'RESIZE'

        utilCol.separator()
        row = utilCol.row()
        row.operator(Exa.ops_name + "nodesutility", text="Align Node Vertically",
                     icon='ARROW_LEFTRIGHT').options = 'ALIGN_Y'
        row.prop(scnProp, 'node_margin', text="Margin")

        utilCol.separator()
        # utilCol.separator()
        # utilCol.operator(Exa.ops_name+"materialutils", text='Connect all modules',
        #                  icon='NODE').options = 'ADJUST_NODE_TREE'
        utilCol.separator()
        utilCol.prop(context.preferences.themes[0].node_editor, 'noodle_curving', text="Smooth Noodle")
        if context.preferences.is_dirty:
            utilCol.separator()
            utilCol.operator("wm.save_userpref", text="Need to save addon_preferences", icon='INFO')

        if active_node and active_node.type == 'GROUP' and active_node.node_tree:
            utilCol.separator()
            savenodegroup = utilCol.operator(Exa.ops_name + "savenodegroup", text="Save Context Node Group")
            savenodegroup.path = scnProp.saveNgpath
            savenodegroup.save_type = save_type
            savenodegroup.full = False
            utilCol.separator()
            utilCol.prop(scnProp, 'saveNgpath', text="Choose path")

        if node_tree:
            utilCol.separator()
            savenodegroup = utilCol.operator(Exa.ops_name + "savenodegroup", text="Save Entire Node Tree")
            savenodegroup.path = scnProp.saveNgpath
            savenodegroup.save_type = save_type
            savenodegroup.full = True

