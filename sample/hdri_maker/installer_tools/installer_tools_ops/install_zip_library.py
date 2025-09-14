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
import json
import os
import time
import zipfile
import threading
import ntpath

import bpy
from bpy.props import StringProperty, EnumProperty, CollectionProperty, IntProperty
from bpy.types import Operator, PropertyGroup
from bpy_extras.io_utils import ImportHelper

from ..check_tools import get_volume_filepath_by_name, get_all_libraries_paths
from ...exaproduct import Exa
from ...utility.text_utils import draw_info
from ...utility.utility import is_good_zip_file, redraw_all_areas, wima, is_inside_path, \
    get_addon_dir, human_time_seconds, get_addon_preferences, is_from_same_drive




class HDRIMAKER_OT_ChooseExaPacks(Operator, ImportHelper):
    """Choose the exapacks to install"""
    bl_idname = Exa.ops_name + "choose_exapacks"
    bl_label = "Choose ExaPacks"
    bl_options = {'INTERNAL'}

    idx: IntProperty(default=0, options={'HIDDEN'})
    options: EnumProperty(items=(('OPEN_BROWSER', "Open Browser", ""), ('REMOVE', "Remove", "")),
                          default='OPEN_BROWSER',
                          options={'HIDDEN'})

    filter_glob: StringProperty(default="*.exapack", options={'HIDDEN'})
    files: CollectionProperty(type=PropertyGroup)
    directory: StringProperty(subtype='DIR_PATH', options={'HIDDEN'})

    def invoke(self, context, event):

        if self.options == 'OPEN_BROWSER':
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            return self.execute(context)

    def execute(self, context):
        libraries_paths = get_all_libraries_paths()

        from ...installer_tools.check_tools import get_volume_info_from_exapack
        if self.options == 'OPEN_BROWSER':
            # This operator add the exapacks to the list, but it doesn't install them
            # To install, call the operator HDRIMAKER_OT_install_exapacks

            if not [file for file in self.files[:] if file.name.endswith('.exapack')]:
                text = "No ExaPack(s) selected"
                draw_info(text, "Info", 'INFO')
                self.report({'INFO'}, text)
                return {'CANCELLED'}

            preferences = get_addon_preferences()
            preferences.exapacks_install.clear()
            for idx, file in enumerate(self.files):
                item = preferences.exapacks_install.add()
                item.idx = idx
                item.filepath = os.path.join(self.directory, file.name)
                # Open zip and get the json file inside
                zip_file = os.path.join(self.directory, file.name)
                if not is_good_zip_file(zip_file):
                    item.is_good_zip = False
                    item.name = file.name
                    item.volume_name = file.name
                    continue

                json_data = get_volume_info_from_exapack(zip_file)
                if not json_data:
                    item.is_good_zip = False
                    item.name = file.name
                    item.volume_name = file.name

                elif json_data.get("product") == Exa.product:
                    item.is_good_zip = True
                    item.name = file.name
                    item.product = json_data.get("product")
                    volume_name = json_data.get('volume_name')
                    if volume_name:
                        item.volume_name = volume_name
                    item.files_dict = json_data.get('files_dict')
                else:
                    # In this case may be a wrong exapack for example from extreme pbr exapack
                    item.name = file.name
                    item.is_wrong_product = True
                    item.product = json_data.get("product")

        if self.options == 'REMOVE':
            preferences = get_addon_preferences()
            preferences.exapacks_install.remove(self.idx)

        return {'FINISHED'}


