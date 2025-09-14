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
##

import os

import bpy
import bpy.utils.previews
from bpy.props import EnumProperty

from .categories_enum import get_mats_categories
from .get_library_utils import current_lib, risorse_lib
from .main_pcoll_attributes import get_winman_main_preview
from .textures_pcoll_attributes import pcoll_texture_prev, pcoll_texture_prev_dir, wm_texture_preview, \
    set_winman_texture_preview
from ..exaconv import get_scnprop
from ..utility.dictionaries import complete_format

preview_collections_texture_dict = {}
main_preview_collection = None

def get_pcoll_texture():
    global preview_collections_texture_dict
    return preview_collections_texture_dict

def reload_textures_prev_icons():
    global main_preview_collection
    # Collezione di preview delle texture nell'interfaccia
    pcol = preview_collections_texture_dict.get("images_preview")
    if pcol:
        print("Rimuovo dalla funzione reload_textures_prev_icons")
        bpy.utils.previews.remove(preview_collections_texture_dict["images_preview"])
        preview_collections_texture_dict.pop("images_preview")

    imagecoll = bpy.utils.previews.new()
    setattr(imagecoll, pcoll_texture_prev(), ())
    setattr(imagecoll, pcoll_texture_prev_dir(), '')
    # Questo sostituisce la dichiarazione di attributi, in base al prodotto in uso

    preview_collections_texture_dict["images_preview"] = imagecoll

# ####################################################################################################################
# #################################################################################################################
# #################################        Textures Previews
# ############################################################################################################
# ########################################################################################################

def update_first_texture(self, context):
    if self.up_category in ['Tools']:
        # set_k_size(self,context)
        try:
            self.k_size = 'NONE'
        except:
            pass
    # enum_material_previews(self,context)
    # wima().xpbr_main_prev = enum_material_previews.first[:-4]
    previews = enum_material_textures(self, context)
    if previews:
        set_winman_texture_preview(previews[0][0])
    else:
        print("No previews into enum_material_previews")


def enum_material_textures(self, context):
    """Images Preview Callback For the Texture manager"""
    scnProp = get_scnprop(context.scene)
    mat_folder = scnProp.up_category
    preview_mat_name = get_winman_main_preview()

    enum_items = []
    image_paths = []

    if context is None:
        return enum_items

    """    
    if scnProp.libraries_selector != 'DEFAULT': #16/03/2021 perché andre questo?
        return empty"""

    k_folder = os.path.join(current_lib(), mat_folder, preview_mat_name, scnProp.k_size)

    imagecoll = preview_collections_texture_dict["images_preview"]

    if k_folder == getattr(imagecoll, pcoll_texture_prev_dir()):
        return getattr(imagecoll, pcoll_texture_prev())

    ######################################
    if os.path.isdir(k_folder):
        for fn in os.listdir(k_folder):
            file_path = os.path.join(k_folder, fn)
            if fn.lower().endswith(complete_format()) and not fn.startswith("."):
                image_paths.append((file_path, fn))

    if not image_paths:
        empty_image_path = os.path.join(risorse_lib(), "empty_showreel", "Empty....jpg")
        image_paths.append((empty_image_path, "Empty....jpg"))

    for i, (filepath, name) in enumerate(image_paths):

        if filepath in imagecoll:
            enum_items.append((filepath, name, "", imagecoll[filepath].icon_id, i))
        else:
            thumb = imagecoll.load(filepath, filepath, 'IMAGE', force_reload=True)
            enum_items.append((filepath, name, "", thumb.icon_id, i))

    setattr(imagecoll, pcoll_texture_prev(), enum_items)
    setattr(imagecoll, pcoll_texture_prev_dir(), k_folder)

    enum_material_textures.indice = [path for (path, i) in image_paths]

    return getattr(imagecoll, pcoll_texture_prev())


# ###############################################################################
# #######################################################################
# ###############################################################

def cat(self, context):
    mats_categories = get_mats_categories()
    # indice categorie
    scn = context.scene
    scnProp = get_scnprop(scn)
    current = scnProp.up_category

    for i in mats_categories["index"]:
        if current == i:
            cat.get = mats_categories["index"].index(i)


def update_texture_preview(self, context):
    scn = context.scene
    scnProp = get_scnprop(scn)
    """
    for main_preview_collection in preview_collections_texture_dict.values():
        bpy.utils.previews.remove(preview_collections_texture_dict)"""
    reload_textures_prev_icons()

    if scnProp.libraries_selector == 'DEFAULT':
        scnProp.libraries_selector = 'USER'


def register_texture_collections():
    # TODO: controllare che funzioni senza l'update set_k_size
    reload_textures_prev_icons()
    from bpy.types import WindowManager
    # For the materials previews:
    setattr(WindowManager,
            wm_texture_preview(),
            EnumProperty(items=enum_material_textures, description="Select by click"))
    # TODO: Controllare che l'update non serva piu realmente:
    # , update=set_k_size))


def unregister_texture_collections():
    from bpy.types import WindowManager

    winman = getattr(WindowManager, wm_texture_preview())
    try:
        del winman
    except:
        pass

    for prv in preview_collections_texture_dict.values():
        print("Rimuovo dalla funzione unregister_texture_collections")
        bpy.utils.previews.remove(prv)
    preview_collections_texture_dict.clear()
