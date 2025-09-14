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

from ..exaproduct import Exa
from ..icons.interfaceicons import get_icon
from ..installer_tools.check_tools import get_volumes_installed, VolumesInstalled
from ..installer_tools.installer_tools_ops.install_zip_library import UnzipLibrary, HDRIMAKER_OT_install_exapacks
from ..utility.fc_utils import show_helps_v2
from ..utility.json_functions import get_json_data
from ..utility.text_utils import wrap_text
from ..utility.utility import get_percentage, DotsRunning, natural_sort_v2, get_version_to_int


# def draw_default_user_lib(self, context, layout):
#     print("Versione draw_default_user_lib 1")
#
#     col = layout.column(align=True)
#     col.label(text='Enter the path to the Default Library (' + get_default_library_folder_name() + ')')
#
#     if self.addon_default_library and os.path.isdir(self.addon_default_library):
#         default_lib_text = self.addon_default_library
#         default_lib_exist = True
#     else:
#         default_lib_text = "Choose the path"
#         default_lib_exist = False
#
#
#
#     row = col.row(align=True)
#     row.operator(Exa.ops_name + "choosepath", text=default_lib_text,
#                  icon='FILE_FOLDER').options = 'LINK_DEFAULT_LIB'
#     if default_lib_exist:
#         row.operator(Exa.ops_name + "resetlibpath", text="", icon='UNLINKED').options = 'RESET_DEFAULT_LIB_PATH'
#     col.label(text='Enter the path of the User Library (' + get_user_library_folder_name() + ')')
#
#     if self.addon_user_library and os.path.isdir(self.addon_user_library):
#         user_lib_text = self.addon_user_library
#         user_lib_exist = True
#     else:
#         user_lib_text = "Choose The Path"
#         user_lib_exist = False
#
#     row = col.row(align=True)
#     row.operator(Exa.ops_name + "choosepath", text=user_lib_text,
#                  icon='FILE_FOLDER').options = 'LINK_USER_LIB'
#     if user_lib_exist:
#         row.operator(Exa.ops_name + "resetlibpath", text="", icon='UNLINKED').options = 'RESET_USER_LIB_PATH'
#


def draw_make_asset_browser_buttons(self, context, layout):
    from ..ui_interfaces.ui_v2.main_ui_v2 import Polling
    if Polling.library_missing:
        return

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    left_row = row.row(align=True)
    left_row.alignment = 'LEFT'
    left_row.label(text="Make Asset Browser:")

    right_row = row.row(align=True)
    right_row.alignment = 'RIGHT'
    show_helps_v2(right_row, docs_key='MAKE_ASSET_BROWSER', icon='QUESTION', emboss=False, text="")

    col.separator()

    row = col.row(align=False)
    if os.path.isdir(self.addon_default_library):
        ab = row.operator(Exa.ops_name + "make_asset_browser", text="Default Library", icon='ASSET_MANAGER')
        ab.library_path = self.addon_default_library
        ab.libraries_selector = 'DEFAULT'
    if os.path.isdir(self.addon_user_library):
        ab = row.operator(Exa.ops_name + "make_asset_browser", text="User Library", icon='ASSET_MANAGER')
        ab.library_path = self.addon_user_library
        ab.libraries_selector = 'USER'

    for lib in self.expansion_filepaths:
        if os.path.isdir(lib.path):
            ab = row.operator(Exa.ops_name + "make_asset_browser", text="Expansion " + lib.name, icon='ASSET_MANAGER')
            ab.library_path = lib.path
            ab.libraries_selector = lib.path


def draw_library_management(self, context, layout):
    from ..ui_interfaces.draw_functions import draw_default_user_lib

    col = layout.column(align=True)
    row = col.row(align=True)
    row.alignment = 'RIGHT'
    show_helps_v2(row, docs_key='UI_LIBRARY_MANAGER', emboss=True)

    draw_default_user_lib(self, context, col)

    col.separator()
    col = col.column()
    col.label(text="Add more library expansions:")
    row = col.row()
    row.label(text="Name")
    row.label(text="Expansion Path")
    for idx, i in enumerate(self.expansion_filepaths):
        row = col.row(align=False)
        row.alert = os.path.isdir(i.path) is False

        split = row.split(factor=0.24)
        split.prop(i, "name", text="")
        row = split.row()
        row.scale_x = 1
        text = i.path if os.path.isdir(i.path) else "Choose Path"
        pathBox = row.box()
        pathBox.scale_y = 0.5
        choosepath = pathBox.operator(Exa.ops_name + "choosepath", text=text, emboss=False)
        choosepath.options = "ADD_EXPANSION_PATH"
        choosepath.index = idx
        # row.prop(i, "path", text="")
        row = row.row()
        remove = row.operator(Exa.ops_name + "expansionpack", text="", icon='CANCEL')
        remove.options = 'REMOVE'
        remove.idx = idx
        col.separator()

    col.operator(Exa.ops_name + "expansionpack", text="Add library", icon='PLUS').options = 'ADD'


