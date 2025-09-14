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

from ..utility.classes_utils import LibraryUtility


def get_json_data_faster(json_path, reload_json=False):
    """Questo velocizza il caricamento di file json da disco, viene memorizzato in una variabile nella classe LibraryUtility
    :param json_path: the json_path
    :param reload_json: if True, reload the json file"""

    if not os.path.isfile(json_path):
        return {}

    from ..utility.json_functions import get_json_data

    if reload_json:
        json_data = get_json_data(json_path)
        if not json_data:
            return {}
        else:
            LibraryUtility.json_paths[json_path] = json_data
            return json_data

    json_data = LibraryUtility.json_paths.get(json_path)
    if json_data:
        return json_data

    else:
        json_data = get_json_data(json_path)
        if json_data:
            LibraryUtility.json_paths[json_path] = json_data
            return json_data

    return {}

def lib_path_exist(prop):
    if prop and os.path.isdir(prop):
        return True


def create_json_material_library_register(path, register_filepath):
    # Crea un registro json di tutti i files presenti in libreria
    total_bytes = 0
    idx = 0

    files_dict = {}
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn.startswith("."):
                continue
            if fn.endswith(".json"):
                continue
            idx += 1
            file_prop = files_dict[idx] = {}

            file_path = os.path.join(root, fn)

            file_prop['name'] = fn
            byts = os.path.getsize(file_path)
            file_prop['size'] = byts
            total_bytes += byts

            root_path = file_path.replace(path, "")
            file_prop['path'] = root_path

    material_list = {}
    mat_idx = 0
    for cat in os.listdir(path):
        if cat == '._data' or cat.startswith("."):
            continue

        cat_folder = os.path.join(path, cat)
        if os.path.isdir(cat_folder):
            for fn in os.listdir(cat_folder):
                mat_idx += 1
                material_list[mat_idx] = fn

    import time
    library_dict = {'total_bytes': total_bytes, 'total_files': idx, 'total_materials': len(material_list),
                    'files': files_dict, 'materials': material_list, 'modified': time.time()}

    json_save_path = os.path.join(register_filepath, "library_register.json")

    from ..utility.json_functions import save_json
    print("Sto salvando il json file in ", json_save_path)
    print("Con library_dict", library_dict)
    save_json(json_save_path, library_dict)


def get_file_source(import_filepath="", from_asset_browser=None):
    """This function must return a .blend file or an .hdr image to create or import a world
    for convenience it will return a dictionary, you can also use the import_filepath parameter to specify a file (It must be a file not a folder)
    return:
    dict = {"file_type": ['BLENDER_FILE', IMAGE], "preview_filepath": preview_filepath, "filename": "filename", "filepath": "filepath"}"""

    from ..utility.utility import get_filename_from_path
    from ..dictionaries.dictionaries import image_format
    from ..exaconv import get_scnprop
    from ..utility.utility import get_addon_preferences
    from ..library_manager.main_pcoll_attributes import get_winman_main_preview
    from ..utility.utility import get_filepath_from_filename


    if import_filepath and os.path.isfile(import_filepath):
        # This case the file has been passed as a parameter so this file will be examined and not the folder
        # it was done to import a file.blend or .hdr from another library especially for the use of the import tool
        # and the use of the addition of a Light/Diffuse/Complete node (That is, the groups of the new version of HDRi Maker)

        filename = get_filename_from_path(import_filepath)
        if import_filepath.endswith(".blend"):
            return {"file_type": 'BLENDER_FILE', "preview_filepath": "", "filename": filename,
                    "filepath": import_filepath}

        image_extension_list = image_format()
        for ext in image_extension_list:
            if import_filepath.endswith(ext):
                return {"file_type": 'IMAGE', "preview_filepath": "", "filename": filename, "filepath": import_filepath}

    # Here instead is the normal use case, that is, the search for a .blend or .hdr file within the library folder
    scnProp = get_scnprop(bpy.context.scene)

    preferences = get_addon_preferences()
    if os.path.isdir(scnProp.libraries_selector):
        root = scnProp.libraries_selector
    elif scnProp.libraries_selector == 'DEFAULT':
        root = preferences.addon_default_library
    elif scnProp.libraries_selector == 'USER':
        root = preferences.addon_user_library

    category_path = os.path.join(root, scnProp.up_category)
    if not os.path.isdir(category_path):
        return {}

    preview_name = get_winman_main_preview()
    material_path = os.path.join(category_path, preview_name)

    if not os.path.isdir(material_path):
        return {}

    variation_path = os.path.join(material_path, scnProp.k_size)
    if not os.path.isdir(variation_path):
        return {}

    default_folder = os.path.join(material_path, 'data', 'previews', 'default')

    preview_filepath = get_filepath_from_filename(default_folder, preview_name)


    blend = next((fn for fn in os.listdir(variation_path) if not "_hdr_mkr_ab" in fn if fn.endswith(".blend")), None)
    if blend:
        return {"file_type": "BLENDER_FILE", "preview_filepath": preview_filepath, "filename": blend,
                "filepath": os.path.join(variation_path, blend)}

    image = next((fn for fn in os.listdir(variation_path) if
                  fn.endswith(".hdr") or fn.endswith(".exr") or fn.endswith(".png") or fn.endswith(".jpg")), None)

    if image:
        return {"file_type": "IMAGE", "preview_filepath": preview_filepath, "filename": image,
                "filepath": os.path.join(variation_path, image)}


