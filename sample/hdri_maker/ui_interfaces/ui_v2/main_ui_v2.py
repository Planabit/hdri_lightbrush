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
import time

import bpy
from bpy.types import Panel

from ..draw_functions import library_missing, draw_add_remove_import, preview_menu, draw_background_menu, \
    draw_hdri_dome_menu, draw_light_studio, draw_save_menu, draw_shadow_catcher_menu, draw_volumetric_menu, \
    draw_sun_studio, draw_progress_making_asset_browser, draw_restart_blender, draw_alert_experimental_version, \
    draw_box_utility
from ...addon_preferences.fc_draw_pref import draw_unzip_installer
from ...convert_old_library_to_new.convert_functions import is_new_library, is_old_default_library, is_old_user_lib
from ...convert_old_library_to_new.convert_ops import ConvertLibraryUtils, HDRIMAKERT_OT_ConvertOldLibrary
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...installer_tools import HDRIMAKER_OT_install_exapacks
from ...library_manager.lib_ops import HDRIMAKER_OT_MakeAssetBrowser
from ...save_tools import HDRIMAKER_OT_BatchModal
from ...utility.text_utils import wrap_text
from ...utility.utility import get_addon_preferences, get_percentage, redraw_all_areas


def refresh_interface():
    """Call Polling and redraw all areas"""
    Polling.poll()
    redraw_all_areas()


class Polling:
    """Questa classe per ragioni di risparmio di risorse, attinge dal pannello Welcome, e memorizza lo stato della situazione in maniera
    che tutti i pannelli attingano a questo stato. Quindi il pannello welcome setta le proptietà di questa classe, e tutti gli altri ne attingono"""

    show_welcome_panel = False
    show_main_panels = False
    show_batch_save_panel = False
    show_batch_scene_panel = False
    library_missing = False
    is_new_default_lib = False
    is_new_user_lib = False
    volume_installed = False
    make_asset_browser_running = False

    @classmethod
    def poll(cls):

        preferences = get_addon_preferences()
        start = time.time()
        cls.is_new_default_lib = is_new_library(preferences.addon_default_library, get_library_type="DEFAULT")
        cls.is_new_user_lib = is_new_library(preferences.addon_user_library, get_library_type="USER")

        # Get one volumes:
        if not cls.volume_installed:
            # This should limit the use of resources to check if the volume is installed, if it exists, it only checks once
            path = os.path.join(preferences.addon_default_library, "._data", "._volumes_installed")
            if os.path.isdir(path):
                volume = next((file for file in os.listdir(path) if file.endswith(".json")), None)
                if volume:
                    cls.volume_installed = True

        if HDRIMAKER_OT_MakeAssetBrowser.is_running():
            cls.show_main_panels = False
            cls.show_welcome_panel = False
            cls.show_batch_save_panel = False
            cls.show_batch_scene_panel = False
            cls.library_missing = False
            cls.make_asset_browser_running = True

        elif HDRIMAKER_OT_BatchModal.is_running():
            cls.show_batch_save_panel = True
            cls.show_batch_scene_panel = False
            cls.show_main_panels = False
            cls.show_welcome_panel = False
            cls.library_missing = False
            cls.make_asset_browser_running = False


        elif HDRIMAKER_OT_install_exapacks.is_running() and not cls.volume_installed:
            cls.show_batch_save_panel = False
            cls.show_batch_scene_panel = False
            cls.show_main_panels = False
            cls.show_welcome_panel = True
            cls.library_missing = False
            cls.make_asset_browser_running = False

        elif cls.is_new_default_lib and cls.is_new_user_lib:
            cls.show_welcome_panel = False
            cls.show_main_panels = True
            cls.show_batch_save_panel = False
            cls.show_batch_scene_panel = False
            cls.library_missing = False
            cls.make_asset_browser_running = False

        elif not cls.is_new_default_lib or not cls.is_new_user_lib:
            cls.show_welcome_panel = True
            cls.show_main_panels = False
            cls.show_batch_save_panel = False
            cls.show_batch_scene_panel = False
            cls.library_missing = True
            cls.make_asset_browser_running = False

        elif [s for s in bpy.data.scenes if get_scnprop(s).scene_id_name == 'BATCH_SCENE']:
            cls.show_batch_scene_panel = True
            cls.show_batch_save_panel = False
            cls.show_main_panels = False
            cls.show_welcome_panel = False
            cls.library_missing = False
            cls.make_asset_browser_running = False

        elif not os.path.isdir(preferences.addon_default_library) or not os.path.isdir(preferences.addon_user_library):
            cls.show_main_panels = False
            cls.show_welcome_panel = True
            cls.show_batch_save_panel = False
            cls.show_batch_scene_panel = False
            cls.library_missing = True
            cls.make_asset_browser_running = False