def draw_first_installation(self, context, layout):
    unzip_running = HDRIMAKER_OT_install_exapacks.is_running()

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.alignment = 'CENTER'
    row.label(text="Welcome to HDRi Maker Library Installation")
    col.separator()
    row = col.row(align=True)
    row.alignment = 'CENTER'
    show_helps_v2(row, docs_key='INSTALL_LIBRARIES', text="How to install libraries", emboss=True)

    col.separator()

    UNZIP = UnzipLibrary

    if unzip_running:
        draw_unzip_installer(self, context, col)
        col.separator()
        draw_exapack_to_install(self, context, col)
        return

    # if not Polling.is_new_default_lib or not Polling.is_new_user_lib:

    if True:

        text = "If this is the first time you run HDRi Maker, please choose the path of the default library where the addon will look for HDRi library files."
        wrap_text(layout=col, string=text, enum=False, text_length=(context.region.width / 6),
                  center=True)

        col.separator()
        # LU = LibraryUtility
        if self.addon_default_library:
            text = "Default Library: " + self.addon_default_library  # + "\\HDRI_MAKER_DEFAULT_LIB"
        else:
            text = "Default Library:"

        row = col.row(align=True)
        if not os.path.isdir(self.addon_default_library):
            row.alert = True

        choosepath = row.operator(Exa.ops_name + "choosepath", text=text, icon='FILE_FOLDER')
        choosepath.options = "LINK_DEFAULT_LIB"
        if self.addon_default_library != "":
            row.operator(Exa.ops_name + "resetlibpath", text="", icon='UNLINKED').options = 'RESET_DEFAULT_LIB_PATH'

        col.separator()

        if self.addon_user_library:
            text = "User Library: " + self.addon_user_library  # + "\\HDRI_MAKER_USER_LIB"
        else:
            text = "User Library:"

        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="If you have never used HDRi Maker, do not indicate the User library path")

        row = col.row(align=True)
        # if not os.path.isdir(self.addon_user_library):
        #     row.alert = True

        choosepath = row.operator(Exa.ops_name + "choosepath", text=text, icon='FILE_FOLDER')
        choosepath.options = "LINK_USER_LIB"
        if self.addon_user_library != "":
            row.operator(Exa.ops_name + "resetlibpath", text="", icon='UNLINKED').options = 'RESET_USER_LIB_PATH'

        col.separator()

    if os.path.isdir(self.addon_default_library):
        col.separator()

        text = """If you have already downloaded the library Volume files (Those with the '.exapack' extension), """ \
               """press the button below and indicate the path where the .exapack files are locate. If you don't have the """ \
               """library files, go to your Order page and download them."""

        wrap_text(layout=col, string=text, enum=False, text_length=(context.region.width / 6), center=True)

        col.separator()

        if UNZIP.finished:
            row = col.row(align=True)
            row.alignment = 'CENTER'
            row.label(text=str(UNZIP.files_copied) + " of " + str(UNZIP.total_files) + " files")
            if UnzipLibrary.volume_file_errors:
                col.separator()
                text = "Some files were not extracted from the volumes marked with the exclamation point, try to press the " \
                       "button 'Install From Exapack Files' below a short additional step will be executed to force the " \
                       "extraction of the files. If the problem persists with that volume, try to download it again from" \
                       " your download page."
                wrap_text(layout=col, string=text, enum=False, text_length=(context.region.width / 6), center=True)

                col.separator()

            row = col.row(align=True)
            row.alignment = 'CENTER'
            row.operator(Exa.ops_name + "finish_confirm", text="Installation finished",
                         icon_value=get_icon("mark_check"))

        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.5
        choose_exapacks = row.operator(Exa.ops_name + "choose_exapacks", text="Choose Exapacks", icon='IMPORT')
        choose_exapacks.options = 'OPEN_BROWSER'

        col.separator()

        installation_ready = draw_exapack_to_install(self, context, col)
        if installation_ready:
            row = col.row(align=True)
            row.prop(self, "exapack_override_installer", text="Override existing files")
            row.prop(self, "keep_exapack_on_disk", text="Keep exapack after install")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 2
            row.operator(Exa.ops_name + "install_exapacks", text="Install from 'exapack' Files", icon='FILE_TICK')


