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
import ast
import ntpath
import os
import platform
import subprocess
from math import radians

import bpy

from .classes_utils import LibraryUtility
from .dictionaries import complete_format
from .json_functions import get_json_data, save_json
from .text_utils import draw_info
from .utility import get_addon_preferences, is_email, get_addon_dir, mesh_selector, set_object_for_ops, \
    set_object_mode
from .utility_ops.store_node_dimension import get_node_dimensions
from ..exaconv import get_colprop, get_objprop


def store_material_user_settings(mat):
    string_dict = {}

    string_dict['use_backface_culling'] = mat.use_backface_culling
    if bpy.app.version < (4, 2, 0):
        string_dict['blend_method'] = mat.blend_method
        string_dict['show_transparent_back'] = mat.show_transparent_back
        string_dict['use_screen_refraction'] = mat.use_screen_refraction
    else:
        string_dict['surface_render_method'] = mat.surface_render_method
        string_dict['use_transparency_overlap'] = mat.use_transparency_overlap
        string_dict['use_raytrace_refraction'] = mat.use_raytrace_refraction

    string_dict['shadow_method'] = mat.shadow_method
    string_dict['alpha_threshold'] = mat.alpha_threshold

    string_dict['refraction_depth'] = mat.refraction_depth
    if bpy.app.version < (4, 2, 0):
        # use_sss_translucency è stato rimosso in Blender 4.2
        string_dict['use_sss_translucency'] = mat.use_sss_translucency

    string_dict['pass_index'] = mat.pass_index
    mat.extremepbr_material_prop.material_user_settings = str(string_dict)


def restore_material_user_settings(mat):
    string_dict = mat.extremepbr_material_prop.material_user_settings  # Il dizionario viene memorizzato sotto forma di stringa
    setting_dict = ast.literal_eval(string_dict)

    for k, v in setting_dict.items():
        setattr(mat, k, v)

    mat.extremepbr_material_prop.material_user_settings = "{}"


def set_to_y_up(obj):
    selected, active = set_object_for_ops(obj)

    obj.rotation_euler.z = radians(180)

    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    for o in selected:
        o.select_set(state=True)
    bpy.context.view_layer.objects.active = active


def flip_axis(obj, axis=(False, False, False)):
    if obj.type != "MESH":
        return

    selected, active = set_object_for_ops(obj)

    set_object_mode(obj)
    bpy.ops.transform.mirror(constraint_axis=axis, use_accurate=True)

    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    bpy.ops.object.mode_set(mode='EDIT')
    mesh_selector(obj, state=True)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    set_object_mode(obj)

    for o in selected:
        o.select_set(state=True)
    bpy.context.view_layer.objects.active = active


def set_colorspace_name(img, name):
    # Questa funzione dovrebbe ovviare al fatto che alcuni utenti si trovano con un sistema colorspace non nativo di Blender, non se ne accorgono nemmeno,
    # alcuni addon vanno a modificare gli spazi colore, e questo è male, poichè l'utente non ne viene a conoscienza.
    # Questo dovrebbe essere davvero evitato, ma succede in continuazione. Quindi il colorspace non sempre si può conoscere, e qui al momento davvero è un bel
    # problema per l'utente finale, il piu delle volte si ritrovano con un sistema di colori ACES. Ma non tutti sono uguali. le nomenclature possono cambiare
    colorspace_names = img.bl_rna.properties['colorspace_settings'].fixed_type.properties['name'].enum_items.keys()
    try:
        img.colorspace_settings.name = name
        return img.colorspace_settings.name
    except:
        draw_info("Unable to set colorspace_settings.name. Colorspace list: " + str(colorspace_names), "Info", 'INFO')


def load_images_from_path(image_path_list):
    data_img_list = []
    img_to_load = [i[1] for i in image_path_list if [cf for cf in complete_format() if i[1].endswith(cf)]]
    for i in img_to_load:
        data_img_list.append(bpy.data.images.load(i))

    return data_img_list


