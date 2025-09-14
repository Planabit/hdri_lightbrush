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

import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator

from ..tools import get_library_info
from ...exaconv import get_imgprop, get_scnprop
from ...exaproduct import Exa
from ...library_manager.main_pcoll_attributes import set_winman_main_preview, get_winman_main_preview
from ...utility.utility import get_addon_preferences, screen_shading_type, wima


class HDRIMAKER_OT_MakeAssetBrowser(Operator):
    bl_idname = Exa.ops_name + "make_asset_browser"
    bl_label = "Make Asset Browser"
    bl_description = "Make a new asset browser"
    bl_options = {'REGISTER', 'UNDO'}

    library_path: StringProperty(subtype='DIR_PATH')

    confirm: EnumProperty(default='NO', description='Confirm the action',
                          items=(('YES', 'Yes', 'Confirm the action'), ('NO', 'No', 'Cancel the action')),
                          name='Confirm', options={'SKIP_SAVE'})

    libraries_selector: StringProperty(default='')

    asset_dict = {}

    abort = False
    finished = False
    asset_scene = None
    _handler = None

    current_asset = 0
    total_assets = 0

    lost_background_files = []

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    @classmethod
    def description(cls, context, properties):
        return "Make/Update a new asset browser"

    def invoke(self, context, event):
        self.asset_dict.clear()
        self.confirm = 'NO'
        self.finished = False
        cls = self.__class__
        cls.current_asset = 0
        cls.total_assets = 0
        cls.abort = False
        cls.lost_background_files.clear()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        addon_preferences = get_addon_preferences()
        from ...utility.text_utils import wrap_text

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        text = "此操作将在当前库中创建和/或更新新的资源浏览器 ( {} ) 并继续?".format(
            self.library_path)
        wrap_text(col, string=text, text_length=(context.region.width / 6.5), center=True)
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(self, "confirm", expand=True)
        col.separator()
        row = col.row(align=True)
        row.label(text="Press ESC to cancel", icon='CANCEL')
        col.separator()

    def remove_all(self, world):
        try:
            bpy.data.worlds.remove(world)
            for image in bpy.data.images:
                imgProp = get_imgprop(image)
                if imgProp.image_id_name:
                    bpy.data.images.remove(image)
        except:
            pass

        for library in bpy.data.libraries:
            bpy.data.libraries.remove(library)

        from ...ops_and_fcs.purge import purge_all
        purge_all()

    def end(self, context):
        if self.asset_scene:
            bpy.data.scenes.remove(self.asset_scene)
        bpy.ops.wm.save_userpref()
        cls = self.__class__
        cls._handler = None

        # Reload First icon and category:
        from ...library_manager.main_pcoll import reload_main_previews_collection
        from ...library_manager.main_pcoll import update_first_icon
        reload_main_previews_collection()

        scnProp = get_scnprop(context.scene)
        update_first_icon(scnProp, context)

        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        refresh_interface()

    def modal(self, context, event):
        cls = self.__class__

        if cls.abort:
            self.remove_all(context.scene.world)
            self.finished = True
            self.end(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':

            from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
            refresh_interface()
            # Check if self.asset_dict is empty:
            if not self.asset_dict:
                self.remove_all(context.scene.world)
                self.finished = True
                self.end(context)
                return {'FINISHED'}

            last_key = list(self.asset_dict.keys())[-1]
            cls.current_asset += 1
            cls._handler = self

            asset_dict_idx = self.asset_dict[last_key]

            a_s_scnProp = asset_dict_idx['a_s_scnProp']
            k_size = asset_dict_idx['k_size']
            total_idx = asset_dict_idx['total_idx']
            cat = asset_dict_idx['cat']
            preview_mat_name = asset_dict_idx['preview_mat_name']
            preview_name = asset_dict_idx['preview_name']
            library_name = asset_dict_idx['library_name']

            a_s_scnProp.libraries_selector = self.libraries_selector
            a_s_scnProp.up_category = cat[0]
            set_winman_main_preview(preview_name)
            # preview_mat_name = get_winman_main_preview()

            screen_shading_type(get_set='SET', shading_type='SOLID')
            a_s_scnProp.k_size = k_size[0]
            total_idx += 1
            bpy.ops.hdrimaker.addbackground(environment='COMPLETE',
                                            invoke_browser=True,
                                            is_from_asset_browser=False,
                                            make_relative_path=True,
                                            hide_info_popup=True)

            from ...asset_browser.asset_browser_utility import asset_browser_create_cat_file
            from ...library_manager.k_size_enum import k_size_compo_string
            if "_" + k_size[0] not in k_size_compo_string(minimum=1, maximum=18):
                mat_version = "Procedural"
            else:
                mat_version = k_size[0]

            catalog_name = "Unknown"
            if Exa.product == 'HDRI_MAKER':
                catalog_name = "HDRi Maker"
            if Exa.product == 'EXTREME_PBR':
                catalog_name = "Extreme PBR"

            if library_name == "DEFAULT":
                library_name = "Default Library"

            elif library_name == "USER":
                library_name = "User Library"

            compiled_cat = catalog_name + "/" + library_name + "/" + mat_version + "/" + cat[
                0] + ":" + catalog_name + "-" + library_name + "-" + mat_version + "-" + \
                           cat[0]
            catalog_id = asset_browser_create_cat_file(self.library_path, compiled_cat)

            # Now we have to mark as asset browser the scene.world:
            world = self.asset_scene.world

            if not world:
                # in questo caso (è capitato a un utente) la cartella del k_size non conteneva files per creare il world
                # Quindi in questo caso nessun world è stato aggiunto alla scena, quindi non c'è nulla da fare
                # Bisogna bypassare questo asset e passare al prossimo
                del self.asset_dict[last_key]
                self.remove_all(world)
                from ...utility.classes_utils import LibraryUtility
                from ...background_tools import HDRIMAKER_OT_AddBackground
                LibraryUtility.please_restart_blender = True
                lost_files = HDRIMAKER_OT_AddBackground._lost_files_from_exapack
                if lost_files:
                    cls.lost_background_files.append(lost_files)
                return {'PASS_THROUGH'}

            world.asset_mark()
            asset_data = world.asset_data
            asset_data.catalog_id = catalog_id

            preview_folder_path = os.path.join(self.library_path, a_s_scnProp.up_category, preview_mat_name, "data",
                                               "previews", "default")
            preview_file = None
            for fn in os.listdir(preview_folder_path):
                if fn.endswith(".png"):
                    preview_file = os.path.join(preview_folder_path, fn)
                    break

            from ...asset_browser.asset_browser_utility import asset_browser_assign_custom_preview
            asset_browser_assign_custom_preview(world, preview_file)

            # Get the tag.json and read the tags and add it into the asset browser tags:
            tags_path = os.path.join(self.library_path, a_s_scnProp.up_category, preview_mat_name, "data",
                                     "tags.json")

            from ...utility.json_functions import get_json_data
            if os.path.isfile(tags_path):
                json_data = get_json_data(tags_path)
                tags = json_data.get("tags")
                if tags:
                    for tag in tags:
                        if tag not in asset_data.tags[:]:
                            asset_data.tags.new(tag)

            mat_info_file = os.path.join(self.library_path, a_s_scnProp.up_category, preview_mat_name, "data", "mat_info.json")

            if os.path.isfile(mat_info_file):
                mat_info = get_json_data(mat_info_file)
                if mat_info:
                    material_info = mat_info.get("material_info")
                    if material_info:
                        author = material_info["author"] if material_info.get("author") else ""
                        license = material_info["license"] if material_info.get("license") else ""
                        license_description = material_info["license_description"] if material_info.get(
                            "license_description") else ""
                        if hasattr(asset_data, "author"):
                            asset_data.author = author
                        if hasattr(asset_data, "description"):
                            asset_data.description = license_description
                        if hasattr(asset_data, "license"):
                            asset_data.license = license

            # Now we have to save the file.blend at the right place:

            # Attenzione, qui bisogna rendere relativi i percorsi delle immagini, altrimenti l'utente non potrà usare l'Asset!
            # Quindi lo farà l'operatore che aggiunge gli sfondi, solo tramite un'opzione assegnabile INTERNAL

            write_path = os.path.join(self.library_path, a_s_scnProp.up_category, preview_mat_name, k_size[0],
                                      preview_name + "_hdr_mkr_ab.blend")
            data_blocks = {self.asset_scene, world}
            bpy.data.libraries.write(write_path, data_blocks)

            # Remove asset_dict_idx from the list:
            del self.asset_dict[last_key]

            self.remove_all(world)

            from ...utility.classes_utils import LibraryUtility
            LibraryUtility.please_restart_blender = True

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Questa operazione va assolutamente eseguita in un file blender nuovo e non salvato

        from ...library_manager.categories_enum import MatDict
        from ...library_manager.main_pcoll import enum_material_previews
        from ...library_manager.k_size_enum import enum_k_size

        cls = self.__class__
        cls.lost_background_files.clear()

        from ...exaconv import get_scnprop
        scn = context.scene
        scnProp = get_scnprop(scn)

        if self.confirm == 'NO':
            self.report({'INFO'}, "Operation cancelled")
            return {'FINISHED'}

        # Controlliamo che la Default Library sia della versione 3.0 in su e sia ok:
        # Per questioni di sicurezza e per non rovinare il progetto all'utente, l'operazione deve essere effettuata in un progetto blender non salvato.
        # Se è già un file di
        if bpy.data.is_saved:
            # if not "hdri_maker_save_asset_browser.blend" in bpy.data.filepath:
            from ...utility.text_utils import draw_info
            text = "Please run this operation in a new Blender project that has not been saved yet."
            self.report({'INFO'}, text)
            draw_info(text, "info", 'INFO')
            return {'FINISHED'}

        if len(bpy.data.objects) > 5 or len(bpy.data.materials) > 5 or len(bpy.data.worlds) > 5:
            text = "To avoid altering your project, I invite you to use a new and unsaved Blender project and try again"
            self.report({'INFO'}, text)
            from ...utility.text_utils import draw_info
            draw_info(text, "Info", "INFO")
            return {'FINISHED'}

        for wrld in bpy.data.worlds:
            self.remove_all(wrld)

        from ...utility.utility import get_addon_preferences
        addon_preferences = get_addon_preferences()
        from ...convert_old_library_to_new.convert_functions import is_new_library
        default_lib_ok = is_new_library(addon_preferences.addon_default_library, get_library_type="DEFAULT")
        if not default_lib_ok:
            self.report({'ERROR'}, "Default Library is not ok, make sure it is a version 3.0 or higher library")
            return {'FINISHED'}

        # self.library_path = current_lib()

        # Bisogna settare la libreria sulla default:

        # Create a fake scene:
        self.asset_scene = bpy.data.scenes.new("HDRIMAKER_AssetBrowser")
        self.asset_scene.use_nodes = True
        a_s_scnProp = get_scnprop(self.asset_scene)

        context.window.scene = self.asset_scene

        library_name = "Unknow"
        library_info = get_library_info(self.library_path)
        if library_info:
            library_name = library_info.get("library_name")

        # --------------------------------------------------------------------------------------------------------------
        # Check asset exists:

        asset_libraries = bpy.context.preferences.filepaths.asset_libraries
        # Check if filepath is already in the list:
        asset_is_linked = False
        for lib in asset_libraries:
            if lib.path == self.library_path:
                asset_is_linked = True
                break

        asset_dict = {}

        a_s_scnProp.libraries_selector = self.libraries_selector

        # Iterate over the categories:
        total_idx = -1
        for cat in MatDict.mats_categories["categories"]:
            if cat[0].lower() in ['empty...', 'tools']:
                continue

            a_s_scnProp.up_category = cat[0]
            # Iterate over the materials into the category:
            preview_image_list = [(N, idx) for (N, n, d, id_n, idx) in enum_material_previews(self, context)]
            for preview_name, idx in preview_image_list:
                set_winman_main_preview(preview_name)
                preview_mat_name = get_winman_main_preview()
                # Now we have to iterate over the material version:
                for k_size in enum_k_size(self, context):
                    if cat[0] in ['Empty Collection...', '']:
                        continue
                    total_idx += 1
                    self.asset_dict[total_idx] = {"a_s_scnProp": a_s_scnProp,
                                                  "k_size": k_size,
                                                  "total_idx": total_idx,
                                                  "cat": cat,
                                                  "preview_mat_name": preview_mat_name,
                                                  "preview_name": preview_name,
                                                  "library_name": library_name}

        # Check if self.asset_dict is empty:
        if not self.asset_dict:
            from ...utility.text_utils import draw_info
            text = "The chosen library to create the asset browser seems to be empty, empty libraries cannot be available for the asset browser."
            draw_info(text, "info", 'INFO')
            self.report({'INFO'}, text)
            return {'FINISHED'}

        # --------------------------------------------------------------------------------------------------------------

        if not asset_is_linked:
            try:
                # Le versioni precedenti di Blender non hanno il parametro check_existing:
                bpy.ops.preferences.asset_library_add(directory=self.library_path, check_existing=True)
            except:
                bpy.ops.preferences.asset_library_add(directory=self.library_path)

            for lib in asset_libraries:
                path = lib.path
                if path == self.library_path:
                    lib.name = "HDRi Maker " + library_name.title()

        from ...asset_browser.asset_functions import write_version_into_library_info
        write_version_into_library_info(self.library_path)

        # --------------------------------------------------------------------------------------------------------------

        cls = self.__class__
        cls.total_assets = len(self.asset_dict)
        self._timer = wima().event_timer_add(0.01, window=context.window)
        wima().modal_handler_add(self)
        return {'RUNNING_MODAL'}


class HDRIMAKER_OT_MakeAssetBrowserAbort(Operator):
    bl_idname = Exa.ops_name + "make_asset_browser_abort"
    bl_label = "Abort"
    bl_description = "Abort the process"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cls = HDRIMAKER_OT_MakeAssetBrowser
        cls.abort = True

        # Nel caso in cui si sia inceppato il meccanismo di HDRIMAKER_OT_MakeAssetBrowser, questo riporta l'interfaccia
        # utente, allo stato iniziale:

        cls._handler = None
        from ...ui_interfaces.ui_v2.main_ui_v2 import Polling
        Polling.make_asset_browser_running = False
        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        refresh_interface()

        return {'FINISHED'}

