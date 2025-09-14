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
from bpy.props import EnumProperty

from .main_pcoll_attributes import pcoll_main_prev, pcoll_main_prev_dir, wm_main_preview, get_winman_main_preview, \
    set_winman_main_preview
from .update_enum_items import preserve_enum_items
from ..exaconv import get_scnprop
from ..library_manager.categories_enum import get_mats_categories
from ..library_manager.get_library_utils import current_lib, risorse_lib
from ..library_manager.tag_filter import tag_search_active, find_tags
from ..utility.utility import get_splitted_path

preview_collections_main_dict = {}
main_preview_collection = None

def get_preview_collections_main_dict():
    global preview_collections_main_dict
    return preview_collections_main_dict


def reload_main_previews_collection():
    global preview_collections_main_dict
    global main_preview_collection
    # Collezione di preview dei materiali nell'interfaccia
    pcol = preview_collections_main_dict.get("library_icons_preview")
    if pcol:
        try:
            print("rimuovo dalla funzione main_preview_collection")
            bpy.utils.previews.remove(main_preview_collection)
        except:
            pass
        # bpy.utils.previews.remove(preview_collections_main_dict["library_icons_preview"])
        preview_collections_main_dict.pop("library_icons_preview")

    main_preview_collection = bpy.utils.previews.new()
    setattr(main_preview_collection, pcoll_main_prev(), ())
    setattr(main_preview_collection, pcoll_main_prev_dir(), '')
    # Questo sostituisce la dichiarazione di attributi, in base al prodotto in uso

    preview_collections_main_dict["library_icons_preview"] = main_preview_collection


def update_tag_search(self, context):
    global preview_collections_main_dict
    mats_categories = get_mats_categories()
    scn = context.scene
    scnProp = get_scnprop(scn)
    current_cat = scnProp.up_category

    current_mat = get_winman_main_preview()

    scnProp.up_category = mats_categories['categories'][0][0]

    mats_categories['library'] = ""  # Questo fa si che venga di nuovo compilata la lista categorie
    setattr(preview_collections_main_dict["library_icons_preview"], pcoll_main_prev_dir(), "")
    enum_material_previews(self, context)

    if current_cat in [c[0] for c in mats_categories['categories']]:
        scnProp.up_category = current_cat
    else:
        if len(mats_categories['categories']) > 1:
            scnProp.up_category = mats_categories['categories'][1][0]
        else:
            scnProp.up_category = mats_categories['categories'][0][0]

    try:
        set_winman_main_preview(current_mat)
    except:
        pass


def enum_material_previews(self, context):
    """Material Preview Callback for material preview"""
    global preview_collections_main_dict

    enum_items = []

    if context is None:
        return enum_items

    scnProp = get_scnprop(context.scene)
    mats_categories = get_mats_categories()

    # if scnProp.libraries_selector == 'DEFAULT':
    category = os.path.join(current_lib(), scnProp.up_category)
    if scnProp.up_category == 'Tools' and scnProp.up_category == mats_categories["categories"][0][0]:
        category = os.path.join(risorse_lib(), scnProp.up_category)

    # else:
    # if scnProp.up_category != 'Empty Collection...':
    #    category = os.path.join(cartella_user,scnProp.up_category)
    if scnProp.up_category == 'Empty Collection...':
        category = os.path.join(risorse_lib(), 'empty_showreel')

    main_preview_collection = preview_collections_main_dict["library_icons_preview"]

    if category == getattr(main_preview_collection, pcoll_main_prev_dir()):
        return getattr(main_preview_collection, pcoll_main_prev())

    image_paths = []
    if category and os.path.exists(category):
        formato = (".png", ".jpg", ".webp")
        for fn in os.listdir(category):
            file_path = os.path.join(category, fn)

            if tag_search_active(scnProp):
                tags_path = os.path.join(file_path, "data", "tags.json")
                if not find_tags(tags_path, scnProp.tag_search, scnProp.tag_exclusion):
                    continue

            if fn.lower().endswith(formato) and not fn.startswith("."):
                image_paths.append((file_path, fn))

            # Qua cerca se i previews sono del nuovo tipo nella cartella previews
            previews_path = os.path.join(category, fn, "data", "previews", "default")

            if os.path.isdir(previews_path):
                for prev in os.listdir(previews_path):
                    if prev.lower().endswith(formato) and not prev.startswith("."):
                        prevpath = os.path.join(previews_path, prev)
                        image_paths.append((prevpath, prev))
                        # Per ora, cerchiamo solo una immagine
                        break

        if not image_paths:
            empty_image_path = os.path.join(risorse_lib(), "empty_showreel", "Empty....jpg")
            image_paths.append((empty_image_path, "Empty....jpg"))

        for idx, (filepath, name) in enumerate(image_paths):

            if name not in ["Empty....jpg"]:
                name = get_splitted_path(filepath)[-5]
            else:
                name = name.replace(".png", "").replace(".jpg", "").replace(".webp", "")

            # name = name.replace(".png", "").replace(".jpg", "").replace(".jpeg", "").replace("_", " ").title()
            if filepath in main_preview_collection:
                # Questo era per il nome del file preview ma si è deciso di scegliere il nome della cartella in quanto si può dare qualsiasi nome al preview
                enum_items.append((name, name, "", main_preview_collection[filepath].icon_id, idx))
            else:
                thumb = main_preview_collection.load(filepath, filepath, 'IMAGE', force_reload=True)
                enum_items.append((name, name, "", thumb.icon_id, idx))


    setattr(main_preview_collection, pcoll_main_prev(), enum_items)
    setattr(main_preview_collection, pcoll_main_prev_dir(), category)

    if enum_items:
        preview_collections_main_dict['indice'] = [i for (path, i) in image_paths]

    return getattr(main_preview_collection, pcoll_main_prev())


def update_first_icon(self, context):
    previews = enum_material_previews(self, context)
    if previews:
        set_winman_main_preview(previews[0][0])
    else:
        print("No previews into enum_material_previews")

    if self.up_category in ['Tools']:
        # set_k_size(self,context)
        try:
            self.k_size = 'NONE'
        except:
            pass
    # enum_material_previews(self,context)
    # wima().xpbr_main_prev = enum_material_previews.first[:-4]


def register_main_previews_collection():
    from bpy.types import WindowManager
    reload_main_previews_collection()
    # For the textures previews:
    setattr(WindowManager,
            wm_main_preview(),
            EnumProperty(items=enum_material_previews, description="Select by click", update=preserve_enum_items))


def unregister_main_previews_collection():
    global preview_collections_main_dict
    for prv in preview_collections_main_dict.values():
        try:
            print("rimuovo le preview dalla funzione unregister_main_previews_collection:")
            bpy.utils.previews.remove(prv)
        except:
            pass
    preview_collections_main_dict.clear()

    from bpy.types import WindowManager
    winman = getattr(WindowManager, wm_main_preview())
    try:
        del winman
    except:
        pass
