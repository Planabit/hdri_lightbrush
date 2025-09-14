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


class GlobalDict:
    k_size_refer = {}
    hdri_preview_collection = {}

class GlobalVar:
    percentuale = 0
    contextEngine = None

class InstallUtility(object):
    instal_index = 0

class LibraryUtility:

    last_default_lib_path = ""
    libraries_ready = False

    please_restart_blender = False


    first_message = {}

    emergency_message = None

    is_official_version = False

    installed_core = False
    online_json_lib_tot_bytes = 0
    online_total_materials = []
    online_total_files = 0

    user_json_lib_tot_bytes = 0
    user_total_materials = []
    user_total_files = 0
    update_ok = False

    show_need_update = True

    lib_percentage_bar = 0
    lib_object_installed = 0
    lib_object_online = 0

    lib_percentage_bar_byte = 0
    lib_object_installed_byte = 0
    lib_object_online_byte = 0

    in_modal_creation_structure = False
    creation_structure_current_percentage = 0
    creation_structure_total_percentage = 0

    in_modal_getalllibrary = False
    creation_getalllibrary_cur_page = 0
    creation_getalllibrary_total_page = 6

    json_paths = {}  # Qui rimangono memorizzate le info della libreria dal file Json, in maniera da non dover caricare piu volte il file Json

    exa_library_volumes = None  # Siccome il file json è grande, lo memorizziamo qui in memoria fino al prossimo riavvio di Blender cosi che l'accesso ai dati è piu veloce



