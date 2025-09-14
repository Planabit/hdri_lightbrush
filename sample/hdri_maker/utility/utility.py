import base64
import datetime
import math
import ntpath
import os
import platform
import re
import shutil
import subprocess
import time
import uuid
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile
from io import BytesIO

import bpy
import numpy as np
from bpy_extras.node_utils import find_node_input
from mathutils import Vector


class TimePassedChecker:
    """Questa piccola classe calcola il tempo passato e se sono passati i secondi (Every) quindi restituisce
    False se dall'ultima volta non sono passati i secondi every. Utile per temporeggiare alcune azioni in un ciclo"""
    current_time = 0
    every = 1

    def __init__(self, every=1):
        TimePassedChecker.every = every

    def time_calculator(self):
        if (time.time() - TimePassedChecker.current_time) >= TimePassedChecker.every:
            TimePassedChecker.current_time = time.time()
            return True


class SocketColor:
    color = (1, 1, 0.5, 1)  # Yellow for the socket Color Type
    vector = (0.3, 0.3, 0.7, 0)  # Blue for the socket Vector Type


def get_node_tree_type(node_tree):
    """Check if the node tree is from a material
    : node_tree: node tree to check, accept any type of node tree"""
    id_data_string = repr(node_tree)
    if id_data_string.startswith("bpy.data.materials"):
        return 'MATERIAL'
    elif id_data_string.startswith("bpy.data.worlds"):
        return 'WORLD'
    elif id_data_string.startswith("bpy.data.scenes"):
        return 'COMPOSITE'


def override_context(get_area='VIEW_3D'):
    """
    Return a context override by area type,
    :area types are: VIEW_3D, IMAGE_EDITOR, NODE_EDITOR, SEQUENCE_EDITOR, CLIP_EDITOR, DOPESHEET_EDITOR, GRAPH_EDITOR,
    NLA_EDITOR, TEXT_EDITOR, CONSOLE, INFO, PREFERENCES, FILE_BROWSER, OUTLINER, PROPERTIES, TOPBAR, STATUSBAR, HEADER,
    TOOLBAR, TOOL_PROPS, FOOTER """
    # Blender in any cases need override context, this function return a valid override context
    override_context = bpy.context.copy()
    for area in bpy.context.screen.areas:
        if area.type == get_area:
            override_context['area'] = area
            override_context['region'] = area.regions[-1]
            override_context['window'] = bpy.context.window
            override_context['screen'] = bpy.context.screen
            override_context['area'] = area
            override_context['region'] = area.regions[-1]
            override_context['scene'] = bpy.context.scene
            override_context['space_data'] = area.spaces.active
            # If the area exist return the override context, else the function return None
            return override_context


def copy_material_settings(from_mat, to_mat):
    """Copy material settings from one material to another"""
    to_mat.use_backface_culling = from_mat.use_backface_culling
    if bpy.app.version < (4, 2, 0):
        # use_sss_translucency è stato rimosso in blender 4.2
        to_mat.use_sss_translucency = from_mat.use_sss_translucency
        to_mat.blend_method = from_mat.blend_method
    else:
        to_mat.surface_render_method = from_mat.surface_render_method

    to_mat.shadow_method = from_mat.shadow_method
    to_mat.alpha_threshold = from_mat.alpha_threshold
    to_mat.use_screen_refraction = from_mat.use_screen_refraction
    to_mat.refraction_depth = from_mat.refraction_depth
    to_mat.pass_index = from_mat.pass_index


def get_filename_from_path(path):
    """Return exact filename from a path"""
    head, tail = ntpath.split(path)
    if not tail:
        from pathlib import Path
        tail = Path(path).name

    return tail or ntpath.basename(head)


def get_splitted_path(path):
    return ntpath.normpath(path).split(ntpath.normpath(os.sep))


def copy_image_channels(from_image, from_channel, to_image, to_channel):
    """Copy a channel from one image to another
    input:
        from_image: image to copy from
        from_channel: channel to copy from
        to_image: image to copy to
        to_channel: channel to copy to
        """
    channels = {"r": 0, "g": 1, "b": 2, "a": 3}
    pixels_from = np.empty(shape=len(from_image.pixels), dtype=np.float32)
    from_image.pixels.foreach_get(pixels_from)
    pixels_to = np.empty(shape=len(from_image.pixels), dtype=np.float32)
    to_image.pixels.foreach_get(pixels_to)

    pixels_to[channels.get(to_channel)::4] = pixels_from[channels.get(from_channel)::4]

    to_image.pixels.foreach_set(pixels_to)
    to_image.update()
    to_image.update_tag()


def set_active_object(ob):
    """Set the active blender object"""

    for o in bpy.context.scene.objects:
        o.select_set(state=True if o == ob else False)
    bpy.context.view_layer.objects.active = ob


def deselect_all():
    """Deselect all the objects in the scene and remove the active object"""
    for o in bpy.context.scene.objects:
        o.select_set(state=False)
    bpy.context.view_layer.objects.active = None


def select_objects(objects):
    """Select a list of blender objects"""
    if type(objects) is not list:
        objects = [objects]

    if not objects:
        return
    for o in bpy.context.scene.objects:
        o.select_set(state=True if o in objects else False)
    bpy.context.view_layer.objects.active = objects[0]


def is_macintosh():
    """Return True if the OS is Macintosh"""
    platform_system = platform.system()
    return platform_system.lower() == 'darwin'


def get_node_and_out_standard(node_tree):
    """Return 2 values, from_node, output node"""

    out_types = ['ALL', 'CYCLES', 'EEVEE']
    for out_type in out_types:
        out = node_tree.get_output_node(out_type)
        if out:
            break

    if not out:
        return None, None

    if not out.inputs[0].is_linked:
        return None, None

    from_node = out.inputs[0].links[0].from_node

    return from_node, out


def image_has_data(img):
    """Return True if the bpy.data.images['my_image'] has data"""
    if not img.has_data:
        try:
            img.update()
        except Exception as e:
            print("Error from image_has_data function: ", e)
            pass

    if img.has_data:
        return True
    else:
        return False


def clear_unused_slot_material(self, context):
    """Remove unused slot material from the material slot list of the active object"""
    active_object = context.object
    selected_objects = [o for o in bpy.context.selected_objects if ob_type_multiple_type(o)]

    bpy.ops.object.select_all(action='DESELECT')

    for o in selected_objects:
        context.view_layer.objects.active = o
        o.select_set(state=True)
        bpy.ops.object.material_slot_remove_unused()

    for o in selected_objects:
        o.select_set(state=True)

    if active_object:
        context.view_layer.objects.active = active_object



def get_mac_address():
    """Return the mac address"""
    mac_adress = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]))
    return mac_adress


