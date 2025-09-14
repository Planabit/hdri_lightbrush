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

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty, FloatProperty, CollectionProperty
from bpy.types import AddonPreferences, PropertyGroup

from .exapack_manager import HdriMakerExaPackToInstall
from .fc_draw_pref import draw_library_management, draw_first_installation, draw_updates_menu, draw_top_addons, \
    draw_helps_menu, draw_make_asset_browser_buttons
from ..exaproduct import get_addon_module_name, Exa
from ..library_manager.libraries_enum import StoreLibraries
from ..ui_interfaces.draw_functions import draw_options_menu, draw_progress_making_asset_browser, \
    draw_restart_blender, socials_buttons
from ..ui_interfaces.ui_v2.main_ui_v2 import Polling
from ..utility.fc_utils import show_helps_v2
from ..utility.text_utils import write_with_icons


def auto_save_preferences(self, context):
    bpy.ops.wm.save_userpref()



def update_expansion(self, context):
    StoreLibraries.libraries = []
    auto_save_preferences(self, context)


def tab_item(self, context):
    f_install = ('LIBRARY_INSTALL',
                 'Install',
                 "Use this menu to install the libraries",
                 'FILE_ARCHIVE',
                 0
                 )
    lib_manager = ('FOLDERS', "Libraries",
                   "Use this menu if you want to re-link existing libraries ora Add new",
                   'FILE_FOLDER', 1)

    options = ('OPTIONS', "Options", "Addon options", 'OPTIONS', 2)

    # helps = ('HELPS', "Helps", "Show Helps", 'QUESTION', 3)

    updates = ('UPDATES', "Updates", "Updates utility", 'FILE_REFRESH', 4)

    # if LibraryUtility.libraries_ready:
    #     tabs = (lib_manager, options, exa, updates)

    # top_addons = ('TOP_ADDONS', "Top Addons", "Top Addons", 'CHECKMARK', 5)

    tabs = (f_install, lib_manager, updates, options, )

    return tabs


class HDRiMakerUpdates(PropertyGroup):
    idx: IntProperty()
    version_button: BoolProperty()
    name: StringProperty()


class HdriMakerExpansionsPackPaths(PropertyGroup):
    name: StringProperty(default="Expansion name Here", update=update_expansion)
    path: StringProperty(subtype='FILE_PATH', update=update_expansion)


class HdriMakerBatchFileList(PropertyGroup):
    idx: IntProperty()
    name: StringProperty()
    world_name: StringProperty()
    filepath: StringProperty(subtype='FILE_PATH')
    filetype: StringProperty(default="")


day_range = []
day_range.append(('NEVER', "Never", "Never check for updates (not recommended)"))
for n in [1, 3, 7, 15, 30]:
    day_range.append((str(n), "Every " + str(n) + " Days", "Check for the update every " + str(n) + " days"))


