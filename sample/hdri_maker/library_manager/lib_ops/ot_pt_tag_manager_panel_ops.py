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
import datetime
import os

import bpy
from bpy.types import Operator

from ..get_library_utils import current_lib
from ..main_pcoll import update_tag_search
from ..main_pcoll_attributes import get_winman_main_preview
from ..tag_filter import tag_search_active
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...utility.json_functions import get_json_data, save_json
from ...utility.text_utils import wrap_text, draw_info
from ...utility.utility import wima

tag_copied = []


class HDRIMAKER_OT_TagManagerPanelOps(Operator):
    """Tag Manager"""
    bl_idname = Exa.ops_name+"tagmanagerpanelops"
    bl_label = "Tag Manager"
    bl_options = {'INTERNAL'}

    options: bpy.props.StringProperty()
    tag_name: bpy.props.StringProperty()
    idx: bpy.props.IntProperty()
    confirm: bpy.props.EnumProperty(default='NO', items=(('YES', "Yes", ""), ('NO', "No", "")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ADD':
            desc = "Add a new tag"
        elif properties.options == 'REMOVE':
            desc = "Remove this tag: " + properties.tag_name
        elif properties.options == 'COPY':
            desc = "Copy all tags in memory"
        elif properties.options == 'PASTE':
            if [tag for tag in tag_copied]:
                desc = "Paste all these tags:    " + ", ".join(tag_copied)
        elif properties.options == 'CLEAR_COPIES':
            desc = "Reset the copied tags, it is just a security not to run into unwanted pastes"
        return desc

    def draw(self, context):

        layout = self.layout
        col = layout.column(align=True)

        if self.options in ['REMOVE', 'PASTE']:
            text = "Are you sure?"

            if self.options == 'REMOVE':
                col.label(text="Are you sure you want to remove this tag? the operation cannot be undone")
            elif self.options == 'PASTE':
                col.label(text="Are you sure you want to paste all these tags in this material here?")
                text = ", ".join(tag_copied)
                tagBox = col.box()
                colBox = tagBox.column(align=True)
                wrap_text(layout=colBox, string=text, enum=False,
                          text_length=(context.region.width / 6.5), center=False, icon="")
                colBox.separator()

            row = col.row()
            row.scale_y = 1.5
            row.prop(self, 'confirm', expand=True)
            col.separator()

    def invoke(self, context, event):

        if self.options == 'REMOVE':
            wima().clipboard = self.tag_name
            self.confirm = 'NO'
            return wima().invoke_props_dialog(self, width=400)
        elif self.options == 'PASTE':
            self.confirm = 'NO'
            return wima().invoke_props_dialog(self, width=400)
        else:
            return self.execute(context)

    def execute(self, context):

        scnProp = get_scnprop(context.scene)

        if self.options == 'REMOVE' and self.confirm == 'NO':
            return {'FINISHED'}

        if self.options == 'CLEAR_COPIES':
            tag_copied.clear()

        mat_preview = get_winman_main_preview()

        data_path = os.path.join(current_lib(), scnProp.up_category, mat_preview, "data")
        if not os.path.isdir(data_path):
            text = "The structure of this material folder does not allow you to save the tag"
            draw_info(text, "Info", 'INFO')
            return {'FINISHED'}

        json_path = os.path.join(data_path, "tags.json")
        if os.path.isfile(json_path):
            json_data = get_json_data(json_path)
            json_tags = json_data.get("tags")
            if not json_tags: json_tags = json_data["tags"] = []
        else:
            json_data = {}
            json_tags = json_data["tags"] = []

        if self.options == 'ADD':

            scnProp.temp_tag = scnProp.temp_tag.replace(" ", "")

            if scnProp.temp_tag.lower() in [t.lower() for t in json_tags]:
                text = "Attention, this tag is already present in the tag list, remember that it is not case sensitive, all tags will be made lowercase."
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}
            if scnProp.temp_tag.isspace() or scnProp.temp_tag == "":
                text = "Please enter a valid name for the tag, in the box on the left side"
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}

            json_tags.append(scnProp.temp_tag.lower())

        elif self.options == 'REMOVE':
            json_tags.pop(self.idx)

        elif self.options == 'COPY':
            tag_copied.clear()
            for tag in json_tags:
                tag_copied.append(tag)
            return {'FINISHED'}

        elif self.options == 'PASTE':
            if self.confirm == 'NO':
                return {'FINISHED'}
            for tag in tag_copied:
                if tag.lower() not in [t.lower() for t in json_tags]:
                    json_tags.append(tag)

        today = datetime.date.today()
        json_data['date'] = str(today.strftime("%d/%m/%Y"))

        json_tags = sorted(json_tags)
        json_data["tags"] = json_tags
        save_json(json_path, json_data)

        if self.options == 'ADD':
            text = "Tag added: " + scnProp.temp_tag
            draw_info(text, "Info", 'INFO')

        if tag_search_active(scnProp):
            update_tag_search(scnProp, context)

        return {'FINISHED'}
