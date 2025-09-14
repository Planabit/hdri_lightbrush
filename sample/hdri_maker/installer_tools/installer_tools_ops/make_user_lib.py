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

from bpy.types import Operator

from ...exaproduct import Exa


class HDRIMAKER_OT_make_user_library(Operator):
    bl_idname = Exa.ops_name + "make_user_library"
    bl_label = "User Library"
    bl_description = "Create a user library"
    bl_options = {'INTERNAL'}

    @classmethod
    def description(cls, context, properties):
        return "Make The User Library Folder"

    def execute(self, context):

        from ...utility.utility import get_addon_preferences
        from ...convert_old_library_to_new.convert_functions import is_new_library

        addon_prefs = get_addon_preferences()

        if not os.path.isdir(addon_prefs.addon_default_library):
            text = "Default Library not found, please first create a default library, if you are not sure what to do," \
                   " check the documentation, use the question marks you find in the interface to access the detailed documentation"
            from ...utility.text_utils import draw_info
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        user_library_path = os.path.join(os.path.dirname(addon_prefs.addon_default_library), Exa.product.upper() + "_USER_LIB")

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

        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        refresh_interface()

        return {'FINISHED'}
