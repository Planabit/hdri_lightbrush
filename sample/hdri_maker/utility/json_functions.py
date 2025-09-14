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

import json
import os

def is_valid_json_text(json_text):
    # Buona cosa testare se il file json è valido prima di tutto, accetta solo stringhe!
    # Quindi utile per "requests.get"
    try:
        json_object = json.loads(json_text)
        return json_object
    except:
        return False

def get_json_data(path, remove_if_invalid=False):
    # Carica il json in una variabile data, se non esiste il path restituisce None
    broken_json = False
    data = None
    if os.path.isfile(path):
        with open(path) as f:
            # noinspection PyBroadException
            try:
                data = json.load(f)
            except:
                print("From Fc get_json_data, Invalid Json file:", path)
                broken_json = True

    if broken_json:
        if remove_if_invalid:
            try:
                os.remove(path)
            except:
                print("From Fc get_json_data, Can't remove invalid json file:", path)

    return data

def create_json_data(data_list):
    # Funzione che scrive il json dato un dizionario
    data = {}
    for element, value in data_list.items():
        data[element] = value
    return data

def save_json(save_path, data, indent=4):
    # Funzione che salva il json dato un dizionario
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)