class HDRIMAKER_PT_AdminPanel(Panel):
    bl_label = "HDRIMaker Admin Panel"
    bl_idname = "HDRIMAKER_PT_AdminPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        preferences = get_addon_preferences()
        return preferences.debug

    def draw(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)

        layout = self.layout
        col = layout.column(align=True)

        split = col.split()
        col_1 = split.column(align=True)
        col_1.label(text="ExaPack Prefix Name")
        col_1.prop(scnProp, 'exapack_prefix_name', text="")

        col_2 = split.column(align=True)
        col_2.label(text="Incremental Index")
        col_2.prop(scnProp, 'exapack_preindex', text="")

        col.separator()

        col.prop(scnProp, 'exapack_ignore_material_version', text="Ignore Material Version")

        col.separator()
        col.prop(scnProp, 'exapack_library_type', text="Library Type")
        col.separator()
        col.prop(scnProp, 'exapack_library_name', text="Library Name")

        col.separator()

        row = col.row()
        row.scale_y = 1.5
        row.operator(Exa.ops_name + "create_zip", text="Create ExaPack")

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.prop(scnProp, 'exapack_pause', text="ExaPack Pause")

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.prop(scnProp, 'exapack_terminate', text="ExaPack Terminate")

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.prop(scnProp, 'exapack_cores', text="Cores to use")

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        from ...installer_tools import HDRIMAKER_OT_CreateZipLibrary
        row.label(text="Cores active: " + str(HDRIMAKER_OT_CreateZipLibrary._threads_in_use))

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.operator(Exa.ops_name + "make_json_exacollection", text="Make JSON ExaCollection")

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.operator(Exa.ops_name + "generate_zips_json", text="Make JSON Zips register")

        col.separator()
        row = col.row()
        row.scale_y = 1.5
        row.operator(Exa.ops_name + "create_tag_and_mat_info", text="Create Tag and Mat Info into the addon folder")


class HDRIMAKER_PT_Welcome(Panel):
    bl_label = "Welcome To HDRi Maker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(self, context):
        """If the libraries are not linked, show the welcome panel"""
        Polling.poll()  # Chiamare solo da qui, tutto il resto dei pannelli farà riferimento alle proprietà di questa classe Polling
        return Polling.show_welcome_panel

    def draw(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        preferences = get_addon_preferences()

        layout = self.layout

        if HDRIMAKERT_OT_ConvertOldLibrary.is_running():
            layout.enabled = False
        col = layout.column(align=True)

        if HDRIMAKER_OT_install_exapacks.is_running():
            draw_unzip_installer(preferences, context, col)

        if Polling.library_missing:
            library_missing(self, context, col)

        if is_old_default_library(preferences.addon_default_library):
            col.separator()
            col.label(text="", icon='INFO')
            text = "The default library is not updated to the new version, please convert it to the new version using the button below"
            wrap_text(col, text, text_length=(context.region.width / 6.5), center=True)

            col.operator(Exa.ops_name + "convertoldlibrary",
                         text="Convert Default to new library",
                         icon='FOLDER_REDIRECT').options = 'DEFAULT'

            col.separator()
            choosepath = col.operator(Exa.ops_name + "choosepath",
                                      text="Destination: " + scnProp.convert_to_new_default_lib_path,
                                      icon='FILE_FOLDER')
            choosepath.options = 'CONVERT_DEFAULT_LIB_PATH'

        if is_old_user_lib(preferences.addon_user_library):
            col.separator()
            col.label(text="", icon='INFO')
            text = "The user library is not updated to the new version, please convert it to the new version using the button below"
            wrap_text(col, text, text_length=(context.region.width / 6.5), center=True)

            col.operator(Exa.ops_name + "convertoldlibrary",
                         text="Convert User Lib to new library",
                         icon='FOLDER_REDIRECT').options = 'USER'

            col.separator()
            choosepath = col.operator(Exa.ops_name + "choosepath",
                                      text="Destination: " + scnProp.convert_to_new_user_lib_path, icon='FILE_FOLDER')
            choosepath.options = 'CONVERT_USER_LIB_PATH'

        if HDRIMAKERT_OT_ConvertOldLibrary.is_running():
            CLU = ConvertLibraryUtils
            preferences.float_bar_0 = get_percentage(CLU.files_copied, CLU.total_files)

            row = col.row()
            row.alignment = 'CENTER'
            row.label(text=str(CLU.files_copied) + "/" + str(CLU.total_files))
            row = col.row()
            row.enabled = False
            row.prop(preferences, 'float_bar_0', text="", slider=True)


class HDRIMAKER_PT_BatchSave(Panel):
    """This panel is shown when the user is in the batch mode during the save of the Background List"""
    bl_label = "Batch Mode"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"

    @classmethod
    def poll(self, context):
        return Polling.show_batch_save_panel

    def draw(self, context):
        layout = self.layout
        preferences = get_addon_preferences()

        col = layout.column(align=True)
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="Percent Complete:")
        preferences.float_bar_0 = HDRIMAKER_OT_BatchModal.progress()
        col.label(text="Completed:")
        col.prop(preferences, 'float_bar_0', text="", emboss=True, slider=True)
        col.separator()
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="To cancel the process, keep pressing the ESC key")


