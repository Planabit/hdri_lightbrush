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
import threading
import time
import zipfile
import ntpath

import numpy as np

lock = threading.Lock()

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from ...exaconv import get_scnprop
from ...exaproduct import Exa


def get_volume_info_file_list(source_path, library_name=""):
    import zipfile
    full_file_list = []
    for fn in os.listdir(source_path):
        if not fn.endswith(".exapack"):
            continue
        # Get the volume info file from the zip file:
        with open(os.path.join(source_path, fn), "rb") as zip_file:
            with zipfile.ZipFile(zip_file) as zf:
                for file in zf.namelist():
                    # Check if file is .json file:
                    if not file.endswith(".json"):
                        continue
                    # Get the values by the "volume_info" key:
                    with zf.open(file) as json_file:
                        json_data = json.load(json_file)
                        volume_info = json_data.get("product")
                        if volume_info == Exa.product:
                            # In questo caso è un volume di library del prodotto corrente:
                            files_dict = json_data.get("files_dict")
                            for idx, value in files_dict.items():
                                full_file_list.append(value["file_path"])

    return full_file_list


class CompileVolumeIdx:
    """Controlla se esiste il volume n., nel caso esiste già, incrementa il volume_index fino a raggiungere un volume non esistente
    e restituisce il nome del volume da creare"""

    def __init__(self, volume_version, volume_index, directory, preindex, exapack_prefix_name):
        self.preindex = preindex
        self.volume_index = volume_index
        self.directory = directory
        self.volume_version = volume_version
        self.zip_file_name = ""
        self.exapack_prefix_name = exapack_prefix_name

    def run(self):
        from ...exaconv import get_scnprop
        scnProp = get_scnprop(bpy.context.scene)

        # if len_preindex == 1 The decine is 10 elif len_preindex == 2 The decine is 100 elif len_preindex == 3 The decine is 1000, etc.
        if self.preindex == "00":
            decine = 10
            zeros = "0"
        elif self.preindex == "000":
            decine = 100
            zeros = "00"
        elif self.preindex == "000":
            decine = 1000
            zeros = "000"
        elif self.preindex == "0000":
            decine = 10000
            zeros = "0000"

        # volume_index is the volume number, but we need to add to the left the zeros, so we can have a correct order
        # in the file explorer
        volume_index = self.preindex + str(self.volume_index)

        # Bisogna controllare che il numero di caratteri non superi il numero di caratteri del preindex, altrimenti, bisogna cancellare gli zeri a sinistra

        # if preindex is 00 and the volume_index is 1, the volume_index is 01, if the volume_index is 10, the volume_index is 10
        # if preindex is 000 and the volume_index is 1, the volume_index is 001, if the volume_index is 10, the volume_index is 010, if the volume_index is 100, the volume_index is 100
        # Etc.

        compiled_index = volume_index[-len(self.preindex):]

        # compiled_index = self.preindex + str(self.volume_index) if self.volume_index < decine else str(self.volume_index)
        if self.volume_version:
            self.zip_file_name = self.exapack_prefix_name + "_" + self.volume_version + "_Vol_" + compiled_index + ".exapack"
        else:
            self.zip_file_name = self.exapack_prefix_name + "_Vol_" + compiled_index + ".exapack"
        # Check if the zip file already exists:
        if os.path.exists(os.path.join(self.directory, self.zip_file_name)):
            # If exists increment the self.volume_index and run again:
            self.volume_index += 1
            self.run()

        return self.zip_file_name


