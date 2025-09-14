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
import ntpath
import time

from ..library_manager.tools import get_json_data_faster
from ..utility.classes_utils import LibraryUtility
from ..utility.json_functions import get_json_data, save_json
from ..utility.utility import get_addon_preferences, get_percentage, natural_sort_v2


def update_installed_file_register():
    """ Questa funzione ha il compito di eliminare i files nel registro che non esistono piu nella libreria,
    questo può accadere specialmente se l'utente cancella manualmente un file o una cartella materiale, o una
    cartella Categoria, qualsiasi cosa cancellata manualmente rimane nel registro, quindi risulterà installata
    anche se in realtà non esiste. Quindi il registro deve aggiornarsi sulle azioni di aggiornamento dei materiali
    o di un ulteriore installazione"""

    preferences = get_addon_preferences()
    installed_file_register = os.path.join(preferences.addon_default_library, "._data", "installed_file_register.json")

    if not os.path.isfile(installed_file_register):
        return

    register_json_data = get_json_data(installed_file_register)
    if not register_json_data:
        return

    files = register_json_data.get('files')
    if not files:
        return

    for relativePath, unixTime in files.copy().items():
        filePath = os.path.join(preferences.addon_default_library, relativePath)
        if not os.path.isfile(filePath):
            files.pop(relativePath)
            register_json_data['total_files'] -= 1

    register_json_data['files'] = files
    register_json_data['modified'] = int(time.time())
    save_json(installed_file_register, register_json_data)



def get_info_library_bar():
    LibraryUtility.lib_percentage_bar = 0
    LibraryUtility.lib_object_installed = 0
    LibraryUtility.lib_object_online = 0
    # Funzione per aggiornare i valori percentuali delle librerie installate.
    # Chiamare il meno possibile per non sovraccaricare il processore.

    preferences = get_addon_preferences()
    installed_file_register_json = os.path.join(preferences.addon_default_library, "._data", "installed_file_register.json")
    library_info_json = os.path.join(preferences.addon_default_library, "._data", "library_info.json")


    installed_file_register_data = get_json_data_faster(installed_file_register_json)
    library_info_data = get_json_data_faster(library_info_json)

    if not installed_file_register_data or not library_info_data:
        return

    online_files_count = installed_files_count = 0

    installed_file_register_data = get_json_data(installed_file_register_json)
    library_info_data = get_json_data(library_info_json)


    if installed_file_register_data and library_info_data:
        installed_files = installed_file_register_data.get("files")
        if installed_files:
            installed_files_count = len([f for f in installed_files if f != "A_library_utility\\ESSENTIAL_LIB.zip"])

        online_files = library_info_data.get("online_files")
        if online_files:
            for idx in online_files:
                name = online_files[idx].get("name")
                if name != "ESSENTIAL_LIB.zip":
                    online_files_count += 1


        LibraryUtility.lib_percentage_bar = get_percentage(installed_files_count, online_files_count)
        LibraryUtility.lib_object_installed = installed_files_count
        LibraryUtility.lib_object_online = online_files_count



def get_volume_filepath_by_name(volume_name):
    """This function returns the volume filepath by name"""

    preferences = get_addon_preferences()
    volumes_installed_path = os.path.join(preferences.addon_default_library, "._data", "._volumes_installed")
    if not os.path.isdir(volumes_installed_path):
        return

    for volume_json_file in os.listdir(volumes_installed_path):
        # Read from the zip file the volume info
        volume_path = os.path.join(volumes_installed_path, volume_json_file)
        json_data = get_json_data(volume_path)

        if not json_data:
            continue

        if json_data.get("volume_name") == volume_name:
            return volume_path

