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
from ...icons.interfaceicons import get_icon
from ...library_manager.main_pcoll_attributes import get_winman_main_preview


class HDRIMAKER_PT_ShaderEditor(bpy.types.Panel):
    bl_label = "Module Manager"
    # bl_idname = "HDRIMAKER_PT_ShaderEditor"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HDRi Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return check_shader_area_ok(context)

    def draw(self, context):

        scn = context.scene
        scnProp = get_scnprop(scn)

        if scnProp.scene_id_name == 'SAVE_MATERIAL':
            return

        preview_mat_name = get_winman_main_preview()

        mat = None
        active_node = None
        ob = context.object
        if ob:
            mat = ob.active_material
            node_tree = context.space_data.edit_tree
            if node_tree and node_tree.nodes:
                active_node = node_tree.nodes.active

        layout = self.layout
        col = layout.column(align=True)

        row = col.row()
        row.operator(Exa.ops_name + "open_preferences", text="Helps", icon_value=get_icon('extreme_addons_32')).options = 'HELPS'
        row.label(text="")

        col.separator()

        # row = create_col.row(align=True)
        # row.scale_y = 1.5
        # row.operator(Exa.ops_name+"materialadd", text='Create empty Module', icon='ADD').options = 'IMPORT_EMPTY_MODULE'
        # row.operator(Exa.ops_name+"addfxmodule", text='Create empty Fx', icon='ADD').options = 'EMPTY_FX'
        # row.scale_x = 0.5
        # row.operator(Exa.ops_name+"remove_background", text='Remove', icon='REMOVE').options = 'REMOVE_MATERIAL'
        # create_col.separator()

        # if ob:
        #     col.template_list("EXTREMEPBR_UL_MaterialSlots", "", ob, "material_slots", ob, "active_material_index",
        #                       rows=3)