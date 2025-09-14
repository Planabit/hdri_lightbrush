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
import json
import os
import platform
import socket

import bpy

from ..exaproduct import Exa
from ..utility.json_functions import save_json, get_json_data
from ..utility.text_utils import draw_info
from ..utility.utility import get_addon_preferences, get_mac_address, open_user_pref, base_64_to_encode_string, \
    get_blender_addons_folder, base_64_to_decode_string, get_addon_dir


def get_extreme_addons_folder(product_subfolder=""):

    blender_addons_folder = get_blender_addons_folder()
    if not os.path.isdir(blender_addons_folder):
        return ""

    exa_folder = os.path.join(blender_addons_folder, 'ExtremeAddons')
    if not os.path.isdir(exa_folder):
        try:
            os.mkdir(exa_folder)
            if not product_subfolder:
                return exa_folder
        except OSError as e:
            print("From exa_folder()", e)
            return ""

    if not product_subfolder:
        return exa_folder

    product_folder = os.path.join(exa_folder, product_subfolder)
    if os.path.isdir(product_folder):
        return product_folder
    else:
        try:
            os.mkdir(product_folder)
            return product_folder
        except OSError as e:
            print("From product_folder()", e)
            return ""

def set_login_data():
    data = context_addon_data()
    if not data:
        return

    preferences = get_addon_preferences()

    email = data.get("email")
    if email:
        preferences.exa_mail = preferences.exa_mail_hide = base_64_to_decode_string(email)

    password = data.get("password")
    if password:
        preferences.exa_password = preferences.exa_password_hide = base_64_to_decode_string(password)

    product_license = data.get("license")
    if product_license:
        preferences.exa_product_license = preferences.exa_product_license_hide = base_64_to_decode_string(
            product_license)

def context_addon_data(data=None, get_data="ADDON_DATA_FILE", remove_if_invalid=False):
    """Se vuoi scrivere il contenuto, compila il campo data={}
    altrimenti non scrivere nulla se vuoi semplicemente ottenere il contenuto del json"""

    extreme_addons_folder = get_extreme_addons_folder(product_subfolder="hdri_maker_data")
    if not os.path.isdir(extreme_addons_folder):
        return

    if get_data == 'ADDON_DATA_FILE':
        file_name = Exa.addon_data_file

    elif get_data == 'ADDON_DATA':
        file_name = Exa.addon_data_utils_file

    context_addon_data_json = os.path.join(extreme_addons_folder, file_name)
    if data:
        # Qui deve inserire i nuovi dati, tenendo i vecchi, se già presenti le keys, queste vengono sovrascritti (Ovviamente)
        if os.path.isfile(context_addon_data_json):

            existent_json_data = get_json_data(context_addon_data_json)
            if not existent_json_data:
                try: os.remove(existent_json_data)
                except: pass

                return

            for key, value in data.items():
                existent_json_data[key] = value
            save_json(context_addon_data_json, existent_json_data)
        else:
            save_json(context_addon_data_json, data)

        return data

    if os.path.isfile(context_addon_data_json):
        data = get_json_data(context_addon_data_json, remove_if_invalid=remove_if_invalid)
        return data

def add_ids(computer_name_encoded, mac_encoded, system_os):
    addon_preferences = get_addon_preferences()
    item = addon_preferences.computer_ids.add()
    item.idx = len(addon_preferences.computer_ids) + 1
    item.pcName = computer_name_encoded
    item.mac_adress = mac_encoded
    item.system_os = system_os