class VolumesInstalled:

    volumes_installed = []
    online_json_data = None

    def __init__(self, recompile=True, reset=False):
        self.recompile = recompile
        if reset:
            cls = self.__class__
            cls.volumes_installed.clear()

    def get_online_json_data(self):
        cls = self.__class__
        if cls.online_json_data:
            return cls.online_json_data
        from ..library_manager.get_library_utils import risorse_lib
        online_json_path = os.path.join(risorse_lib(), 'online_utility', "exa_library_volumes.json")
        online_json_data = get_json_data(online_json_path)
        cls.online_json_data = online_json_data
        return cls.online_json_data

    def get(self):
        """Get the list of volume names installed from the library path if exists /._data/.volumes_installed/VolumeName.json"""
        cls = self.__class__
        from ..exaproduct import Exa

        preferences = get_addon_preferences()

        galp = get_all_libraries_paths()
        all_lib_paths = [galp.get("DEFAULT")] + galp.get("EXPANSION")

        if not self.recompile:
            if cls.volumes_installed:
                return cls.volumes_installed
        else:
            cls.volumes_installed.clear()


        for path in all_lib_paths:
            volumes_installed_path = os.path.join(path, "._data", "._volumes_installed")
            if not os.path.isdir(volumes_installed_path):
                continue

            for fn in os.listdir(volumes_installed_path):

                if not fn.endswith(".json"):
                    continue
                json_path = os.path.join(volumes_installed_path, fn)
                # Open json data:
                json_data = get_json_data(json_path)
                if not json_data:
                    continue

                if json_data.get("product") != Exa.product:
                    continue

                volume_name = json_data.get("volume_name")
                if not volume_name:
                    continue

                cls.volumes_installed.append(volume_name)

        cls.volumes_installed = natural_sort_v2(cls.volumes_installed)

        return cls.volumes_installed


def get_all_libraries_paths():
    """This function returns the list of all the libraries paths"""
    preferences = get_addon_preferences()

    libraries_paths = {"DEFAULT": preferences.addon_default_library, "USER": preferences.addon_user_library,
                       "EXPANSION": []}

    # Get the libraries into the expansion (If exists):
    for expansion in preferences.expansion_filepaths:
        path = expansion.path
        libraries_paths['EXPANSION'].append(path)


    return libraries_paths

def get_volume_info_from_exapack(zipfile):
    """This function returns the volume information from the exapack file as json data"""
    import zipfile as zf
    import json

    try:
        with zf.ZipFile(zipfile, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if not file.endswith(".json"):
                    continue

                with zip_ref.open(file) as json_file:
                    data = json.load(json_file)
                    # Check if into data exist the volume_info key, if so, return the data:
                    if type(data) == dict and data.get("volume_info"):
                        return data
    except:
        return None


def is_file_in_data_folder(relative_filepath):
    """This function checks if the filepath is a data folder"""
    # Is unuseful check if os.path.exists, we need only to check if the path of the file is in the data folder
    # And we check with the relative path
    if not "data" in relative_filepath:
        return False

    # The data folder is placed always in the root of the library at the level root\\Abandoned\\Roofless Ruins\\data\\
    # Check if data folder is placed at the 3 level of the root

    relative_filepath = ntpath.normpath(relative_filepath)
    split_path = relative_filepath.split(ntpath.normpath(os.sep))
    if len(split_path) < 3:
        return False

    if split_path[2] == "data":
        return True

def get_volumes_installed():
    """Get the list of volume names installed from the library path if exists /._data/.volumes_installed/VolumeName.json"""

    from ..exaproduct import Exa
    volumes_installed = []

    preferences = get_addon_preferences()

    galp = get_all_libraries_paths()
    all_lib_paths = [galp.get("DEFAULT")] + galp.get("EXPANSION")

    for path in all_lib_paths:
        volumes_installed_path = os.path.join(path, "._data", "._volumes_installed")
        if not os.path.isdir(volumes_installed_path):
            continue

        for fn in os.listdir(volumes_installed_path):
            if not fn.endswith(".json"):
                continue
            json_path = os.path.join(volumes_installed_path, fn)
            # Open json data:
            json_data = get_json_data(json_path)
            if not json_data:
                continue

            if json_data.get("product") != Exa.product:
                continue

            volume_name = json_data.get("volume_name")
            if not volume_name:
                continue

            volumes_installed.append(volume_name)

    return volumes_installed









