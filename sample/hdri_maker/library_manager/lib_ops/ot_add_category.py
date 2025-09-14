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

from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator

from ..categories_enum import get_mats_categories, enum_up_category
from ..get_library_utils import current_lib
from ..main_pcoll import enum_material_previews
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...utility.text_utils import draw_info
from ...utility.utility import wima, replace_forbidden_characters


class HDRIMAKER_OT_AddCategory(Operator):
    """Add New category to save new materials"""

    bl_idname = Exa.ops_name+"addcategory"
    bl_label = "Library utils"
    bl_options = {'INTERNAL'}

    rename_folder: StringProperty()
    options: StringProperty()
    confirm: EnumProperty(default='NO', items=(('NO', "No", ""), ('YES', "Yes", "")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ADD_NEW_CATEGORY':
            desc = "Add New category to save new materials"

        elif properties.options == 'RENAME_CATEGORY':
            desc = "Rename the active category (It is only possible for the user category)"
        return desc

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.prop(self, 'rename_folder', text="New Name")

        col.label(text="Are you sure to: " + self.options.title().replace("_", " ") + " ?")
        row = col.row(align=True)
        row.scale_y = 2
        row.prop(self, 'confirm', expand=True)

    def invoke(self, context, event):

        self.rename_folder = ""

        scn = context.scene
        scnProp = get_scnprop(scn)
        self.confirm = 'NO'
        if self.options == 'ADD_NEW_CATEGORY':
            if scnProp.cat_name_save == "":
                text = "Enter a name please"
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}

            for cartelle in os.listdir(current_lib()):
                if scnProp.cat_name_save.lower() == cartelle.lower():
                    text = "Warning, the category already exists in your library, try another name"
                    draw_info(text, "Info", 'INFO')
                    return {'FINISHED'}

        return wima().invoke_props_dialog(self, width=500)

    def execute(self, context):

        mats_categories = get_mats_categories()
        scn = context.scene
        scnProp = get_scnprop(scn)

        if scnProp.cat_name_save == '':
            return {'FINISHED'}

        scnProp.cat_name_save = scnProp.cat_name_save[0].upper() + scnProp.cat_name_save[1:]
        scnProp.cat_name_save = replace_forbidden_characters(scnProp.cat_name_save)
        dirName = os.path.join(current_lib(), scnProp.cat_name_save)

        os.mkdir(dirName)

        mats_categories['library'] = ""

        enum_up_category(self, context)
        enum_material_previews(self, context)

        scnProp.up_category = scnProp.cat_name_save

        scnProp.cat_name_save = ''

        return {'FINISHED'}