def get_addon_dir():
    """Mantenere sempre in questo livello di modulo, oppure creare un get dirname che restituisca esattamente il nome della folder principale"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_blender_addons_folder():
    """Funzione che restituisce il percorso alla cartella ...\Roaming\Blender Foundation\Blender"""
    try:
        # Questa ipotesi è per il caso in cui l'addon è installato in
        # - ...\Roaming\Blender Foundation\Blender\x.x\scripts\addons
        # - ...\Roaming\Blender Foundation\Blender\x.x\extensions\user_default o anche in altre cartelle dentro extensions
        context_addon_folder = get_addon_dir()
        addon_folder_path = Path(context_addon_folder).parents[3]
        return addon_folder_path
    except:
        # Se qui si ha un errore nel try, significa che è una cartella personalizzate dell'utente, e potrebbe essere anche
        # in un livello c:\Addons\my_addon... quindi bisogna iterare al primo livello disponibile.
        # Se il livello è c:\Addons\my_addon, allora si restituisce c:\Addons
        return Path(get_addon_dir()).parents[0]


def addon_dir_is_in_path(path):
    """Return True if the addon folder is in the path"""
    if get_addon_dir() in path:
        return True


def get_addon_preferences():
    from ..exaproduct import get_addon_module_name
    # Il nome dell'addon in questo caso è la cartella che lo contiene
    addon_name = get_addon_module_name()
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return addon_prefs



def reset_image_color(img, color):
    """Reset the image color"""
    if img.source != 'GENERATED':
        img.source = 'GENERATED'

    img.generated_color = color


def is_good_zip_file(file):
    """Return True if the file is a good zip file"""
    try:
        zfile = zipfile.ZipFile(file)
    except zipfile.BadZipfile as ex:
        return False

    return True

    #
    #
    #
    # time_start = time.time()
    # try:
    #     ret = zfile.testzip() # Troppo Lento! 20 Secondi per un file da 2GB
    # except:
    #     return False
    #
    # if ret is not None:
    #     # bad zip file
    #     return False
    # else:
    #     # Good zipfile
    #     return True


def get_gpu_memory():
    """Return the gpu memory"""
    _output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
    ACCEPTABLE_AVAILABLE_MEMORY = 1024
    COMMAND = "nvidia-smi --query-gpu=memory.free --format=csv"
    memory_free_info = _output_to_list(subprocess.check_output(COMMAND.split()))[1:]
    memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]

    return memory_free_values


def get_view_3d_area():
    """Return the 3d view area"""
    space_area_3d = None
    all_areas = []
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space_area_3d = space
        else:
            all_areas.append(area)

    return space_area_3d


def get_asset_browser_area():
    """Return the 3d view area"""
    file_browser = None
    dicts = {}
    # for area in bpy.context.screen.areas:
    #     if area.type == 'FILE_BROWSER':
    #         dicts["area"] = area
    #         for space in area.spaces:
    #             if space.type == 'FILE_BROWSER':
    #                 dicts["space"] = space

    for window in bpy.context.window_manager.windows:
        dicts["window"] = window
        dicts["screen"] = window.screen
        for area in dicts["screen"].areas:
            if area.type == 'FILE_BROWSER':
                dicts["area"] = area
                for space in area.spaces:
                    if space.type == 'FILE_BROWSER':
                        dicts["space"] = space
                        # Store the selected_asset_files
                        if space.params.use_filter:
                            dicts["selected_asset_files"] = space.params.filter_glob
                        else:
                            dicts["selected_asset_files"] = ""

    return dicts


def mesh_selector(obj, state=True):
    """Select all the mesh of the object"""
    if obj.type != 'MESH':
        return

    for poly in obj.data.polygons:
        poly.select = state


def redraw_all_areas():
    """Redraw all the areas, so it refresh the viewport"""
    for screen in bpy.data.screens:
        for area in screen.areas:
            area.tag_redraw()


def set_shading_type(type):
    """Set the shading type of the 3d view"""
    space_area_3d = get_view_3d_area()
    previus_type = space_area_3d.shading.type
    if type:
        space_area_3d.shading.type = type

    return previus_type


def set_object_for_ops(obj):
    """Select only the active object"""
    selected = bpy.context.selected_objects[:]
    active = bpy.context.view_layer.objects.active
    for o in selected:
        o.select_set(state=False)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(state=True)

    return selected, active


def base_64_to_encode_string(to_encode):
    """Return the base64 encoded string"""
    encode = to_encode.encode("utf-8")
    b64 = base64.b64encode(encode)
    decode = b64.decode("utf-8")
    return decode


def base_64_to_decode_string(to_decode, decode_type='utf-8'):
    """Return the base64 decoded string"""
    return base64.b64decode(to_decode).decode(decode_type)


def is_email(email):
    """Return True if the string is an email"""
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True


def replace_forbidden_characters(text, replace_with='_'):
    """Replace the forbidden characters with the replace_with string (Default: '_')"""
    for w in text:
        if w in """"'[@!#$%^&*()<>?/\|}{~:]'""":
            text = text.replace(w, replace_with)
    return text