def draw_unzip_installer(self, context, layout):
    UNZIP = UnzipLibrary
    self.float_bar_0 = get_percentage(UNZIP.files_copied, UNZIP.total_files)
    self.float_bar_1 = get_percentage(UNZIP.unpacked_files, UNZIP.packed_files)
    col = layout.column(align=True)
    col.separator()

    if UNZIP.prepare_is_running:
        # La funzione sta analizzando i file da installare:
        row = col.row(align=True)
        row.alignment = 'CENTER'
        DR = DotsRunning(refresh_time=1)
        dots = DR.dots()
        row.label(text=dots + " I'm analyzing the files to install: " + str(UNZIP.total_files) + " files " + dots)
        col.separator()
        row = col.row(align=True)
        row.operator(Exa.ops_name + "abort_zip_install", text="Cancel installation", icon='CANCEL')
        return

    # row = col.row(align=True)
    # row.alignment = 'CENTER'
    # row.label(text="Installing files from pack: " + UNZIP.volume_name)
    # row = col.row(align=True)
    # row.label(text="")
    # row.prop(self, "float_bar_1", text="")
    # row.label(text="")

    col.separator()
    row = col.row(align=True)
    row.alignment = 'CENTER'
    row.label(text="Do not close this window during installation (You can minimize)")

    col.separator()

    row = col.row(align=True)
    row.alignment = 'CENTER'
    DR = DotsRunning(refresh_time=1)
    dots = DR.dots()
    row.label(text=dots + " " + str(UNZIP.files_copied) + " of " + str(UNZIP.total_files) + " files " + dots)
    row = col.row(align=True)
    row.scale_y = 1.5
    row.prop(self, "float_bar_0", text="")
    row.operator(Exa.ops_name + "abort_zip_install", text="", icon='CANCEL')
    row = col.row(align=True)
    row.alignment = 'CENTER'
    # Translate:
    text = "If you want to stop the installation you can press the 'Cancel' (x) button next to the bar above, " \
           "you can resume the installation later. The process will resume from where you stopped it."

    wrap_text(layout=col, string=text, enum=False, text_length=(context.region.width / 6), center=True)


