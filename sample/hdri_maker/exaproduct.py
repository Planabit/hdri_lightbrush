# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Copyright 2024(C) Andrea Donati
#
import os
from pathlib import Path

import toml


def change_old_api_to_v3(url):
    """This function changes the old API to the new one."""
    old_api = "https://extreme-addons.com/wp-json/ea-repository/v2/"
    api_v3 = "https://extreme-addons.com/wp-json/exa/v3/"
    if old_api in url:
        url = url.replace(old_api, api_v3)
    return url


def get_docs_homepage():
    """Nota bene, questa funzione restituisce la homepage della documentazione, e attenzione, se non esiste il file exa_manual.json
    non restituisce nulla, questo è studiato per non far aspettare tempo all'utente per la connessione, o se la connessione non c'è"""

    json_file = os.path.join(os.path.dirname(__file__), "addon_resources", "online_utility", "exa_manual.json")
    if not os.path.isfile(json_file):
        return ""

    import json
    json_data = None
    try:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
    except:
        return ""

    if not json_data:
        return ""

    docs_homepage = json_data.get("docs_homepage")
    if docs_homepage:
        return docs_homepage

    return ""

p = Path(__file__).with_name('blender_manifest.toml')
class Exa(object):
    # Use ops_name in the operators as a prefix for the idname
    ops_name = "hdrimaker."

    blender_manifest = toml.load(p)

    product = 'HDRI_MAKER'
    product_id = 89
    addon_data_file = "hdri_maker_data.json"
    addon_data_utils_file = "hdri_maker_data_utils.json"

    library_version = 3  # This is the version of the library for this version of the addon

    url_docs = get_docs_homepage()
    ulr_website = "https://www.extreme-addons.com"

    # ------------------------------------------------------------------------------------------
    # -----------------------------    Urls solo su Exa
    # url_core = "https://extreme-addons.com/wp-json/ea-repository/v2/getCore"
    # url_core = "https://extreme-addons.com/wp-json/exa/v3/getCore?product=EXTREME_PBR"

    # url_json_lib = "https://extreme-addons.com/wp-json/ea-repository/v2/getAllLibraries"
    # url_json_lib = "https://extreme-addons.com/wp-json/exa/v3/getAllLibraries"
    # url_activation = "https://extreme-addons.com/wp-json/ea-license/v1/verify" ( V1 )
    # url_activation = "https://extreme-addons.com/wp-json/exa/v3/getToken"

    url_refresh_token = "https://extreme-addons.com/wp-json/exa/v3/refreshToken"

    # ------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------
    # -----------------------------    Exa settings:
    urls_orderpages = ["https://raw.githubusercontent.com/ExtremeAddons/extreme_addons_docs/master/exa_orderpages.json"]

    urls_social = ["https://raw.githubusercontent.com/ExtremeAddons/extreme_addons_docs/master/exa_social.json"]

    urls_exa_urls = ["https://raw.githubusercontent.com/ExtremeAddons/extreme_addons_docs/master/exa_urls.json"]

    urls_news = ["https://raw.githubusercontent.com/ExtremeAddons/extreme_addons_docs/master/exa_news.json"]

    # ------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------
    # -----------------------------    Exa Product:
    urls_update = ["https://raw.githubusercontent.com/ExtremeAddons/hdri_maker_docs/master/exa_update.json"]  # on?product=EXTREME_PBR&type=Updates

    urls_manual = ["https://raw.githubusercontent.com/ExtremeAddons/hdri_maker_docs/master/exa_manual.json"]

    urls_exa_libraries_volumes = ["https://raw.githubusercontent.com/ExtremeAddons/hdri_maker_docs/master/exa_library_volumes.json"]

    top_addons = ["https://raw.githubusercontent.com/ExtremeAddons/extreme_addons_docs/master/exa_top_addons.json"]


addons = []
def get_addon_module_name():
    """Da Blender 4.2 il nome dell'addon sarà tipo "bl_ext.user_default.addon_name" e non piu "addon_name" se installato
     nella nuova maniera, altrimenti restituirà sempre il nome corretto"""
    # Attenzione, questo restituisce il nome
    if addons:
        return addons[0]

    addon_folder_name = __name__.split(".")[-2] # questo è il nome della cartella dell'addon

    import addon_utils
    for mod in addon_utils.modules():
        if addon_folder_name in mod.__name__:
            addons.append(mod.__name__)
            return mod.__name__