def get_or_create_expansion(exapack):
    """This function create the expansion folder (Installed) or return the existing one"""
    from ...library_manager.tools import get_library_info

    lib_paths = get_all_libraries_paths()
    expansion_paths = lib_paths.get('EXPANSION')


    rvi = read_volume_info(exapack)
    json_data = rvi.get('json_data')

    if not json_data:
        return

    library_name = json_data.get('library_name')

    if not library_name:
        return

    library_type = json_data.get('library_type')

    if library_type == 'default_library':
        return

    for filepath in expansion_paths:

        json_data = get_library_info(filepath)
        if not json_data:
            continue

        if json_data.get('library_name') == library_name:
            return filepath

    # Se siamo arrivati qui vuol dire che non esiste ancora un expansion con questo nome
    # Quindi lo creiamo e restituiamo il path

    preferences = get_addon_preferences()
    addon_default_library = preferences.addon_default_library
    # Tentiamo di creare una cartella vicino alla libreria di default
    if not os.path.isdir(addon_default_library):
        return

    # Get the parent folder
    parent_folder = os.path.dirname(addon_default_library)
    new_expansion_path = os.path.join(parent_folder, library_name)
    if os.path.isdir(new_expansion_path):
        # Controlliamo se la cartella contiene ._data/library_info.json
        json_data = get_library_info(new_expansion_path)
        if json_data.get('library_name') == library_name:
            # Qui potrebbe essere il caso che la cartella dell'espansione esiste, ma non esiste la preferences.expansion_filepaths, perchè magari l'utente l'ha cancellata dalla lista
            # Delle librerie espansioni
            if not [item.path for item in preferences.expansion_filepaths if item.path == new_expansion_path]:
                item = preferences.expansion_filepaths.add()
                item.name = library_name
                item.path = new_expansion_path
                item.display = True
            return new_expansion_path

        else:
            # Creiamo una nuova cartella poichè questa è a rischio di essere una libreria, aggiungiamo un numero incrementale tipo "expansion_001" e così via
            # al nome della cartella
            for i in range(1, 100):
                new_expansion_path = os.path.join(parent_folder, f"{library_name}_{i:03d}")
                if not os.path.isdir(new_expansion_path):
                    os.mkdir(new_expansion_path)
                    break
    else:
        try:
            os.mkdir(new_expansion_path)
        except:
            print("Unable to create new expansion folder {}".format(new_expansion_path))
            return


    item = preferences.expansion_filepaths.add()
    item.name = library_name
    item.path = new_expansion_path
    item.display = True

    # Create the ._data/library_info.json file
    from ...library_manager.get_library_utils import make_library_info
    make_library_info(new_expansion_path, "expansion_library", library_name=library_name)

    # Save preferences
    bpy.ops.wm.save_userpref()


    return new_expansion_path