def draw_exapack_to_install(self, context, layout):
    if not self.exapacks_install[:]:
        return

    unzip_running = HDRIMAKER_OT_install_exapacks.is_running()

    box = layout.box()
    col = box.column(align=True)

    VI = VolumesInstalled(recompile=True)
    volume_installed = VI.get()

    # Get if almost 1 file is_good_file
    installation_ready = None
    for idx, exapack in enumerate(self.exapacks_install):
        exapack_error = False
        if UnzipLibrary.volume_file_errors:
            # In questo caso, la funzione di estrazione ha riportato un errore in un file o piu, durante l'estrazione di esso
            # Verrà segnalato nell'interfaccia e il file .exapack non verrà rimosso
            # Controlliamo tra le chiavi se il volume_name è questo exapack.volume_name
            if exapack.volume_name in UnzipLibrary.volume_file_errors.keys():
                exapack_error = True

        zeros = "0" * (3 - len(str(idx)))
        recompiled_idx = zeros + str(idx)

        if exapack.is_good_zip:
            installation_ready = True
            split = col.split(align=True, factor=0.4)
            split.label(text=recompiled_idx + " - " + exapack.name.replace(".exapack", ""),
                        icon='FILE_ARCHIVE')


        elif exapack.is_wrong_product:
            row = col.row(align=True)
            row.alert = True
            al_col = row.column(align=True)
            al_col.label(text=recompiled_idx + " - " + exapack.name.replace(".exapack",
                                                                            "") + " (Wrong product) " + exapack.product,
                         icon='LIBRARY_DATA_BROKEN')
            al_col.label(text="This '.exapack' file is from a different product than EXTREMEPBR, please remove it.")
            choose_exapacks = row.operator(Exa.ops_name + "choose_exapacks", text="", icon='REMOVE')
            choose_exapacks.options = "REMOVE"
            choose_exapacks.idx = idx
            continue

        else:
            row = col.row(align=True)
            row.alert = True
            text = recompiled_idx + " - " + "This file ( {} ) may be corrupted, it may have happened because of the incomplete download, try to download this file again," \
                                            " before proceeding with the installation I advise you to download the file again, make sure the download is complete.".format(
                exapack.name)
            sub_col = row.column(align=True)
            wrap_text(layout=sub_col, string=text, enum=False, text_length=(context.region.width * .2), center=True,
                      icon='LIBRARY_DATA_BROKEN')
            row.label(text="")

            choose_exapacks = row.operator(Exa.ops_name + "choose_exapacks", text="", icon='REMOVE')
            choose_exapacks.options = "REMOVE"
            choose_exapacks.idx = idx
            continue

        exapack_is_installed = None
        if volume_installed:
            if exapack.volume_name in volume_installed:
                exapack_is_installed = True

        if UnzipLibrary.volume_name == exapack.volume_name:
            exapack.float_bar_percentage = get_percentage(UnzipLibrary.unpacked_files, UnzipLibrary.packed_files)
        elif exapack_is_installed:
            exapack.float_bar_percentage = 100
        row = split.row(align=True)
        row.separator()
        in_row = row.row(align=False)
        in_row.enabled = False
        in_row.prop(exapack, "float_bar_percentage", text="", slider=True)
        row.separator()

        if exapack_error:
            row.label(text="_Problem_", icon_value=get_icon("danger"))
            if unzip_running:
                row.label(text="Wait for the extraction to finish")
            else:
                row.label(text="Press install to retry")

        elif exapack_is_installed:
            row.label(text="Installed", icon_value=get_icon("mark_check"))
        else:
            row.label(text="_________", icon='DOT')

        if unzip_running:
            row.label(text="")
        else:
            choose_exapacks = row.operator(Exa.ops_name + "choose_exapacks", text="", icon='REMOVE')
            choose_exapacks.options = "REMOVE"
            choose_exapacks.idx = idx

        # if exapack_error:
        #     # Segnaliamo l'errore:
        #     s_col = col.column(align=True)
        #     text = "An error during installation. Try again, if the problem persists, download and replace this {}.exapack ".format(exapack.volume_name)
        #     s_col.label(text=text)

    return installation_ready


def draw_online_exapacks(self, context, layout, installed_volumes=None, exa_library_volumes=None):

    col = layout.column(align=True)

    if not exa_library_volumes:
        col.label(text="Press Check library updates!", icon='INFO')
        return

    if not exa_library_volumes:
        return

    exapacks = exa_library_volumes.get("exapacks")
    if not exapacks:
        return

    keys = natural_sort_v2(exapacks.keys())
    exapacks = {key: exapacks[key] for key in keys}

    col.separator()
    split = col.split(align=True, factor=0.5)
    index_name_col = split.column(align=True)
    box = index_name_col.box()
    box.label(text="Exapack available", icon='NETWORK_DRIVE')
    checkmark_col = split.column(align=True)
    box = checkmark_col.box()
    box.label(text="Status", icon='IMPORT')
    uninstall_col = split.column(align=True)
    box = uninstall_col.box()
    box.label(text="Uninstall")

    for idx, (name, values) in enumerate(exapacks.items()):
        sIdx = str(idx)
        zeros = "0" * (3 - len(sIdx))
        sIdx = zeros + sIdx
        # split = col.split()
        # row = col.row(align=True)
        # row.alignment = 'LEFT'
        box = index_name_col.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        row.label(text=sIdx + " -")
        row.label(text=name)
        if name in installed_volumes:
            box = checkmark_col.box()
            box.label(text="Installed", icon_value=get_icon("mark_check"))
            box = uninstall_col.box()
            box.operator(Exa.ops_name + "remove_volume", text="Remove", icon='CANCEL').volume_name = name + ".json"
        else:
            box = checkmark_col.box()
            box.label(text="Not Installed", icon_value=get_icon("mark_x"))
            box = uninstall_col.box()
            box.label(text="")