def get_disk_info(disk, get_human=False):
    """Return the disk info, get_human=True return the human readable size"""

    if not os.path.isdir(os.path.dirname(disk)):
        return 0, 0, 0
    try:
        total, used, free = shutil.disk_usage(disk)

        if get_human:
            total = (total // (2 ** 30))
            used = (used // (2 ** 30))
            free = (free // (2 ** 30))
    except:
        return 0, 0, 0

    return total, used, free


def get_version_to_int(version):
    """Get the version to int, for example (2, 83, 0) to 28300"""
    version = str(version)
    numerical_string = ''
    for item in version:
        if item.isdigit():
            numerical_string += item

    if numerical_string:
        return int(numerical_string)


def natural_sort(text):
    """Natural sort"""

    # Natural sort is a sorting algorithm that sorts human readable text
    def isnum(text):
        return int(text) if text.isdigit() else text

    return [isnum(c) for c in re.split('(\d+)', text)]


def natural_sort_v2(l):
    # This function is from stackoverflow. https://stackoverflow.com/questions/4836710/is-there-a-built-in-function-for-string-natural-sort
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def wima():
    """Return Context Window_Manager"""
    return bpy.context.window_manager


def change_area(from_type, to_type):
    """Change the area type, useful for example to change the area type from 'VIEW_3D' to 'IMAGE_EDITOR'"""
    area_changed = from_type
    for area in bpy.context.screen.areas:
        if area.ui_type == from_type:
            area.ui_type = to_type
            area_changed = area
            break
    return area_changed


def replace_all_string(text, from_list, replace):
    """Replace all the string in the from_list with the replace string"""
    for i in from_list:
        text = text.replace(i, replace)
    return text


### Special thanks at "Markus von Broady" from this answer:
# https://blender.stackexchange.com/questions/123503/get-position-of-node-socket-in-python/252856?noredirect=1#comment430901_252856
# The three functions below have been adapted for the purpose used here

def is_hidden(socket):
    """Return True if the socket is hidden"""
    return socket.hide or not socket.enabled


def is_tall(node, socket):
    """Return True if the socket is tall"""
    if socket.type != 'VECTOR':
        return False
    if socket.hide_value:
        return False
    if socket.is_linked:
        return False
    if node.type == 'BSDF_PRINCIPLED' and socket.identifier == 'Subsurface Radius':
        return False
    return True


def get_socket_location(node, get_socket=None):
    """Funzione che restituisce le posizioni nel node_tree dei socket del nodo
        se get_socket, viene restituita solo la posizione di get_socket"""
    # This function is inspired by the answer of "Markus von Broady" which I thank very much. The answer can be found here on "blender.stackexchange"
    # https://blender.stackexchange.com/questions/123503/get-position-of-node-socket-in-python

    X_OFFSET = -1.0
    Y_TOP = -34.0
    Y_BOTTOM = 16.0
    Y_OFFSET = 22.0
    # 2 offsets
    VEC_BOTTOM = 28.0
    VEC_TOP = 32.0

    sockets = {}

    from ..utility.utility_ops.store_node_dimension import get_node_dimensions
    dimensions = get_node_dimensions(node)

    x = node.location.x + dimensions[0] + X_OFFSET
    y = node.location.y + Y_TOP
    for output in node.outputs:
        if is_hidden(output):
            continue
        # sockets[output] = {'type': 'output', 'location': (x, y)}
        y -= Y_OFFSET
        sockets[output] = {'type': 'output', 'location': (x, y)}
        if get_socket and get_socket == output:
            return sockets

    x = node.location.x
    y = node.location.y - dimensions[1] + Y_BOTTOM
    for input in reversed(node.inputs):
        if is_hidden(output):
            continue
        tall = is_tall(node, input)
        y += VEC_BOTTOM * tall
        # sockets[input] = {'type': 'input', 'location': (x, y)}
        y += Y_OFFSET + VEC_TOP * tall
        sockets[input] = {'type': 'input', 'location': (x, y)}
        if get_socket and get_socket == input:
            return sockets

    return sockets


def set_group_input_default_value(node_tree, name, value):
    if bpy.app.version < (4, 0, 0):
        ng_input = node_tree.inputs.get(name)
        if ng_input: ng_input.default_value = value
    else:
        ng_input = next((i for i in node_tree.interface.items_tree if i.item_type == 'SOCKET' if i.in_out == 'INPUT' if
                         i.name == name), None)
        if ng_input: ng_input.default_value = value


def return_name_without_numeric_extension(name):
    """Return the name without the numeric extension, for example "Cube.001" to "Cube" """
    if len(name) > 3:
        if name[-3:].isnumeric() and name[-4] == ".":
            return name[:-4]
    return name


def get_numeric_suffix(name):
    """Return the numeric suffix of the name, for example "Cube.001" to "001" """
    return name[-4:] if len(name) > 4 and name[-4] == "." and name[-3:].isnumeric() else ""


def set_bake_name(name, type='object'):
    """Set the bake name, for example "Cube" to "Cube_bake" """
    suffix = name[-4:] if len(name) > 4 and name[-4] == "." and name[-3:].isnumeric() else ""
    if type == 'object':
        new_name = return_name_without_numeric_extension(name) + '_Bake' + suffix
    return new_name


def ob_type_multiple_type(ob):
    """Return the object type, for example 'MESH' to 'MESH, CURVE'"""
    if ob is None:
        return
    objType = getattr(ob, 'type', '')
    if objType in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'GPENCIL']:
        return True
    else:
        return


def remove_frames(group, exclusion_list):
    """Remove the frames from the group, the frames in the exclusion_list are not removed"""
    for n in group.nodes:
        if n.type == 'FRAME' and n not in exclusion_list:
            group.nodes.remove(n)


def open_user_pref(context, preferences_tabs=None):
    """Opens the Blender Preferences menu, directly to the context addon"""

    if not context:
        context = bpy.context

    from ..exaproduct import Exa
    addon_name = Exa.blender_manifest['name']
    package_id = Exa.blender_manifest['id']

    from ..exaproduct import get_addon_module_name
    addon_module_name = get_addon_module_name()
    addon_prefs = get_addon_preferences()

    bpy.ops.screen.userpref_show('INVOKE_DEFAULT')

    if bpy.app.version < (4, 2, 0):
        context.preferences.active_section = 'ADDONS'
        context.window_manager.addon_search = addon_name
        bpy.ops.preferences.addon_expand(module=addon_module_name)
        bpy.ops.preferences.addon_show(module=addon_module_name)
    else:
        context.preferences.active_section = 'EXTENSIONS'
        context.window_manager.extension_search = addon_name

        repo_index = get_addon_repo_index(addon_name)
        if repo_index:
            bpy.ops.extensions.package_show_set(pkg_id=package_id, repo_index=repo_index)
            bpy.ops.extensions.package_show_settings(pkg_id=package_id, repo_index=repo_index)

    if preferences_tabs:
        addon_prefs.preferences_tabs = preferences_tabs


    if 'COMMUNITY' not in context.window_manager.addon_support:
        try:
            context.window_manager.addon_support = context.window_manager.addon_support | {'COMMUNITY'}
        except Exception as e:
            print("Error from open_user_pref function: ", e)
            pass


def render_preset(scene, engine='CYCLES', device='GPU', progressive='PATH', samples=16, max_bounces=4, diffuse_bounces=4, glossy_bounces=12,
                  transparent_max_bounces=8, transmission_bounces=1, volume_bounces=256, render_tiles=256, resolution_x=256,
                  resolution_y=256, resolution_percentage=100, film_transparent=False, color_mode='RGBA', file_format='PNG'):
    """Set the render preset, Acepted values for the parameters:
    engine: 'CYCLES', 'BLENDER_EEVEE'/'BLENDER_EEVEE_NEXT',
    device: 'CPU', 'GPU',
    progressive: True, False"""

    scene.render.engine = engine
    scene.cycles.device = device
    scene.cycles.progressive = progressive
    scene.cycles.samples = scene.eevee.taa_render_samples = samples
    scene.cycles.max_bounces = max_bounces
    scene.cycles.diffuse_bounces = diffuse_bounces
    scene.cycles.glossy_bounces = glossy_bounces
    scene.cycles.transparent_max_bounces = transparent_max_bounces
    scene.cycles.transmission_bounces = transmission_bounces
    scene.cycles.volume_bounces = volume_bounces
    if bpy.app.version < (3, 0, 0):
        scene.render.tile_x = scene.render.tile_y = render_tiles

    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = resolution_percentage
    scene.render.film_transparent = film_transparent

    scene.render.image_settings.file_format = file_format
    scene.render.image_settings.color_mode = color_mode

    # Eevee:
    scene.eevee.use_gtao = scene.eevee.use_ssr = scene.eevee.use_ssr_refraction = True
    scene.eevee.use_gtao_bent_normals = scene.eevee.use_gtao_bounce = scene.eevee.use_ssr_halfres = False


def remove_duplicate_consecutive(string, input):
    """Remove the duplicate consecutive characters from the string, for example "aaabbbccc" to "abc" """
    import itertools
    return ''.join(input if a == input else ''.join(b) for a, b in itertools.groupby(string))


def get_in_out_group(node_tree):
    """Return the input and output nodes into the node_group, if they exist"""
    input_nodes = []
    output_nodes = []
    for n in node_tree.nodes:
        if n.type == "GROUP_INPUT" and n not in input_nodes:
            input_nodes.append(n)
        if n.type == "GROUP_OUTPUT":
            if n.is_active_output and n not in output_nodes:
                output_nodes.append(n)
    return input_nodes, output_nodes


def get_node_by_part_of_name_and_type(name, type, node_tree):
    """Return the node with the name and type, if the name is in name and the type is the same"""
    node = None
    for n in node_tree.nodes:
        if n.type == type:
            if name in n.name:
                node = n
    return node


def safety_node_link(node_tree, from_node, to_node, from_socket, to_socket):
    """Link the nodes, if the nodes are not linked, this function is only for avorid blender crash, but not really necessary"""
    if None in (node_tree, from_node, to_node, from_socket, to_socket):
        return
    # Sembra esserci un bug in blender sui link dei gruppi , quindi testiamo con l'uso di path_resolve

    # Qui poichè accetta, sia il nome del socket, sia il numero dell'indice (int)
    from_socket = '"' + str(from_socket) + '"' if isinstance(from_socket, str) else str(from_socket)
    to_socket = '"' + str(to_socket) + '"' if isinstance(to_socket, str) else str(to_socket)

    SocketOut = node_tree.path_resolve('nodes["' + from_node.name + '"].outputs[' + from_socket + ']')
    SocketIn = node_tree.path_resolve('nodes["' + to_node.name + '"].inputs[' + to_socket + ']')

    node_tree.links.new(SocketIn, SocketOut)



def store_properties_into_dict(source):
    """Store the property of the source object into a dictionary, return the dictionary with the property,
    usefull for store the property of the object before modify it,
    For example if you need to modify a bpy.data.scenes['My Scene'].cycles.device = 'GPU' and you need to restore the value after,
     or if you need to modify a bpy.data.scenes['My Scene'].cycles.samples = 100 and you need to restore the value after"""

    # Retrieve the property of the object and they sub property if property is not readonly, use only blender api
    properties_dict = {}
    for key in source.bl_rna.properties.keys():
        if key == 'pixels':  # Ci mette troppo sulle immagini nel caso
            continue
        # Preserve if getattr produce error in some cases (Like custom prop from another addon)
        try:
            source_attribute = getattr(source, key)
        except:
            continue

        if not source.is_property_readonly(key):
            # Store into dict:
            properties_dict[key] = source_attribute

    return properties_dict


def store_attributes(source):
    """Store the attributes of the source object into a dictionary, return the dictionary with the attributes,
    useful for store the attributes of the object before modify it,
    For example if you need to modify a bpy.data.scenes['My Scene'].cycles.device = 'GPU' and you need to restore the value after"""

    # Retrieve the attributes of the object and they sub property if property is not readonly, use only blender api
    attributes_dict = {}
    for key in source.bl_rna.properties.keys():
        if not source.is_property_readonly(key):
            # Get the attribute:
            source_attribute = getattr(source, key)
            # Store into dict:
            attributes_dict[key] = source_attribute
    # Return the dict:
    return attributes_dict


def restore_attributes(source, attributes_dict):
    """Restore the attributes of the source object from the attributes_dict, return the source object,
    useful for restore the attributes of the object after modify it,
    For example if you need to modify a bpy.data.scenes['My Scene'].cycles.device = 'GPU' and you need to restore the value after"""
    # Restore the attributes of the object and they sub property if property is not readonly, use only blender api
    for key, value in attributes_dict.items():
        try:
            setattr(source, key, value)
        except:
            pass


def copy_attributes(source, destination, exlude=['pixels']):
    """Copy the attributes from the source to the destination.
    source: the source object from copy the attributes
    destination: the destination object where copy the attributes
    exlude: the list of attributes to exclude from the copy"""
    for key in source.bl_rna.properties.keys():
        if key in exlude:
            continue
        if not hasattr(destination, key):
            continue

        if not source.is_property_readonly(key):
            source_attribute = getattr(source, key)
            # In some cases, the attribute is not writable, so we skip it (Unknow reason)
            try:
                setattr(destination, key, source_attribute)
            except:
                pass


def copy_object(ob, new_name):
    """Copy the object from data.objects, return the new object, for example: copy_object(ob, "new_name")"""
    if ob.data:
        copy_data = ob.data.copy()
    copy_ob = ob.copy()
    # copy_ob.name = return_name_without_numeric_extension(copy_ob.name)

    if ob.data:
        copy_ob.data = copy_data
        copy_ob.data.name = new_name

    copy_ob.name = new_name

    return copy_ob


def join_multiple_group_inputs(node_tree):
    """Join the multiple group inputs nodes into one, useful for the node_group"""
    # Join tra tutti i nodi di tipo Inputs in un unico singolo inputs
    nodes = node_tree.nodes
    links = node_tree.links

    input_nodes, output_nodes = get_in_out_group(node_tree)

    if len(input_nodes) < 2:
        return

    new_input = nodes.new('NodeGroupInput')
    new_input.location = 0, 0

    for node in input_nodes:
        for idx, out in enumerate(node.outputs):
            for l in out.links:
                to_socket = l.to_socket
                links.new(new_input.outputs[idx], to_socket)
                # safety_node_link(node_tree, new_input, l.to_node, idx, to_socket.name)

    for n in input_nodes:
        nodes.remove(n)


def remove_nodes(node_tree, keep_output=False):
    """Remove all nodes from the node_tree.nodes, if keep_output is True, keep the output node if present, else create a new output node"""
    output_node = None
    nodes = node_tree.nodes
    for n in nodes:
        if n.type == 'OUTPUT_MATERIAL' and keep_output:
            n.is_active_output = True
            output_node = n
            continue
        nodes.remove(n)

    # In this case we need to create a new output node, because the function have keep_output=True
    if keep_output and not output_node:
        node_tree_type = get_node_tree_type(node_tree)
        if node_tree_type == 'MATERIAL':
            output_node = nodes.new('ShaderNodeOutputMaterial')
        elif node_tree_type == 'WORLD':
            output_node = nodes.new('ShaderNodeOutputWorld')

        output_node.location = 0, 0
        output_node.is_active_output = True


def check_if_textures_exist(path):
    """Check if the textures exist, return True if exist, False if not exist"""
    # Controlla se ci sono texture nel path
    cf = (
        ".png", ".jpg", ".bmp", ".sgi", ".rgb", ".bw", ".jpeg", ".jp2", ".j2c", ".tga", ".cin", ".dpx", ".exr", ".hdr",
        ".tif", ".tiff", ".mov", ".mpg", ".mpeg", ".dvd", ".vob", ".mp4", ".avi", ".dv", ".ogg", ".ogv", ".mkv", ".flv")
    check = None
    for fn in os.listdir(path):
        if fn.lower().endswith(cf):
            if os.path.isfile(os.path.join(path, fn)):
                check = True
    return check


def bmesh_create_object(ob_data, obj_type):
    """Create the object from the bmesh data, return the new object, type acepted: 'CUBE', UV_SPHERE' (For now)"""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob_data)
    if obj_type == 'CUBE':
        bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
    if obj_type == 'UV_SPHERE':
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=1, calc_uvs=True)
    if obj_type == 'PLANE':
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1, calc_uvs=True)

    bm.to_mesh(ob_data)
    bm.free()
    ob_data.update()