class HDRIMAKER_OT_install_exapacks(Operator):

    bl_idname = Exa.ops_name + "install_exapacks"
    bl_label = "Install Exapack library"
    bl_options = {'INTERNAL'}

    # filter_glob: StringProperty(options={'HIDDEN'}, default='*.exapack')
    # filepath: StringProperty(options={'HIDDEN'}, subtype='DIR_PATH')
    # directory: StringProperty(options={'HIDDEN'}, subtype='DIR_PATH')

    _handler = None
    _timer = None

    @classmethod
    def description(cls, context, properties):
        desc = "Choose the path where are contained the .exapack library files"
        return desc

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    # def invoke(self, context, event):
    #     context.window_manager.fileselect_add(self)
    #     return {'RUNNING_MODAL'}

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

        # Try to reload the Library Preview:
        try:
            from ...library_manager.main_pcoll import reload_main_previews_collection
            reload_main_previews_collection()
        except:
            pass


        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        refresh_interface()

        print("HDRIMAKER_OT_install_exapacks Process Ending")


    def execute(self, context):

        from ...utility.utility import get_addon_preferences
        from ...utility.text_utils import draw_info
        from ...convert_old_library_to_new.convert_functions import is_old_default_library
        from ...convert_old_library_to_new.convert_functions import is_old_user_lib
        from ...convert_old_library_to_new.convert_functions import is_new_library
        from ...exaconv import get_scnprop

        # In questo caso si tenta di sovrascrivere la libreria di default nella libreria già esistente
        addon_prefs = get_addon_preferences()
        scnProp = get_scnprop(context.scene)

        # Ci sono varie casistiche in con cui l'utente potrebbe interagire:

        # 1) L'utente non ha inserito un percorso valido, o l'addon non ha i permessi per accedere al percorso:
        if not os.path.isdir(addon_prefs.addon_default_library):
            text = "The path {} is not valid".format(addon_prefs.addon_default_library)
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        # 2) L'utente ha scelto il percorso delle librerie precedenti alla version 3.0 e non le ha convertite,
        # e sta procedendo all'installazione dei file .exapack
        # - Solution: Ignorare la cartella di destinazione, e creare la nuova libreria nella stessa directory dove si trova
        # - la cartella della vecchia libreria:
        # Quindi controllare se è una vecchia libreria:
        if is_old_default_library(addon_prefs.addon_default_library):
            # Se è una vecchia libreria, allora la nuova libreria va creata nella stessa directory dove si trova la vecchia
            destination_path = os.path.join(os.path.dirname(addon_prefs.addon_default_library),
                                            "HDRI_MAKER_DEFAULT_LIB")
            if not os.path.exists(destination_path):
                os.mkdir(destination_path)
            # Cambiare il percorso dell'utente al nuovo destination_path
            addon_prefs.addon_default_library = destination_path

        # 3) Controllare che il percorso inserito non sia quello nella cartella degli addon di Blender:
        if is_inside_path(addon_prefs.addon_default_library, get_addon_dir()):
            text = "Please do not use the path of the addon directory, is not a good idea, choose another path and try again"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        # 4) Controllare che il percorso inserito non sia quello della cartella user library:
        if is_old_user_lib(addon_prefs.addon_default_library) or is_new_library(addon_prefs.addon_default_library,
                                                                                get_library_type='USER'):
            # In questo caso l'utente ha inserito il percorso default alla user library, quindi non è possibile installare
            text = "The path chosen ( {} )for the Default Library is the same of the User Library, please choose another path".format(
                addon_prefs.addon_default_library)
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        #
        # The user in the case of the first installation inserts a path that does not contain "HDRI_MAKER_DEFAULT_LIB" and therefore it is not a library
        # so you have to create the folder "HDRI_MAKER_DEFAULT_LIB" and insert the path of this folder in the variable addon_default_library
        if not "HDRI_MAKER_DEFAULT_LIB" in addon_prefs.addon_default_library:
            # Ottenere il percorso completo con la cartella "HDRI_MAKER_DEFAULT_LIB", se la cartella non esiste, crearla
            destination_path = os.path.join(addon_prefs.addon_default_library, "HDRI_MAKER_DEFAULT_LIB")
            if not os.path.exists(destination_path):
                os.mkdir(destination_path)
                addon_prefs.addon_default_library = destination_path
            else:
                # Se esiste è perchè l'utente ha già installato "HDRI_MAKER_DEFAULT_LIB" in precedenza, ma non ha inserito il percorso corretto:
                addon_prefs.addon_default_library = destination_path


        # L'utente potrebbe inserire un percorso "USER Library" che non è una libreria USER Library Ma è un semplice percorso,
        # quindi bisogna controllare se è una libreria USER della versione corrente o precedente, nel caso non fosse nessuna delle due,
        # bisogna creare la cartella "HDRI_MAKER_USER_LIB" e inserire il percorso di questa cartella nella variabile addon_user_library
        if os.path.isdir(addon_prefs.addon_user_library):
            # Check if the path is a USER Library of the current version or a previous version
            if not is_old_user_lib(addon_prefs.addon_user_library) and not is_new_library(addon_prefs.addon_user_library, get_library_type='USER'):
                # in questo caso bisogna creare o agganciare la cartella "HDRI_MAKER_USER_LIB" se esiste:
                # Ultimo controllo giusto per essere sicuri che la cartella non sia già presente:
                destination_path = os.path.join(addon_prefs.addon_user_library, "HDRI_MAKER_USER_LIB")
                if not os.path.isdir(destination_path):
                    os.mkdir(destination_path)
                    addon_prefs.addon_user_library = destination_path
                    from ...library_manager.get_library_utils import make_library_info
                    make_library_info(addon_prefs.addon_user_library, 'USER')
                else:
                    # Nel caso esista già la cartella, al 99.9% è perchè l'utente ha già installato "HDRI_MAKER_USER_LIB" in precedenza
                    addon_prefs.addon_user_library = destination_path

        # Controllare il percorso alla User Library, controllare se l'utente ha inserito un percorso esistente:
        if not os.path.isdir(addon_prefs.addon_user_library):
            # In questo caso il percorso non esiste, quindi tentare di andare allo stesso percorso in cui si trova la libreria di default:
            user_library_path = os.path.join(os.path.dirname(addon_prefs.addon_default_library), "HDRI_MAKER_USER_LIB")
            # Controllare se la cartella esiste, se non esiste, crearla:
            if not os.path.exists(user_library_path):
                os.mkdir(user_library_path)
            # Cambiare il percorso dell'utente al nuovo destination_path
            addon_prefs.addon_user_library = user_library_path
            # Controllare se la destination_path ora è una libreria USER della versione corrente:
            if not is_new_library(addon_prefs.addon_user_library, get_library_type='USER'):
                # Se no, bisogna creare la cartella ._data e il file library_info.json con i seguenti valori:
                from ...library_manager.get_library_utils import make_library_info
                # Questo scrive la cartella ._data e il file library_info.json nel percorso di destinazione
                make_library_info(addon_prefs.addon_user_library, 'USER')
            # Continuare tranquillamente, in questo caso, l'utente potrà cambiare in un secondo momento la User Library se presente




        # In quest'ultimo caso, se la libreria non è riconosciuta come una libreria nuova, è perchè manca la cartella "._data" e il file "library_info.json"
        if not is_new_library(addon_prefs.addon_default_library, get_library_type='DEFAULT'):
            # Se no, bisogna creare la cartella ._data e il file library_info con i seguenti valori:
            from ...library_manager.get_library_utils import make_library_info
            # Questo scrive la cartella ._data e il file library_info.json nel percorso di destinazione
            make_library_info(addon_prefs.addon_default_library, 'DEFAULT')

        preferences = get_addon_preferences()
        files_to_install = []
        for item in preferences.exapacks_install:
            if not item.is_good_zip:
                continue
            if item.product != Exa.product:
                continue
            if not os.path.isfile(item.filepath):
                continue

            files_to_install.append(item.filepath)


        if not files_to_install:
            # Traduci in Inglese:
            text = "No file to install from the list"
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        # Create the expansion path and item if it not exist:
        for filepath in files_to_install:
            get_or_create_expansion(filepath)

        cls = self.__class__
        cls._handler = self

        # I need 1 filepath to check in the next class, if the path source is the same of the path destination (For calculate the free space)
        from_dir = os.path.dirname(files_to_install[0])

        all_libraries_paths = get_all_libraries_paths()


        UNZIP = UnzipLibrary(from_dir=from_dir,
                             files_to_install=files_to_install,
                             addon_default_library=addon_prefs.addon_default_library,
                             keep_exapack_on_disk=addon_prefs.keep_exapack_on_disk,
                             override=preferences.exapack_override_installer,
                             all_libraries_paths=all_libraries_paths)
        thread = threading.Thread(target=UNZIP.execute)

        UNZIP.threads.clear()
        UNZIP.threads.append(thread)

        thread.name = "UNZIP"
        thread.stop = False
        thread.start()

        self._timer = wima().event_timer_add(0.1, window=context.window)
        wima().modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if event.type == 'TIMER':
            redraw_all_areas()
            cls = self.__class__

            thread = next((th for th in UnzipLibrary.threads), None)
            if not cls._handler:
                self.cancel(context)
                return {'FINISHED'}

            elif UnzipLibrary.finished:
                self.cancel(context)
                return {'FINISHED'}

            elif UnzipLibrary.error_msg:
                draw_info(UnzipLibrary.error_msg, "INFO", 'INFO')
                self.cancel(context)
                return {'CANCELLED'}

            elif not thread:
                self.cancel(context)
                return {'FINISHED'}

        return {'PASS_THROUGH'}


