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
import os.path

import bpy

from .get_library_utils import default_library_ok
from ..convert_old_library_to_new.convert_functions import is_new_library
from ..exaconv import get_scnprop
from ..ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
from ..utility.utility import get_addon_preferences
from ..web_tools.get_user_data import context_addon_data


def set_libraries_location():
    addon_preferences = get_addon_preferences()
    # Qui setta nel json i percorsi delle librerie da tenere in memoria
    data = {}
    if is_new_library(addon_preferences.addon_default_library, get_library_type="DEFAULT"):
        data['default_lib'] = addon_preferences.addon_default_library
    # else:
    #     if not os.path.isdir(addon_preferences.addon_default_library):
    #         data['default_lib'] = ""

    if is_new_library(addon_preferences.addon_user_library, get_library_type="USER"):
        data['user_lib'] = addon_preferences.addon_user_library
    # else:
    #     if not os.path.isdir(addon_preferences.addon_default_library):
    #         data['user_lib'] = ""

    expansion_filepaths = addon_preferences.expansion_filepaths

    for exp in expansion_filepaths:
        if exp.name and os.path.isdir(exp.path):
            expansion_libs = data.get("expansion_libs")
            if not expansion_libs:
                data['expansion_libs'] = {}
            data['expansion_libs'][exp.name] = exp.path

    if data:
        context_addon_data(data=data)


def get_libraries_location(adjust=None):
    """Questa funzione tenta di restituire i percorsi di dove erano installate le librerie sul disco utente
    nel caso esistano vecchi percorsi nel json che non ci sono piu, questi vengono cancellati
    Input: adjust=Bool Questo se True, applica i percorsi trovati nel json,
    se i percorsi attuali dell'addon non sono impostati correttamente
    """
    addon_data = context_addon_data(remove_if_invalid=True)
    if not addon_data:
        return

    addon_preferences = get_addon_preferences()

    default_lib = addon_data.get("default_lib")
    user_lib = addon_data.get("user_lib")

    if default_lib and os.path.isdir(default_lib):
        default_library_ok(path=default_lib)
        if adjust:
            addon_preferences.addon_default_library = default_lib

    if user_lib and os.path.isdir(user_lib):
        if os.path.isdir(user_lib):
            if adjust:
                addon_preferences.addon_user_library = user_lib

    # Qui vogliamo ottenere anche i percorsi delle librerie espansioni se esistono

    expansion_libs = addon_data.get("expansion_libs")
    if expansion_libs:
        for name, location in expansion_libs.items():
            # Search if the expansion name is installed
            expansions = addon_preferences.expansion_filepaths
            if not name in [exp.name for exp in expansions if name == exp.name]:
                # In questo caso va aggiunta la nuova espansione
                if os.path.isdir(location):
                    expansion_filepaths = addon_preferences.expansion_filepaths
                    exp = expansion_filepaths.add()
                    exp.name = name
                    exp.path = location
                    exp.display = True

    refresh_interface()

    return {"default_lib": default_lib, "user_lib": user_lib, "expansion_libs": expansion_libs}


def update_lib(self, context):
    try:
        scnProp = get_scnprop(context.scene)
        scnProp.libraries_selector = 'DEFAULT'
        set_libraries_location()
        bpy.ops.wm.save_userpref()
    except:
        pass
