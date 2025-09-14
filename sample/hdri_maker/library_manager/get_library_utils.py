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

from ..exaconv import get_scnprop
from ..exaproduct import Exa
from ..utility.classes_utils import LibraryUtility
from ..utility.json_functions import get_json_data
from ..utility.utility import get_addon_dir, get_addon_preferences



def default_library_ok(path=None):
    """Funzione che restituisce se la libreria default è ok
    puoi inserire un path per controllare che sia un percorso alla default library,
    di default, controlla da solo"""

    addon_prefs = get_addon_preferences()
    default_lib = addon_prefs.addon_default_library if not path else path
    if LibraryUtility.last_default_lib_path:
        if LibraryUtility.last_default_lib_path == default_lib:
            if os.path.isdir(LibraryUtility.last_default_lib_path):
                return True

    lib_ok = False
    if os.path.isdir(default_lib):
        library_info_file = os.path.join(default_lib, "._data", "library_info.json")
        if os.path.isfile(library_info_file):
            library_info = get_json_data(library_info_file)
            if library_info:
                lib_product = library_info.get("library_product")
                lib_version = library_info.get("library_version")
                if lib_product and lib_product == Exa.product:
                    if lib_version and lib_version == Exa.library_version:
                        lib_ok = True
                        LibraryUtility.last_default_lib_path = addon_prefs.addon_default_library

    return lib_ok

def user_library_ok():
    addon_prefs = get_addon_preferences()
    user_lib = addon_prefs.addon_user_library
    return os.path.isdir(user_lib)

def libraries_ready():
    if user_library_ok() and default_library_ok():
        return True

def libraries_path():
    # DEFAULT per tutte le librerie di tipo predefinito
    # USER solo per la libreria dell'utente
    # Le librerie aggiunte come espansioni daranno a libraries_selector il percorso esatto a quella libreria
    scn = bpy.context.scene

    scnProp = get_scnprop(scn)

    addon_prefs = get_addon_preferences()

    risorse = os.path.join(get_addon_dir(), "addon_resources")

    if scnProp.libraries_selector == 'DEFAULT':
        current_library = bpy.path.abspath(addon_prefs.addon_default_library)
    elif scnProp.libraries_selector == 'USER':
        current_library = bpy.path.abspath(addon_prefs.addon_user_library)
    elif os.path.isdir(scnProp.libraries_selector):
        current_library = bpy.path.abspath(scnProp.libraries_selector)
    else:
        current_library = ""

    return current_library, risorse

def current_lib():
    current_library, risorse_library = libraries_path()
    return current_library

def risorse_lib():
    current_library, risorse_library = libraries_path()
    return risorse_library


def set_material_preview(libraries_selector, up_category, material_preview):
    """Funzione che setta il materiale di preview per la libreria"""
    scn=bpy.context.scene
    scnProp = get_scnprop(scn)
    try: scnProp.libraries_selector = libraries_selector
    except: pass
    try: scnProp.up_category = up_category
    except: pass

    try:
        from library_manager.main_pcoll_attributes import set_winman_main_preview
        set_winman_main_preview(material_preview)
    except: pass


def make_library_info(path, library_type, library_name=""):

    if library_type == 'DEFAULT' or library_name == "":
        library_name = 'DEFAULT'

    json_data = \
        {
            "library_version": Exa.library_version,
            "library_product": Exa.product,
            "library_type": library_type,
            "library_name": library_name
        }

    data_folder = os.path.join(path, "._data")
    if not os.path.isdir(data_folder):
        os.mkdir(data_folder)
    library_info_file = os.path.join(data_folder, "library_info.json")
    import json
    with open(library_info_file, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

    # Write readme file:
    # Make title with big letters:
    title = library_type.title()
    readme_file = os.path.join(data_folder, "README.txt")

    text = "Please, do not modify or delete anything contained in the ._data folder, " \
           "otherwise the addon may not work properly." \
           "If you intend to move the libraries manually from one computer to another, you can do it safely," \
           " just make sure that it contains the ._data folder"

    with open(readme_file, 'w') as outfile:
        outfile.write(f"{title} library for {Exa.product} {Exa.library_version}")
        # Make blank line:
        outfile.write("\r")
        # Keep text column like the text declared above:
        for line in text.splitlines():
            outfile.write(f"\r{line}")

    return json_data