class UnzipLibrary:
    total_files = 0
    files_copied = 0

    packed_files = 0
    unpacked_files = 0

    finished = False

    error_msg = None
    threads = []
    finish = False
    cancelled = False

    prepare_is_running = False

    volume_name = ""
    volume_file_errors = {}

    def __init__(self, from_dir, files_to_install, addon_default_library, override=False,
                 keep_exapack_on_disk=False,
                 all_libraries_paths=[]):  # List of zip files
        self.from_dir = from_dir  # Used to know from where the zip file is coming from
        self.addon_default_library = addon_default_library  # The path of the HDRI_MAKER_DEFAULT_LIB folder
        self.override = override  # If True, override the existing files
        self.files_to_install = files_to_install  # The path of the folder where the zip files are located
        self.zip_files = []
        self.keep_exapack_on_disk = keep_exapack_on_disk
        self.volume_info_data = None
        self.install_start_time = time.time()
        self.all_libraries_paths = all_libraries_paths
        self.lock = threading.Lock()

        cls = self.__class__
        cls.total_files = 0
        cls.files_copied = 0
        cls.finished = False
        cls.error_msg = None
        cls.cancelled = False
        cls.volume_name = ""
        cls.prepare_is_running = False
        cls.threads.clear()
        cls.volume_file_errors = {}

    def execute(self):
        self.lock.acquire()

        prepare = self.prepare()
        if prepare:
            self.install()

        self.lock.release()

    def prepare(self):
        cls = self.__class__
        cls.prepare_is_running = True

        bad_zips = []
        incompatible_zips = []

        # Questo è solo per comodità, serve per controllare al volo quali file duplicati ci sono
        files_control = []

        self.volume_zips = {}

        total_size_uncompressed = 0
        # Get all zip files in the directory:
        index = -1
        for exapack_filepath in self.files_to_install:
            read_volume = read_volume_info(exapack_filepath)
            json_data = read_volume.get('json_data')
            if not json_data:
                continue

            files_dict = json_data.get('files_dict')
            if not files_dict:
                continue

            library_type = json_data.get("library_type")

            print("Library Type: ", library_type)
            install_destination = None
            if library_type == "default_library":
                install_destination = self.addon_default_library
            elif library_type == "expansion_library":
                # In questo caso dobbiamo controllare nella lista delle librerie installate (Sottoforma di espansioni) se esiste già una libreria con lo stesso nome
                # Se esiste, l'installazione avvene in tale cartella
                # Il processo di creazione avviene al di fuori di questa classe, poichè qui siamo in modalità multythread
                # Blender potrebbe facilmente crashare se si tenta di usare le sue API in questo contesto.
                library_name = json_data.get("library_name")
                if library_name:
                    all_lib = self.all_libraries_paths['EXPANSION']
                    print("All Lib: ", all_lib)
                    for dir in all_lib:
                        # Get ._data folder if exists:
                        data_folder = os.path.join(dir, "._data")
                        if not os.path.isdir(data_folder):
                            continue
                        from ...utility.json_functions import get_json_data
                        library_info = os.path.join(data_folder, "library_info.json")
                        if not os.path.isfile(library_info):
                            continue
                        library_info_data = get_json_data(library_info)
                        if not library_info_data:
                            continue

                        if library_info_data.get("library_name") == library_name:
                            install_destination = dir
                            break

            if not install_destination:
                # In questo caso Eccezzionale, che non dovrebbe succeder
                # non è stata trovata probabilmente corrispondenza nella lista delle librerie delle espansioni
                # O non è stata creata alcuna libreria per qualche motivo sconosciuto al momento. O per via di qualche permesso
                print("No install destination found for: ", exapack_filepath)
                install_destination = self.addon_default_library

            files_to_copy = {}
            for idx, values in files_dict.items():
                # Questo ci serve per sapere quali file esistono e quali no, di conseguenza calcolare il size per eventualmente fermare il ciclo
                file_size = values.get("file_size")
                file_name = values.get("file_name")
                file_path = values.get("file_path")

                # Prima di aggiungere il file al dizionario, bisogna controllare se il file è già presente nel dizionario self.volume_zips,
                # Questo è importante perchè i file data/preview/tags etc... sono presenti in tutti i volumi,
                # quindi verrebbero decompressi piu volte inutilmente con un grosso dispendio di tempo
                # ------------------------------- #
                if file_path not in files_control:
                    files_control.append(file_path)
                else:
                    continue
                # ------------------------------- #

                if os.path.isfile(ntpath.normpath(os.path.join(install_destination, file_path))):
                    if not self.override:
                        cls.total_files += 1
                        cls.files_copied += 1
                        continue

                files_to_copy[idx] = values
                total_size_uncompressed += file_size
                cls.total_files += 1

            # library_type è il tipo di libreria Enum In DEFAULT
            # library_type = json_data.get("library_type")

            # install_destination = None
            # if library_type == "default_library":
            #     install_destination = self.addon_default_library
            # elif library_type == "expansion_library":
            #     # In questo caso dobbiamo controllare nella lista delle librerie installate (Sottoforma di espansioni) se esiste già una libreria con lo stesso nome
            #     # Se esiste, l'installazione avvene in tale cartella
            #     # Il processo di creazione avviene al di fuori di questa classe, poichè qui siamo in modalità multythread
            #     # Blender potrebbe facilmente crashare se si tenta di usare le sue API in questo contesto.
            #     library_name = json_data.get("library_name")
            #     if library_name:
            #         all_lib = self.all_libraries_paths['EXPANSION']
            #         for dir in all_lib:
            #             # Get ._data folder if exists:
            #             data_folder = os.path.join(dir, "._data")
            #             if not os.path.isdir(data_folder):
            #                 continue
            #             from ...utility.json_functions import get_json_data
            #             library_info = os.path.join(data_folder, "library_info.json")
            #             if not os.path.isfile(library_info):
            #                 continue
            #             library_info_data = get_json_data(library_info)
            #             if not library_info_data:
            #                 continue
            #
            #             if library_info_data.get("library_name") == library_name:
            #                 install_destination = dir
            #                 break

            # if not install_destination:
            #     # In questo caso Eccezzionale, che non dovrebbe succeder
            #     # non è stata trovata probabilmente corrispondenza nella lista delle librerie delle espansioni
            #     # O non è stata creata alcuna libreria per qualche motivo sconosciuto al momento. O per via di qualche permesso
            #     print("No install destination found for: ", exapack_filepath)
            #     install_destination = self.addon_default_library

            index += 1
            self.volume_zips[index] = {}
            self.volume_zips[index]["zip_file"] = exapack_filepath
            self.volume_zips[index]["volume_name"] = json_data["volume_name"]
            self.volume_zips[index]["files_to_copy"] = files_to_copy
            self.volume_zips[index]["install_destination"] = install_destination
            # Replace the volumes is made for example to replace in the future, 2 libraries for example with only 1,
            # In into the only 1 is specified the volumes to replace, so the volumes json into register will be replaced
            replace_the_volumes = json_data.get("replace_the_volumes")
            if replace_the_volumes:
                self.volume_zips[index]["replace_the_volumes"] = replace_the_volumes  # This is a list of volumes to replace

        # Aggiornare e Riorganizzare l'ordine di self.volume_zips in base alla quantità di file in esso, l'ordine è: Piu file ci sono, prima viene decompresso
        # self.volume_zips = {k: v for k, v in
        #                     sorted(self.volume_zips.items(), key=lambda item: len(item[1]["files_to_copy"]),
        #                            reverse=True)}

        # Get the free space of the destination path:
        import shutil
        free_space = shutil.disk_usage(self.addon_default_library).free
        if is_from_same_drive(self.from_dir, self.addon_default_library):
            if self.keep_exapack_on_disk:
                # In this case, if the user wants to keep the exapack files, it is not necessary to check the free space, because
                # The free space will almost certainly be sufficient, because the exapack files will be deleted at the end of the process
                # And during the process the files from them, those already installed, will be removed.
                if total_size_uncompressed > free_space:
                    tot_size_str = str(round(total_size_uncompressed / 1024 / 1024 / 1024, 2)) + " GB"
                    text = "The free space on the disk is not enough to install the files," \
                           "the free space on the disk is: " + str(round(free_space / 1024 / 1024 / 1024, 2)) + " GB, " \
                           "the total size of the files is: " + tot_size_str + " If you want to save space, check the box 'Remove exapack after install' and try again"

                    cls.error_msg = text
                    cls.prepare_is_running = False
                    return
        else:
            if total_size_uncompressed > free_space:
                tot_size_str = str(round(total_size_uncompressed / 1024 / 1024 / 1024, 2)) + " GB"
                text = "The free space on the disk is not enough to install the files, please free some space and try again, " \
                       "the free space on the disk is: " + str(round(free_space / 1024 / 1024 / 1024, 2)) + " GB, " \
                                                                                                            "the total size of the files is: " + tot_size_str

                cls.error_msg = text
                cls.prepare_is_running = False
                return

        if bad_zips:
            from ...utility.text_utils import draw_info
            text = "The following .exapack files are not valid: " + ", ".join(bad_zips)
            text += "These .exapack files are corrupted, and cannot be used, this may have happened during the download, " \
                    "please try to download the following files again:" \
                    " ".join(bad_zips)
            cls.error_msg = text
            cls.prepare_is_running = False
            return

        # if not self.volume_zips:
        #     text = "No valid '.exapack' file found in the indicated directory ( {} ), please indicate the path where you downloaded the .exapack files," \
        #            "if you have not yet downloaded the .exapack files, go to the download page and download them".format(
        #         self.directory)
        #     cls.error_msg = text
        #     cls.prepare_is_running = False
        #     return

        cls.prepare_is_running = False
        # If all is ok, return True:
        return True

    def install(self):
        # Test senza thread = 1:39:14.541967 (HD Esterno Su USB 3.0 Su Stesso HD Esterno)
        # Test senza thread = 0:34:05.824981 (Da HD Interno A SSD)
        # Test con thread = 40+minuti (Da HD Interno A SSD) (Non perfomante, ma funziona)
        # Test senza thread = 0:50:26.529850 (Da SSD A SSD) , non buono

        cls = self.__class__
        install_start_time = time.time()

        # Ottenere il numero di core liberi:
        cores = 16

        # import threading
        # lock = threading.Lock()
        for idx, volume in self.volume_zips.items():
            if cls.cancelled or cls.error_msg or cls.finished:
                return
            error_extracting = self.unzip(volume)
            if error_extracting:
                cls.volume_file_errors[volume['volume_name']] = error_extracting
                print("An error occurred while extracting the files from the .exapack file: ", volume['volume_name'])
                print("Error with this file(s): ", error_extracting)

        print("Install finished in: ", time.time() - install_start_time)
        cls.finished = True

    def unzip(self, volume):

        cls = self.__class__
        # for idx, value_dict in volume.items():
        zip_file = volume["zip_file"]
        volume_name = volume["volume_name"]
        files_to_copy = volume["files_to_copy"]
        install_destination = volume["install_destination"]
        # Replace the volumes, is a list, if into the list there are a volume name, and the volume name is about an already installed volume,
        # We need to go into the \._data\._volumes_installed\ and delete the json file of the volume if it exists, because, the current package
        # is a newer version of the volume, and we need to replace the old one with the new one
        # Example Old Volumes 2 GB, can be replaced into the future with a new volume of 4 GB, so we need to delete the old volume
        replace_the_volumes = volume.get("replace_the_volumes")
        #
        # Importante, poichè i filepath nel dizionario hanno // mentre i file hanno /

        filepaths = [ntpath.normpath(values.get("file_path")) for idx, values in files_to_copy.items()]

        cls.volume_name = volume_name
        # Extract 1 by 1 the zip files:
        error_extracting = {}
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # L'estrazione dei file, deve avvenire in maniera selettiva,
            # Se l'exapack è di tipo "default_library" esso deve essere installato direttamente nella cartella "default_library"
            # Se l'exapack è di tipo "user_library" esso deve essere installato nella cartella "user_library"
            # Se invece l'exapack è di tipo "expansion" bisogna controllare il nome della libreria, e controllare che essa sia già
            # in parte installata nei percorsi, se non è installata, bisogna aggiungere un nuovo "Expansion Path" e installare l'exapack
            # Nel nuovo percorso

            # Get the list of all files in the zip file:
            files = zip_ref.namelist()
            cls.packed_files = len(files)
            cls.unpacked_files = 0
            for file in files:
                cls.unpacked_files += 1
                if file in ['', 'README.txt']:
                    continue

                if ntpath.normpath(file) not in filepaths:
                    continue

                if not HDRIMAKER_OT_install_exapacks.is_running():
                    cls.cancelled = True
                    return

                if cls.cancelled:
                    cls.finished = True
                    return

                if cls.finish:
                    cls.finished = True
                    return

                # Extract the file:
                time_start = time.time()

                # Get zip file name without extension
                print("Extracting: ", file)
                # print zip file name:
                print("From Exapack: ", zip_file)
                try:
                    zip_ref.extract(file, install_destination)
                except Exception as e:
                    print("Error extracting: ", file, "From Exapack: ", zip_file)
                    error_extracting[file] = e
                    continue

                print("File extracted: {} in {} seconds".format(file, time.time() - time_start))
                print("The file are now in: ", install_destination)
                print("Total Time: ", human_time_seconds(time.time() - self.install_start_time))
                print("# ------------------------------- #")
                cls.files_copied += 1

        if type(replace_the_volumes) == list:
            for v_name in replace_the_volumes:
                print("v_name: ", v_name)

                volume_info_file = get_volume_filepath_by_name(v_name)
                if not volume_info_file:
                    continue

                if os.path.exists(volume_info_file):
                    try:
                        os.remove(volume_info_file)
                    except Exception as e:
                        print("Error removing the file: ", volume_info_file, "Error: ", e)

        #     write_volumes_installed(self.addon_default_library, self.volume_info_data)
        cls.volume_name = ""

        if error_extracting:
            # In this case, the zip file is not deleted, some files are "Bad Zip File" strange bug about the zip file py module
            return error_extracting

        if not self.keep_exapack_on_disk:
            # Try to remove the zip file:
            try:
                os.remove(zip_file)
            except:
                pass


