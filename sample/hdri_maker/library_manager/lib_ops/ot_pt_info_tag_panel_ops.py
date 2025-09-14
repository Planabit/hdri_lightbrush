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
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

from ..lib_ops.ot_pt_tag_manager_panel_ops import tag_copied
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...icons.interfaceicons import get_icon
from ...utility.json_functions import get_json_data
from ...utility.text_utils import wrap_text
from ...utility.utility import wima


class HDRIMAKER_OT_InfoTagPanelOps(Operator):
    """Show information about this material"""
    bl_idname = Exa.ops_name+"infotagpanelops"
    bl_label = "Material info and Tag"
    bl_options = {'INTERNAL'}

    options: StringProperty()
    info_path: StringProperty()
    tags_path: StringProperty()
    node_groups: StringProperty()
    mat_info_json = None
    show_info: BoolProperty(default=False, description="Show Material Info")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        if self.options in ['SHOW_JSON_MAT_INFO', 'SHOW_MAT_INFO']:
            if self.options == 'SHOW_JSON_MAT_INFO':
                self.mat_info_json = get_json_data(self.info_path)
            return wima().invoke_props_dialog(self, width=400)

    def draw(self, context):
        options = self.options
        layout = self.layout
        material_info = None

        scnProp = get_scnprop(context.scene)

        # current_idx = str([i.replace(".png","").replace(".jpg","") for i in preview_collections_main_dict['indice']].index(mat_preview) + 1)
        # full_idx = str(len(preview_collections_main_dict['indice']))

        # layout.label(text=current_idx + "/" + full_idx)

        box = layout.box()
        col = box.column(align=False)

        if options == 'SHOW_JSON_MAT_INFO':
            material_info = self.mat_info_json.get("material_info") if self.mat_info_json else self.mat_info_json

        else:
            node_group = bpy.data.node_groups[self.node_groups]
            if node_group.get('exa_mat_info'):
                material_info = node_group['exa_mat_info'].get("material_info")

        col.prop(self, 'show_info', text="Show Info & License", icon = 'TRIA_DOWN' if self.show_info else 'TRIA_RIGHT', emboss = False)

        if material_info:
            if self.show_info:
                for key, value in material_info.items():
                    if key == "original_name":
                        continue
                    if value:
                        split = col.split(factor=0.3)
                        split.label(text=key.title().replace("_", " "))

                        if key == "website_url":
                            text = "Open Website: " + material_info['website_name'] if material_info.get('website_name') else 'Online url'
                            webbrowser = split.operator(Exa.ops_name+"open_web_browser", text=text, icon='URL')
                            webbrowser.options = "OPEN_URL"
                            webbrowser.url = value

                        elif key == "license_link":
                            text = material_info['license'] if material_info.get('license') else 'Show'
                            webbrowser = split.operator(Exa.ops_name+"open_web_browser", text="License documentation", icon='URL')
                            webbrowser.options = "OPEN_URL"
                            webbrowser.url = value
                        else:
                            subCol = split.column(align=True)
                            wrap_text(subCol, value.title().replace("_", " "), text_length=45)
                            # row.label(text=value.title().replace("_", " "))

        if options == 'SHOW_MAT_INFO':
            ng_description = node_group.hdri_prop_nodetree.ng_description
            wrap_text(col, ng_description, None, 60, True, "")

        elif options == 'SHOW_JSON_MAT_INFO':
            tags = None
            tags_json_data = get_json_data(self.tags_path)

            if tags_json_data:
                tags = tags_json_data.get("tags")

            tagBox = layout.box()
            tagCol = tagBox.column(align=True)
            row = tagCol.row(align=True)
            row.label(text="Tags", icon_value=get_icon('tag'))
            row.prop(scnProp, 'edit_tag', text="Edit Tags")
            tagCol.separator()

            # if tags:
            len_characters = 0
            tagSubox = tagCol.box()
            tagSuCol = tagSubox.column(align=False)
            if tags:
                row = tagSuCol.row(align=True)
                for idx, tag in enumerate(tags):
                    len_characters += len(tag)
                    if len_characters > 35:
                        row = tagSuCol.row(align=True)
                        len_characters = 0

                    if scnProp.edit_tag:
                        row.emboss = 'PULLDOWN_MENU'
                        tagOps = row.operator(Exa.ops_name+"tagmanagerpanelops", text=tag)
                        tagOps.options = 'REMOVE'
                        tagOps.idx = idx
                        tagOps.tag_name = tag
                    else:
                        row.label(text=tag)

            if scnProp.edit_tag:
                row = tagSuCol.row(align=True)
                if tag_copied:
                    row.operator(Exa.ops_name+"tagmanagerpanelops", text="", icon='CANCEL').options = 'CLEAR_COPIES'
                    row.label(text="")
                    row.operator(Exa.ops_name+"tagmanagerpanelops", text="Paste", icon='PASTEDOWN').options = 'PASTE'
                else:
                    row.label(text="")
                    row.label(text="")

                if tags:
                    row.operator(Exa.ops_name+"tagmanagerpanelops", text="Copy", icon='COPYDOWN').options = 'COPY'

                tagCol.separator()
                row = tagCol.row(align=True)
                row.operator(Exa.ops_name+"searchtags", text="", icon='VIEWZOOM')
                row.prop(scnProp, 'temp_tag', text="")
                row = row.row(align=True)
                row.scale_x = 0.5
                tagOps = row.operator(Exa.ops_name+"tagmanagerpanelops", text="Add tag", icon='ADD')
                tagOps.options = 'ADD'
