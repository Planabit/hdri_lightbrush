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
# #

import os

from ..exaproduct import Exa
from .requests_utility import requests_get, get_json_from_respose
from ..utility.json_functions import save_json, get_json_data
from ..utility.utility import get_version_to_int


def get_json_online(urls=None, params=None, save_name="", show_popup=True):
    """In questo processo, se non riesce a scaricare un file json, restituisce un file json pre-scritto su disco"""
    media_content = None
    # Questa funzione, quando viene chiamata (Cioè all'apertura del menu Social & Updates) o in altre occasioni, tenta di connettersi a internet e restituisce un file json
    # Se non riesce a connettersi , o il file json non è corretto , utilizzerà il file json già presente in extreme pbr
    # In sostanza scrive il json nella directory di extreme pbr, in maniera da averlo sempre sul disco

    from ..library_manager.get_library_utils import risorse_lib

    json_folder = os.path.join(risorse_lib(), "online_utility")
    if not os.path.isdir(json_folder):
        os.mkdir(json_folder)
    json_file = os.path.join(json_folder, save_name)

    media_exa = None
    # Numero tentativi prima di lanciare un messaggio di errore di connessione nel caso tutte le url siano offline o affini
    total_try = len(urls) - 1
    for idx, url in enumerate(urls):
        # Se l'ultimo tentativo fallisce, lancia un messaggio all'utente
        get_status = True if total_try == idx else False

        if ('extreme-addons') in url:
            referrer = {"referrer": Exa.blender_manifest['name'] + " " + Exa.blender_manifest['edition'] + " " + str(Exa.blender_manifest['version'])}
            params = {"id": Exa.product_id}
            time_out = 10
        else:
            params = None
            referrer = None
            time_out = 10

        # TODO: Pensare a una requests post per tenere traccia da dove arrivano richieste e a mettere le richieste tutte in un posto solo
        # Andre qui il primo tentativo lo fai a extreme addons, url ancora da definire
        print(Exa.product + " Try to connect from: " + url)
        media_exa = requests_get(url, params=params, timeout=time_out, headers=referrer, get_status=get_status)
        if media_exa:
            print(Exa.product + " Connected from:", url)
            break

    if media_exa:
        # media_exa è una risposta di requests
        json_data = get_json_from_respose(media_exa, url, show_popup=show_popup)
        if json_data:  # Se non è un json valido non lo scrive, e mantiene il json che esiste già
            json_exa_data = json_data.get("data")
            if json_exa_data:
                json_data = json_exa_data
            save_json(json_file, json_data)

    # Questo passaggio è per essere sicuri di restituire qualcosa all'utente, nel caso la chiamata non avesse successo,
    # sul disco potrebbero esserci salvati json precedenti, quindi utilizzerebbe quelli
    json_data = get_json_data(json_file)

    if json_data:
        return json_data
    else:
        # Se non trova un file json, restituisce un dizionario vuoto, da usare con metodo get() quindi nessun errore in caso
        return {}


def get_lost_updates_list(updates):
    # Questa funzione restituisce una lista di eventuali updates persi, esamina la versioni in comparazione a quella
    # corrente.
    if updates is None:
        return []

    updates_copy = updates.copy()

    current_int_version = get_version_to_int(Exa.blender_manifest.get('version'))
    for update_key in list(updates_copy):
        version_int = get_version_to_int(update_key)
        # If current_int_version is None, need to bypass the check
        if version_int is None or current_int_version is None:
            continue
        if version_int <= current_int_version:
            updates_copy.pop(update_key, None)

    return updates_copy