def read_volume_info(filepath):
    """Read the json called '.volume_info' in the zip file or into a folder, if ok return True"""

    json_file = None

    # In this case the filepath is a zip file:
    if not is_good_zip_file(filepath):
        return {"status": 'BAD_ZIP_FILE'}

    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        # Get the json file from the zip file:
        for file in zip_ref.namelist():
            if file.endswith('.json'):
                # Open the json file and get the 'volume_info' data:
                with zip_ref.open(file) as json_file:
                    json_data = json.load(json_file)
                    product = json_data.get('product')
                    if product == Exa.product:
                        return {"status": True, "json_data": json_data}

    # In questo caso nessun file json è stato trovato o il file non è valido:
    return {"status": False}


class HDRIMAKER_OT_AbortZipInstall(Operator):
    """Abort the installation of the zip files"""
    bl_idname = Exa.ops_name + "abort_zip_install"
    bl_label = "Abort Exapack Install"
    bl_options = {'REGISTER', 'UNDO'}

    confirm: EnumProperty(items=(('YES', "Yes", ""), ('NO', "No", "")), default='NO')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Are you sure you want to abort the installation?")
        row = col.row(align=True)
        row.alignment = 'CENTER'
        text = "( All installed files will remain as such, you can resume at a later time )"
        row.label(text=text)
        col.separator()
        row = col.row(align=True)
        row.prop(self, "confirm", expand=True)
        col.separator()
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Press Ok To Confirm or Esc to continue the installation")
        col.separator()

    def invoke(self, context, event):
        self.confirm = 'NO'
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        if self.confirm == 'NO':
            return {'CANCELLED'}

        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface

        # Abort the class:
        UnzipLibrary.cancelled = True
        # Abort the modal operator:
        cls = HDRIMAKER_OT_install_exapacks
        cls._handler = None

        refresh_interface()
        return {'FINISHED'}