def smart_projection_on_object(ob, ob_mode, scene, bake_layer, angle_limit, island_margin, area_weight, correct_aspect,
                               scale_to_bounds):
    """Smart UV projection on the object"""
    # Qui si prepara la smart_projection, universale con input ben definiti
    # Utilizzo il nome dell'uv_layers, poichè l'assegnazione di una varibile ritorna allo stato precedente, invece con una stringa si
    # Appunto perchè non sempre l'oggetto passato a questa funzione potrebbe avere nemmeno 1 layer attivo
    from_uv_layer = ob.data.uv_layers.active
    if from_uv_layer:
        from_uv_layer = from_uv_layer.name
        from_uv_active_render = ob.data.uv_layers[from_uv_layer].active_render

    ob.data.uv_layers.active = ob.data.uv_layers[bake_layer.name]
    ob.data.uv_layers[bake_layer.name].active_render = True

    ob.data.uv_layers.update()

    for o in scene.objects:
        o.select_set(state=True if o == ob else False)
    bpy.context.view_layer.objects.active = ob
    set_object_mode(ob)
    for f in ob.data.polygons:
        f.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project(angle_limit=angle_limit, island_margin=island_margin, area_weight=area_weight,
                             correct_aspect=correct_aspect, scale_to_bounds=scale_to_bounds)
    bpy.ops.object.mode_set(mode=ob_mode)

    ob.data.uv_layers.update()

    if from_uv_layer:
        ob.data.uv_layers.active = ob.data.uv_layers[from_uv_layer]
        ob.data.uv_layers[from_uv_layer].active_render = from_uv_active_render


def return_valid_image_file(shaderPath):
    """Return the valid image file, if not exist return None"""
    cf = (
        ".png", ".jpg", ".bmp", ".sgi", ".rgb", ".bw", ".jpeg", ".jp2", ".j2c", ".tga", ".cin", ".dpx", ".exr", ".hdr",
        ".tif", ".tiff", ".mov", ".mpg", ".mpeg", ".dvd", ".vob", ".mp4", ".avi", ".dv", ".ogg", ".ogv", ".mkv", ".flv")
    file = os.path.isfile(bpy.path.abspath(shaderPath))
    if file:
        file = bpy.path.abspath(shaderPath)
        if file.endswith(cf):
            return file
    return


def hide_unide_unused_sockets(node, bool):
    """Hide or unhide the unused sockets"""
    for n_input in node.inputs:
        if not n_input.is_linked:
            n_input.hide = bool
    for n_output in node.outputs:
        if not n_output.is_linked:
            n_output.hide = bool


def url_to_domain_name(url):
    """Return the domain name from the url, example: https://www.google.com -> google"""
    domain = urlparse(url).netloc
    return domain


def save_text_file(string, path):
    """Save the string in a text file"""
    with open(path, "w") as fh:
        fh.write(string)


def get_percentage(part, whole, decimal=2):
    """Return the percentage of the part in the whole"""
    if whole == 0:
        return 0.00
    percentage = 100 - (((whole - part) / whole) * 100)
    if percentage > 100:
        return 100

    return round(percentage, decimal)


def save_data_to_file(data, path, append=False):
    """Save the data to a file"""
    with open(path, "ab" if append else "wb") as fh:
        fh.write(data)


def get_walk_files(path="", get_files=[], skip_files=[], get_by_extensions=[]):
    """
    Restituisce un dizionario che contiene il seguente esempio:
    {idx: {"fullpath": "",
           "relativepath": "",
           "filename": "",
           "foldername": ""}
    path= the path you want to analyze
    get_files = list of filename to get (example "filename.ext")
    skip_files = list of filenames you want to exclude from the walk
    get_by_extension = If the file endswith for example ".png"
    """
    fdict = {}
    index = -1
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn not in skip_files:
                if get_files:
                    if fn not in get_files:
                        continue

                if get_by_extensions:
                    if not [ext for ext in get_by_extensions if ext in fn]:
                        continue

                full_path = os.path.join(root, fn)
                # relative_path è il percorso relativo a dove si trova la libreria, cioè la folder principale della libreria
                # è utile per confrontare il registro online, poichè anch'esso ha un indice di path relativi a quella folder
                relative_path = os.path.relpath(full_path, path)
                fileProp = {"fullpath": full_path,
                            "relativepath": relative_path,
                            "filename": fn,
                            "foldername": os.path.basename(os.path.dirname(root))}
                index += 1
                fdict[index] = fileProp

    return fdict


def split_path(path=""):
    """Split the path in a list of folders, for example: /home/user/folder -> [home, user, folder]"""
    npath = ntpath.normpath(path)
    path_splitted = npath.split(ntpath.normpath(os.sep))
    return path_splitted


def is_subduplicate_path(path=""):
    """Return True if the path is a subduplicate path, for example: /home/user/folder/folder -> True"""

    """Controllo dedicato per vedere se l'utente non inserisce per sbaglio come path un path del genere:
    //path//EXTREME_PBR_LIBRARY//EXTREME_PBR_LIBRARY"""
    splitted_path = split_path(path)
    if splitted_path:
        folder_name = splitted_path[-1]
        if len([folder for folder in splitted_path if folder_name in folder]) > 1:
            return True


def byte_to_string(byte):
    """Convert the byte in a string"""
    return str(byte, "utf-8")


def bytes_to_human(size, dp=2):
    """Return the size in human readable format, for example: 1024 -> 1.00 KB or 1048576 -> 1.00 MB"""
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{dp}f} {unit}"


def gb_to_bytes(gb):
    """Return the size in bytes, for example: 1 GB -> 1073741824 bytes"""
    bts = gb * 1073741824
    # Check if the bts is a float, if not return an int
    # If bts == Float, transform it in int
    if type(bts) == float:
        bts = int(bts)
    return bts


def human_time_seconds(seconds):
    """Return the seconds in human readable format, for example: 60 -> 1 min, or 3600 -> 1 hour"""
    return str(datetime.timedelta(seconds=seconds))


def get_zip_file_names(zip_file, only_file=True):
    """Return list of files inside the zip file
    zip_file = FilePath
    only_file = If True, return only the real file, if False return Files, and Directories"""
    with ZipFile(zip_file, 'r') as zipObj:
        files = zipObj.namelist()
    if only_file:
        return [name for name in files if not name.endswith('/')]
    else:
        return files