def load_starting_message(set_has_been_read=False):
    """Cerca e carica il file json al primo avvio. Se esiste il file first_message.json
    utile per mostrare all'utente i cambiamenti una volta avviato HDRi Maker
    Potrà eliminare questo messaggio tramite bottone. E non vedermo mai piu"""
    data = None
    LibraryUtility.first_message = {}
    first_message_file = os.path.join(get_addon_dir(), "first_message.json")
    if os.path.isfile(first_message_file):
        data = get_json_data(first_message_file)

    if data:
        has_been_read = data.get("has_been_read")
        if has_been_read is not None:
            if set_has_been_read:
                data["has_been_read"] = set_has_been_read
                save_json(first_message_file, data)
                LibraryUtility.first_message = {}
                return first_message_file

            if not has_been_read:
                LibraryUtility.first_message = data

    return first_message_file


def center_relative_nodes(node_tree, node_list, relative_node, direction='X', align_relative=False):
    if not node_list:
        return

    nodes = node_tree.nodes

    dir = 0 if direction == 'X' else 1
    # sum_node_space = sum([n.dimensions[dir] for n in node_list])
    sum_node_space = sum([get_node_dimensions(n)[dir] for n in node_list])

    node_list_midpoint_loc = node_list[0].location[dir] - (sum_node_space / 2)
    # relative_node_midpoint_loc = relative_node.location[dir] - (relative_node.dimensions[dir] / 2)
    relative_node_midpoint_loc = relative_node.location[dir] - (get_node_dimensions(relative_node)[dir] / 2)

    node_list[0].location[dir] = relative_node_midpoint_loc + (sum_node_space / 2)

    node_list[0].select = True
    nodes.active = node_list[0]
    align_node_xy(node_tree, node_list, direction, margin=50, master_node=node_list[0])


def align_node_xy(node_tree, node_list, direction, margin=50, master_node=None):
    nodes = node_tree.nodes

    dir = 0 if direction == 'X' else 1

    if not node_list:
        return
    nodes.update()
    top_down = sorted(node_list, key=lambda x: x.location[dir], reverse=True if direction == 'Y' else False)

    if master_node:
        top_down.remove(master_node)
        top_down.insert(0, master_node)

    nodes.update()
    for idx, n in enumerate(top_down):
        if idx == 0:  # Salta il primo perchè è il capostipite
            continue

        n.location.x = top_down[0].location[1 if dir == 0 else 0]
        # n.location.y = top_down[idx - 1].location[dir] - (top_down[idx - 1].dimensions[dir] + margin)
        n.location.y = top_down[idx - 1].location[dir] - (get_node_dimensions(top_down[idx - 1])[dir] + margin)
    nodes.update()
    return top_down


def show_hide_user_data(status=False):
    """Mostra o nasconde i campi delle credenziali"""
    addon_preferences = get_addon_preferences()
    addon_preferences.exa_mail_bool = status
    addon_preferences.exa_password_bool = status
    addon_preferences.exa_product_license_bool = status


def check_format_license():
    """Questa funzione controlla il corretto inserimento del formato licenza"""

    addon_preferences = get_addon_preferences()

    if len(addon_preferences.exa_product_license) == 6:
        # Caso in cui l'utente spesso inserisce BM case
        text = "It seems that you are using a product id, it is not a valid license, the valid license can be found on your license page on extreme-addons"
        draw_info(text, "Info", 'INFO')
        addon_preferences.exa_product_license_bool = True
        return

    if len(addon_preferences.exa_product_license) != 36:
        text = "The license must be 36 characters, including dashes ( - ), please double check your license from your license page on Extreme-Addons.com You can go to this page by clicking the 'License Page' button below"
        draw_info(text, "Info", 'INFO')
        addon_preferences.exa_product_license_bool = True
        return

    if not is_email(addon_preferences.exa_mail):
        text = "Insert a valid Mail (" + addon_preferences.exa_mail + ") is not a valid mail"
        draw_info(text, "Info", 'INFO')
        addon_preferences.exa_mail_bool = True
        return

    return True


def blend_exist():
    blend_file = bpy.data.filepath
    if not os.path.isfile(blend_file):
        text = "Please save the project before proceeding"
        draw_info(text, "Info", 'INFO')
        return
    if bpy.data.is_saved:
        return True


def open_folder(folder_path):
    # Questo serve per aprire una cartella del sistema operativo, quindi si apre proprio un popup con folder del sistema operativo

    if not os.path.isdir(folder_path):
        text = "This path '" + folder_path + "' not exist"
        draw_info(text, "Info", 'INFO')

    else:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", folder_path])
        else:
            subprocess.Popen(["xdg-open", folder_path])

        text = "The path could not be opened: (" + folder_path + ") contact the programmer to notify this message"