def multi_process(files_dict=None, exapack_library_path=None, library_path=None,
                  total_files_index=None, total_files=None, preindex=None, pause=None, lock=None,
                  exapack_prefix_name=None, exapack_ignore_material_version=False, library_type="", library_name=""):
    import zipfile
    # Create the zip file, during the creation we need to check the size of the zip file, if the size is greater than 2Gb
    # we need to create a new zip file with a suffix Vol_1, Vol_2, etc...

    if lock:
        lock.acquire()

    volume_index = 1
    # Size of the file uncompressed
    uncompressed_size = 0

    files_idx = 0
    json_files_dict = {}

    volume_version = files_dict["volume_version"]
    current_size = files_dict["current_size"]
    files = files_dict['files']

    if exapack_ignore_material_version:
        volume_version = ""

    zip_file_name = CompileVolumeIdx(volume_version, volume_index, exapack_library_path, preindex,
                                     exapack_prefix_name).run()
    zip_file_path = os.path.join(exapack_library_path, zip_file_name)

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Write zipfile:
        for idx, file in enumerate(files):
            # Check if the file is already in the zip file at the same path:

            rel_path = ntpath.normpath(os.path.relpath(file, library_path))
            # Tranform the zip_file.namelist() from / to \, because the rel_path is in windows format
            zip_file_namelist = [ntpath.normpath(x) for x in zip_file.namelist()]

            if rel_path in zip_file_namelist:
                # Alcuni problemi con duplicati.json tag e mat_info.json
                # Iniziato da quando abbiamo fatto il "No Volume types"
                print("File already exists in the zip file, skipping... {}".format(file))
                continue


            while pause:
                continue
            files_idx += 1
            # Get the size of the file to archive it into the zip file:
            file_size = os.path.getsize(file)
            uncompressed_size += file_size

            total_files_index += 1
            print("# --------------------- #")
            print("ZipName: ", zip_file_name)
            print("#", total_files_index, " of ", total_files)
            print("Writing file: ", file)
            print("To directory: ", exapack_library_path)


            zip_file.write(file, os.path.relpath(file, library_path))

            json_files_dict[files_idx] = {}
            json_files_dict[files_idx]['file_size'] = file_size
            json_files_dict[files_idx]['file_name'] = os.path.basename(file)
            json_files_dict[files_idx]['file_path'] = os.path.relpath(file, library_path)

        json_data = write_json(zip_file, files_idx, volume_version, zip_file_name, uncompressed_size, json_files_dict, library_type, library_name)
        write_readme(zip_file)

    # Scrivi file json anche nella directory dove è stato scritto il file exapack, poichè ci servirà da caricare su github
    # Per tenere traccia dei volumi creati

    if lock:
        lock.release()



