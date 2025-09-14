#   #
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version
#    of the License, or (at your option) any later version.
#   #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#   #
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software Foundation,
#    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#   #
#   Copyright 2024(C) Andrea Donati
import os

from ..exaproduct import Exa
from ..utility.json_functions import get_json_data


class LibStatus:
    # Queste variabili sono per far determinare una volta sola all'avvio se l'addon è linkato alle librerie nuove o vecchie
    new_default_is_ok = None
    new_user_is_ok = None
    # old_default_ok e old_user_ok serve per capire se la libreria default Vecchia versione è effettivamente ok,
    # importante per poi passare alla conversione
    old_default_ok = None
    old_user_ok = None

    # default_last_path e user_last_path tiene in memoria il percorso della libreria utente Vecchia, per non doverla cancellare
    default_last_path = ""
    user_last_path = ""

def is_old_default_library(default_lib_path):
    """Questa funzione deve determinare se la libreria linkata alla default, è la default library vecchia di HDRi Maker"""

    if not os.path.isdir(default_lib_path):
        LibStatus.old_default_ok = None
        return None

    folder_finded = []
    for fn in os.listdir(default_lib_path):
        filepath = os.path.join(default_lib_path, fn)
        if not os.path.isdir(filepath):
            continue
        '01k_library'
        if fn.lower() in ['1k_library', '2k_library', '4k_library', '8k_library', 'preview_hdri', '01k_library', '02k_library', '04k_library', '08k_library']:
            folder_finded.append(fn)

    if not "preview_hdri" in folder_finded:
        LibStatus.old_default_ok = False
        return False

    if len(folder_finded) > 2:
        LibStatus.old_default_ok = True
        return True


def is_new_library(library_path, get_library_type="DEFAULT"):
    """Questa funzione deve determinare se è la nuova user library"""

    # Questo caso per risolvere velocemente se già il controllo è stato fatto all'avvio
    if get_library_type == "DEFAULT" and LibStatus.default_last_path == library_path and LibStatus.new_default_is_ok:
        return LibStatus.new_default_is_ok
    elif get_library_type == "USER" and LibStatus.user_last_path == library_path and LibStatus.new_user_is_ok:
        return LibStatus.new_user_is_ok

    # Qui controlliamo subito se c'è il file library_info.json, se esiste è la libreria nuova, quindi ok
    _data_folder = os.path.join(library_path, '._data')
    if os.path.isdir(_data_folder):
        library_info_file = os.path.join(_data_folder, 'library_info.json')
        if os.path.isfile(library_info_file):
            json_data = get_json_data(library_info_file)
            if json_data:
                library_version = json_data.get("library_version")
                library_product = json_data.get("library_product")
                library_type = json_data.get("library_type")
                if library_version == Exa.library_version:
                    if library_product == Exa.product:
                        if library_type == get_library_type:
                            if get_library_type in "USER":
                                LibStatus.new_user_is_ok = True
                                LibStatus.user_last_path = library_path
                            elif get_library_type == "DEFAULT":
                                LibStatus.new_default_is_ok = True
                                LibStatus.default_last_path = library_path
                            return True

    return False
    # Qui determiniamo se la libreria user è quella vecchia, usiamo un metodo di controllo sui 2 file (Preview.png, file.blend)
    # dobbiamo determinare se ogni preview ha un file.blend, e in quale percentuale

def is_old_user_lib(root):
    """This function must determine if the user library is the old user library of HDRi Maker"""
    if not os.path.isdir(root):
        LibStatus.old_user_ok = None
        return None

    try:
        list_dir = os.listdir(root)
    except:
        return None

    true_list = 0
    len_cats = False
    for cat in os.listdir(root):
        if len_cats is False:
            len_cats = int(len_cats)
        len_cats += 1
        category_path = os.path.join(root, cat)
        # Qui si va ad analizzare con la funzione is_old_user_category, se la cartella è una categoria vecchia
        # Qui la funzione cerca se almeno il 80% delle preview ha un file.blend quindi se si può considerare una libreria vecchia
        if is_old_user_category(category_path):
            true_list += 1

    if true_list == 0 or len_cats == 0:
        return

    if true_list == len_cats:
        return True

    if len_cats == 0:
        # Avoid division by zero, in this case is not old user library
        return None

    percentage = (true_list / len_cats) * 100

    # Se per almeno un 80% le categorie sembrano essere delle vecchie librerie di HDRi Maker,
    # la funzione restituisce True
    if percentage >= 80:
        return True


def is_old_user_category(category_path):
    """Questa funzione determina se la libreria è la vecchia libreria User Library, precedente alla versione 3.0
    bisogna passare una categoria, questa funzione è utile anche al controllo durante la conversione dalla vecchia alla
    nuova categoria, restituisce True o False"""

    same_dimension = False
    same_list = False

    # Nella vecchia libreria ci sono i file preview e blend insieme

    if not os.path.isdir(category_path):
        # Non è una directory, quindi facilmente è un files
        return False

    # L'utente può avere categorie vuote (Create e mai usate), quindi se la categoria è vuota, bisogna considerarla come valida

    previews = []
    blends = []
    total_files = 0

    # Try the os.listdir() function, if it fails, return False
    try:
        listdir = os.listdir(category_path)
    except:
        return False

    for fn in os.listdir(category_path):
        if fn.endswith(".png"):
            previews.append(fn.split(".png")[0])
        elif fn.endswith(".blend"):
            blends.append(fn.split(".blend")[0])
        total_files += 1

    # A malincuore, se la categoria è vuota, bisogna considerarla come valida, poichè l'utente potrebbe averla creata e mai usata
    if total_files == 0:
        return True

    if previews == blends:
        if len(previews) == 0 or len(blends) == 0:
            # Qui la lista corrisponde, sia per numero che per contenuto, quindi al 99% è una user library
            return False
        else:
            return True

    # Qui si calcola in percentuale, se un 80% o piu corrisponde, la libreria è ok, poichè l'utente potrebbe aver modificato
    # qualcosa manualmente, quindi la diamo per buona
    max_list = len(max(previews, blends))  # Qui si ottiene la lista piu lunga per il calcolo percentuale
    intersect = len(
        list(set(previews).intersection(blends)))  # Qui si ottiene la quantità di oggetti uguali nelle 2 liste (Match)

    if intersect == 0:
        # Avoiding division by zero, in this case is not a user library
        return None

    percentage = (max_list / intersect) * 100
    # max_list / intersect can be 0 so we need to use the multiplication to avoid ZeroDivisionError:


    if percentage >= 80:
        # print(previews, blends)
        return True
