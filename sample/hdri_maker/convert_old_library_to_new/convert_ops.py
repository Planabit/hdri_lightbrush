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
from bpy.props import StringProperty
from bpy.types import Operator

from ..exaconv import get_scnprop
from ..exaproduct import Exa
from ..utility.json_functions import get_json_data
from ..utility.text_utils import draw_info, wrap_text
from ..utility.utility import wima, get_addon_preferences, get_k_size_from_fn, \
    get_filename_from_path, get_walk_files, redraw_all_areas, copy_file, human_time_seconds, get_addon_dir


class HDRIMAKERT_OT_ConvertOldLibrary(Operator):
    """Convert Old Library to the new library"""

    bl_idname = Exa.ops_name + "convertoldlibrary"
    bl_label = "Convert Old Library"
    bl_options = {'INTERNAL', 'UNDO'}

    _timer = None
    _handler = None

    options: StringProperty(default="")

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'DEFAULT':
            desc = "Convert Default Library to new library"
        elif properties.options == 'USER':
            desc = "Convert User Library to new library"

        return desc

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        box = col.box()
        col_box = box.column(align=True)
        # Translate text into English:
        text = "This operation, if you agree, will convert your old {} library to the new one. This is necessary to make the old libraries work " \
               "with the new version of the addon. This process can take a long time, it depends on the amount of files " \
               "Alternatively, you can download the new libraries from the site where you purchased the addon. If you are not sure, do nothing and decide whether to keep " \
               "the old library or download the new one.".format(self.options.upper())

        wrap_text(layout=col_box, string=text, enum=False, text_length=(context.region.width / 20),
                  center=True)

        col.separator()
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="Press Ok to start the conversion, or Esc to abort")
        col.separator()

    def invoke(self, context, event):
        scn = context.scene

        scnProp = get_scnprop(scn)

        if self.options == 'DEFAULT' and not os.path.isdir(scnProp.convert_to_new_default_lib_path):
            text = "Please choose a valid DESTINATION path for the default library conversion"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        elif self.options == 'USER' and not os.path.isdir(scnProp.convert_to_new_user_lib_path):
            text = "Please choose a valid DESTINATION path for the user library conversion"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        return wima().invoke_props_dialog(self, width=550)

    def modal(self, context, event):
        if event.type == 'TIMER':
            redraw_all_areas()
            thread = next((th for th in ConvertLibraryUtils.threads), None)
            if not HDRIMAKERT_OT_ConvertOldLibrary._handler:
                self.cancel(context)
                return {'FINISHED'}

            elif ConvertLibraryUtils.finished:
                preferences = get_addon_preferences()
                scnProp = get_scnprop(context.scene)
                # In this case the thread has finished, so we need to link the new path to the new library:
                if self.options == 'DEFAULT':
                    preferences.addon_default_library = ConvertLibraryUtils.destination_root
                    scnProp.convert_to_new_default_lib_path = ""

                elif self.options == 'USER':
                    preferences.addon_user_library = ConvertLibraryUtils.destination_root
                    scnProp.convert_to_new_user_lib_path = ""

                self.cancel(context)
                return {'FINISHED'}

            elif not thread:
                self.cancel(context)
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        cls = self.__class__
        cls._handler = None
        redraw_all_areas()
        try:
            # Chiamando l'operatore da invoke, se l'utente preme ESC finirà qui, quindi non esistendo un handler assegnato
            # darà errore
            wima().event_timer_remove(self._timer)
        except:
            pass

        print("HDRIMAKERT_OT_ConvertOldLibrary Process Ending")

    def execute(self, context):
        scn= context.scene
        scnProp = get_scnprop(scn)

        ConvertLibraryUtils.finished = False

        addon_prefs = get_addon_preferences()

        if self.options == 'DEFAULT':

            default_lib_path = bpy.path.abspath(addon_prefs.addon_default_library)
            if not os.path.isdir(default_lib_path):
                draw_info(
                    "Please check the paths of the libraries in addon preferences It appears not to be linked correctly",
                    "Info", 'INFO')
                self.cancel(context)
                return {'CANCELLED'}

            addon_resource_path = os.path.join(get_addon_dir(), "addon_resources")

            CLU = ConvertLibraryUtils(scnProp, default_lib_path=default_lib_path, addon_resource_path=addon_resource_path)
            thread = threading.Thread(target=CLU.convert_default_library_to_new)

        elif self.options == 'USER':
            user_lib_path = bpy.path.abspath(addon_prefs.addon_user_library)
            if not os.path.isdir(user_lib_path):
                draw_info(
                    "Please check the paths of the libraries in addon preferences It appears not to be linked correctly",
                    "Info", 'INFO')
                self.cancel(context)
                return {'CANCELLED'}

            CLU = ConvertLibraryUtils(scnProp, user_lib_path=user_lib_path)
            thread = threading.Thread(target=CLU.convert_user_lib)
        else:
            return {'FINISHED'}

        cls = self.__class__
        cls._handler = self

        CLU.threads.clear()
        CLU.threads.append(thread)
        thread.name = "ConvertLibraryUtils"
        thread.stop = False
        thread.start()

        self._timer = wima().event_timer_add(0.05, window=context.window)
        wima().modal_handler_add(self)

        return {'RUNNING_MODAL'}


