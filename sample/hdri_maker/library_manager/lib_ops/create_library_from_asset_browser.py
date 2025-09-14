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
import shutil
import threading

import bpy
from bpy.props import StringProperty, EnumProperty
from bpy_types import Operator

from ...exaconv import get_scnprop, k_size_base
from ...exaproduct import Exa
from ...save_tools.save_utility import render_background_preview
from ...utility.json_functions import get_json_data
from ...utility.text_utils import wrap_text
from ...utility.utility import remove_all_bpy_data, redraw_all_areas, retrieve_nodes, render_preset, \
    replace_forbidden_characters


def get_k_size_if_exists_in_name(name):
    """Ottiene la dimensione dell'immagine se è presente nel nome"""
    k_sizes = k_size_base(minimum=1, maximum=24)
    # k_sizes is list of strings like ["1k", "2k", "4k", "8k", "16k", "24k"]

    # Identifichiamo se c'è una dimensione nell'immagine
    for k_size in k_sizes:
        if k_size in name.lower():
            # Assicuriamoci che prima del numero non ci sia una lettera e dopo il k non ci sia una lettera
            idx = name.lower().find(k_size)
            if idx == 0 or not name[idx - 1].isalpha():
                if idx + len(k_size) == len(name) or not name[idx + len(k_size)].isalpha():
                    return k_size

    return None


def get_addon_special_asset_folder(folder_path):
    """Ottiene la cartella che contiene i dati per il browser degli asset dell'addon"""
    folder_name = "_{}_assets_catalog".format(Exa.blender_manifest["name"].lower().replace(" ", "_"))
    folder = os.path.join(folder_path, folder_name)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    return folder


def get_asset_browser_folder(path):
    """Questa funzione determina se il percorso è a una cartella che contiene il file blender_assets.cats.txt"""
    if os.path.isdir(path):
        file = os.path.join(path, "blender_assets.cats.txt")
        if os.path.isfile(file):
            return file