def unzip(filepath, to_dir):
    "Unzip and into return get the files list"
    zip_files = ""
    with ZipFile(filepath, 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall(to_dir)
        zip_files = zipObj.namelist()

    # Restituisce solo files reali /path/folder/file.ext e non percorsi /path/folder/
    real_files = []
    for name in zip_files:
        if not name.endswith('/'):
            real_files.append(name)

    return real_files


def human_datetime():
    """Return the current datetime in human readable format, for example: 2020-12-31 23:59:59"""
    now = datetime.datetime.now()
    human_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return human_time


def write_into_txt_file(txt_file, lines=[]):
    """Write the lines into the txt file"""
    file1 = open(txt_file, "a")
    for line in lines:
        file1.writelines(line)
    file1.close()  # to change file access modes


def is_node_group(node_tree):
    """Return if node_tree is a node group, example: node_tree = bpy.data.node_groups["NodeGroup"], return True"""
    if not repr(node_tree).startswith("bpy.data.materials"):
        if not repr(node_tree).startswith("bpy.data.worlds"):
            return True


def string_has_numbers(string):
    return any(char.isdigit() for char in string)


def get_k_size_from_fn(fn):
    """Return string with k size, Like 01k or similar.
    String need to contain the right nomenclature, like 01k or 1k, separated by _ (Undercore)"""
    if os.path.isfile(fn):
        fn = get_filename_from_path(fn)

    from pathlib import Path
    fn = Path(fn).stem  # Elimina l'estensione file dal nome

    fn_splitted = fn.split("_")

    size = next((substring for substring in fn_splitted if string_has_numbers(substring) if "k" in substring.lower()),
                None)
    if not size:
        return

    return size


def delete_file_or_folder(filepath):
    """Accept File Paths or Folder Paths"""
    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
            return True
        except:
            return

    elif os.path.isdir(filepath):
        try:
            shutil.rmtree(filepath)
            return True
        except:
            return


# def copy_file(source, destination):
#     """Copy the file from source to destination, example: source = "C:/source/file.ext", destination = "C:/destination/file.ext",
#     acepts any file type"""
#     import sys, os
#     if sys.platform == "win32":
#         os.system('xcopy "%s" "%s"' % (source, destination))
#     else:
#         with open(source, 'rb') as filein:
#             with open(destination, 'wb') as fileout:
#                 shutil.copyfileobj(filein, fileout, 128 * 1024)


def copy_file(src, dst, buffer_size=10485760, perserveFileDate=True):
    '''
    Copies a file to a new location. Much faster performance than Apache Commons due to use of larger buffer
    @param src:    Source File
    @param dst:    Destination File (not file path)
    @param buffer_size:    Buffer size to use during copy
    @param perserveFileDate:    Preserve the original file date
    '''
    #    Check to make sure destination directory exists. If it doesn't create the directory
    time_start = time.time()
    print("Starting to copy file: " + src + " to " + dst)
    dstParent, dstFileName = os.path.split(dst)
    if (not (os.path.exists(dstParent))):
        os.makedirs(dstParent)

    #    Optimize the buffer for small files
    buffer_size = min(buffer_size, os.path.getsize(src))
    if (buffer_size == 0):
        buffer_size = 1024

    if shutil._samefile(src, dst):
        raise shutil.Error("`%s` and `%s` are the same file" % (src, dst))
    for fn in [src, dst]:
        try:
            st = os.stat(fn)
        except OSError:
            # File most likely does not exist
            pass
        else:
            # XXX What about other special files? (sockets, devices...)
            if shutil.stat.S_ISFIFO(st.st_mode):
                raise shutil.SpecialFileError("`%s` is a named pipe" % fn)
    with open(src, 'rb') as fsrc:
        with open(dst, 'wb') as fdst:
            shutil.copyfileobj(fsrc, fdst, buffer_size)

    if (perserveFileDate):
        shutil.copystat(src, dst)

    time_end = time.time()
    print("Finished copying file: " + src + " to " + dst + " in " + str(time_end - time_start) + " seconds")


def purge_all_group_names(node_tree):
    """Purge all the group names from the node tree, example, from name "Group.001" to "Group" """
    nodes = node_tree.nodes
    # From the function retrieve_nodes, we have all the nodes and sub-nodes inside the node_tree
    nodes = retrieve_nodes(node_tree)
    for n in nodes:
        if not has_nodetree(n):
            continue
        n.node_tree.name = return_name_without_numeric_extension(n.node_tree.name)
        n.name = return_name_without_numeric_extension(n.node_tree.name)


def sub_nodes(node):
    """Return the sub nodes of a node, example: node = bpy.data.node_groups["NodeGroup"].nodes["Node"].node_tree.nodes["SubNode"] etc..."""
    # Esamina tutti i nodi dei grouppi:
    yield node
    if node.type == 'GROUP':
        if node.node_tree:
            for n in node.node_tree.nodes:
                yield from sub_nodes(n)


def retrieve_nodes(node_tree):
    """Return all the nodes and sub-nodes of the node_tree, example: node_tree = bpy.data.node_groups["NodeGroup"]
    return all the nodes and sub-nodes inside the node_tree and sub-node_tree
    :input node_tree: all type of node_tree, for example: bpy.data.node_groups["NodeGroup"] or bpy.data.materials["Material"].node_tree etc..."""

    # Restituisce anche il genitore , nella lista sarà il secondo valore
    node_list = []
    if not node_tree:
        return node_list

    def sub_node_tree(n_tree):
        for n in n_tree.nodes:
            node_list.append(n)
            if n.type == 'GROUP' and hasattr(n, 'node_tree') and n.node_tree:
                sub_node_tree(n.node_tree)
            elif hasattr(n, 'node_tree') and n.node_tree:
                sub_node_tree(n.node_tree)

    for n in node_tree.nodes:
        node_list.append(n)
        if n.type == 'GROUP' and hasattr(n, 'node_tree') and n.node_tree:
            sub_node_tree(n.node_tree)
        elif hasattr(n, 'node_tree') and n.node_tree:
            sub_node_tree(n.node_tree)

    return node_list


def get_node_row(node, hide_node_types=[]):
    """Return the row of the node in the shader editor"""
    row = {}
    if not hasattr(node, 'inputs'):
        return {}

    for idx, i in enumerate(node.inputs):
        if not i.is_linked:
            continue
        from_node = i.links[0].from_node

        if from_node not in row.values():
            if from_node.type not in hide_node_types:
                row[idx] = from_node

    return row


def organize_node_tree_groups_ui(data, layout, get_volume=False, get_displace=False):
    if not data.use_nodes:
        return

    node_tree = data.node_tree
    nodes = node_tree.nodes

    nodes_dict = {}
    out = node_tree.get_output_node('ALL')

    if not out:
        return

    node_row = get_node_row(out)
    if node_row:
        nodes_dict['0'] = node_row
        for idx, n in node_row.items():
            node_row = get_node_row(n)
            nodes_dict['1'] = node_row
            for idx, n in node_row.items():
                node_row = get_node_row(n)
                nodes_dict['2'] = node_row
                for idx, n in node_row.items():
                    node_row = get_node_row(n)
                    nodes_dict['3'] = node_row
                    for idx, n in node_row.items():
                        node_row = get_node_row(n)
                        nodes_dict['4'] = node_row

    return nodes_dict


def panel_node_draw(layout, id_data, input_name):
    if not id_data.use_nodes:
        return False

    node_tree = id_data.node_tree

    node = node_tree.get_output_node('ALL')
    if node:
        input = find_node_input(node, input_name)
        if input:
            layout.template_node_view(node_tree, node, input)
        else:
            layout.label(text="Incompatible output node")
    else:
        layout.label(text="No output node")

    return True


def has_nodetree(id_data):
    """Return if id_data has a nodetree, for example: id_data = bpy.data.materials["Material"] or id_data = bpy.data.worlds["World"]"""
    if not hasattr(id_data, 'node_tree'):
        return False
    if id_data.node_tree is None:
        return False

    return True


def hide_object(o, hide=True, use_hide_render=None, use_hide_viewport=None, use_hide_set=None):
    """Hide an object, example: o = bpy.data.objects["Object"], from the viewport and the render
    :param o: the object to hide
    :param hide: True to hide, False to unhide
    :param use_hide_render (Optional): if True, hide/un the object only from the render
    :param use_hide_viewport (Optional): if True, hide/un the object only from the viewport
    :param use_hide_set (Optional): if True, hide/un the object only from the hide_set"""

    if (use_hide_render, use_hide_viewport, use_hide_set) == (None, None, None):
        o.hide_render = hide
        o.hide_viewport = hide
        o.hide_set(state=hide)
        return
    if use_hide_render:
        o.hide_render = hide
    if use_hide_viewport:
        o.hide_viewport = hide
    if use_hide_set:
        o.hide_set(state=hide)

def is_hidden_object(o, get='ALL'):
    """Return if the object is hidden, example: o = bpy.data.objects["Object"], get = 'RENDER' or 'VIEWPORT' or 'HIDE_GET' or 'ALL'
    return True if the object is hidden, False if not hidden, None if get = 'ALL'"""

    if get == 'RENDER':
        return o.hide_render
    if get == 'VIEWPORT':
        return o.hide_viewport
    if get == 'HIDE_SET':
        return o.hide_get()
    if get == 'ALL':
        if o.hide_render or o.hide_viewport or o.hide_get():
            return True
        return False



def lock_object(objs, hide_select=None, location=(True, True, True), rotation=(True, True, True),
                scale=(True, True, True)):
    """Lock an object, example: ob = bpy.data.objects["Object"], This make the object unmovable, but not from the transform panel"""
    # Check if objs is a list or a single object
    if not isinstance(objs, list):
        objs = [objs]

    for ob in objs:
        ob.lock_location = location
        ob.lock_rotation = rotation
        ob.lock_scale = scale
        if hide_select is not None:
            ob.hide_select = hide_select


def set_vertex_color(ob, v_col_name, color=(0, 0, 0, 1), make_active=True):
    """Set the vertex color of an object, example: ob = bpy.data.objects["Object"], v_col_name = "VertexColor", color = (0, 0, 0, 1)"""
    if ob.type != 'MESH':
        return

    v_col = ob.data.vertex_colors.get(v_col_name)
    if not v_col:
        v_col = ob.data.vertex_colors.new(name=v_col_name)

    for vCol in ob.data.vertex_colors[v_col.name].data:
        for i in range(len(vCol.color) - 1):
            if i % 4 == 0:
                vCol.color[i] = color[0]
                vCol.color[i + 1] = color[1]
                vCol.color[i + 2] = color[2]
                vCol.color[i + 3] = color[3]


def matrix_to_world(ob, co):
    """Return the world coordinates of a local coordinate"""
    mat = ob.matrix_world
    loc = mat @ co
    return loc


def data_from_string(id_data_string):
    """Accepted string:
    "bpy.data.materials", "bpy.data.worlds", "bpy.data.node_groups" """
    if id_data_string == "bpy.data.materials":
        return bpy.data.materials
    if id_data_string == "bpy.data.worlds":
        return bpy.data.worlds
    if id_data_string == "bpy.data.node_groups":
        return bpy.data.node_groups


def data_to_string(id_data):
    """Accepted data:
    bpy.data.materials, bpy.data.worlds, bpy.data.node_groups"""
    if id_data == bpy.data.materials:
        return "bpy.data.materials"
    if id_data == bpy.data.worlds:
        return "bpy.data.worlds"
    if id_data == bpy.data.node_groups:
        return "bpy.data.node_groups"


def center_view(view_location=(0, 0, 2), view_distance=5.73,
                view_rotation=(0.7071067094802856, 0.7071068286895752, 0.0, 0.0)):
    """Center the 3D view at a specific location, with a specific distance and rotation"""
    for space in [area.spaces[0] for area in bpy.context.window.screen.areas if area.type == 'VIEW_3D']:

        space.region_3d.view_perspective = 'PERSP'
        space.region_3d.view_rotation = view_rotation
        space.region_3d.view_location = view_location
        space.region_3d.view_distance = view_distance

        if space.region_3d.view_perspective == 'CAMERA':
            space.region_3d.view_perspective = 'PERSP'
            bpy.ops.view3d.view_camera()


def show_overlays(state=True):
    """Show or hide the overlays in the 3D viewport"""
    area = get_view_3d_area()
    if area:
        area.overlay.show_overlays = state


def create_camera_and_place(scene, name="Camera", camera_id_name="", lens=12, location=(0, 0, 0),
                            rotation_in_degrees=(90, 0, 0), is_scene_camera=True):
    rotation = Vector(rotation_in_degrees)
    rotation.x += math.radians(90)
    rotation.z *= -1

    """Create a camera object and place it in the scene, to decide the camera resolution use the scene render settings"""
    cam_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, cam_data)

    scene.collection.objects.link(camera)

    camera.data.type = 'PERSP'
    camera.data.lens = lens
    camera.location = location
    camera.rotation_euler = rotation
    camera.hdri_prop_obj.object_id_name = camera_id_name

    if is_scene_camera:
        scene.camera = camera

    return camera