def read_volumename_from_zip(zip_filepath):
    """Read the json called '.volume_info' from zipfile and return the volume name"""

    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        if '.volume_info' in zip_ref.namelist():
            json_file = zip_ref.read('.volume_info')

    if json_file:
        json_data = json.loads(json_file)
        volume_name = json_data.get('volume_name')

    return volume_name

# Il file viene scritto già

# def write_volumes_installed(path, volume_info_data):
#     """Write into .data folder a json file named '.installed_volumes.json' with the name of the volume installed"""
#     # Open json file from zip_filepath:
#
#     _data_path = os.path.join(path, '._data')
#     if not os.path.isdir(_data_path):
#         os.mkdir(_data_path)
#
#     installed_volumes = os.path.join(_data_path, 'installed_volumes')
#     if not os.path.isdir(installed_volumes):
#         os.mkdir(installed_volumes)
#
#     # Get the volume name:
#     volume_name = volume_info_data.get('volume_name')
#
#     # Write the file into in installed_volumes folder:
#     volume_info_file = os.path.join(installed_volumes, volume_name + '.json')
#     save_json(volume_info_file, volume_info_data)

class HDRIMAKER_OT_FinishConfirm(Operator):
    """Confirm the end of the installation"""
    bl_idname = Exa.ops_name + "finish_confirm"
    bl_label = "Finish Confirm"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        # Abort the class:
        UnzipLibrary.finished = False
        # Abort the modal operator:
        cls = HDRIMAKER_OT_install_exapacks
        cls._handler = None

        # Remove all the files from collection property:

        preferences = get_addon_preferences()
        preferences.exapacks_install.clear()

        refresh_interface()
        return {'FINISHED'}
