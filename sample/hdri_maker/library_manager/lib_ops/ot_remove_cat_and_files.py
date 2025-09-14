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
import shutil

import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator

from ..categories_enum import update_first_cat
from ..get_library_utils import current_lib
from ..main_pcoll import update_first_icon, reload_main_previews_collection
from ..main_pcoll_attributes import get_winman_main_preview
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...utility.text_utils import wrap_text, draw_info
from ...utility.utility import wima


class HDRIMAKER_OT_RemoveLibTools(Operator):
    """Remove active category and materials. WARNING! All materials contained in this category will be deleted, please consider if it is what you really want!"""

    bl_idname = Exa.ops_name+"remove_lib_tool"
    bl_label = "Delete options"
    bl_options = {'INTERNAL', 'UNDO'}

    options: StringProperty()
    confirm: EnumProperty(default='NO', items=(('YES', "Yes", ""), ('NO', "No", "")))

    @classmethod
    def description(cls, context, properties):

        if properties.options == 'REMOVE_CATEGORY':
            desc = "It 'DEFINITIVELY' and irreversibly removes the currently selected category from the User library. Attention, all materials contained in it will be deleted."

        elif properties.options == 'REMOVE_MATERIAL':
            desc = """It 'DEFINITIVELY' and irreversibly removes the material from the User library."""

        else:
            desc = properties.options

        return desc

    def draw(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        if self.options == 'REMOVE_MATERIAL':
            text = "Are you sure you want to completely remove ( " + get_winman_main_preview() + " ) material from ( " + scnProp.up_category + " ) category?"
        else:
            text = "Are you sure you want to completely delete this category? ( " + scnProp.up_category + " ) All materials contained in it (if any) will be deleted!"
        wrap_text(col, text, None, 90, True, "")

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.prop(self, 'confirm', expand=True)
        col.separator()
        col.label(text="Press Esc to abort, or choose 'No' and Press 'Ok' ")

    def invoke(self, context, event):
        self.confirm = 'NO'
        return wima().invoke_props_dialog(self, width=500)

    def execute(self, context):
        if self.confirm == 'NO':
            return {'FINISHED'}

        scn = context.scene
        scnProp = get_scnprop(scn)
        savelib = current_lib()

        if self.options == 'REMOVE_CATEGORY':

            if savelib:
                if not scnProp.up_category:
                    return {'FINISHED'}
                if scnProp.up_category == 'Empty Collection...':
                    return {'FINISHED'}

                shutil.rmtree(os.path.join(savelib, scnProp.up_category))

                if scnProp.libraries_selector != 'DEFAULT':
                    update_first_cat(self, context)

        if self.options == 'REMOVE_MATERIAL':
            preview_mat_name = get_winman_main_preview()

            if preview_mat_name == '':
                return {'FINISHED'}
            if preview_mat_name == 'Empty...':
                return {'FINISHED'}

            folder_path = os.path.join(savelib, scnProp.up_category, preview_mat_name)
            if os.path.exists(folder_path):
                print("Removing folder: " + folder_path)
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    text = "Error while deleting material: " + str(e)
                    draw_info(text, "Info", 'INFO')
                    self.report({'INFO'}, text)
                    return {'CANCELLED'}

            reload_main_previews_collection()
            update_first_icon(scnProp, context)


        return {'FINISHED'}