def set_render_attributes(scene, attributes_dict):
    """Set the render attributes of the scene"""
    for key, value in attributes_dict.items():
        try:
            if hasattr(scene.render, key):
                setattr(scene.render, key, value)
        except:
            pass


class Mtrx:
    """A class to handle standard vector operations"""
    last_scalars = {}
    last_rotation = {}

    def __init__(self, data_id, vertex_location, scalar, pivot=(0, 0, 0)):
        self.data_id = data_id
        self.vertex_location = vertex_location
        self.scalar = scalar
        self.pivot = pivot

    def scale_vertex(self):
        """Scale a vertex"""
        if not Mtrx.last_scalars.get(self.data_id):
            Mtrx.last_scalars[self.data_id] = 1

        p = Vector(self.pivot)
        v_co = Vector(self.vertex_location)

        current_value = (self.scalar / Mtrx.last_scalars[self.data_id])

        v_co -= p
        v_co.x *= current_value
        v_co.y *= current_value
        v_co.z *= current_value
        v_co += p

        Mtrx.last_scalars[self.data_id] = self.scalar

        return v_co

    # def rotation_vertex(self):
    #     """Rotate a vertex"""
    #     if not Mtrx.last_rotation.get(self.data_id):
    #         Mtrx.last_rotation[self.data_id] = (0, 0, 0)
    #
    #     p = Vector(self.pivot)
    #     v_co = Vector(self.vertex_location)
    #
    #     current_value = (self.scalar - Mtrx.last_rotation[self.data_id])
    #
    #     v_co -= p
    #     v_co.rotate(Euler(current_value, 'XYZ'))
    #     v_co += p
    #
    #     Mtrx.last_rotation[self.data_id] = self.scalar
    #
    #     return v_co