class HdriMakerPreferences(AddonPreferences):

    bl_idname = get_addon_module_name()

    preferences_tabs: EnumProperty(update=auto_save_preferences,
                                   items=tab_item)

    # ------------------------------------------------------------------------------------------------------------------
    # Default Library

    addon_default_library: StringProperty(name="HDRI_MAKER_DEFAULT_LIB", subtype='DIR_PATH',
                                          description='You must choose the "HDRi_MAKER_LIB" folder you downloaded.')

    # ------------------------------------------------------------------------------------------------------------------
    # User Library

    addon_user_library: StringProperty(name="User Library", subtype='DIR_PATH',
                                       description="""If you had previously created a material library (With HDRi Maker), 
                                       enter the path If this is the first time you do it, you need to create a folder 
                                       in a path that you feel is appropriate (The folder must be new and empty) 
                                       and use it as a materials save folder.To the rest, HDRi Maker thinks of saving correctly""")

    # ------------------------------------------------------------------------------------------------------------------

    float_bar_0: FloatProperty(default=0.0, min=0, max=100, subtype='PERCENTAGE')
    float_bar_1: FloatProperty(default=0.0, min=0, max=100, subtype='PERCENTAGE')

    out_of_memory: BoolProperty(default=False,
                                description="This causes a message to be shown wherever you want, it must be assigned 0+ (GB), if the available disk memory is less than (Your choose)")
    need_update: BoolProperty(default=False, description="Show the Need update alert")
    update_urgency: BoolProperty(default=False, description="If true, need urgency the update")

    show_labels: BoolProperty(default=False, description="Show enum label in preview buttons",
                              update=auto_save_preferences)

    expansion_filepaths: CollectionProperty(name="Expansion filepath", type=HdriMakerExpansionsPackPaths)

    # _/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\

    icons_preview_size: FloatProperty(update=auto_save_preferences, min=0.5, max=2, default=1.5,
                                      description='Choose the previews icons dimension. Tips: Correct size = 1')
    icons_popup_size: FloatProperty(update=auto_save_preferences, min=0.5, max=2, default=1.5,
                                    description='Choose the popup icons dimension. Tips: Correct size = 1')
    show_labels: BoolProperty(default=False, description="Show enum label in preview buttons",
                              update=auto_save_preferences)

    # _/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\

    show_creator_utility: BoolProperty(default=False,
                                       description="Show in the Shader Editor, a panel for World Material and library creators. If you are not a material creator, please do not use this as it may damage the main library")

    from_batch_path: StringProperty(subtype='DIR_PATH')
    file_list_prop: CollectionProperty(name="Background List", type=HdriMakerBatchFileList)

    # Exapack:
    exapacks_install: CollectionProperty(name="Exapacks", type=HdriMakerExaPackToInstall)
    exapack_override_installer: BoolProperty(default=False,
                                             description="Override the files if the file exists into destination path "
                                                         "(Only if the the library already exists)")

    # Mantieni gli exapack sul disco (Richiede molta memoria disco, inutili una volta installati)
    # Translate:
    #
    keep_exapack_on_disk: BoolProperty(name="Keep Exapack on disk",
                                       default=False,
                                       description="Keep exapacks files on disk "
                                                   "(Requires a lot of disk memory, useless once installed)")

    debug: BoolProperty(default=False)

    show_addon_updates: BoolProperty(default=False, description="Show the addon updates")
    show_library_updates: BoolProperty(default=False, description="Show the library updates")

    updates_props: CollectionProperty(name="Updates", type=HDRiMakerUpdates)

    check_update_frequency_control: EnumProperty(items=day_range, default='NEVER', description="Check frequency updates",
                                                 update=auto_save_preferences)

    remind_me_later_update: IntProperty(default=0, description="Remind me later update")

    def draw(self, context):

        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="")
        write_with_icons(row, "HORIZONTAL", Exa.blender_manifest['name'], False, 1)
        if Polling.make_asset_browser_running:
            draw_progress_making_asset_browser(self, context, col)
            return

        draw_restart_blender(self, context, layout)

        show_helps_v2(row, docs_key='PREFERENCES_MENU')
        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text=str(Exa.blender_manifest['version']))

        col.separator()

        socials_buttons(col, text="Socials:", center=False)
        col.separator()

        row = col.row()
        row.scale_y = 2
        row.prop(self, "preferences_tabs", text='Choose', expand=True)

        if self.preferences_tabs == 'LIBRARY_INSTALL':
            draw_first_installation(self, context, col)

        if self.preferences_tabs == 'FOLDERS':
            draw_library_management(self, context, layout)
            draw_make_asset_browser_buttons(self, context, layout)

        if self.preferences_tabs == 'OPTIONS':
            draw_options_menu(self, context, layout)

        if self.preferences_tabs == 'UPDATES':
            draw_updates_menu(self, context, col)

        if self.preferences_tabs == 'HELPS':
            draw_helps_menu(self, context, col)

        if self.preferences_tabs == 'TOP_ADDONS':
            draw_top_addons(self, context, layout)
