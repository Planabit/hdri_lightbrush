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

from bpy.types import Operator

from ..check_tools import VolumesInstalled
from ...convert_old_library_to_new.convert_functions import is_new_library
from ...exaproduct import Exa
from ...utility.text_utils import draw_info


class HDRIMAKER_OT_try_compile_exapack(Operator):
    bl_idname = Exa.ops_name + "try_compile_exapack"
    bl_label = "Compare with Exapack"
    bl_description = "Compare this snippet with the one in Exapack"
    bl_options = {'REGISTER', 'INTERNAL'}

    libraries_files = {}

    @classmethod
    def description(cls, context, properties):

        desc = "Compare the installed files only for the default library with those in the Exapack online files, and " \
               "compile the list of exapack completely installed, it also works if you come from an update from " \
               "Extreme PBR with libraries installed via the Extreme-Addons.com website"

        return desc

    def execute(self, context):
        # get all files installed into the default_library and other libraries
        from ...utility.utility import get_addon_preferences

        VolumesInstalled.volumes_installed.clear()  # Importante, questo tiene traccia dei volumi installati.
        VolumesInstalled.online_json_data = None

        cls = self.__class__

        preferences = get_addon_preferences()
        addon_default_library = preferences.addon_default_library

        if not is_new_library(addon_default_library, get_library_type="DEFAULT"):
            text = "You must install the default library to use this function"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        from ...library_manager.get_library_utils import risorse_lib
        exa_library_volumes_file = os.path.join(risorse_lib(), 'online_utility', "exa_library_volumes.json")

        if not os.path.isfile(exa_library_volumes_file):
            text = "Press Check library updates, and try again"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        from ...utility.json_functions import get_json_data
        exa_library_volumes_data = get_json_data(exa_library_volumes_file)

        if not exa_library_volumes_data:
            text = "Press Check library updates, and try again"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        exapacks = exa_library_volumes_data.get('exapacks')
        if not exapacks:
            text = "Press Check library updates, and try again"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        cls.libraries_files['DEFAULT_LIBRARY'] = []
        index = 0
        for root, dirs, files in os.walk(addon_default_library):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), addon_default_library)
                cls.libraries_files['DEFAULT_LIBRARY'].append(relative_path)
                index += 1

        # Ora che abbiamo tutti i file della default library in formato relativo, possiamo compararli col formato relativo
        # presente nei files Exapack Library.json online, per capire quali file mancano.

        data_folder = os.path.join(addon_default_library, "._data")
        if not os.path.isdir(data_folder):
            try:
                os.mkdir(data_folder)
            except:
                text = "Failed to create the ._data folder, please check the permissions, try to execute Blender as administrator"
                draw_info(text, "Info", 'INFO')
                self.report({'INFO'}, text)
                return {'CANCELLED'}

        volumes_installed_path = os.path.join(addon_default_library, "._data", "._volumes_installed")
        if not os.path.isdir(volumes_installed_path):
            try:
                os.mkdir(volumes_installed_path)
            except:
                text = "Failed to create the ._volumes_installed folder, please check the permissions, try to execute Blender as administrator"
                draw_info(text, "Info", 'INFO')
                self.report({'INFO'}, text)
                return {'CANCELLED'}

        for volume_name, volumes_data in exapacks.items():
            files_dict = volumes_data.get('files_dict')
            if not files_dict:
                continue

            new_volume = {}
            n = new_volume = {}
            v_name_key = exapacks[volume_name]
            n['volume_info'] = v_name_key.get('volume_info')
            n['product'] = v_name_key.get('product')
            n['library_name'] = v_name_key.get('library_name')
            n['library_type'] = v_name_key.get('library_type')
            n['library_version'] = v_name_key.get('library_version')
            n['total_files'] = v_name_key.get('total_files')
            n['volume_version'] = v_name_key.get('volume_version')
            n['volume_name'] = v_name_key.get('volume_name')
            n['uncompressed_size'] = v_name_key.get('uncompressed_size')
            n['replace_the_volumes'] = v_name_key.get('replace_the_volumes')
            fd = n['files_dict'] = {}

            total_files = 0
            for dict_index, index_dict in files_dict.items():
                file_path = index_dict.get('file_path')
                if not file_path:
                    continue
                if not file_path in cls.libraries_files['DEFAULT_LIBRARY']:
                    continue

                new_file_dict = fd[dict_index] = {}
                new_file_dict['file_size'] = index_dict.get('file_size')
                new_file_dict['file_name'] = index_dict.get('file_name')
                new_file_dict['file_path'] = index_dict.get('file_path')
                total_files += 1

            # Len files_dict se il numero di chiave 8Stringa) non è negativo
            files_dict_number = len([key for key in files_dict.keys() if key.isdigit() and int(key) >= 0])

            if total_files == files_dict_number:
                # In questo caso scriviamo il json con il nome del volume, e con la data new_volume_name al percorso
                # volumes_installed_path
                from ...utility.json_functions import save_json
                save_path = os.path.join(volumes_installed_path, volume_name + ".json")
                save_json(save_path, new_volume)

        VolumesInstalled.volumes_installed.clear()  # Importante, questo tiene traccia dei volumi installati.
        VolumesInstalled.online_json_data = None

        return {'FINISHED'}