class CalculateZip:

    dizionario = {}
    @staticmethod
    def calculate_zip_size(directory, file, write_json=True):
        from ...utility.json_functions import get_json_data

        # directory is the root and file is the file to calculate the size

        # Get relative path file, as filename

        relate_filepath = os.path.relpath(file, directory)

        # Write zip file size into json file
        json_register_file = os.path.join(directory, "._data", "zips_size_register.json")

        # Check if filename is already in json file

        json_data = get_json_data(json_register_file)
        if json_data:
            mem_zip_size = json_data.get(relate_filepath)
            if mem_zip_size:
                print("Zip size already calculated, skipping... {}".format(relate_filepath))
                # Add into dizionario:
                CalculateZip.dizionario[relate_filepath] = mem_zip_size
                return mem_zip_size

        # generate_time = time.time()
        # mem_zip = generate_zip(file)
        # mem_zip_size = sys.getsizeof(mem_zip)
        # Create a zip file provvisorio per calcolare la dimensione del file zippato
        # Create temp file into windows temp directory
        import tempfile

        temp_dir = tempfile.gettempdir()
        # Generate univoque name for the temp file:
        import uuid
        temp_file_name = str(uuid.uuid4()) + ".zip"
        temp_file_path = os.path.join(temp_dir, temp_file_name)
        # Write the zip file:

        generate_time = time.time()
        print("Write temp zip file: ", temp_file_path)
        with zipfile.ZipFile(temp_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(file, os.path.relpath(file, directory))

        mem_zip_size = os.path.getsize(temp_file_path)

        print("Mem value: ", mem_zip_size)
        print("Time to generate zip: ", time.time() - generate_time)

        file_register = {relate_filepath: mem_zip_size}
        if write_json:
            if json_data:
                json_data.update(file_register)
            else:
                json_data = file_register
            with open(json_register_file, 'w') as outfile:
                # Make indent to 4 spaces
                json.dump(json_data, outfile, indent=4)

        # Add into dizionario:
        CalculateZip.dizionario[relate_filepath] = mem_zip_size

        # Delete temp file:
        os.remove(temp_file_path)

        return mem_zip_size

class HDRIMAKER_OT_GenerateZipsJson(Operator):

    bl_idname = Exa.ops_name+"generate_zips_json"
    bl_label = "Generate Zips Json"
    bl_description = "Generate Zips Json"
    bl_options = {'INTERNAL'}

    @classmethod
    def description(cls, context, properties):
        desc = "Generate a json file in ._data with the dimensions of all zipped files, it zips the files and calculates " \
                "the size of the zipped file, so that when exapack are created, they are all calculated based on the " \
                "actual size of the zipped packages. Useful to keep the dimensions of the exapack files as close as possible " \
                "to the size of 2 GB per package, because some users may have timeout problems with too large files. " \
                "Especially on Blendermarket. "

        return desc

    def execute(self, context):

        from ...utility.json_functions import get_json_data
        from ...library_manager.get_library_utils import libraries_path

        CalculateZip.dizionario = {}

        scn = context.scene

        addon_current_library, risorse = libraries_path()

        files = []
        idx = 0
        for root, dirnames, filenames in os.walk(addon_current_library):
            # Avoid the folder named ._data
            if os.path.basename(root) == "._data":
                continue
            for filename in filenames:
                idx += 1
                print(idx, "Adding file: ", os.path.join(filename))
                files.append(os.path.join(root, filename))

        print("Files listed")

        # Get core numbe
        scnProp = get_scnprop(scn)
        files_split = np.array_split(files, scnProp.exapack_cores)

        # Create a list of processes that we want to run calculate_zip_size
        processes = []
        for idx, files in enumerate(files_split):
            # Pay attention, the funcion calculate_zip_size acept only 1 file per time
            for file in files:
                t = threading.Thread(target=CalculateZip.calculate_zip_size, args=(addon_current_library, file, False))
                processes.append(t)
                t.start()

            # We need to get the result of the function calculate_zip_size
            # So we need to wait for all the processes to finish
            for process in processes:
                process.join()

            # At the end we need to grab the CalculateZip.dizionario and write it into a json file
            json_register_file = os.path.join(addon_current_library, "._data", "zips_size_register.json")
            new_json_data = CalculateZip.dizionario
            # Add new_json_data to json_register_file:

            json_data = get_json_data(json_register_file)
            if json_data:
                json_data.update(new_json_data)
            else:
                json_data = new_json_data
            # use indent = 4 to write the json file in a more readable way
            with open(json_register_file, 'w', encoding='utf-8') as outfile:
                print("Writing json file: ", json_register_file)
                json.dump(json_data, outfile, indent=4)

            # Reset the processes list
            processes = []


        return {'FINISHED'}


class HDRIMAKER_OT_CreateZipLibrary(Operator):
    """This operator creates the compressed library volumes from the decompressed original library
    It divides them into 1k_Vol_1, 2k_Vol_2, etc ...
    If over time, the original library expands, it will be checked if the file exists in the compressed archive,
    if it is present in it, it is bypassed, if not, a subsequent volume to the volume of such category will be written
    (Example, The 1k volume at the moment only reaches 1k_vol_1, if one day, new files are added, and there are files in the 1k folder,
    they will not be added to the 1k_vol_1 volume, but to the 1k_vol_2 volume, and so on), This is because the end user must know which volumes he has installed,
    and they must not change over time, otherwise it would be very confusing
    """

    bl_idname = Exa.ops_name + "create_zip"
    bl_label = "Create Zip"
    bl_options = {'INTERNAL'}

    # Get the ImportHelper mixin class, remove the properties it adds
    # to the class
    filter_glob: StringProperty(options={'HIDDEN'}, default='*.exapack')
    filepath: StringProperty(options={'HIDDEN'}, subtype='DIR_PATH')
    directory: StringProperty(options={'HIDDEN'}, subtype='DIR_PATH')

    volume_packed_list = None
    total_files_index = 0
    total_files = 0

    threads = []
    cpu_cores = 8

    _threads_in_use = 0

    _timer = None

    @classmethod
    def decription(cls, context, properties):
        return "Create a zip file from a library"

    def invoke(self, context, event):
        cls = self.__class__
        cls._threads_in_use = 0
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        from ...utility.utility import get_addon_preferences
        from ...library_manager.k_size_enum import k_size_compo_string
        from ...exaconv import get_scnprop


        scnProp = get_scnprop(context.scene)

        preferences = get_addon_preferences()

        # Ottengo il registro completo dei files che sono già stati compressi in formato exapack in precedenza,
        # dal percorso di destinazione, per mantenere sempre i volumi invariati e aggiungere in modo incrementale
        # I nuovi files in nuovi volumi
        # file archiviati

        # Create the "HDRi_Maker_ExaPack_Library" folder if not exists:)

        if not scnProp.exapack_library_name.lower() in self.directory.lower():
            self.directory = os.path.join(self.directory, scnProp.exapack_library_name)

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

        archived_files = get_volume_info_file_list(self.directory, library_name=scnProp.exapack_library_type)

        # Get the library path:
        # addon_current_library = preferences.addon_current_library

        from ...library_manager.get_library_utils import libraries_path
        addon_current_library, risorse = libraries_path()

        # Into the library we have the files in this structure:
        # 1) Root folder (addon_current_library)
        #   - 2) Category folders
        #       - 3) Material folders
        #
        #           - A) Version folders (Can be more than one), usually the names are (01k, 02k, 04k, 08k, 16k) in rare cases are the name of the material version
        #               -  Material files (can be more than one and can be .blend or .hdr or .exr or other)
        #           - B) Version folders (Can be more than one), usually the names are (01k, 02k, 04k, 08k, 16k) in rare cases are the name of the material version
        #               -  Material files (can be more than one and can be .blend or .hdr or .exr or other)
        #           - C) Etc...
        #               - Etc...
        #           - 4) data folder
        #               - tags.json
        #
        #               - 5) previews folder
        #                   - default folder
        #                       - preview.png

        # Creiamo un dizionario contenente i nomi delle cartelle contenute nelle directory "Material folders"
        # e i relativi files
        k_list = k_size_compo_string(minimum=1, maximum=20)
        limit = 0

        full_files = {}
        idx = -1
        for root, dirs, files in os.walk(addon_current_library):
            for fn in files:
                # # Get the relative path of folder from the library path
                full_path = os.path.join(root, fn)
                rel_path = os.path.relpath(full_path, addon_current_library)

                if "._data" in rel_path:
                    # I file contenuti nella cartella ._data non vengono compressi, poichè essi vengono generati in fase di decompressione
                    continue

                # Check if file is already archived:
                if rel_path in archived_files:
                    print("File already archived: " + rel_path)
                    continue

                # # Split the relative path and get the  3rd element (the Version folder)
                rel_path_split = rel_path.split(ntpath.normpath(os.sep))
                # # Get the name of the Version folder
                if len(rel_path_split) < 3:
                    continue
                idx += 1

                # Get the name of the Category folder
                category_folder_name = rel_path_split[0]
                # Get material folder name:
                material_folder_name = rel_path_split[1]
                # Get the name of the Version folder:
                version_folder_name = rel_path_split[2]

                if version_folder_name != 'data':
                    full_files[idx] = {}
                    # Tutte le versioni del materiale
                    if not full_files[idx].get(version_folder_name):
                        full_files[idx][version_folder_name] = []
                    # Qui aggiungiamo i file del materiale della versione
                    full_files[idx][version_folder_name].append(full_path)

                    # Get the data folder files:
                    data_folder_path = os.path.join(addon_current_library, category_folder_name, material_folder_name,
                                                    'data')
                    if os.path.exists(data_folder_path):
                        for data_root, data_dirs, data_files in os.walk(data_folder_path):
                            for data_fn in data_files:
                                data_full_path = os.path.join(data_root, data_fn)
                                data_rel_path = os.path.relpath(data_full_path, addon_current_library)
                                if not full_files[idx].get('data'):
                                    full_files[idx]['data'] = []
                                full_files[idx]['data'].append(data_full_path)

        if not full_files:
            # In this case we have archived all the files in the library, there are into exapack files
            text = "No files to archive"
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        volumes_versions = {}
        for idx, (key, value) in enumerate(full_files.items()):
            version_name = list(value.keys())[0]

            # Check if list(values.keys())[1] exists
            if len(list(value.keys())) == 1:
                # In this case we need to interrupt the loop and report the error into a popup:
                self.report({'ERROR'},
                            "The material {} has no version, check the console".format(str(key) + str(value)))
                return {'CANCELLED'}

            if version_name:
                if not "_" + version_name in k_list:
                    version_name = 'Main'

            if not volumes_versions.get(version_name):
                volumes_versions[version_name] = []

            # Into version_name we have all the files of the material
            volumes_versions[version_name].append(value)



        # Now we have to create the zip files

        # Len the number of files to archive:

        self.total_files_index = 0
        self.total_files = len(full_files)

        # Per fare dei test, elimino da volume version volumi 16k etc...
        # for item in ['18k', '17k', '16k', 'Main']:
        #     if item in volumes_versions.keys():
        #         del volumes_versions[item]

        current_size = 0

        pack_max = 2.0 * 1024 * 1024 * 1024  # in  # As +/- 2.2 GB Uncompressed

        volumes_index = 0
        volumes_packed = {}

        # TODO: Mettere a posto questa parte, non suddivide bene i pacchetti nella dimensione voluta, specialmente per i file 1k e quelli 2k
        #  probabilmente è dovuto al fatto che i file 1k e 2k sono molto più piccoli dei file 4k e 8k e quindi non riesce a raggiungere la dimensione voluta
        number_of_volumes = 0
        len_files = []
        # last_volume_version, is used to store the volume_version, if volume_version is different from last_volume_version,
        # an if statement is executed, this if statement, make possible to create a new volume
        last_volume_version = None
        make_only_1_version = False
        zip_size = 0
        for idx, (volume_version, files_value) in enumerate(volumes_versions.items()):
            print("volume_index ", volumes_index, "Volume version: " + volume_version)
            # if volumes_index == 0:
            #     # Only the first time we create the first volume
            #     current_size = 0
            #     volumes_packed[volumes_index] = {}
            #     volumes_packed[volumes_index]['volume_version'] = volume_version
            #     volumes_packed[volumes_index]['files'] = []

            # Questa condizione, scelta dall'interfaccia. Se è selezionata, non bada alle versioni, e scrive tutti i file in un unico volume
            # Dove unico volume, si intende "Senza versione", tutta la libreria viene scritta neza 1k version.
            # Questo è stato fatto per le espansioni tipo "HDRMaps" dove non volevamo creare volumi separati, ma mantenere
            # la libreria in un unico volume divisa per exapack. (Il problema era che ci sono troppo zip di piccole dimensioni.
            # Vogliamo tenere piu compatte le espansioni.

            if not scnProp.exapack_ignore_material_version:
                if last_volume_version != volume_version:
                    print("Under volume version: " + volume_version)
                    zip_size = 0
                    current_size = 0
                    volumes_index += 1
                    volumes_packed[volumes_index] = {}
                    volumes_packed[volumes_index]['volume_version'] = volume_version
                    volumes_packed[volumes_index]['current_size'] = current_size
                    volumes_packed[volumes_index]['files'] = []
                    last_volume_version = volume_version

            else:
                if not make_only_1_version:
                    zip_size = 0
                    current_size = 0
                    volumes_index += 1
                    volumes_packed[volumes_index] = {}
                    volumes_packed[volumes_index]['volume_version'] = volume_version
                    volumes_packed[volumes_index]['current_size'] = current_size
                    volumes_packed[volumes_index]['files'] = []
                    make_only_1_version = True



            # Dobbiamo dividere i file in base alla grandezza dei files contenuti in files_value, essa non deve superare i 2.2 GB
            # Ma deve contenere tutti i file contenuti nel percorso della cartella data
            # Esempio di files_value:
            # {'16k':
            #      [
            #          'G:\\3D Studio 2018\\Hdri Maker\\Hdri Maker 1.1\\HDRI_MAKER_DEFAULT_LIB\\Abandoned\\Roofless Ruins\\16k\\roofless_ruins_16k.hdr'],
            #  'data':
            #      [
            #          'G:\\3D Studio 2018\\Hdri Maker\\Hdri Maker 1.1\\HDRI_MAKER_DEFAULT_LIB\\Abandoned\\Roofless Ruins\\data\\tags.json',
            #          'G:\\3D Studio 2018\\Hdri Maker\\Hdri Maker 1.1\\HDRI_MAKER_DEFAULT_LIB\\Abandoned\\Roofless Ruins\\data\\previews\\default\\roofless_ruins.png']},

            for sIdx, data_and_mat_version in enumerate(files_value):
                # list_item sono solo 2 chiavi! La cartella versione e la cartella data!!!!
                # Quindi key, value sono qui di seguito! Dono solo 2 elementi, contenenti piu files!!!
                for key, value in data_and_mat_version.items():
                    # Qui sono sempre praticamente 2 chiavi per ogni items abbiamo {'16k': ['path1', 'path2', etc... ], 'data': ['path1', 'path2', etc... ]}
                    version = key
                    files = value
                    for file in files:
                        if file not in len_files:
                            len_files.append(file)
                        current_size += os.path.getsize(file)

                        volumes_packed[volumes_index]['current_size'] = current_size
                        volumes_packed[volumes_index]['files'].append(file)

                        zip_size += CalculateZip.calculate_zip_size(addon_current_library, file)

                # Only if the current size is equal or greater than the pack_max we create a new volume
                if zip_size >= pack_max:
                    # print(volumes_index, "Maximum size reached with the volume_version: " + str(volume_version))
                    # print("The size of the volume is: " + str(current_size))
                    # # Print size in GB:
                    # print("As Gb: " + str(current_size / 1024 / 1024 / 1024))
                    zip_size = 0
                    current_size = 0
                    volumes_index += 1
                    volumes_packed[volumes_index] = {}
                    volumes_packed[volumes_index]['volume_version'] = volume_version
                    volumes_packed[volumes_index]['current_size'] = current_size
                    volumes_packed[volumes_index]['files'] = []

            # Get next volume_versions:


        self.volume_packed_list = [file_dict for key, file_dict in volumes_packed.items()]

        # Now order the self.volume_packed_list by the size of the files, this avoid the creation of the example:
        # Vol_1 100Mb, Vol_2 2GB, to Vol_1 2GB, Vol_2 100Mb (Example)
        # PS: The filename is asigned to the exapack file into the multiprocessing function
        self.volume_packed_list = sorted(self.volume_packed_list, key=lambda k: k['current_size'], reverse=True)


        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        scn = context.scene
        scnProp = get_scnprop(scn)

        if scnProp.exapack_pause:
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            if not self.volume_packed_list and not self.threads:
                self.report({'INFO'}, "Exapacked finished!")
                return {'FINISHED'}

            for th in self.threads:
                # Se c'è un thread attivo, continua a passare il controllo
                if not th.is_alive():
                    self.threads.remove(th)

            if scnProp.exapack_terminate:
                # Qui devo terminare tutti i thread attivi aspettando che finiscano, poichè è stato premuto il tasto di terminazione
                if not self.threads:
                    return {'FINISHED'}
                else:
                    return {'PASS_THROUGH'}

            cls = self.__class__
            cls.threads_in_use = len(self.threads)

            # from ...utility.utility import get_addon_preferences
            # preferences = get_addon_preferences()

            from ...library_manager.get_library_utils import libraries_path
            addon_current_library, risorse = libraries_path()

            if len(self.threads) < scnProp.exapack_cores:
                # Se c'è almeno un thread libero, avvia un nuovo thread
                if not self.volume_packed_list:
                    # Se non ci sono piu files da archiviare, termina
                    text = "Exapacked finished!"
                    print(text)
                    self.report({'INFO'}, text)
                    return {'FINISHED'}

                files_dict = self.volume_packed_list.pop(0)
                # Create a thread for each core:
                print("scnProp.exapack_library_type: " + str(scnProp.exapack_library_type))
                t = threading.Thread(target=multi_process, args=(
                    files_dict, self.directory, addon_current_library, self.total_files_index,
                    self.total_files,
                    scnProp.exapack_preindex, scnProp.exapack_pause, None, scnProp.exapack_prefix_name,
                    scnProp.exapack_ignore_material_version,
                    scnProp.exapack_library_type,
                    scnProp.exapack_library_name))
                # Make synchronous the threads:
                self.threads.append(t)
                t.start()

        return {'PASS_THROUGH'}


def write_readme(zip_file):
    readme_file_name = "README.txt"

    readme_text = "Avoid extracting files manually, use HDRi Maker addon to extract files, in the preferences " \
                  "of HDRi Maker there is a dedicated section for installing via .exapack files"

    # Write readme file directly into the zip file:
    zip_file.writestr(readme_file_name, readme_text)


def write_json(zip_file, files_idx, volume_version, zip_file_name, uncompressed_size, files_dict, library_type, library_name):
    volume_name = zip_file_name.replace(".exapack", "")

    json_file_name = volume_name + ".json"

    json_data = {"volume_info": Exa.product + "_" + library_type,
                 "product": Exa.product,
                 "library_name": library_name,
                 "library_type": library_type,
                 "library_version": Exa.library_version,
                 "total_files": files_idx,
                 "volume_version": volume_version,
                 "volume_name": volume_name,
                 "uncompressed_size": uncompressed_size,
                 "replace_the_volumes": [],
                 # this is for the future, if pack size can be more than 2GB on Blender (now is 2GB because 2+GB can be made problem with some users)
                 "files_dict": files_dict}
    # Write the json directly into the zip file:
    # Now into the ._volume_installed folder write the json file:

    json_filepath = os.path.join("._data", "._volumes_installed", json_file_name)
    json_size = len(json.dumps(json_data))

    # Nel dizionario json bisogna aggiungere (Per comodità mettiamo un idx -1) nel file json
    # Durante la fase di installazione, avviene un controllo sul json del volume, esso contiene la lista dei file da decomprimere
    # Questo appunto, rende il json file un file da decomprimere.

    files_dict[-1] = {'file_size': json_size, 'file_name': json_file_name, 'file_path': json_filepath}
    # Questo files_dict va aggiunto al dizionario files_dict che viene passato alla funzione write_json:
    json_data.update(
        {"files_dict": files_dict, "total_files": files_idx + 1, "uncompressed_size": uncompressed_size + json_size})
    zip_file.writestr("._data/._volumes_installed/" + json_file_name, json.dumps(json_data, indent=4))

    return json_data


class HDRIMAKER_OT_MakeJsonExaCollection(Operator):

    bl_idname = Exa.ops_name + "make_json_exacollection"
    bl_label = "Make Json Exacollection"
    bl_description = "Make Json Exacollection"
    bl_options = {'INTERNAL'}

    filter_glob: StringProperty(options={'HIDDEN'}, default='*.exapack')
    directory: StringProperty(options={'HIDDEN'}, subtype='DIR_PATH')

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # Get all json files in the folder and check if they are valid, we need to check if the json file "volume_info": "HDRI_MAKER_default_library"
        # If the json file is valid, we need to add the json file to the list of the exacollection
        scn = context.scene
        scnProp = get_scnprop(scn)


        import zipfile

        json_data_list = []
        for file in os.listdir(self.directory):
            if not file.endswith(".exapack"):
                continue

            # Find the json file inside the exapack file, the json file must be contained in the ._data/._volumes_installed folder
            # We need to check if into json file contain the keys values:

            # ("volume_info") != Exa.product + "_default_library"
            # "product") != Exa.product
            # "library_type") != "default_library"

            zip_file = zipfile.ZipFile(os.path.join(self.directory, file), 'r')
            for file_name in zip_file.namelist():
                if file_name.endswith(".json"):
                    # Load the json data from zipfile: (Avoid to use get_json_data function, because it is not possible to load json data from zipfile)
                    json_data = json.loads(zip_file.read(file_name).decode("utf-8"))
                    # if json_data.get("volume_info") != Exa.product + "_default_library":
                    #     continue
                    # if json_data.get("product") != Exa.product:
                    #     continue
                    # if json_data.get("library_type") != "default_library":
                    #     continue
                    # if json_data.get("volume_info") != "{}_{}".format(Exa.product, scnProp.exapack_library_type):
                    #     continue
                    if json_data.get("product") != Exa.product:
                        continue
                    # if json_data.get("library_type") != scnProp.exapack_library_type:
                    #     continue
                    json_data_list.append(json_data)

        if not json_data_list:
            self.report({'ERROR'}, "No valid json files (Exapack) found in the directory {}".format(self.directory))
            return {'CANCELLED'}

        # Now we have a list of json files, we need to create the exacollection json file:
        datetime = int(time.time())
        collection_name = "hdri_maker_official_exapacks"
        collection_version = "1.0"

        exapacks = {}
        for json_data in json_data_list:
            volume_name = json_data.get("volume_name")
            exapacks[volume_name] = json_data

        exa_collection_json_data = {
            "collection_name": collection_name,
            "collection_version": collection_version,
            "datetime": datetime,
            "volume_quantity": len(json_data_list),
            "info": "This is the list of all exapacks available for HDRI Maker addon",
            "exapacks": exapacks
        }

        # Now we have the exacollection json data, we need to write the json file:
        from ...utility.json_functions import save_json
        save_path = os.path.join(self.directory, "exa_library_volumes.json")
        # Save json and keep the indent:
        save_json(save_path, exa_collection_json_data) # , indent=4)
        text = "Exa collection json file created successfully"
        print(text)
        self.report({'INFO'}, text)

        return {'FINISHED'}


class HDRIMAKER_OT_CreateTagAndMatInfo(Operator):

    bl_idname = Exa.ops_name + "create_tag_and_mat_info"
    bl_label = "Create Tag And Mat Info"
    bl_description = "Create Tag And Mat Info"
    bl_options = {'INTERNAL'}

    @classmethod
    def description(cls, context, properties):
        desc = """Crea un mini pacchetto dedicato ai vecchi utenti, cosi da avere i nuovi tag e le nuove info materiali sulle librerie convertite"""
        return desc

    def execute(self, context):

        import shutil
        from ...library_manager.get_library_utils import libraries_path

        # Get current library path:
        scn = context.scene
        scnProp = get_scnprop(scn)

        addon_current_library, risorse = libraries_path()

        # Create the structure inside the addon folder

        conversion_utility_folder = os.path.join(risorse, "conversion_utility")

        # Make the structure inside the conversion_utility folder:

        # Make same name folder "addon_current_library" inside the conversion_utility folder:
        store_library_folder = os.path.join(conversion_utility_folder, os.path.basename(addon_current_library))
        if not os.path.exists(store_library_folder):
            os.mkdir(store_library_folder)


        for category in os.listdir(addon_current_library):
            if category.startswith("."):
                continue

            # Create category folder inside the library folder:
            store_category_folder = os.path.join(store_library_folder, category)
            if not os.path.exists(store_category_folder):
                os.mkdir(store_category_folder)

            cat_path = os.path.join(addon_current_library, category)


            for mat in os.listdir(cat_path):
                # Create material folder inside the category folder:
                store_mat_folder = os.path.join(store_category_folder, mat)
                if not os.path.exists(store_mat_folder):
                    os.mkdir(store_mat_folder)

                mat_folder = os.path.join(cat_path, mat)

                for version_and_data in os.listdir(mat_folder):
                    # Create version folder inside the material folder:
                    store_version_folder = os.path.join(store_mat_folder, version_and_data)
                    if not os.path.exists(store_version_folder):
                        os.mkdir(store_version_folder)

                    if version_and_data == 'data':
                        data_folder = os.path.join(mat_folder, version_and_data)
                        for fn in os.listdir(data_folder):
                            if fn.endswith(".json"):
                                #Copy the json file inside the version folder:
                                file_from = os.path.join(data_folder, fn)
                                file_to = os.path.join(store_version_folder, fn)
                                shutil.copy(file_from, file_to)


        return {'FINISHED'}