def store_computer_ids(computer_name_encoded, mac_encoded, system_os):
    addon_preferences = get_addon_preferences()

    # qui deve massimo inserire 3 mac adress diversi, per non dare problemi agli utenti se cambiano la scheda con cui si connettono
    if len(addon_preferences.computer_ids) < 3:
        # Caso primo adress registrazione
        added = False
        if not [n for n in addon_preferences.computer_ids if n.pcName == computer_name_encoded]:
            if not [n for n in addon_preferences.computer_ids if n.system_os == system_os]:
                if not [n for n in addon_preferences.computer_ids if n.mac_adress == mac_encoded]:
                    add_ids(computer_name_encoded, mac_encoded, system_os)
                    added = True

        if not added:
            # Caso in cui pc Name e Os siano uguali ma la scheda di rete diversa:
            if [n for n in addon_preferences.computer_ids if n.pcName == computer_name_encoded]:
                if [n for n in addon_preferences.computer_ids if n.system_os == system_os]:
                    if not [n for n in addon_preferences.computer_ids if n.mac_adress == mac_encoded]:
                        add_ids(computer_name_encoded, mac_encoded, system_os)

    if addon_preferences.last_ok_computer:
        for item in addon_preferences.computer_ids:
            if item.pcName + "," + item.system_os + "," + item.mac_adress == addon_preferences.last_ok_computer:
                # Deve restituire sempre questa tripletta per avere i dati di accesso giusti
                return item.pcName, item.mac_adress, item.system_os

    return computer_name_encoded, mac_encoded, system_os


def user_credential_ok():
    # bpy.ops.extremepbr.checklicense(show_message=False)
    bpy.ops.extremepbr.checklicensev2(show_message=False)
    preferences = get_addon_preferences()

    if preferences.exa_license in ['LICENSE_TO_DO', 'LICENSE_VALIDATION_FAILED', 'LICENSE_IN_USE_BY_ANOTHER_COMPUTER']:
        open_user_pref(None, 'EXA')
        text = "Please enter your credentials correctly to continue the process you requested" + \
               "Problem: " + preferences.exa_license.title().replace("_", " ")
        draw_info(text, "Info", 'INFO')
        return False
    elif preferences.exa_license == 'OFFLINE':
        return False
    else:
        return True

def get_user_data(chunk=0, get_json=False):
    """ Chiamata standard per attivare l'addon """
    blender_version = ""
    try:
        blender_version = bpy.app.version_string
    except:
        pass

    preferences = get_addon_preferences()

    mac_address = get_mac_address()
    computer_name = socket.getfqdn(socket.gethostname())
    system_os = platform.system()

    clean_mail = preferences.exa_mail.replace(" ", "")
    mail_encoded = base_64_to_encode_string(clean_mail)
    passw_encoded = base_64_to_encode_string(preferences.exa_password)
    mac_encoded = base_64_to_encode_string(mac_address)
    computer_name_encoded = base_64_to_encode_string(computer_name)

    computer_name_encoded, mac_encoded, system_os = store_computer_ids(computer_name_encoded, mac_encoded, system_os)

    data = {
        "passw_encr": 1,
        "email": mail_encoded,
        "license": preferences.exa_product_license.replace(" ", ""),
        "password": passw_encoded,
        "mac": mac_encoded,
        "pcName": computer_name_encoded,
        "OS": system_os,
        "product": Exa.product,
        "version": str(Exa.blender_manifest.get("version")),
        "blender": blender_version,
        "chunk": chunk
    }


    if get_json:
        data = json.dumps(data, indent=None)

    return data

def get_token_from_json():
    token = refresh_token = None
    risorse = os.path.join(get_addon_dir(), "addon_resources")
    json_path = os.path.join(risorse, "online_utility", "exa_tok.json")
    if not os.path.isfile(json_path):
        return None, None

    data = get_json_data(json_path)
    if data:
        token = data.get("token")
        refresh_token = data.get("refresh_token")

    return token, refresh_token

def write_tokens_to_json(token=None, refresh_token=None):

    risorse = os.path.join(get_addon_dir(), "addon_resources")
    json_path = os.path.join(risorse, "online_utility", "exa_tok.json")

    if os.path.isfile(json_path):
        data = get_json_data(json_path)
        if not data:
            data = {}
    else:
        data = {}

    if token:
        data['token'] = token
    if refresh_token:
        data['refresh_token'] = refresh_token

    save_json(json_path, data)

    return data

