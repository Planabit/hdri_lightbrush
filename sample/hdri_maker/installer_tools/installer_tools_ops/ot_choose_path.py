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
from bpy.props import StringProperty, IntProperty
from bpy.types import Operator

from ...exaconv import get_default_library_folder_name, get_user_library_folder_name, get_scnprop
from ...exaproduct import Exa
from ...utility.text_utils import draw_info
from ...utility.utility import wima, get_addon_preferences, redraw_all_areas, is_inside_path


class HDRIMAKER_OT_ChoosePath(Operator):
    """Choose a Path"""
    bl_idname = Exa.ops_name+"choosepath"
    bl_label = "Choose path"
    bl_options = {'INTERNAL'}

    options: StringProperty(options={'HIDDEN'})
    directory: StringProperty(subtype='DIR_PATH')
    filepath: StringProperty()
    index: IntProperty(options={'HIDDEN'})
    override = None

    def invoke(self, context, event):
        self.filepath = ""
        wima().fileselect_add(self)
        return {'RUNNING_MODAL'}

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'MAKE_DIRS_PATHS':
            desc = "Choose a path"
        return desc

    def execute(self, context):

        addon_prefs = get_addon_preferences()
        scn = context.scene
        scnprop = get_scnprop(scn)

        # Questo operatore sceglie solo un percorso, il tipo di options dirà cosa fare
        if self.options == 'MAKE_DIRS_PATHS':
            if os.path.isdir(self.directory):
                addon_prefs.install_temp_root_default_lib = ""
                addon_prefs.install_temp_root_user_lib = ""

                addon_prefs.addon_default_library = ""
                addon_prefs.addon_user_library = ""
                addon_prefs.install_temp_root_default_lib = os.path.join(self.directory, get_default_library_folder_name())
                addon_prefs.install_temp_root_user_lib = os.path.join(self.directory, get_user_library_folder_name())

        elif self.options == 'USER_LIB_EXIST':
            if os.path.isdir(self.directory):
                addon_prefs.install_temp_root_user_lib = ""
                addon_prefs.addon_user_library = os.path.normpath(self.directory)

            redraw_all_areas()

        elif self.options == 'LINK_DEFAULT_LIB':
            default_lib = os.path.normpath(self.directory)
            if os.path.isdir(default_lib):
                addon_prefs.addon_default_library = default_lib

            from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
            refresh_interface()

        elif self.options == 'LINK_USER_LIB':
            user_lib = os.path.normpath(self.directory)
            if os.path.isdir(user_lib):
                addon_prefs.addon_user_library = user_lib

            from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
            refresh_interface()

        elif self.options == 'ADD_EXPANSION_PATH':
            # Aggiunge percorso alle espansioni
            dir = os.path.normpath(self.directory)
            if os.path.isdir(dir):
                # self.index è dato dall'enum della collection prop (expansion_filepaths)
                addon_prefs.expansion_filepaths[self.index].path = dir
            from ...library_manager.tools import get_library_info
            library_info = get_library_info(dir)
            if library_info:
                library_name = library_info.get("library_name")
                if library_name:
                    addon_prefs.expansion_filepaths[self.index].name = library_name
                else:
                    # Se non c'è il nome della libreria, mettiamo il nome della cartella
                    addon_prefs.expansion_filepaths[self.index].name = os.path.basename(dir)
            else:
                # Se non c'è il nome della libreria, mettiamo il nome della cartella
                addon_prefs.expansion_filepaths[self.index].name = os.path.basename(dir)

        elif self.options == 'BAKE_PATH':
            scnProp = get_scnprop(context.scene)
            scnProp.bake_dirpath = os.path.normpath(self.directory)
            return {'FINISHED'}

        elif self.options == 'BATCH_FROM_PATH':
            dir = os.path.normpath(self.directory)
            addon_prefs.from_batch_path = dir

        elif self.options == 'CONVERT_DEFAULT_LIB_PATH':
            dir_path = os.path.normpath(self.directory)
            if is_inside_path(addon_prefs.addon_default_library, dir_path):
                scnprop.convert_to_new_default_lib_path = ""

                text = "Please select a path outside the default library, you are trying to convert the default library inside itself"
                draw_info(text, "Info", "INFO")
                return {'CANCELLED'}

            scnprop.convert_to_new_default_lib_path = dir_path

        elif self.options == 'CONVERT_USER_LIB_PATH':
            dir_path = os.path.normpath(self.directory)
            if is_inside_path(addon_prefs.addon_user_library, dir_path):
                scnprop.convert_to_new_user_lib_path = ""

                text = "Please select a path outside the user library, you are trying to convert the user library inside itself"
                draw_info(text, "Info", "INFO")
                return {'CANCELLED'}

            scnprop.convert_to_new_user_lib_path = dir_path

        bpy.ops.wm.save_userpref()

        redraw_all_areas()

        return {'FINISHED'}