class ConvertLibraryUtils:
    total_files = 0
    files_copied = 0
    finished = False

    error_msg = None
    threads = []
    finish = False
    cancelled = False
    destination_root = ""

    def __init__(self, scnProp, default_lib_path=None, user_lib_path=None, addon_resource_path = None):
        self.default_lib_path = default_lib_path
        self.user_lib_path = user_lib_path
        self.scnProp = scnProp
        self.addon_resource_path = addon_resource_path
        cls = self.__class__
        cls.destination_root = ""

    def convert_default_library_to_new(self):

        from pathlib import Path
        import time

        time_start = time.time()
        cls = self.__class__
        cls.destination_root = os.path.join(self.scnProp.convert_to_new_default_lib_path, 'HDRI_MAKER_DEFAULT_LIB')
        # ------------------------------------------------------------------------------------------------------------------
        # 0) Create the library root folder
        if not os.path.isdir(cls.destination_root):
            os.mkdir(cls.destination_root)

        old_preview_paths = os.path.join(self.default_lib_path, 'preview_hdri')

        hdr_files = get_walk_files(path=self.default_lib_path, get_by_extensions=[".hdr", ".exr"])


        ConvertLibraryUtils.total_files = len(hdr_files)
        ConvertLibraryUtils.files_copied = 0

        category_paths = []
        for fn in os.listdir(old_preview_paths):
            path = os.path.join(old_preview_paths, fn)
            if os.path.isdir(path):
                category_paths.append(path)

        # Bisogna ottenere il registro json dei volumi exapack online inerente ai volumi default_library
        # Questo perchè se l'utente decide di convertire la libreria, sarebbe cosa buona, comparare i file una volta
        # ricombinati nella nuova libreria, con quelli online, in maniera da ricreare il registro json dei volumi
        # altrimenti l'utente dovrà scaricare tutto nuovamente. ma io voglio evitare, visto che l'utente dovrebbe già
        # avere tutto in locale, quindi non dovrebbe essere un problema, ma comunque è da fare.
        # --------------------------------------------------------------------------------------------------------------
        hdr_filename_list = [v['filename'] for k, v in hdr_files.items()]
        volumes_path = os.path.join(self.addon_resource_path, "conversion_utility", "volumes")
        for fn in os.listdir(volumes_path):
            if not fn.endswith(".json"):
                continue

            json_file = os.path.join(volumes_path, fn)
            json_data = get_json_data(json_file)
            files_dict = json_data['files_dict']
            volume_files = []
            match_files = []
            for idx, value in files_dict.items():
                file_name = value['file_name']
                # Append filename if ends with .hdr, .png
                if file_name.endswith(".hdr") or file_name.endswith(".exr"):
                    volume_files.append(file_name)
                    if file_name in hdr_filename_list:
                        match_files.append(file_name)

            # Se il 90% dei file del volume_files sono presenti in match_files, allora si può procedere

            if len(match_files) / len(volume_files) >= 0.9:
                data_lib_folder = os.path.join(cls.destination_root, "._data")
                if not os.path.isdir(data_lib_folder):
                    os.mkdir(data_lib_folder)
                v_installed_folder = os.path.join(data_lib_folder, "._volumes_installed")
                if not os.path.isdir(v_installed_folder):
                    os.mkdir(v_installed_folder)
                # Copy the json file into the volumes_installed folder
                json_file = os.path.join(volumes_path, fn)
                to_path = os.path.join(v_installed_folder, fn)
                shutil.copy(json_file, to_path)

        # --------------------------------------------------------------------------------------------------------------
        # In questa dir ci sono i file tags.json e mat_info.json
        fake_structure = os.path.join(self.addon_resource_path, "conversion_utility", "HDRI_MAKER_DEFAULT_LIB")

        material_dict = {}
        for path in category_paths:
            for preview_file_name in os.listdir(path):
                k_list = material_dict[preview_file_name] = []

                cat_folder_name = get_filename_from_path(path)

                preview_file_name_path = os.path.join(path, preview_file_name)
                if preview_file_name.startswith("."):
                    continue
                if not os.path.isfile(preview_file_name_path):
                    continue

                new_path_category = os.path.join(cls.destination_root, cat_folder_name)
                # ------------------------------------------------------------------------------------------------------
                # 1) Creo cartella Categoria
                if not os.path.isdir(new_path_category):
                    os.mkdir(new_path_category)

                # ------------------------------------------------------------------------------------------------------
                # 2) Creo cartella del materiale
                filename_title = preview_file_name.replace(".png", "").replace("_", " ").title()

                mat_folder_path = os.path.join(new_path_category, filename_title)
                if not os.path.isdir(mat_folder_path):
                    os.mkdir(mat_folder_path)

                # ------------------------------------------------------------------------------------------------------
                # 3) Creo data folder
                data_folder = os.path.join(mat_folder_path, 'data')
                if not os.path.isdir(data_folder):
                    os.mkdir(data_folder)

                # Cerco di copiare i file tags.json e mat_info.json dalla cartella fake_structure:
                # Il percorso è lo stesso tranne per il root della cartella
                fake_data = os.path.join(fake_structure, cat_folder_name, filename_title, 'data')
                for fn in os.listdir(fake_data):
                    if fn.endswith(".json"):
                        json_file = os.path.join(fake_data, fn)
                        to_path = os.path.join(data_folder, fn)
                        shutil.copy(json_file, to_path)


                # ------------------------------------------------------------------------------------------------------
                # 4) Creo preview folder
                preview_folder = os.path.join(data_folder, 'previews')
                if not os.path.isdir(preview_folder):
                    os.mkdir(preview_folder)

                # ------------------------------------------------------------------------------------------------------
                # 5) Create the default folder
                default_preview_folder = os.path.join(preview_folder, 'default')
                if not os.path.isdir(default_preview_folder):
                    os.mkdir(default_preview_folder)

                # ------------------------------------------------------------------------------------------------------
                # 6) Copy and remove from source the preview image:
                source = os.path.join(path, preview_file_name)
                destination = os.path.join(default_preview_folder, preview_file_name)
                copy_file(source, destination)

                # ------------------------------------------------------------------------------------------------------
                # 7) Ottengo i file per dimensione, e creo le corrispettive cartelle
                dict_to_pop = []
                for key, value in hdr_files.items():
                    if not HDRIMAKERT_OT_ConvertOldLibrary._handler:
                        ConvertLibraryUtils.finished = True
                        return

                    fn = value['filename']
                    filepath = value['fullpath']

                    k_size_str = get_k_size_from_fn(fn)

                    if not [ext for ext in [".hdr", ".ext"] if fn.endswith(ext)]:
                        continue

                    clean_fn = Path(fn.replace(k_size_str, "").replace("_", " ")).stem.strip()
                    clean_filename_title = filename_title.replace("_", " ").strip()

                    if clean_fn.lower() != clean_filename_title.lower():
                        continue

                    if k_size_str.lower() in ["01k", "02k", "04k", "08k"]:
                        k_size_str = k_size_str.replace("0", "")

                    k_list.append(fn)

                    # ------------------------------------------------------------------------------------------
                    # 8) Creo la corrispettiva k size folder:
                    k_folder_destination = os.path.join(mat_folder_path, k_size_str)
                    if not os.path.isdir(k_folder_destination):
                        os.mkdir(k_folder_destination)

                    # --------------------------------------------------------------------------------------------------
                    # 9) Copio il file nella cartella k size
                    destination = os.path.join(k_folder_destination, fn)

                    # --------------------------------------------------------------------------------------------------
                    # 10) Questo per non copiare i file già copiati nel caso di interruzioni bug Se il file è di diverse
                    # dimensioni, probabilmente destination è danneggiato, e va riscritto.
                    size_source = os.path.getsize(filepath)
                    size_destination = None
                    if os.path.exists(destination):
                        size_destination = os.path.getsize(destination)

                    if size_source != size_destination:
                        copy_file(filepath, destination)

                    # Qui elimino i file già copiati dal dizionario, cosi da diminuire il tempo di ricerca
                    # all'interno di esso
                    dict_to_pop.append(key)
                    ConvertLibraryUtils.files_copied += 1

                for index_to_pop in dict_to_pop:
                    hdr_files.pop(index_to_pop)
                print("# ---")
                try:
                    print("File Copied: ", get_filename_from_path(source))
                except:
                    pass
                print("Time: ", human_time_seconds(time.time() - time_start))

        errors = {}
        for mat, hdris in material_dict.items():
            if len(hdris) != 5:
                errors[mat] = hdris


        # Create the ._data folder and json file with the data:
        from ..library_manager.get_library_utils import make_library_info
        make_library_info(cls.destination_root, 'DEFAULT')

        from ..library_manager.tools import create_json_material_library_register
        _data_folder = os.path.join(cls.destination_root, '._data')
        if not os.path.isdir(_data_folder):
            os.mkdir(_data_folder)
        create_json_material_library_register(cls.destination_root, _data_folder)

        ConvertLibraryUtils.finished = True

        return cls.destination_root

    def convert_user_lib(self):
        cls = self.__class__
        cls.destination_root = os.path.join(self.scnProp.convert_to_new_user_lib_path, 'HDRI_MAKER_USER_LIB')
        # 0) Create the library root folder
        if not os.path.isdir(cls.destination_root):
            os.mkdir(cls.destination_root)

        previews_files = [fn for root, dirs, files in os.walk(self.user_lib_path) for fn in files if
                          fn.endswith(".png")]
        ConvertLibraryUtils.total_files = len(previews_files)
        ConvertLibraryUtils.files_copied = 0

        # We need to store the files into a json file (installed_file_register.json)
        for category in os.listdir(self.user_lib_path):
            category_path = os.path.join(self.user_lib_path, category)

            full_files = [os.path.join(category_path, fn) for fn in os.listdir(category_path) if
                          os.path.isfile(os.path.join(category_path, fn))]

            preview_files = [path for path in full_files if path.endswith(".png")]
            blend_files = [path for path in full_files if path.endswith(".blend")]

            for preview in preview_files:

                preview_fn = get_filename_from_path(preview)
                for blend_filepath in blend_files:
                    blend_fn = get_filename_from_path(blend_filepath)

                    clean_preview_fn = os.path.splitext(preview_fn)[0]
                    clean_blend_fn = os.path.splitext(blend_fn)[0]

                    if clean_blend_fn == clean_preview_fn:

                        # Crea cartella della categoria
                        category_folder = os.path.join(cls.destination_root, category)
                        if not os.path.isdir(category_folder):
                            os.mkdir(category_folder)

                        # Crea cartella del materiale
                        material_folder = os.path.join(category_folder, clean_preview_fn)
                        if not os.path.isdir(material_folder):
                            os.mkdir(material_folder)

                        # crea cartella data nella cartella materiale
                        data_folder = os.path.join(material_folder, "data")
                        if not os.path.isdir(data_folder):
                            os.mkdir(data_folder)

                        preview_folder = os.path.join(data_folder, "previews")
                        if not os.path.isdir(preview_folder):
                            os.mkdir(preview_folder)

                        default_folder = os.path.join(preview_folder, "default")
                        if not os.path.isdir(default_folder):
                            os.mkdir(default_folder)

                        # ----------------------------------------------------------------------------------------------
                        # Copia del file Preview
                        preview_destination = os.path.join(default_folder, preview_fn)
                        size_source = os.path.getsize(preview)
                        size_destination = None
                        if os.path.exists(preview_destination):
                            size_destination = os.path.getsize(preview_destination)

                        if size_source != size_destination:
                            copy_file(preview, preview_destination)

                        # ----------------------------------------------------------------------------------------------

                        # Crea cartella contenente il file .blend nella cartella materiale
                        file_folder = os.path.join(material_folder, clean_blend_fn)
                        if not os.path.isdir(file_folder):
                            os.mkdir(file_folder)

                        # ----------------------------------------------------------------------------------------------
                        # Copia del file Blend
                        blend_destination = os.path.join(file_folder, blend_fn)
                        size_source = os.path.getsize(blend_filepath)
                        size_destination = None
                        if os.path.exists(blend_destination):
                            size_destination = os.path.getsize(blend_destination)

                        # Copy only if the file is not already copied, check with size
                        if size_source != size_destination:
                            copy_file(blend_filepath, blend_destination)

                        # ----------------------------------------------------------------------------------------------

                ConvertLibraryUtils.files_copied += 1

        # At the end of the process, we need to create a json file into ._data folder, and write into it the
        # {
        # 	"library_version": Exa.library_version,
        # 	"library_product": "HDRI_MAKER",
        # 	"library_type": "DEFAULT"/"USER",
        # }
        # This is needed to identify the library as a valid one, and to be able to update it in the future.
        from ..library_manager.get_library_utils import make_library_info
        make_library_info(cls.destination_root, library_type='USER', library_name='USER')

        from ..library_manager.tools import create_json_material_library_register
        _data_folder = os.path.join(cls.destination_root, "._data")
        if not os.path.isdir(_data_folder):
            os.mkdir(_data_folder)
        create_json_material_library_register(cls.destination_root, _data_folder)

        ConvertLibraryUtils.finished = True