class HDRIMAKER_PT_BatchScene(Panel):
    """This panel is shown when into the project is present the batch scene"""

    bl_label = "HDRi Maker Batch Scene"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return Polling.show_batch_scene_panel

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="A 'Batch scene' has been created")
        col.label(text="to save the previous background")
        col.label(text="for security reasons, remove it")
        col.label(text="manually by pressing this button:")
        row = layout.row(align=True)
        row.scale_y = 2
        removescene = row.operator(Exa.ops_name + "removescene", text="Remove Scene", icon='CANCEL')
        removescene.scene_id_name = 'BATCH_SCENE'


class HDRIMAKER_PT_MainPanel(Panel):
    bl_label = "HDRi Maker Studio"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"

    @classmethod
    def poll(cls, context):
        return Polling.show_main_panels

    def draw(self, context):
        layout = self.layout
        # draw_alert_experimental_version(self, context, layout)
        draw_restart_blender(self, context, layout)
        preview_menu(self, context, layout)
        draw_add_remove_import(self, context, layout)
        # draw_box_utility(self, context, layout)



class HDRIMAKER_PT_BackgroundMenu(Panel):
    bl_label = "World"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return Polling.show_main_panels

    def draw(self, context):
        layout = self.layout
        draw_background_menu(self, context, layout, hide_drop=True)


class HDRIMAKER_PT_DomeMenu(Panel):
    bl_label = "Dome"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return Polling.show_main_panels

    def draw(self, context):
        layout = self.layout
        draw_hdri_dome_menu(self, context, layout, hide_drop=True)


class HDRIMAKER_PT_Volumetric(Panel):
    bl_label = "Volumetric"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return Polling.show_main_panels

    def draw(self, context):
        layout = self.layout
        draw_volumetric_menu(self, context, layout, hide_drop=True)


class HDRIMAKER_PT_ShadowCatcher(Panel):
    bl_label = "Shadow Catcher"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return Polling.show_main_panels

    def draw(self, context):
        layout = self.layout
        draw_shadow_catcher_menu(self, context, layout)


class HDRIMAKER_PT_SaveMenu(Panel):
    bl_label = "Save"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return Polling.show_main_panels

    def draw(self, context):
        layout = self.layout
        draw_save_menu(self, context, layout, hide_drop=True)


class HDRIMAKER_PT_LightStudio(Panel):
    bl_label = "Lights"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return Polling.show_main_panels

    def draw(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)

        layout = self.layout
        col = layout.column(align=True)
        draw_light_studio(self, context, col)
        col.separator()
        draw_sun_studio(self, context, col)
        if bpy.app.version < (4, 2, 0):
            col.separator()
            row = col.row(align=True)
            row.label(text="Eevee Shadow Detail:")
            row.prop(scnProp, 'shadow_detail', text="")


class HDRIMAKER_PT_MakeAssetBrowser(Panel):
    bl_label = "Make Asset Browser"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(cls, context):
        return Polling.make_asset_browser_running

    def draw(self, context):
        layout = self.layout

        addon_preferences = get_addon_preferences()

        draw_progress_making_asset_browser(addon_preferences, context, layout)