def draw_updates_menu(self, context, layout):
    col = layout.column(align=True)
    col.separator()
    box = col.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.prop(self, 'show_addon_updates', text="Addon Updates",
             icon='DOWNARROW_HLT' if self.show_addon_updates else 'RIGHTARROW', emboss=False)
    if self.need_update:
        row.label(text="New version available", icon='INFO')
    else:
        row.label(text="")
    show_helps_v2(row, docs_key="ADDON_UPDATES")
    if self.show_addon_updates:
        col.separator()
        draw_addon_updates(self, context, col)

    layout.separator()
    # Section Installed:
    box = layout.box()
    col = box.column(align=True)

    # # In order to show an alert if there are updates available we need to len the list of exapacks installed and len the list of exapacks available online
    show_lib_update_alert = False
    from ..library_manager.get_library_utils import risorse_lib
    online_json_path = os.path.join(risorse_lib(), 'online_utility', "exa_library_volumes.json")
    installed_json_path = os.path.join(self.addon_default_library, '._data', "._volumes_installed")
    # DEVO ANCHE SOMMARE LE EVENTUALI ESPANSIONI!:

    VI = VolumesInstalled(recompile=False)
    installed_volumes = VI.get()
    online_json_data = VI.get_online_json_data()

    if os.path.exists(online_json_path) and os.path.isdir(installed_json_path):
        # Len the list of files into installed_json_path folder

        from ..utility.json_functions import get_json_data
        # online_json_data = get_json_data(online_json_path)
        if online_json_data:
            volume_quantity = online_json_data.get("volume_quantity")
            if volume_quantity:
                if volume_quantity > len(installed_volumes):
                    show_lib_update_alert = True

    row = col.row(align=True)
    row.prop(self, 'show_library_updates', text="Library Updates",
             icon='DOWNARROW_HLT' if self.show_library_updates else 'RIGHTARROW', emboss=False)
    if show_lib_update_alert:
        row.label(text="New libraries available!", icon='INFO')
    else:
        row.label(text="")
    show_helps_v2(row, docs_key='LIBRARY_UPDATE')

    if self.show_library_updates:
        col.separator()
        row = col.row(align=True)

        row.operator(Exa.ops_name + "get_library_updates", text="Check library updates", icon='FILE_REFRESH')
        row.operator(Exa.ops_name + "try_compile_exapack", text="Try compile Exapack", icon='FILE_REFRESH')
        # row.operator(Exa.ops_name + "reload_exapacks_list", text="Update Lists", icon='FILE_REFRESH')

        col.separator()
        # split = col.split(align=True, factor=0.5)
        draw_online_exapacks(self, context, col, installed_volumes=installed_volumes, exa_library_volumes=online_json_data)



def draw_installed_volumes(self, context, layout):
    col = layout.column(align=True)
    volumes = get_volumes_installed()
    if not volumes:
        col.label(text="No volumes installed")

    row = col.row(align=True)
    row.alignment = 'CENTER'
    row.label(text="Installed Packs:", icon='FILE_ARCHIVE')
    col.separator()

    # Sorting volumes
    volumes = natural_sort_v2(volumes)

    for idx, v in enumerate(volumes):
        sIdx = str(idx)
        zeros = "0" * (3 - len(sIdx))
        sIdx = zeros + sIdx

        split = col.split(align=True, factor=0.9)
        row = split.row(align=True)
        row.alignment = 'LEFT'
        row.label(text=sIdx + " -")
        row.label(text=v)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.operator(Exa.ops_name + "remove_volume", text="", icon='CANCEL').volume_name = v + ".json"


