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
import ntpath
import os.path

from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from ..check_tools import is_file_in_data_folder, VolumesInstalled
from ...exaproduct import Exa
from ...utility.fc_utils import show_helps_v2
from ...utility.text_utils import wrap_text


class HDRIMAKER_OT_remove_volume(Operator):
    bl_idname = Exa.ops_name + "remove_volume"
    bl_label = "Remove Volumes"
    bl_options = {'INTERNAL'}

    confirm: EnumProperty(default='NO', items=(('NO', "No", ""), ('YES', "Yes", "")))
    volume_name: StringProperty()

    @classmethod
    def description(cls, context, properties):
        return "Remove selected volumes from the list"

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        col = box.column()
        row = col.row()
        row.alignment = 'CENTER'

        show_helps_v2(row, 'REMOVE_VOLUME')
        text = "Are you sure you want to remove selected volume?"
        text_2 = "All files in the library from this volume will be deleted!"
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="", icon='ERROR')
        row.label(text=text)
        row.label(text="", icon='ERROR')
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="", icon='ERROR')
        row.label(text=text_2)
        row.label(text="", icon='ERROR')

        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(self, 'confirm', expand=True)

        text = "Choose 'Yes' and press 'Ok' to remove the selected volumes. Or choose 'No' or pres 'Esc' to cancel this operation."
        wrap_text(col, text, text_length=(context.region.width / 6.5), center=True)

        col.separator()

    def invoke(self, context, event):
        self.confirm = 'NO'
        return context.window_manager.invoke_props_dialog(self, width=450)

    def execute(self, context):
        if self.confirm == 'NO':
            return {'CANCELLED'}

        # Open json file:
        from ...utility.json_functions import get_json_data
        from ...utility.utility import get_addon_preferences

        preferences = get_addon_preferences()
        addon_default_library = preferences.addon_default_library

        # Qui bisogna identificare il percorso della libreria, poichè potrebbe essere una espansione

        libraries_paths = [addon_default_library] + [item.path for item in preferences.expansion_filepaths if
                                                     os.path.isdir(item.path)]

        json_data = None
        for lib_path in libraries_paths:
            library_path = lib_path
            # Esaminiamo tutti gli eventuali percorsi per trovare qual'è quello dove si trova il volume
            volume_json_path = os.path.join(library_path, "._data", "._volumes_installed", self.volume_name)
            json_data = get_json_data(volume_json_path)
            if json_data:
                break

        if not json_data:
            self.report({'ERROR'}, "Error reading json file")
            return {'CANCELLED'}

        files_dict = json_data.get('files_dict')
        if not files_dict:
            self.report({'ERROR'}, "Error reading json file, no files_dict found")
            return {'CANCELLED'}

        for idx, value in files_dict.items():
            file_path = value.get('file_path')
            full_path = ntpath.normpath(os.path.join(library_path, file_path))
            if not os.path.isfile(full_path):
                continue
            if is_file_in_data_folder(file_path):
                # Se è rimasta solo la cartella "data" allora va cancellata, quindi bisogna procedere
                # Otteniamo il percorso alle prime 2 cartelle di file_path
                split = file_path.split(ntpath.normpath(os.sep))
                if len(split) > 2:
                    mat_folder = os.path.join(library_path, split[0], split[1])
                    # Controlliamo in mat_folder se ci sono piu di 1 cartella:
                    if len(os.listdir(mat_folder)) > 1:
                        # Se ci sono piu di 1 cartella allora non possiamo cancellare la cartella "data"
                        continue
            try:
                # Since the json file is present in the list of if I set it with the value -1
                # it is deleted along with the other files
                os.remove(full_path)
                # Check if the file folder is empty and remove it
                # Let's keep the "._volumes_installed" folder even if it could be empty
                if "._volume_installed" not in full_path:
                    folder_path = os.path.dirname(full_path)
                    # Qui controlliamo se c'è il file dell'asset browser, di solito finisce in ab.blend, se è rimasto
                    # solo quello allora va rimosso cosi da eliminare la cartella, potrebbe esserci anche un file json
                    # dalle librerie del server, quindi nel caso eliminare pure quello. Il json si chiama exa_files.json
                    # e anche se c'è un file con estensione .xtmp (Nel caso un download della versione precedente non
                    # è andato a buon fine) va eliminato pure quello
                    useless_files = [fn for fn in os.listdir(folder_path) if
                                     fn.endswith("ab.blend") or fn.endswith(".xtmp") or fn.endswith("exa_files.json")]
                    for file in useless_files:
                        try:
                            os.remove(os.path.join(folder_path, file))
                        except:
                            pass

                    if not os.listdir(folder_path):
                        os.rmdir(folder_path)

                    # Check if the material folder is empty and remove it
                    split = file_path.split(ntpath.normpath(os.sep))
                    from ...utility.utility import root_path_is_empty
                    if len(split) > 2:
                        mat_folder = os.path.join(library_path, split[0], split[1])
                        # Controlliamo in mat_folder se ci sono piu di 1 files:
                        if root_path_is_empty(mat_folder):
                            try:
                                os.rmdir(mat_folder)
                            except:
                                pass
                    # Check if category folder is empty and remove it
                    if len(split) > 1:
                        cat_folder = os.path.join(library_path, split[0])
                        # Controlliamo in cat_folder se ci sono piu di 1 files:
                        if root_path_is_empty(cat_folder):
                            try:
                                os.rmdir(cat_folder)
                            except:
                                pass

            except Exception as e:
                self.report({'ERROR'}, "Error removing file: {} ".format(full_path) + str(e))
                return {'CANCELLED'}

        if os.path.isfile(volume_json_path):
            try:
                os.remove(volume_json_path)
            except:
                pass


        VolumesInstalled.volumes_installed.clear()  # Importante, questo tiene traccia dei volumi installati.
        VolumesInstalled.online_json_data = None

        from ...utility.utility import redraw_all_areas
        redraw_all_areas()

        return {'FINISHED'}
