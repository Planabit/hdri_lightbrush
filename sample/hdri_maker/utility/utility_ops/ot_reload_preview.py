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
import shutil

from bpy.props import EnumProperty
from bpy.types import Operator


from ...exaproduct import Exa
from ...utility.text_utils import draw_info, wrap_text


def restore_icon_images(preview_files):
    for file in preview_files:
        if "_hdri_maker_patch" in file:
            # Controlliamo che nella stessa directory del file c'è un altro file con lo stesso nome ma senza "_hdri_maker_patch"
            # Se c'è, allora cancelliamo il file con "_hdri_maker_patch"
            if file.endswith(".png"):
                original_name = file.replace("_hdri_maker_patch.png", ".png")
            elif file.endswith(".jpg"):
                original_name = file.replace("_hdri_maker_patch.jpg", ".jpg")
            else:
                continue

            if os.path.isfile(original_name):
                os.remove(file)
            else:
                # Altrimenti rimuoviamo dal nome "_hdri_maker_patch.png"
                os.rename(file, original_name)

    number = 0
    for file in preview_files:
        original_name = file
        # Copy file to the same directory with a new name using shutil.copy()
        if file.endswith(".png"):
            temp_name = file.replace(".png", "_hdri_maker_patch.png")
        elif file.endswith(".jpg"):
            temp_name = file.replace(".jpg", "_hdri_maker_patch.jpg")
        else:
            continue

        shutil.copy(file, temp_name)
        os.remove(file)
        os.rename(temp_name, file)
        number += 1
        print(number, "Restored icon image: " + file)


class HDRIMAKER_OT_restore_all_icons_patch(Operator):

    bl_idname = Exa.ops_name + "restore_all_icons_patch"
    bl_label = "Previews Patch"
    bl_options = {'INTERNAL'}

    confirm: EnumProperty(default='NO', items=(('NO', "No", ""), ('YES', "Yes", "")))

    @classmethod
    def description(cls, context, properties):
        desc = "This operator solves the problem of previews that are not displayed correctly, do not run it if you have not encountered this problem"
        return desc

    def invoke(self, context, event):
        self.confirm = 'NO'
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        text = "This operator solves the problem of previews that are not displayed correctly, do not run it if you have not encountered this problem " \
               "This operation can take a few minutes"
        wrap_text(layout=col, string=text, enum=False, text_length=(context.region.width / 6.5), center=True,
                  icon="")
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(self, "confirm", expand=True)

    def execute(self, context):

        if self.confirm == 'NO':
            return {'CANCELLED'}

        from ...library_manager.get_library_utils import libraries_path
        from ...library_manager.main_pcoll import reload_main_previews_collection
        from ...utility.utility import get_addon_dir
        from ...icons.interfaceicons import register_custom_icons, unregister_custom_icons

        current_lib, risorse = libraries_path()


        if not os.path.isdir(current_lib):
            text = "This path does not exist: " + current_lib + " make sure to select the correct Library and try again"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)

            return {'CANCELLED'}

        # Check if into the

        preview_files = []
        for root, dirs, files in os.walk(current_lib):
            for file in files:
                if file.endswith(".png"):
                    # Check if the root contain the "previews" folder:
                    if "previews" in root:
                        preview_files.append(os.path.join(root, file))

        for cat in os.listdir(current_lib):
            cat_folder = os.path.join(current_lib, cat)
            # Qui potrebbero esserci files che non sono cartelle, quindi dobbiamo controllare, perchè se è una user library
            # nella vecchia versione venivano salvai i previews nella cartella della categoria
            if cat.endswith(".png") or cat.endswith(".jpg"):
                if os.path.isfile(cat_folder):
                    preview_files.append(cat_folder)
            if os.path.isdir(cat_folder):
                for mat in os.listdir(cat_folder):
                    mat_folder = os.path.join(cat_folder, mat)
                    if os.path.isdir(mat_folder):
                        preview_folder = os.path.join(mat_folder, 'data', 'previews', 'default')
                        if os.path.isdir(preview_folder):
                            for file in os.listdir(preview_folder):
                                if file.endswith(".png") or file.endswith(".jpg"):
                                    preview_files.append(os.path.join(preview_folder, file))

        # Aggiungiamo i file extreme_pbr\addon_resources\Shader Maker

        shader_maker = os.path.join(get_addon_dir(), "addon_resources", "Tools")
        if os.path.isdir(shader_maker):
            for root, dirs, files in os.walk(shader_maker):
                for file in files:
                    if file.endswith(".png"):
                        preview_files.append(os.path.join(root, file))

        # Siccome vedo che ci sono stati problemi anche con le icone Preview, inseriamo anche loro nella lista:

        icons_path = os.path.join(get_addon_dir(), "icons", "addon_icons")
        for root, dirs, files in os.walk(icons_path):
            for file in files:
                if file.endswith(".png") or file.endswith(".jpg"):
                    preview_files.append(os.path.join(root, file))

        empty_showreel_folder = os.path.join(get_addon_dir(), 'addon_resources', 'empty_showreel')
        if os.path.isdir(empty_showreel_folder):
            for file in os.listdir(empty_showreel_folder):
                if file.endswith(".png") or file.endswith(".jpg"):
                    preview_files.append(os.path.join(empty_showreel_folder, file))

        restore_icon_images(preview_files)
        reload_main_previews_collection()

        unregister_custom_icons()
        register_custom_icons()

        return {'FINISHED'}





