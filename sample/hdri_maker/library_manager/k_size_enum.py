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

from .get_library_utils import current_lib
from .main_pcoll_attributes import get_winman_main_preview
from .textures_pcoll import enum_material_textures
from .textures_pcoll_attributes import set_winman_texture_preview
from ..exaconv import get_scnprop
from ..utility.utility import natural_sort

k_size_list = {'list': [], 'preview': '', 'old_index': 0}


def get_k_size_list():
    global k_size_list
    return k_size_list


def update_k_size(self, context):
    global k_size_list
    k_size_list['old_index'] = next((k_size_list['list'].index(i) for i in k_size_list['list'] if i[0] == self.k_size),
                                    None)


def set_k_size(self, context):
    global k_size_list
    scnProp = get_scnprop(context.scene)

    # Questa funzione utile per settare un k_size, poiché se si passa da aver selezionato 8k a un materiale che non ha tale indice, si scala di 1
    old_idx = k_size_list.get('old_index')
    current_list_k_size = enum_k_size(self, context)
    current_idx_list = len(current_list_k_size) - 1

    if old_idx and old_idx > current_idx_list:
        scnProp.k_size = current_list_k_size[current_idx_list][0]
    elif scnProp.k_size == '':
        scnProp.k_size = current_list_k_size[0][0]

    # Set the first material !TEXTURE! preview
    first_textures = enum_material_textures(self, context)[0][0]
    set_winman_texture_preview(first_textures)


# ###########################################################################################################
# ##############================Size Of Texture==============################################################
def k_size_compo_string(minimum=1, maximum=18):
    k_strings = []
    k_strings.append("_05k")
    for n in range(minimum, maximum):
        k_strings.append("_" + str(n) + "k")
        if n < 10:
            k_strings.append("_0" + str(n) + "k")
    return k_strings


def enum_k_size(self, context):
    global k_size_list
    preview = get_winman_main_preview()

    if k_size_list["preview"] == preview:
        return k_size_list["list"]

    k_size_list["list"].clear()
    k_size_list["preview"] = preview

    scnProp = get_scnprop(context.scene)

    current_cat_dir = os.path.join(current_lib(), scnProp.up_category)

    k_list = []
    if os.path.isdir(current_cat_dir):
        material_folder_path = os.path.join(current_cat_dir, preview)
        if os.path.isdir(material_folder_path):
            for idx, k_folder in enumerate(os.listdir(material_folder_path)):
                if k_folder != 'data' and not k_folder.startswith("."):
                    if os.path.isdir(os.path.join(material_folder_path, k_folder)):
                        # Se sono presenti 2 cartelle di versioni differenti, queste prendono il nome del suffisso per poter essere
                        # selezionate dal menu.
                        # Quindi controlla se la cartella alla fine finisce col nome del preview (che è già senza estensione)
                        k_list.append(k_folder)

    if k_list:
        k_list.sort(key=natural_sort)
        for idx, item in enumerate(k_list):
            if "05k" in item.lower():
                k_size_list['list'].insert(0, (item, "½k", "", idx))
            else:
                k_size_list['list'].append((item, item, "", idx))

    else:
        k_size_list['list'].append(('NONE', 'None', "", 0))

    return k_size_list['list']