def draw_addon_updates(self, context, layout):
    from ..library_manager.get_library_utils import risorse_lib
    from ..utility.json_functions import get_json_data

    col = layout.column(align=True)
    row = col.row(align=True)
    row.alignment = 'CENTER'
    row.scale_y = 1.5
    row.operator(Exa.ops_name + "check_for_updates", text="Check addon updates", icon='FILE_REFRESH')

    json_path = os.path.join(risorse_lib(), 'online_utility', "exa_orderpages.json")
    if os.path.isfile(json_path):

        json_data = get_json_data(json_path)
        if json_data:
            orderpages = json_data.get("orderpages")
            if orderpages:
                wrap_text(col, "Go to your orderpage:", False, 80, True, None)
                row = col.row(align=True)
                for key, value in orderpages.items():
                    if key.lower() == 'blendermarket':
                        wb = row.operator(Exa.ops_name + "open_web_browser", text=key.title(),
                                          icon_value=get_icon('blender_market_logo'))
                    elif key.lower() == 'gumroad':
                        wb = row.operator(Exa.ops_name + "open_web_browser", text=key.title(),
                                          icon_value=get_icon('gumroad_logo'))
                    else:
                        wb = row.operator(Exa.ops_name + "open_web_browser", text=key.title())
                    wb.options = 'OPEN_URL'
                    wb.url = value

    json_path = os.path.join(risorse_lib(), 'online_utility', "exa_update.json")
    if not os.path.isfile(json_path):
        return

    json_data = get_json_data(json_path)
    if not json_data:
        return

    updates = json_data.get("updates")
    if not updates:
        return

    from ..web_tools.webservice import get_lost_updates_list
    lost_update_list = get_lost_updates_list(updates)
    len_lost_updates = len(lost_update_list)

    if len(lost_update_list) == 0:
        if 'beta' in Exa.blender_manifest['release'].lower() or 'alpha' in Exa.blender_manifest['release'].lower():
            text = "You are using a test version ( {} )".format(Exa.blender_manifest['release'])
            col.label(text=text)
        else:
            col.label(text="Your version " + Exa.blender_manifest['name'] + " " + Exa.blender_manifest['edition'] + " " + str(
                Exa.blender_manifest['version']) + " is correctly updated")
            col.label(text="This is great, remember to always keep the addon updated")

    else:
        col.separator()
        heather_box = col.box()
        heather_col = heather_box.column()
        text = "Your version " + Exa.blender_manifest['name'] + " " + Exa.blender_manifest['edition'] + " " + str(
            Exa.blender_manifest['version']) + " needs to be updated"
        wrap_text(heather_col, text, None, 80, True, None)

        text = "You missed these " + str(len_lost_updates) + " updates:"
        wrap_text(heather_col, text, None, 80, True, None)

        text = "Click on the Expand Arrows below to see what has been done in the released versions"
        wrap_text(heather_col, text, None, 100, True, None)

    col.separator()
    row = col.row(align=True)
    row.alignment = 'LEFT'
    row.label(text="Updates List:")
    col.separator()
    current_version_int = get_version_to_int(Exa.blender_manifest['version'])
    for idx, (update_key, update_data) in enumerate(updates.items()):
        # Check if the current version of the addon is the current update_key:
        dict_version_int = get_version_to_int(update_key)

        update_item = next((p for p in self.updates_props if p.idx == idx), None)
        if not update_item:
            break

        s_box = col.box()
        s_col = s_box.column(align=True)
        row = s_col.row(align=True)
        row.prop(update_item, 'version_button', text="Update " + update_item.name,
                 icon='DOWNARROW_HLT' if update_item.version_button else 'RIGHTARROW_THIN', emboss=False)

        if dict_version_int == current_version_int:
            row.label(text="< -- You are Here")
            row.label(text="", icon_value=get_icon('mark_check'))
        elif dict_version_int > current_version_int:
            row.label(text="Lost update")
            row.label(text="", icon='ERROR')
        else:
            row.label(text="")
            row.label(text="", icon='CHECKMARK')

        if not update_item.version_button:
            continue

        # if return_version_to_int(update_key) > get_version_to_int(Exa.blender_manifest.get("version")):
        open_url = update_data.get("url")
        if open_url:
            row = s_col.row()
            row.scale_y = 2
            wb = row.operator(Exa.ops_name + "open_web_browser", text="Check out what's new",
                              icon_value=get_icon('newspaper'))
            wb.options = 'OPEN_URL'
            wb.url = open_url

        # box = s_col.box()

        if not update_item:
            continue

        update_row = s_col.row(align=True)

        for update_info_key, update_info_value in update_data.items():

            if update_info_key == "date":
                date = update_info_value
                update_row.label(text="Date: " + date, icon='TIME')
            elif update_info_key == "name":
                name = update_info_value
                update_row.label(text="Name: " + name)
            elif update_info_key == "edition":
                edition = update_info_value
                update_row.label(text="Edition: " + edition)

        descriptions = update_data.get("descriptions")

        if descriptions:
            for idx, (description_key, description_value) in enumerate(descriptions.items()):
                descriptions_box = s_col.box()
                descriptions_col = descriptions_box.column(align=True)
                title = description_value.get("title")
                description = description_value.get("description")
                row = descriptions_col.row()
                if title:
                    row.label(text=title, icon='DOT')
                if description:
                    wrap_text(descriptions_col, description, None, int(context.region.width * .15), False, "")