def is_import_tools():
    from ..exaconv import get_scnprop
    from ..library_manager.main_pcoll_attributes import get_winman_main_preview

    scnProp = get_scnprop(bpy.context.scene)
    preview_name = get_winman_main_preview()

    if scnProp.libraries_selector == 'DEFAULT' and \
            scnProp.up_category == 'Tools' and \
            preview_name == "Import Background":
        return True


def is_assemble_studio():
    from ..exaconv import get_scnprop
    from ..library_manager.main_pcoll_attributes import get_winman_main_preview

    scnProp = get_scnprop(bpy.context.scene)
    preview_name = get_winman_main_preview()

    if scnProp.libraries_selector == 'DEFAULT' and \
            scnProp.up_category == 'Tools' and \
            preview_name == "Light Studio":
        return True


def create_material_folders(root, material_name, mat_variant_folder_names=[]):
    """ This function creates the folders of a material and its variations in the library,
    input: root (Cat Path), material_name and the list of the material variants as mat_variant_folder_names=[]
    Return dict with folders path, Exmple:
    keys in {material: paths, data: paths, previews: paths, default: paths, variant_paths = [paths]}
    """

    folders_dict = {}

    folders_dict['material'] = os.path.join(root, material_name)
    if not os.path.isdir(folders_dict['material']):
        os.mkdir(folders_dict['material'])

    folders_dict['data'] = os.path.join(folders_dict['material'], "data")
    if not os.path.isdir(folders_dict['data']):
        os.mkdir(folders_dict['data'])

    folders_dict['previews'] = os.path.join(folders_dict['data'], "previews")
    if not os.path.isdir(folders_dict['previews']):
        os.mkdir(folders_dict['previews']
                 )
    folders_dict['default'] = os.path.join(folders_dict['previews'], "default")
    if not os.path.isdir(folders_dict['default']):
        os.mkdir(folders_dict['default'])

    folders_dict['variant_paths'] = []
    for foldername in mat_variant_folder_names:
        variant = os.path.join(folders_dict['material'], foldername)
        if not os.path.isdir(variant):
            os.mkdir(variant)
        folders_dict['variant_paths'].append(variant)

    return folders_dict


def get_library_info(library_path):
    """Get the library_info.json data from the library folder if exists"""
    json_path = os.path.join(library_path, "._data", "library_info.json")
    if not os.path.isfile(json_path):
        return {}

    from ..utility.json_functions import get_json_data
    json_data = get_json_data(json_path)
    if not json_data:
        return {}

    return json_data


def get_volume_name_by_folder_name(library_root, input_folder_path):

    """This function is used to return the exapack in which the file_name or file_path is contained"""

    from ..utility.json_functions import get_json_data
    from ..library_manager.get_library_utils import risorse_lib
    from ..web_tools.webservice import get_json_online
    from ..exaproduct import Exa
    from ..utility.utility_dependencies import normalize_path

    # Formuliamo il percorso relativo a library_root:
    input_folder_path = input_folder_path.replace(library_root, "")
    input_folder_path = normalize_path(input_folder_path, remove_start_sep=True, remove_end_sep=True)
    # Togliamo il primo slash e l'ultimo slash se presenti:

    path = os.path.join(risorse_lib(), "online_utility", "exa_library_volumes.json")

    if not os.path.isfile(path):
        get_json_online(urls=Exa.urls_exa_libraries_volumes, save_name="exa_library_volumes.json",
                        show_popup=False)
        path = os.path.join(risorse_lib(), "online_utility", "exa_library_volumes.json")
        if not os.path.isfile(path):
            return ""

    json_data = get_json_data(path)
    if not json_data:
        get_json_online(urls=Exa.urls_exa_libraries_volumes, save_name="exa_library_volumes.json",
                        show_popup=False)
        path = os.path.join(risorse_lib(), "online_utility", "exa_library_volumes.json")
        if not os.path.isfile(path):
            return ""

    exapacks = json_data.get("exapacks")
    if not exapacks:
        print("The key 'exapacks' is not present in the json file, this should not happen!")
        return ""

    for expack_name, exapack_dict in exapacks.items():
        if not exapack_dict:
            continue

        files_dict = exapack_dict.get("files_dict")
        if not files_dict:
            continue

        for str_idx, file_size_name_path in files_dict.items():
            if not type(file_size_name_path) == dict:
                continue

            file_size = file_size_name_path.get("file_size")
            file_name = file_size_name_path.get("file_name")
            file_path = file_size_name_path.get("file_path")

            # file_path è scritto in questa maniera:  "City-Town Location\\Parametric Pavilion\\10k\\parametric_pavilion_10k.exr"
            file_path = normalize_path(file_path)
            
            # Adesso controlliamo il percorso file_path, togliendo il nome del file dal percorso:
            file_path = file_path.replace(file_name, "")
            # Lo normalizziamo:
            file_path = normalize_path(file_path, remove_start_sep=True, remove_end_sep=True)

            # Ora controlliamo se il percorso file_path è uguale al percorso input_folder_path:
            if file_path == input_folder_path:
                # in questo caso abbiamo trovato il nome del volume, quindi restituiamo il nome dell'exapack:
                return expack_name

    return ""

