class HDRIMAKER_OT_convert_asset_browser_to_addon_expansion(Operator):
    bl_idname = Exa.ops_name + "convert_asset_browser_to_addon_expansion"
    bl_label = "Convert Asset Browser to Addon Expansion"
    bl_description = "Try to convert the asset browser to addon library expansion"
    bl_options = {'INTERNAL'}

    folder_path: StringProperty(subtype='DIR_PATH')
    override: EnumProperty(default='NO', items=[('NO', "No", "No"), ('YES', "Yes", "Yes")],
                           name="Overwrite existing files")

    _handler = None
    _timer = None

    total_todo = 0
    total_done = 0

    progress_percentage = 0

    search_blend_files = False
    search_blend_files_completed = False
    search_tags_and_make_preview = False
    search_tags_and_make_preview_completed = False

    enum_blend_files = -1

    all_blend_files = {}

    @classmethod
    def progress(cls):
        return cls.progress_percentage

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        text_length = context.region.width * .025

        text = "You are about to proceed with the conversion of the asset browser into an expansion library of {}".format(
            Exa.blender_manifest["name"])
        wrap_text(layout=col, string=text, enum=False, text_length=text_length, center=True)

        col.separator()

        text = "Overwrite existing files?"
        wrap_text(layout=col, string=text, enum=False, text_length=text_length, center=True)

        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(self, "override", text="Overwrite existing files", expand=True)

        col.separator()

        text = "Press OK to proceed or ESC to cancel"
        wrap_text(layout=col, string=text, enum=False, text_length=text_length, center=True)

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            redraw_all_areas()

            cls = self.__class__
            if not cls.search_blend_files and not cls.search_blend_files_completed:
                t = threading.Thread(target=self.search_all_blend_files, args=(context,))
                t.start()
                # self.search_all_blend_files(context)

            if cls.search_blend_files_completed:
                if cls.all_blend_files:
                    self.create_library(context)
                else:
                    self.cancel(context)
                    return {'FINISHED'}

            # if not cls.search_tags_and_make_preview_completed:
            #     self.create_library()

            # if cls.search_blend_files_completed and cls.search_tags_and_make_preview_completed:
            #     self.cancel(context)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        cls = self.__class__
        cls.search_blend_files = False
        cls.search_tags_and_make_preview = False
        cls.search_blend_files_completed = False
        cls.search_tags_and_make_preview_completed = False
        cls.all_blend_files.clear()
        cls.enum_blend_files = -1
        cls.total_todo = 0
        cls.total_done = 0
        scnProp = get_scnprop(context.scene)
        self.folder_path = scnProp.libraries_selector

        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):

        asset_browser_file = get_asset_browser_folder(self.folder_path)
        if not asset_browser_file:
            self.report({'ERROR'}, "The folder does not contain the asset browser file")
            return {'FINISHED'}

        cls = self.__class__
        cls.search_blend_files = False
        cls.search_tags_and_make_preview = False

        cls._handler = self
        self._timer = context.window_manager.event_timer_add(0.2, window=context.window)

        context.window_manager.modal_handler_add(self)

        # Set the render preset
        render_preset(context.scene, samples=8)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        try:
            context.window_manager.event_timer_remove(self._timer)
        except:
            pass
        cls = self.__class__
        cls._handler = None

        redraw_all_areas()
        return {'CANCELLED'}

    def search_all_blend_files(self, context):
        """Carica tutti i file.blend nel progetto corrente, esamina tutti i bpy.data.worlds se sono taggati con asset_data,
        se lo sono li importa uno a uno nel progetto corrente, quindi esamina tutti i tags, e da esso crea un dizionario json
        che sarà il dizionario che serve per creare le categorie della libreria"""

        cls = self.__class__
        cls.search_blend_files = True

        cls.all_blend_files_dict = {}
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if not file.endswith(".blend"):
                    continue

                cls.enum_blend_files += 1
                cls.all_blend_files[cls.enum_blend_files] = {"blender_file": os.path.join(root, file),
                                                             "hdr_files": [],
                                                             "thumbnail": "",
                                                             "is_image": False}

                # Search in the folder for hdr files
                for fn in os.listdir(root):
                    if fn.endswith(".hdr"):
                        cls.all_blend_files[cls.enum_blend_files]["hdr_files"].append(os.path.join(root, fn))
                    if "thumbnail" in fn and fn.endswith((".png", ".jpg", ".webp")):
                        cls.all_blend_files[cls.enum_blend_files]["thumbnail"] = os.path.join(root, fn)

        cls.search_blend_files_completed = True
        cls.search_blend_files = False

    def create_library(self, context):
        cls = self.__class__

        json_file = os.path.join(self.folder_path + "_assets_catalog.json")

        addon_expansion_path = get_addon_special_asset_folder(self.folder_path)

        json_data = get_json_data(json_file, remove_if_invalid=False)
        if not json_data:
            json_data = {}

        # Ora ogni file.blend va caricato ed esaminato.
        # get the first items of the cls.all_blend_files dict:
        info_dict = list(cls.all_blend_files.items())[0][1]

        cls.total_todo = len(cls.all_blend_files)

        blend_file = info_dict["blender_file"]
        hdr_files = info_dict["hdr_files"]
        thumbnail = info_dict["thumbnail"]

        with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
            imported_worlds = [name for name in data_from.worlds]
            data_to.worlds = imported_worlds

        # Esaminiamo ora se il world è taggato con asset_data
        for world in imported_worlds:
            thumbnail_exists = False
            if not world.asset_data:
                continue

            context.scene.world = world
            # Cerchiamo il nodo TEX_ENVIRONMENT se esiste
            all_sub_nodes = retrieve_nodes(world.node_tree)
            tex_environment = [n for n in all_sub_nodes if n.type == "TEX_ENVIRONMENT"]
            is_procedural = False
            if len(tex_environment) == 1:
                # In questo caso molto probabilmente non è un world procedurale, ma un world con un hdr o una immagine di sfondo
                # Quindi teniamo buono il world anche eventualmente se ci sono hdr_files multipli utilizziamo il nodo TEX_ENVIRONMENT
                is_procedural = False
            else:
                is_procedural = True

            for tag in world.asset_data.tags:
                # I tag creano le categorie della libreria, ma in questo caso le categorie possono contenere piu volte lo stesso sfondo
                tag_name = tag.name
                if not tag_name:
                    continue

                tag_name = replace_forbidden_characters(tag_name, replace_with='_')

                # Creiamo la cartella per il tag
                tag_folder = os.path.join(addon_expansion_path, tag_name)

                if not os.path.isdir(tag_folder):
                    os.makedirs(tag_folder)

                material_folder = os.path.join(tag_folder, world.name)
                if not os.path.isdir(material_folder):
                    os.makedirs(material_folder)

                material_data = os.path.join(material_folder, "data")
                if not os.path.isdir(material_data):
                    os.makedirs(material_data)

                previews_folder = os.path.join(material_data, "previews")
                if not os.path.isdir(previews_folder):
                    os.makedirs(previews_folder)

                preview_default = os.path.join(previews_folder, "default")
                if not os.path.isdir(preview_default):
                    os.makedirs(preview_default)

                thumbnail_file = os.path.join(preview_default, world.name + ".webp")
                if thumbnail_exists:
                    # Copiamo il file thumbnail nella cartella previews
                    shutil.copyfile(thumbnail_exists, thumbnail_file)

                else:
                    render_background_preview(bpy.context.scene, thumbnail_file, lens=12, camera_loc=[0, 0, 0],
                                              file_format='WEBP')

                thumbnail_exists = thumbnail_file

                if is_procedural:
                    material_var_folder = os.path.join(material_folder, world.name)
                else:
                    for hdr_file in hdr_files:
                        # Copiamo il file hdr nella cartella data
                        hdr_file_name = os.path.basename(hdr_file)
                        k_size = get_k_size_if_exists_in_name(hdr_file_name)
                        if k_size:
                            folder_name = k_size
                        else:
                            img = bpy.data.images.load(hdr_file)
                            size_x = img.size[0]
                            k_size = size_x / 1024

                        material_var_folder = os.path.join(material_folder, k_size)
                        if not os.path.isdir(material_var_folder):
                            os.makedirs(material_var_folder)

        cls.total_done += 1

        # Remove cls.all_blend_files[0] from the dict:
        first_key = next(iter(cls.all_blend_files))
        cls.all_blend_files.pop(first_key)

        remove_all_bpy_data()

        # scriviamo il json file, all'interno della cartella della libreria