def normalize_path(path, remove_start_sep=False, remove_end_sep=False):
    path = ntpath.normpath(path)
    path = os.path.join(path)
    sep = ntpath.normpath(os.sep)
    path = path.replace("/", sep).replace('\\', sep).replace('//', sep)
    if remove_start_sep:
        # Rimuove se "/" o "\\" o "//" è all'inizio del path
        if path.startswith("/") or path.startswith("\\") or path.startswith("//"):
            # Rimuoviamo solo il primo carattere
            path = path[1:]

    if remove_end_sep:
        # Rimuove se "/" o "\\" o "//" è alla fine del path
        if path.endswith("/") or path.endswith("\\") or path.endswith("//"):
            # Rimuoviamo solo l'ultimo carattere
            path = path[:-1]
    return path


def make_multiple_dirs(path="", exist_ok=True):
    path = normalize_path(path)

    try:
        os.makedirs(path, exist_ok=exist_ok)
    except:
        text = "Try to make multiple dirs problem: " \
               "Please close all open folders in your operating system, if the problem persists run Blender as administrator"
        draw_info(text, "Info", 'INFO')


def make_single_dir(path=""):
    try:
        os.mkdir(path)
    except:
        text = "Try to create single dir problem:" \
               "Please close all open folders in your operating system, if the problem persists run Blender as administrator"
        draw_info(text, "Info", 'INFO')


def dir_isdir(path="", draw_alert=False, text="This path does not exist: "):
    path = os.path.normpath(path)
    if os.path.isdir(path):
        return path
    else:
        if draw_alert:
            text += path
            draw_info(text, "Info", 'INFO')
        return False


def create_collection(scn, collection_name="", collection_id_name="", father=None, recycle=True):
    collection = None
    if recycle:
        collection = next((col for col in bpy.data.collections if col.name == collection_name), None)

    if not collection:
        collection = bpy.data.collections.new(collection_name)

    if father:
        get_father = scn.collection.children.get(father)
        if get_father:
            if collection not in get_father.children[:]:
                get_father.children.link(collection)
        else:
            scn.collection.children.link(collection)
    else:
        if collection not in scn.collection.children[:]:
            scn.collection.children.link(collection)

    if collection_id_name:
        colProp = get_colprop(collection)
        colProp.collection_id_name = collection_id_name

    return collection


def create_panoramic_360_camera(scene, location):
    """Create a camera, that will be used to render the panorama, usefull to create 360° HDRIs from current scene"""
    # Create a new camera data block
    cam_pano_data = bpy.data.cameras.new("Camera Pano")
    # Create a new object with that camera data
    camera_panorama = bpy.data.objects.new("Camera", cam_pano_data)
    # Link the camera to the scene
    scene.collection.objects.link(camera_panorama)
    # Make the camera the render camera
    scene.camera = camera_panorama

    camera_panorama.data.type = 'PANO'
    camera_panorama.location = location
    camera_panorama.rotation_euler = (radians(90), 0, 0)
    objProp = get_objprop(camera_panorama)
    objProp.object_id_name = '360_CAMERA_REAL'

    if bpy.app.version < (4, 0, 0):
        camera_panorama.data.cycles.panorama_type = 'EQUIRECTANGULAR'
        camera_panorama.data.cycles.latitude_min = -1.5708
        camera_panorama.data.cycles.latitude_max = 1.5708
        camera_panorama.data.cycles.longitude_min = -3.14159
        camera_panorama.data.cycles.longitude_max = 3.14159

    else:
        camera_panorama.data.panorama_type = 'EQUIRECTANGULAR'
        camera_panorama.data.latitude_min = -1.5708
        camera_panorama.data.latitude_max = 1.5708
        camera_panorama.data.longitude_min = -3.14159
        camera_panorama.data.longitude_max = 3.14159

    camera_panorama.data.shift_x = 0
    camera_panorama.data.shift_y = 0
    camera_panorama.data.clip_start = 0.1
    camera_panorama.data.clip_end = 100000

    return camera_panorama

# Compatibilità nodi
# Translate in English:
# Compatibility nodes