def draw_top_addons(self, context, layout):
    """Draw the top addons"""
    status = True

    layout = self.layout
    col = layout.column(align=True)

    from ..library_manager.get_library_utils import risorse_lib

    json_file = os.path.join(risorse_lib(), 'online_utility', "exa_top_addons.json")
    if not os.path.isfile(json_file):
        status = False

    json_data = get_json_data(json_file)

    if not json_data:
        status = False

    if status is False:
        # In the case the json file is not found or is not valid, draw a button to try to download it again
        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.operator(Exa.ops_name + "topaddonsrefresh", text="Update the list", icon='FILE_REFRESH')
        return

    # La prima serie di keys sono i tipi di prodotto (Addon, Asset, etc)
    for product_type, product_data in json_data.items():
        if product_type == 'info':
            continue

        col.label(text=product_type, icon='PACKAGE')
        # Adesso dobbiamo fare un box che è quello delle categorie di prodotto (Material, Mesh, Simulation, etc)
        for product_category, product_category_data in product_data.items():
            p_c_box = col.box()
            p_c_col = p_c_box.column(align=True)
            p_c_col.label(text=product_category, icon='PACKAGE')
            # Adesso disegniamo i bottoni per i vari prodotti, i bottoni devono essere massimo cinque per row
            for product_name, product_url in product_category_data.items():
                row = p_c_col.row(align=True)
                wb = row.operator(Exa.ops_name + "open_web_browser", text=product_name, icon='URL')
                wb.options = 'OPEN_URL'
                if "blendermarket" in product_url:
                    wb.url = product_url + "&from=hdri-maker-top-addons"
                else:
                    wb.url = product_url

    info = json_data.get('info')
    if not info:
        return

    mail = info.get('mail_to')

    if not mail:
        mail = "extremeaddons@gmail.com"

    sponsor_purpose = "Do you have a good product and you want to be in the list? Contact me!"
    wrap_text(col, sponsor_purpose, text_length=(context.region.width * .5), center=True)

    # Metti a capo il testo con il rientro
    body = "Hello Andrew, I'm interested in your sponsorship program. I would like to know more about it %0D%0A"
    # Insert Blank line:
    body += "%0D%0A"
    body += "%0D%0A"
    body += "My Name is: %0D%0A"
    body += "%0D%0A"
    body += "%0D%0A"
    body += "My product(s): %0D%0A"
    body += "%0D%0A"
    body += "%0D%0A"
    body += "I sell my product on this url: %0D%0A"
    body += "%0D%0A"
    body += "%0D%0A"
    body += "Here a brief description of what I do: %0D%0A"
    body += "%0D%0A"
    body += "%0D%0A"
    body += "%0D%0A"

    mailto = col.operator(Exa.ops_name + "sendmail", text="Contact me", icon='URL')
    mailto.email = mail
    mailto.subject = "I'm interested in a sponsor in HDRi Maker"
    mailto.message = body


def draw_helps_menu(self, context, layout):
    layout = self.layout.column(align=True)
    # Bug Box:
    box = layout.box()
    col = box.column(align=True)
    col.label(text="Documentation & Tutorials", icon='DOCUMENTS')
    col.separator()
    split = col.split(factor=0.4)
    col = split.column(align=True)
    show_helps_v2(col, text="Documentation", docs_key='DOCS', emboss=True)
    show_helps_v2(col, text="Tutorial Playlist", docs_key='TUTORIAL_PLAYLIST', emboss=True)

    layout.separator()

    box = layout.box()
    col = box.column(align=True)
    col.label(text="Bug Report", icon='INFO')
    col.separator()
    split = col.split(factor=0.4)
    col = split.column(align=True)
    show_helps_v2(col, text="How to report a bug?", docs_key="HOW_TO_REPORT_A_BUG", emboss=True)

    col.separator()
    col.operator(Exa.ops_name + "bug_report", text="Report a bug", icon='URL')
    col.operator(Exa.ops_name + "copy_info_to_clipboard", text="System to clipboard", icon='COPYDOWN')
    col.separator()

    layout.separator()

    box = layout.box()
    col = box.column(align=True)
    col.label(text="Support", icon='INFO')
    col.separator()
    split = col.split(factor=0.4)
    col = split.column(align=True)
    show_helps_v2(col, text="FAQs", docs_key="FAQS", emboss=True)
    col.separator()
    show_helps_v2(col, text="Troubleshooting", docs_key="TROUBLESHOOTING", emboss=True)
