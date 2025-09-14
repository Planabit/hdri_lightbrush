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

import bpy

from ..exaproduct import Exa
from ..utility.json_functions import get_json_data, save_json
from ..utility.utility import get_version_to_int


def write_version_into_library_info(lib_path):
    """Questa funzione serve per tenere traccia di quando l'utente ha scritto l'Asset browser, questo ci torna utile in futuro nel caso dovessimo avvisare che
    l'Asser Browser deve essere aggiornato"""

    data_folder = os.path.join(lib_path, '._data')
    if not os.path.exists(data_folder):
        return

    library_info = os.path.join(data_folder, 'library_info.json')
    if not os.path.isfile(library_info):
        return

    data = get_json_data(library_info)
    if not data:
        return

    as_brow_blend_ver = data.get('as_brow_blend_ver')
    if as_brow_blend_ver != bpy.app.version:
        data['as_brow_blend_ver'] = bpy.app.version
        save_json(library_info, data)


    as_brow_comp_ver = data.get('as_brow_comp_ver')
    if as_brow_comp_ver == get_version_to_int(Exa.blender_manifest['version']):
        return

    else:
        # La chiave as_brow_comp_ver potrebbe non esistere, quindi la creiamo in ogni caso, e sarà la versione
        # dell'addon con cui è stata creato il file
        data['as_brow_comp_ver'] = get_version_to_int(Exa.blender_manifest['version'])
        # Salviamo il file
        save_json(library_info, data)


def get_active_asset_filepath(context, get_asset_type='worlds'):
    asset_info = {}

    from pathlib import Path
    import os
    active_library_name = context.area.spaces.active.params.asset_library_ref
    if active_library_name == "LOCAL":  # Current file
        library_path = Path(bpy.data.filepath)  # Will be "." if file has never been saved
    else:
        print("active_library_name", active_library_name)
        library_path = Path(context.preferences.filepaths.asset_libraries.get(active_library_name).path)

    for asset_file in context.selected_asset_files:
        asset_fullpath = library_path / asset_file.relative_path
        if active_library_name == "LOCAL":
            # For some reason the relative path stops at the ID container in local file
            asset_fullpath /= asset_file.local_id.name

        asset_filepath = asset_fullpath.parent.parent

    # Get the data_type from filepath, need to subtract the asset_filepath from the asset_fullpath to get the data_type and data_name
    data_and_name = str(asset_fullpath).replace(str(asset_filepath), "")
    # Data and name si presenta come questo: /worlds/World.001
    # Mi servono di data_type e data_name che saranno rispettivamente worlds e World.001
    # Assicuriamoci di ottenere i nomi con il modulo Path, in maniera da non avere problemi con i nomi di file con spazi
    data_type = Path(data_and_name).parts[1]
    data_name = Path(data_and_name).parts[2]

    folder_path = os.path.dirname(asset_filepath)
    # Get blender file name
    file_name = os.path.basename(asset_filepath)

    get_asset_type = get_asset_type.lower()
    if get_asset_type == 'worlds':
        get_asset_type = 'world'

    if data_type.lower() != get_asset_type.lower():
        return asset_info

    if os.path.isfile(asset_filepath):
        asset_info = {'Status': True,
                      'blend_filepath': asset_filepath,
                      'data_type': data_type,
                      "data_name": data_name,
                      'folder_path': folder_path,
                      "file_name": file_name}

    return asset_info


def try_to_get_hdr_from_asset_filepath(asset_info):
    """Questa funzione analizza con os.walk se nella directory del file.blend del asset-browser è contenuta una immagine HDR o EXR"""

    data_name = asset_info.get('data_name')
    folder_path = asset_info.get('folder_path')

    import os
    hdr_dict = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".hdr") or file.endswith(".exr"):
                if data_name in file:
                    # Qui ci assicuriamo di ottenere l'eventuale file hdr o exr con lo stesso nome del world contenuto nel file .blend se esiste un file
                    # Non è sempre possibile poichè il world potrebbe far fede al percorso relativo, quindi avere il file hdr o exr nella stessa cartella del file .blend
                    # non è sempre possibile ma ci proviamo
                    filepath = os.path.join(root, file)
                    hdr_dict['filename'] = file
                    hdr_dict['filepath'] = filepath
                    break
    return hdr_dict


def get_asset_browser_world(self, context):
    """This function checks if a world asset has been selected and if it is valid"""

    asset_dict = {}

    asset_info = get_active_asset_filepath(context, get_asset_type='worlds')
    status = asset_info.get('Status')
    if not status:
        return asset_dict

    hdri_file_dict = try_to_get_hdr_from_asset_filepath(asset_info)
    hdr_filepath = hdri_file_dict.get('filepath')
    if hdr_filepath:
        # In questo caso abbiamo trovato un file hdr o exr con lo stesso nome del world contenuto nel file .blend quindi
        # Dobbiamo restituire il filepath
        filename = hdri_file_dict.get('filename')
        return {"file_type": 'IMAGE', "preview_filepath": "", "filename": filename, "filepath": hdr_filepath}

    else:
        # In questo caso restiruiamo il file .blend con il nome del world da caricare
        filename = asset_info.get('file_name')
        filepath = asset_info.get('blend_filepath')
        data_name = asset_info.get('data_name')
        return {"file_type": 'BLENDER_FILE', "preview_filepath": "", "filename": filename, "filepath": filepath,
                "data_name": data_name}

    return asset_dict