def override_view_3d_context():
    """Override the 3D view context"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = bpy.context.copy()
                    override['area'] = area
                    override['region'] = region
                    return override


def set_object_mode(active_object):
    """Set the object mode"""
    scn = bpy.context.scene
    objects = scn.objects
    if not objects:
        return

    for ob in objects:
        ob.select_set(state=False)

    selected_objects = []
    for ob in objects:
        if ob.mode in ['EDIT', 'POSE']:
            if not active_object:
                active_object = bpy.context.view_layer.objects.active = ob
            ob.select_set(state=True)
            selected_objects.append(ob)

    if selected_objects:
        bpy.ops.object.mode_set(mode='OBJECT')


def get_filepath_from_filename(filepath, filename):
    """Get filepath from filename
        Input: filepath = 'C:\\Users\\user\\Desktop\\'
               filename = 'test
               if filename is 'test.jpg' or .png' or .jpeg or .bmp' then return filepath + filename
               Output: 'C:\\Users\\user\\Desktop\\test.jpg or .png' or .jpeg or .bmp'
               If file not found return None"""

    # Prova se il file ha queste estensioni, se le ha restituisce il percorso file
    # controlla tutti i formati immagine:
    for extension in ['.jpg', '.jpeg', '.png']:
        complete_filename = filename + extension
        complete_filepath = os.path.join(filepath, complete_filename)
        if os.path.isfile(complete_filepath):
            return complete_filepath

    # Se non è riuscito a trovare il file restituiamo un file contenuto nella cartella se contiene in parte il filename
    # Questo se capita che ci sono dei preview file immagini che si chiamano per esempio: imagename.exr.png

    for file in os.listdir(filepath):
        if filename.replace(" ", "_").lower() in file.replace(" ", "_").lower():
            return os.path.join(filepath, file)



def is_string_cointain_number(string, skip_dot=False):
    """Check if a string contain a number"""
    if skip_dot:
        string = string.replace('.', '')

    return any(char.isdigit() for char in string)


def asign_image_into_render_window(context, image):
    for w in context.window_manager.windows:
        if len(w.screen.areas) != 1:
            continue
        for area in w.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = image


def get_image_from_render_window(context):
    for w in context.window_manager.windows:
        if len(w.screen.areas) != 1:
            continue
        for area in w.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                return area.spaces.active.image


def screen_shading_type(get_set='GET', shading_type='MATERIAL'):
    """Set the shading type enum in [SOLID, WIREFRAME, TEXTURED, MATERIAL, RENDERED]"""
    if not bpy.context.screen:
        # TODO: Tenere d'occhio questo potrebbe dare problemi, ma è necessario in quanto ci sono dei momenti in cui non esiste lo screen
        return

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if get_set == 'GET':
                        return space.shading.type
                    else:
                        space.shading.type = shading_type
                        return space.shading.type


def get_shading_engine():
    """Get which rendering engine is being used based on the type of shading"""
    scn = bpy.context.scene
    engine = scn.render.engine

    shading_type = screen_shading_type(get_set='GET')

    if engine == 'BLENDER_WORKBENCH':
        return engine
    if shading_type == 'MATERIAL':
        return 'BLENDER_EEVEE'
    if shading_type in ['RENDERED', 'SOLID', 'WIREFRAME', 'TEXTURED']:
        return engine


def get_output_node(node_tree):
    """This function returns the output node of the node tree if exist and if is connected and if is_active_output"""
    output_node = None
    for node in node_tree.nodes:
        if node.type == 'OUTPUT_WORLD':
            if node.is_active_output:
                if [i for i in node.inputs if i.is_linked]:
                    output_node = node
                    break

    return output_node


def get_all_blender_shadernodes():
    """This function returns all the shader nodes existing in Blender"""
    ddir = lambda data, filter_str: [i for i in dir(data) if i.startswith(filter_str)]
    get_nodes = lambda cat: [i for i in getattr(bpy.types, cat).category.items(None)]
    cycles_categories = ddir(bpy.types, "NODE_MT_category_SH_NEW")

    shadernodes = []
    for cat in cycles_categories:
        for node in get_nodes(cat):
            shadernodes.append((node.nodetype, node.label))

    return shadernodes


def get_nodes_ranges_xy(node_tree, exclude_nodes=[]):
    """
    This function calculate the min_x/min_y/max_x/max_y values of the nodes locations.

    :node_tree: the node tree
    :exclude_nodes: a list of nodes to exclude from the calculation"""

    nodes = node_tree.nodes
    if not nodes:
        return {}

    locations = [node.location for node in nodes if node not in exclude_nodes]

    min_x = min([i[0] for i in locations])
    max_x = max([i[0] for i in locations])
    min_y = min([i[1] for i in locations])
    max_y = max([i[1] for i in locations])

    # Calculate center x and y
    if len(locations) == 1:
        center_x = locations[0][0]
        center_y = locations[0][1]
    else:
        center_x = (max_x - min_x) / 2
        center_y = (max_y - min_y) / 2

    return {'min_x': min_x, 'max_x': max_x, 'min_y': min_y, 'max_y': max_y, 'center_x': center_x, 'center_y': center_y}


def make_parent(father, object_list=[]):
    """Make parent
    :father: the father object
    :object_list: a list or single object of objects to make parent"""
    if type(object_list) != list:
        object_list = [object_list]

    for ob in object_list:
        # If the object is already parented with father, skip it
        if ob.parent == father:
            continue
        # ob.matrix_world = father.matrix_world
        ob.parent = father
        ob.matrix_parent_inverse = father.matrix_world.inverted()


def make_parent_v2(father, object_list=[]):
    """Make parent
    :father: the father object
    :object_list: a list or single object of objects to make parent"""
    ob_mode = bpy.context.object.mode

    if ob_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    if type(object_list) != list:
        object_list = [object_list]

    # Check if the object is already parented with father
    parented = [ob for ob in object_list if ob.parent == father]
    # If all the objects are already parented with father, skip it and return
    if len(parented) == len(object_list):
        return

    # Old Selected and active object
    selected = bpy.context.selected_objects[:]
    active = bpy.context.active_object

    # Many object can be hide_select, so we need to unhide them
    # Store the hide_select state of the objects and of the father
    hide_select_state = {}
    for ob in [father] + object_list:
        hide_select_state[ob.name] = ob.hide_select
        ob.hide_select = False

    # Make parent using bpy.ops
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = father
    father.select_set(True)
    for ob in object_list:
        ob.select_set(True)

    override = {'object': father, 'selected_editable_objects': object_list}
    if use_temp_override():
        # Use bpy.context.temp_override if the version is 3.2 or higher
        with bpy.context.temp_override(**override):
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    else:
        bpy.ops.object.parent_set(override, type='OBJECT', keep_transform=True)


    # Restore the hide_select state of the objects
    for ob in [father] + object_list:
        ob.hide_select = hide_select_state[ob.name]

    # Restore old selected and active object
    bpy.ops.object.select_all(action='DESELECT')
    for ob in selected:
        ob.select_set(True)
    if active:
        bpy.context.view_layer.objects.active = active

    # Restore old mode
    bpy.ops.object.mode_set(mode=ob_mode)


def un_parent(object_list=[]):
    """Un-parent
    :object_list: a list or single object of objects to unparent"""
    if type(object_list) != list:
        object_list = [object_list]

    for ob in object_list:
        # Check if the object is parented
        if not ob.parent:
            continue
        # Get world location:
        world_loc = ob.matrix_world.to_translation()
        ob.parent = None
        ob.matrix_world.translation = world_loc


def get_vertices_from_vg(ob, vertex_group):
    """Get the vertices from a vertex group"""
    vg = ob.vertex_groups.get(vertex_group)
    if not vg:
        return []
    return [v for v in ob.data.vertices if vg.index in [g.group for g in v.groups]]


def get_edges_from_vg(ob, vertex_group=""):
    """Get the edges from a vertex group"""
    vg = ob.vertex_groups.get(vertex_group)
    if not vg:
        return []

    vg_index = ob.vertex_groups[vertex_group].index
    # Get the vertices if inside the vg_index
    vertices = [v.index for v in ob.data.vertices if vg_index in [vg.group for vg in v.groups]]
    edges = [e for e in ob.data.edges if e.vertices[0] in vertices and e.vertices[1] in vertices]

    return edges


def subdivide_mesh(ob, vertex_group="", cuts=1, len_vertices=False, use_grid_fill=True):
    """Subdivide mesh"""
    # Get Vertex group index
    if vertex_group:
        if not ob.vertex_groups.get(vertex_group):
            return
        edges = get_edges_from_vg(ob, vertex_group)
    else:
        edges = ob.data.edges

    import bmesh
    # Get the bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.edges.ensure_lookup_table()

    # Get the edges
    bm_edges = [bm.edges[i.index] for i in edges]

    # Subdivide
    bmesh.ops.subdivide_edges(bm, edges=bm_edges, use_grid_fill=use_grid_fill, cuts=cuts)

    # Update the mesh
    bm.to_mesh(ob.data)
    bm.free()

    # Update the mesh
    ob.data.update()

    if len_vertices:
        # Len now the vertices into the vertex group
        return len(get_vertices_from_vg(ob, vertex_group))


def un_subdivide_mesh(ob, vertex_group="", iterations=2, len_vertices=False):
    """Un Subdivide mesh"""
    import bmesh
    # Get Vertex group index
    if vertex_group:
        if not ob.vertex_groups.get(vertex_group):
            return
        vertices = get_vertices_from_vg(ob, vertex_group)
    else:
        vertices = ob.data.vertices

    # Get the bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()

    bm_verts = [bm.verts[v.index] for v in vertices]

    # Un-Subdivide
    bmesh.ops.unsubdivide(bm, verts=bm_verts, iterations=iterations)

    # Update the mesh
    bm.to_mesh(ob.data)
    bm.free()

    # Update the mesh
    ob.data.update()

    if len_vertices:
        return len(ob.data.vertices)


def set_object_bounds(ob, display_type='BOUNDS'):
    """Set object bounds"""
    if ob.type != 'MESH':
        return

    if display_type == 'BOUNDS':
        # In this case, the object need to be showed only in the viewport with the display_type = 'BOUNDS'
        ob.hide_render = True
        ob.visible_camera = False
        ob.visible_diffuse = False
        ob.visible_glossy = False
        ob.visible_transmission = False
        ob.visible_volume_scatter = False
        ob.visible_shadow = False
        ob.show_bounds = True
        ob.hide_render = True
        ob.display_type = 'BOUNDS'

    elif display_type == 'TEXTURED':
        # In this case, the object need to be showed in the viewport and in the render
        ob.hide_render = False
        ob.visible_camera = True
        ob.visible_diffuse = True
        ob.visible_glossy = True
        ob.visible_transmission = True
        ob.visible_volume_scatter = True
        ob.visible_shadow = True
        ob.show_bounds = False
        ob.hide_render = False
        ob.display_type = 'TEXTURED'


def use_temp_override():
    """Use temp override if the version is 3 or higher"""
    version = bpy.app.version
    major = version[0]
    minor = version[1]
    if major < 3 or (major == 3 and minor < 2):
        return False
    else:
        return True


def create_curve_circle(name="Circle", radius=1, vertices=4, resolution_u=8, location=(0, 0, 0), rotation=(0, 0, 0),
                        collection=None):
    """Create a circle curve"""
    # Create the Circle
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, enter_editmode=False, location=location, rotation=rotation)
    circle = bpy.context.active_object
    circle.name = name
    circle.data.resolution_u = resolution_u

    # Link on collection if circle is not in the collection
    if collection:
        # Unlink circle from context collection (bpy.ops) work on the context collection, so we need to move the object in the right collection
        if circle.users_collection[0] != collection:
            bpy.context.collection.objects.unlink(circle)

        if circle not in collection.objects[:]:
            collection.objects.link(circle)
    return circle


def create_empty_object(name="Empty", collection=None, empty_display_type='CUBE', size=1, location=(0, 0, 0),
                        rotation=(0, 0, 0)):
    """Create an empty object and link to the context.scene"""
    # Create an empty object
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = empty_display_type
    empty.empty_display_size = size
    empty.location = location
    empty.rotation_euler = rotation
    if collection:
        collection.objects.link(empty)
    else:
        bpy.context.scene.collection.objects.link(empty)
    return empty


def create_light(name="Light", light_type='POINT', collection=None, energy=100, use_contact_shadow=True,
                 color=(1, 1, 1), location=(0, 0, 0),
                 rotation=(0, 0, 0), size=2, size_y=2, light_color=(1, 1, 1)):
    """Create a light"""
    light = bpy.data.lights.new(name, light_type)
    light.energy = energy
    light.color = color
    light.use_contact_shadow = use_contact_shadow
    light_obj = bpy.data.objects.new(name, light)
    light_obj.location = location
    light_obj.rotation_euler = rotation
    light_obj.data.color = light_color
    if hasattr(light_obj.data, 'size'):
        light_obj.data.size = size
    if hasattr(light_obj.data, 'size_y'):
        light_obj.data.size_y = size_y
    if collection:
        collection.objects.link(light_obj)
    else:
        bpy.context.scene.collection.objects.link(light_obj)
    return light_obj


def create_circle_mesh(name="Circle", radius=1, vertices=4, location=(0, 0, 0), rotation=(0, 0, 0),
                       collection=None, fill=False):
    """Create a circle mesh"""
    mesh = bpy.data.meshes.new(name)
    circle = bpy.data.objects.new(name, mesh)
    # Create the circle with bmesh
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=fill, cap_tris=fill, segments=vertices, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    mesh.vertices.update()
    circle.location = location
    circle.rotation_euler = rotation
    if collection:
        collection.objects.link(circle)
    else:
        bpy.context.scene.collection.objects.link(circle)

    return circle


def get_edge_vertex_location_divided(obj, divide=2):
    """Get the location of the edge vertex divided, use only object with only one edge"""
    # La funzione divide il numero di vertici di un edge per il numero di volte specificato, e restituisce la lista delle posizioni dei vertici
    # La funzione funziona solo con oggetti con un solo edge

    # Get the vertices (only one edge)
    vertices = obj.data.vertices

    # Divide the vertices number by the number of times specified
    len_vertices = len(vertices)
    len_vertices_divided = len_vertices / divide

    # Get the location of the vertices, but transform local coordinate in world coordinate
    vertices_location = [obj.matrix_world @ vertices[i].co for i in range(len_vertices)]

    # vertices_location = [v.co for v in vertices]

    # Get the location of the vertices divided
    vertices_location_divided = []
    for i in range(divide):
        vertices_location_divided.append(vertices_location[int(i * len_vertices_divided)])

    # The location into vertices_location_divided are in obj local coordinate, so we need to transform in world coordinate
    vertices_location_divided_world = [obj.matrix_world @ v for v in vertices_location_divided]

    return vertices_location_divided


def apply_object_scale(object, children=[]):
    """Apply the scale of the object and the children"""

    # Keep in memory the selected objects and the evenutal active object
    selected_objects = bpy.context.selected_objects[:]
    active_object = bpy.context.view_layer.objects.active

    # Deselect all the objects
    if active_object:
        active_object.select_set(False)
    for obj in selected_objects:
        obj.select_set(False)

    # Make acrive the object
    object.select_set(True)
    bpy.context.view_layer.objects.active = object

    # Select the children
    for child in children:
        child.select_set(True)

    # Apply the scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Deselect the object
    object.select_set(False)

    # Restore the selected objects and the evenutal active object
    for obj in selected_objects:
        obj.select_set(True)
    if active_object:
        bpy.context.view_layer.objects.active = active_object


# Check if the path b is inside the path a
def is_inside_path(path_a, path_b):
    """This function check if the path b is children of path_a"""

    # Get the path of the path_a
    path_a = os.path.abspath(path_a)

    # Get the path of the path_b
    path_b = os.path.abspath(path_b)

    # Check if the path_b is inside the path_a
    if path_b.startswith(path_a):
        return True
    else:
        return False


class DotsRunning:
    """Report animated dots during the installation process"""
    dots_number = 0
    timer = 0

    def __init__(self, refresh_time=0.5):
        cls = self.__class__

        if cls.dots_number > 3:
            cls.dots_number = 0
        # Execute every refresh_time seconds
        if time.time() - cls.timer > refresh_time:
            cls.dots_number += 1
            cls.timer = time.time()

    def dots(self):
        dots = "." * self.__class__.dots_number
        return dots


def is_from_same_drive(path_a, path_b):
    """Compare the path of the disk, return True if the path are the same"""
    # Get the path of the path_a
    path_a = os.path.abspath(path_a)

    # Get the path of the path_b
    path_b = os.path.abspath(path_b)

    # Compare the path of the disk
    if os.path.splitdrive(path_a)[0] == os.path.splitdrive(path_b)[0]:
        return True
    else:
        return False


def make_local(data_id):
    """This function make local a data-block because if the data-block
    is imported from another file, it is not possible to modify it"""
    if not data_id:
        return
    if data_id.library:
        # In this case is not local, we need to make local
        data_id.make_local()


def replace_substring_if_exists(string, substring, new_substring):
    """Replace a substring if it exists"""
    if substring in string:
        string = string.replace(substring, new_substring)
    return string


# Controllo se i file e le cartelle sono aperte o in uso sul computer prima di rinominarli

def is_subfolder_and_files_in_use(path):
    """Check if the file is in use"""
    # Check if path is complete path
    if not os.path.isabs(path):
        return

    # Try to rename the path:
    try:
        os.rename(path, path)
    except:
        return True

    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.rename(file_path, file_path)
            except:
                return True

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rename(dir_path, dir_path)
            except:
                return True


def generate_zip(files):
    mem_zip = BytesIO()

    # Check if files is a list
    if not isinstance(files, list):
        files = [files]

    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f)

    return mem_zip


def root_path_is_empty(path):
    """Controlla se il percorso e tutte le sotto cartelle sono vuote da files"""

    if not os.path.isdir(path):
        return False

    for root, dirs, files in os.walk(path):
        for file in files:
            return False

    return True


def set_active_material(ob, material):
    if not hasattr(ob, 'data'):
        return
    if not hasattr(ob.data, 'materials'):
        return

    for idx, mat in enumerate(ob.data.materials):
        if mat == material:
            ob.active_material_index = idx
            break


def hide_modifiers(context, obj):
    if type(obj) != list:
        obj = [obj]

    objects_mods = []
    for ob in obj:
        for mod in ob.modifiers:
            if mod.show_viewport:
                mod.show_viewport = False
                objects_mods.append(mod)

        ob.data.update()
        ob.data.update_tag()
        ob.update_tag()
        ob.modifiers.update()

    context.area.tag_redraw()
    context.scene.update_tag()
    context.view_layer.update()
    return objects_mods


def unhidden_modifiers(context, objects_mods):
    for mod in objects_mods:
        mod.show_viewport = True

    context.area.tag_redraw()
    context.scene.update_tag()
    context.view_layer.update()


def string_to_number(string):
    """Data la stringa numerica, restituisce il numero e le eventuali operazioni"""
    # Controlliamo che nella stringa ci siano solo numeri od operazioni o punti o virgole
    accepted_char = "0123456789+-*/.,"
    # Rimuoviamo tutti i caratteri non presenti in accepted_char
    string = ''.join([char for char in string if char in accepted_char])
    # Ora convertiamo la stringa in un numero tenendo presente anche le operazioni
    try:
        # eval is safety because we already removed all the not accepted char!
        number = eval(string)
        return number
    except:
        return 0


def safety_eval(eval_string):
    """Questa funzione deve controllare che la stringa eval sia di Blender per evitare potenziali danni"""
    import bpy  # Make sure to import the bpy module! Don't remove it!

    string_accepted = [
        "bpy.data.materials",
        "bpy.data.worlds",
        "bpy.data.node_groups",
        "bpy.data.images",
        "bpy.data.textures",
        "bpy.data.brushes",
        "bpy.data.curves",
        "bpy.data.fonts",
        "bpy.data.grease_pencils",
        "bpy.data.lamps",
        "bpy.data.lattices",
        "bpy.data.meshes",
        "bpy.data.metaballs",
        "bpy.data.movieclips",
        "bpy.data.objects",
        "bpy.data.particles",
        "bpy.data.screens",
        "bpy.data.scenes",
        "bpy.data.speakers",
        "bpy.data.texts"]

    denied_string = [".cancel(",
                     ".remove(",
                     ".delete(",
                     ".unlink("]

    if not eval_string.startswith(tuple(string_accepted)):
        return False

    if any([string in eval_string for string in denied_string]):
        return False

    try:
        data = eval(eval_string)
    except Exception as e:
        print("Error From Safety Eval: " + str(e))
        return False

    return data


def remove_all_bpy_data():
    """Remove all the bpy data"""
    import bpy  # Make sure to import the bpy module! Don't remove it!

    for world in bpy.data.worlds:
        bpy.data.worlds.remove(world)
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for image in bpy.data.images:
        bpy.data.images.remove(image)
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)
    for node_group in bpy.data.node_groups:
        bpy.data.node_groups.remove(node_group)


def mesh_select_mode(get_set=None, set_mode=None):
    """Set the mesh select mode enum in [VERT, EDGE, FACE]"""

    mesh_select_mode = bpy.context.tool_settings.mesh_select_mode

    if get_set == 'GET':
        return mesh_select_mode

    if not set_mode:
        return

    if type(set_mode) == list:
        vert = edge = face = False
        for mode in set_mode:
            if mode == 'VERT':
                mesh_select_mode[0] = True
                vert = True
            if mode == 'EDGE':
                mesh_select_mode[1] = True
                edge = True
            if mode == 'FACE':
                mesh_select_mode[2] = True
                face = True

        if not vert:
            mesh_select_mode[0] = False
        if not edge:
            mesh_select_mode[1] = False
        if not face:
            mesh_select_mode[2] = False

    else:
        if set_mode == 'VERT':
            mesh_select_mode[0] = True
            mesh_select_mode[1] = False
            mesh_select_mode[2] = False
        elif set_mode == 'EDGE':
            mesh_select_mode[0] = False
            mesh_select_mode[1] = True
            mesh_select_mode[2] = False
        elif set_mode == 'FACE':
            print("Imposto Face")
            mesh_select_mode[0] = False
            mesh_select_mode[1] = False
            mesh_select_mode[2] = True



def get_addon_repo_index(addon_name):
    """In Blender 4.2 gli addon possono essere installati nella nuova maniera, cioè come estensioni, essi possono essere installati
    in diverse cartelle, che saranno dei repo, ogni repo ha un indice, questa funzione restituisce l'indice del repo in
    cui è installato l'addon.
    :param addon_name: il nome dell'addon, il nome è quello del manifest o ex bl_info"""

    if bpy.app.version < (4, 2, 0):
        return -1

    import addon_utils

    file = None
    for m in addon_utils.modules():
        if m.bl_info['name'] == addon_name:
            file = m.__file__
            break

    # I miei addon sono sempre con l'__init__ nella root, cosi:     ...\\path_to\\my_addon\\__init__.py
    # Io devo trovare il percorso completo fino a path_to da file
    if not file:
        return -1

    addon_path = os.path.dirname(file)
    # Ora che abbiamo tolto il file __init__.py, dobbiamo togliere anche il nome dell'addon
    addon_path = os.path.dirname(addon_path)
    addon_path = os.path.normpath(addon_path)

    repos = bpy.context.preferences.extensions.repos
    import addon_utils
    for idx, repo in enumerate(repos):
        repo_dir = os.path.normpath(repo.directory)
        if repo_dir == addon_path:
            return idx