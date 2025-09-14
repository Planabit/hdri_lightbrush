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
import os

import bpy

from ..functions import check_shader_area_ok
from ...exaconv import get_scnprop, get_ngprop, get_sckprop
from ...exaproduct import Exa
from ...library_manager.get_library_utils import current_lib
from ...library_manager.main_pcoll_attributes import get_winman_main_preview
from ...utility.text_utils import wrap_text
from ...utility.utility_4 import get_ng_inputs


class HDRIMAKER_PT_LibraryCreatorUtility(bpy.types.Panel):
    bl_label = "Library Creator Utility"
    # bl_idname = "HDRIMAKER_PT_TextureBrowser"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HDRi Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return check_shader_area_ok(context)
    

    def draw(self, context):

        scnProp = get_scnprop(context.scene)
        col = self.layout.column(align=True)
        preview_mat_name = get_winman_main_preview()

        mat = None
        active_node = None
        ob = context.object
        if ob:
            mat = ob.active_material
            node_tree = context.space_data.edit_tree
            if node_tree and node_tree.nodes:
                active_node = node_tree.nodes.active

        opsBox = col.box()
        colops = opsBox.column(align=True)

        mat_dir = current_lib()

        colops.operator(Exa.ops_name + "redraw_all_previews", text="Redraw All Preview", icon='RESTRICT_RENDER_OFF')
        colops.separator()

        pyops = colops.operator(Exa.ops_name+"pythonops", text="Open Material Folder")
        pyops.options = 'OPEN_FOLDER'
        colops.separator()
        # colops.operator(Exa.ops_name+"createbatchpreviews", text="Start Batch Previews")

        path = os.path.join(mat_dir, scnProp.up_category, preview_mat_name)
        if not os.path.isdir(path):
            path = os.path.join(mat_dir, scnProp.up_category)
        pyops.open_path = path

        colops.separator()
        # if scnProp.up_category != "Tools":
        #     colops.operator(Exa.ops_name+"renamematerialfiles", text="Change material file name")

        allertCol = colops.column(align=True)
        allertCol.alert = True
        text = "This section is very dangerous if you are not a texture or material manufacturer, you should not use it at all, you could compromise the entire library!"
        wrap_text(layout=allertCol, string=text, enum=False, text_length=60, center=True,
                  icon="")
        jsnBox = col.box()
        jcol = jsnBox.column(align=False)

        text = "Attention, these buttons in this box will replace the current json, if you just want to replace single parameters, use the screen below"
        wrap_text(layout=jcol, string=text, enum=False, text_length=(context.region.width / 6.5),
                  center=False, icon="")

        op = jcol.operator(Exa.ops_name+"librarymanipulator", text="Create current cat mat_info.json",
                           icon='FILE_NEW')
        op.options = 'CREATE_BATCH_JSON_CURRENT_CAT'
        op.descriptions = "Batch create the mat_info.json file for current category library"
        jcol.separator()

        op = jcol.operator(Exa.ops_name+"librarymanipulator", text="Create entire mat_info.json", icon='FILE_NEW')
        op.options = 'CREATE_BATCH_JSON'
        op.descriptions = "Batch create the mat_info.json file for the entire library"
        jcol.separator()
        ############

        if ob and mat:
            node = context.space_data.edit_tree.nodes.active
            if node and node.type == 'GROUP' and node.node_tree and get_ngprop(
                    node.node_tree).group_id_name == 'MODULE':
                op = jcol.operator(Exa.ops_name+"librarymanipulator", text="Create single mat_info.json",
                                   icon='FILE_NEW')
                op.options = 'CREATE_SINGLE_JSON'
                op.descriptions = "Create the mat_info.json file for the current material"
                op.active_node = node.name

        subBox = col.box()
        subCol = subBox.column(align=False)
        row = subCol.row()
        row.alignment = 'CENTER'
        row.label(text="Material Info:")

        subCol.prop(scnProp, 'storage_method', text="Storage Method")
        subCol.prop(scnProp, 'permission', text="Permission")
        subCol.prop(scnProp, 'author', text="Author")
        subCol.prop(scnProp, 'website_name', text="Website Name")
        subCol.prop(scnProp, 'website_url', text="Author Website")
        subCol.prop(scnProp, 'license', text="License")
        subCol.prop(scnProp, 'license_link', text="License Link")
        subCol.prop(scnProp, 'license_description', text="License Description")
        subCol.operator(Exa.ops_name+"librarymanipulator", text="Replace into Json").options = 'REPLACE_MATERIAL_INFO'

        subBox = col.box()
        subCol = subBox.column(align=False)
        row = subCol.row()
        row.alignment = 'CENTER'
        row.label(text="Material Settings:")

        # subCol.prop(scnProp, 'use_backface_culling', text="Backface Culling")
        # subCol.prop(scnProp, 'blend_method', text="Blend Mode")
        # subCol.prop(scnProp, 'shadow_method', text="Shadow Mode")
        # subCol.prop(scnProp, 'alpha_threshold', text="Clip Threshold", slider=True)
        # subCol.prop(scnProp, 'refraction_depth', text="Refraction Depth")
        # subCol.prop(scnProp, 'use_screen_refraction', text="Screen Space Refraction")
        # subCol.prop(scnProp, 'use_sss_translucency', text="Subsurface Translucent")
        # subCol.operator(Exa.ops_name+"librarymanipulator",
        #                 text="Replace into Json").options = 'REPLACE_MATERIAL_SETTINGS'

        col.separator()
        subBox = col.box()
        subCol = subBox.column(align=True)
        row = subCol.row()
        row.alignment = 'CENTER'
        row.label(text="Group Inputs variation:")
        row = subCol.row()
        row.alignment = 'CENTER'
        row.label(text="(Only for single save, requires the module to be selected)")
        subCol.operator(Exa.ops_name+"librarymanipulator",
                        text="Replace into Json").options = 'REPLACE_GROUP_INPUT_PROPERTIES'
        subCol.separator()

        if ob and mat:
            node_tree = context.space_data.edit_tree
            module = node_tree.nodes.active
            if module and module.type == 'GROUP' and module.node_tree and get_ngprop(
                    module.node_tree).group_id_name == 'MODULE':
                for idx, inp in enumerate(module.inputs):
                    socket = get_ng_inputs(module.node_tree, index=idx)
                    sckProp = get_sckprop(socket)
                    split = subCol.split(factor=0.9)
                    split.prop(inp, 'default_value', text=inp.name)
                    split.prop(sckProp, 'store_property', text="R")