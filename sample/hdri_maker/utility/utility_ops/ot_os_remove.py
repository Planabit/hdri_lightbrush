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

from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator

from ..classes_utils import LibraryUtility
from ..utility import wima, redraw_all_areas
from ...exaproduct import Exa
from ...library_manager.get_library_utils import risorse_lib
from ...utility.utility_dependencies import load_starting_message
from ...web_tools.get_user_data import get_extreme_addons_folder


class HDRIMAKER_OT_purge_cache(Operator):
    bl_idname = Exa.ops_name + "purge_cache"
    bl_label = "Remove"
    bl_options = {'INTERNAL'}

    path: StringProperty()
    options: StringProperty()
    confirm: EnumProperty(default='NO', items=(('NO', "No", ""), ('YES', "Yes", "")))
    attribute: StringProperty()

    @classmethod
    def description(cls, context, properties):
        options = properties.options
        desc = ""
        if options == 'PURGE_EXA_CACHE':
            desc = "Removes stored data about Library Paths, User Data"
        return desc

    def invoke(self, context, event):
        self.confirm = 'NO'
        return wima().invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        col.separator()
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="Are you sure? Check it well")
        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.prop(self, 'confirm', expand=True)
        col.separator()
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="Press Yes and Ok to confirm, or Esc To Abort")

    def execute(self, context):

        if self.confirm == 'NO':
            return {'FINISHED'}

        if self.options == 'PURGE_EXA_CACHE':
            # Remove all the files in the extreme addons folder, Extreme addons folder is external to the addon folder
            ExtremeAddons_folder = get_extreme_addons_folder()
            if ExtremeAddons_folder:
                hdri_maker_data_folder = os.path.join(ExtremeAddons_folder, 'hdri_maker_data')
                if hdri_maker_data_folder:
                    for fn in os.listdir(hdri_maker_data_folder):
                        fp = os.path.join(hdri_maker_data_folder, fn)
                        if os.path.isfile(fp):
                            try:
                                os.remove(fp)
                            except:
                                pass
                        elif os.path.isdir(fp):
                            try:
                                shutil.rmtree(fp)
                            except:
                                pass

            # Folder containing the exa_update file etc.
            online_utility_folder = os.path.join(risorse_lib(), 'online_utility')
            if online_utility_folder:
                for fn in os.listdir(online_utility_folder):
                    fp = os.path.join(online_utility_folder, fn)
                    if os.path.isfile(fp):
                        try:
                            os.remove(fp)
                        except:
                            pass
                    elif os.path.isdir(fp):
                        try:
                            shutil.rmtree(fp)
                        except:
                            pass

        redraw_all_areas()
        return {'FINISHED'}
