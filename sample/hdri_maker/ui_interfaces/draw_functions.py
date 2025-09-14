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

import bpy

from .draw_update_utility import update_icons_message
from ..background_tools import HDRIMAKER_OT_sync_node_background_rotation
from ..background_tools.background_fc import get_nodes_dict
from ..dictionaries.dictionaries import get_annotations
from ..dome_tools.dome_fc import get_dome_objects, get_sun_objects
from ..exaconv import get_ngprop, get_ndprop, get_sckprop, get_scnprop, get_default_library_folder_name, \
    get_user_library_folder_name, get_objprop, get_matprop, get_wrlprop
from ..exaproduct import Exa
from ..icons.interfaceicons import get_icon
from ..library_manager.get_library_utils import current_lib
from ..library_manager.k_size_enum import get_k_size_list
from ..library_manager.main_pcoll_attributes import wm_main_preview, get_winman_main_preview
from ..library_manager.tools import is_import_tools, is_assemble_studio
from ..light_studio.light_studio_fc import get_light_studio_objects
from ..shadow_catcher.shadow_catcher_fc import get_shadow_catcher_objects
from ..utility.classes_utils import LibraryUtility
from ..utility.dictionaries import socket_forbidden
from ..utility.enum_blender_native import get_blender_icons
from ..utility.fc_utils import show_helps_v2
from ..utility.json_functions import save_json
from ..utility.text_utils import write_with_icons, wrap_text
from ..utility.utility import get_in_out_group, get_addon_preferences, wima, \
    panel_node_draw, get_node_and_out_standard, SocketColor, has_nodetree, get_percentage, image_has_data, \
    is_hidden_object
from ..utility.utility_4 import get_ng_inputs


def draw_restart_blender(self, context, layout):
    if LibraryUtility.please_restart_blender:
        col = layout.column(align=True)
        col.separator()
        text = "Please restart Blender to make the asset browser library effective"
        wrap_text(col, string=text, text_length=(context.region.width / 6.5), center=True)

        class_name = self.__class__.__name__
        if class_name != "HdriMakerPreferences":
            # This message is only shown in preferences
            return

        from ..library_manager.lib_ops import HDRIMAKER_OT_MakeAssetBrowser
        lost_files = HDRIMAKER_OT_MakeAssetBrowser.lost_background_files
        if lost_files:
            col.separator()
            row = col.row()
            row.label(text="Some files seem to be missing, here is the list:")
            show_helps_v2(layout=row, text="Check why", docs_key='MISSING_FILES_ASSET_BROWSER_CREATION', emboss=True)
            col.separator()

            for idx, lost_dict in enumerate(lost_files):
                preview_name = lost_dict.get('preview_name')
                category = lost_dict.get('category')
                k_size = lost_dict.get('k_size')
                exapack = lost_dict.get('exapack')
                if preview_name and k_size and exapack:
                    text = f"Background name: {preview_name} - Version: {k_size} - From: {exapack}.exapack"
                    col.label(text=text)

            if len(lost_files) > 0:
                col.separator()
                col.label(text="Try to reinstall the exapack indicated above")

        return True


def draw_progress_making_asset_browser(self, context, layout):
    col = layout.column(align=True)
    col.separator()
    col.label(text="Making/updating the asset browser:")

    from ..library_manager.lib_ops import HDRIMAKER_OT_MakeAssetBrowser
    current = HDRIMAKER_OT_MakeAssetBrowser.current_asset
    total = HDRIMAKER_OT_MakeAssetBrowser.total_assets

    self.float_bar_0 = get_percentage(current, total)
    row = col.row(align=True)
    row.prop(self, 'float_bar_0', text="", slider=True)
    row.operator(Exa.ops_name + "make_asset_browser_abort", text="", icon='CANCEL')
    col.label(text="Press the button (x) to cancel")
    col.separator()
    col.label(text="Please do not close this window during the process")





def preview_menu(self, context, layout):
    scnProp = get_scnprop(context.scene)
    addon_prefs = get_addon_preferences()
    preview_mat_name = get_winman_main_preview()

    col = layout.column(align=True)

    update_icons_message(col, addon_prefs, open_preferences=True)

    split = col.split(factor=0.25, align=True)
    col_1 = split.column()
    col_1.operator(Exa.ops_name + "open_preferences", text="Helps",
                   icon_value=get_icon('extreme_addons_32')).options = 'HELPS'
    col_1.operator(Exa.ops_name + "searchcategories", text="Category:")

    col_2 = split.column()
    row = col_2.row(align=True)
    row.prop(scnProp, 'libraries_selector', text="")
    show_helps_v2(row, docs_key='MAIN_PANEL')
    row = col_2.row(align=True)
    row.prop(scnProp, 'up_category', text="")

    row.label(text="", icon_value=get_icon('transparent'))
    # cabtae = row.operator(Exa.ops_name + "convert_asset_browser_to_addon_expansion", text="", icon='ERROR')
    # cabtae.folder_path = scnProp.up_category
    #
    # cls = HDRIMAKER_OT_convert_asset_browser_to_addon_expansion
    # if cls.is_running():
    #     col.separator()
    #     DR = DotsRunning(refresh_time=1)
    #     dots = DR.dots()
    #     row = col.row(align=True)
    #     row.alignment = 'CENTER'
    #     row.label(text=dots + "Try to convert" + dots)
    #     row = col.row(align=True)
    #     row.alignment = 'CENTER'
    #     row.label(text="Search for asset: {}".format(cls.enum_blend_files))
    #
    #     if cls.total_todo > 0:
    #         col.separator()
    #         row = col.row(align=True)
    #         row.alignment = 'CENTER'
    #         row.label(text="Convert progress: {}/{}".format(str(cls.total_done), str(cls.total_todo)))

    # row.label(text="", icon_value=get_icon('transparent'))

    col.separator()
    # col.operator(Exa.ops_name+"scrollmaterial", text="", icon_value=get_icon('up')).options = 'UP'
    col.operator(Exa.ops_name + "scrollmaterial", text="", icon='TRIA_UP_BAR').options = 'UP'
    col.separator()
    row = col.row(align=True)
    left_row = row.row(align=True)
    left_row.scale_y = addon_prefs.icons_preview_size * 6
    # left_row.operator(Exa.ops_name+"scrollmaterial", text="", icon_value=get_icon('left')).options = 'LEFT'
    left_row.operator(Exa.ops_name + "scrollmaterial", text="", icon='TRIA_LEFT_BAR').options = 'LEFT'
    previewRow = row.row(align=True)
    previewRow.scale_y = addon_prefs.icons_preview_size
    if self.bl_space_type == 'VIEW_3D':
        mat_preview_size = addon_prefs.icons_popup_size * 5
    else:
        mat_preview_size = 3

    previewRow.template_icon_view(wima(), wm_main_preview(), scale_popup=mat_preview_size,
                                  show_labels=True if addon_prefs.show_labels else False)
    right_row = row.row(align=True)
    right_row.scale_y = addon_prefs.icons_preview_size * 6
    # right_row.operator(Exa.ops_name+"scrollmaterial", text="",
    #                    icon_value=get_icon('right')).options = 'RIGHT'
    right_row.operator(Exa.ops_name + "scrollmaterial", text="",
                       icon='TRIA_RIGHT_BAR').options = 'RIGHT'
    col.separator()
    # col.operator(Exa.ops_name+"scrollmaterial", text="", icon_value=get_icon('down')).options = 'DOWN'
    split = col.split(factor=0, align=True)

    sp_col_1 = split.column(align=True)
    sp_col_1.operator(Exa.ops_name + "open_preferences", text="", icon='OPTIONS').options = 'OPTIONS'

    sp_col_3 = split.column(align=True)
    sp_col_3.operator(Exa.ops_name + "scrollmaterial", text="", icon='TRIA_DOWN_BAR').options = 'DOWN'

    sp_col_3 = split.column(align=True)
    sp_col_3.operator(Exa.ops_name + "reloadpreviewicons", text="", icon='LOOP_BACK')

    box = col.box()
    colBox = box.column(align=True)
    if scnProp.tag_search.isspace() or scnProp.tag_search == "":
        depresStat = False
    else:
        depresStat = True

    row = colBox.row()
    row.prop(scnProp, 'menu_tag_search', text="", icon_value=get_icon('tag'))

    # if preview_mat_name != "Empty...":
    row.emboss = 'PULLDOWN_MENU'
    row.operator(Exa.ops_name + "searchmaterials", text=preview_mat_name, icon='VIEWZOOM')

    mat_info_path = os.path.join(current_lib(), scnProp.up_category, preview_mat_name, "data", "mat_info.json")
    tags_path = os.path.join(current_lib(), scnProp.up_category, preview_mat_name, "data", "tags.json")

    if os.path.isfile(mat_info_path) or os.path.isfile(tags_path):
        icon = 'INFO' if os.path.isfile(tags_path) else 'EVENT_I'
        op = row.operator(Exa.ops_name + "infotagpanelops", text="", icon=icon)
        op.options = 'SHOW_JSON_MAT_INFO'
        op.info_path = mat_info_path
        op.tags_path = tags_path
    elif not os.path.isfile(tags_path):
        # Se non esiste il json dei tags, lo crea al volo
        data_path = os.path.dirname(tags_path)
        if os.path.isdir(data_path):
            if os.path.basename(data_path) == "data":
                save_json(tags_path, {"tags": []})

    if scnProp.libraries_selector == 'USER':
        if scnProp.up_category != 'Empty Collection...':
            if get_winman_main_preview() != "Empty...":
                row.operator(Exa.ops_name + "redrawpreview", text="", icon='RENDER_STILL')

    # else:
    #     row.label(text="", icon='NONE')
    # row.operator(Exa.ops_name+"reloadpreviewicons", text="", icon='LOOP_BACK')

    if scnProp.menu_tag_search:
        write_with_icons(colBox, "HORIZONTAL", "Search Tag", False, 1.2)
        colBox.prop(scnProp, 'tag_search', text="Search")
        colBox.prop(scnProp, 'tag_exclusion', text="Exclude")
        colBox.separator()

    # The user's choice only appears if there are more than 1k resolution of k maps
    # In any case, by default, the first map will always be, so no problem
    # This only happens on the default library, because the User is based on .blend files

    # if scnProp.libraries_selector != 'USER':
    k_size_list = get_k_size_list()
    len_k_size = len(k_size_list['list'])
    if scnProp.k_size not in ['', 'NONE'] and len_k_size > 1:
        row = colBox.row()
        # row.enabled = False if ProgressBarProp.show_progress_bar else True
        row.prop(scnProp, 'k_size', expand=True)


def draw_background_menu(self, context, layout, hide_drop=False):
    scn = context.scene
    scnProp = scn.hdri_prop_scn

    id_data_string = "bpy.data.worlds"

    col = layout.column(align=True)

    if not hide_drop:
        col.prop(scnProp, 'menu_environment', text='Background',
                 icon_value=get_icon('Menu open' if scnProp.menu_environment else 'Menu close'))

        if not scnProp.menu_environment:
            return

    world = scn.world
    if not world or not world.use_nodes:
        box = col.box()
        col = box.column(align=True)
        text = "Add a World to control properties from this menu"
        wrap_text(col, string=text, text_length=(context.region.width / 6.5), center=True)
        return

    if world.library:
        text = "To make the world editable, press the button below"
        wrap_text(col, string=text, text_length=(context.region.width * .15), center=True)
        col.operator(Exa.ops_name + "make_local", text="Make Local", icon='LINKED')

    # wrlProp = scn.world.hdri_prop_world
    # if not wrlProp.world_hdri_maker_version and wrlProp.world_id_name:
    #     draw_old_background_menu(self, context, col)
    #     return

    node_tree = world.node_tree

    from_node, output = get_node_and_out_standard(node_tree)
    if not output:
        col.label(text="Problem with the World node tree nodes", icon='ERROR')
        col.separator()
        col.operator(Exa.ops_name + "solvenodesproblem", text="Try to fix",
                     icon='FILE_REFRESH').options = 'SOLVE_WORLD_NODES_PROBLEM'
        return

    if not [i for i in output.inputs if i.is_linked]:
        col.label(text="No nodes connected to the output node")
        return

    nodes = node_tree.nodes
    nodes_dict = get_nodes_dict(node_tree)
    mixer = nodes_dict.get('MIXER')
    complete = nodes_dict.get('COMPLETE')
    diffuse = nodes_dict.get('DIFFUSE')
    light = nodes_dict.get('LIGHT')
    vectors = nodes_dict.get('VECTORS')

    environment_col = None
    if mixer or complete or diffuse or light or vectors:
        environment_box = layout.box()
        environment_col = environment_box.column(align=True)

    # if not mixer:
    if complete:
        title_row = environment_col.row(align=True)
        light_ops = title_row.operator(Exa.ops_name + "addremovegroups", text="Diffuse", icon='ADD')
        light_ops.options = 'ADD'
        light_ops.node_task = 'DIFFUSE'
        light_ops.invoke_browser = True if is_import_tools() else False
        light_ops.is_from_asset_browser = False

        # center_row = title_row.row()
        # center_row.alignment = 'CENTER'
        # center_row.label(text=" ", icon='NODETREE')
        light_ops = title_row.operator(Exa.ops_name + "addremovegroups", text="Light", icon='ADD')
        light_ops.options = 'ADD'
        light_ops.node_task = 'LIGHT'
        light_ops.invoke_browser = True if is_import_tools() else False
        light_ops.is_from_asset_browser = False
        environment_col.separator()
        draw_panel_sliders_group(world, environment_col, complete,
                                 id_data_string=id_data_string, show_tooltip=True, show_hide_option=False,
                                 show_reset_value=True, show_node_label=True, docs_url_key="COMPLETE_GROUP_BACKGROUND")

    # diffuse = light = None
    # if nodes_dict.get('MIXER'):
    #     diffuse, light = get_diffuse_and_light_nodes(nodes_dict['MIXER'])

    if diffuse or light:
        col = environment_col.column(align=True)
        row = col.row(align=True)

        if diffuse:
            del_diffuse_ops = row.operator(Exa.ops_name + "addremovegroups", text="", icon='REMOVE')
            del_diffuse_ops.options = 'REMOVE'
            del_diffuse_ops.node_task = 'DIFFUSE'
            del_diffuse_ops.invoke_browser = False
            del_diffuse_ops.is_from_asset_browser = False

            ops = row.operator(Exa.ops_name + "addremovegroups", text="Diffuse", icon='DOWNARROW_HLT')
            ops.node_task = 'DIFFUSE'
            ops.invoke_browser = True if is_import_tools() else False
            ops.is_from_asset_browser = False

        if light:
            row.operator(Exa.ops_name + "flipdiffuselight", text="", icon='ARROW_LEFTRIGHT')

            ops = row.operator(Exa.ops_name + "addremovegroups", text="Light", icon='DOWNARROW_HLT')
            ops.node_task = 'LIGHT'
            ops.invoke_browser = True if is_import_tools() else False
            ops.is_from_asset_browser = False

            del_diffuse_ops = row.operator(Exa.ops_name + "addremovegroups", text="", icon='REMOVE')
            del_diffuse_ops.options = 'REMOVE'
            del_diffuse_ops.node_task = 'LIGHT'
            del_diffuse_ops.invoke_browser = False
            del_diffuse_ops.is_from_asset_browser = False

        if mixer:
            mixer_ngprop = get_ngprop(mixer.node_tree)
            if mixer_ngprop.mixer_type in ['',
                                           'LIGHT_MIXER']:  # '' è perchè 'LIGHT_MIXER' è stato aggiunto dopo prima l'attributo non esisteva
                environment_col.separator()
                wrlProp = get_wrlprop(world)
                environment_col.prop(wrlProp, 'light_path', text="Light Path")
            else:
                inputs_unlinked = [i for i in mixer.inputs if not i.is_linked]
                environment_col.separator()
                draw_panel_sliders_group(world, environment_col, mixer,
                                         id_data_string=id_data_string, show_tooltip=True, show_reset_value=True,
                                         show_node_label=True, docs_url_key="Z_MIXER",
                                         show_hide_option=len(inputs_unlinked) > 0)

        environment_split = environment_col.split(align=True)
        if diffuse:
            col_1 = environment_split.column(align=True)
            col_1.separator()
            # col_1.label(text=diffuse.label, icon='NODETREE')
            draw_panel_sliders_group(world, col_1, diffuse,
                                     id_data_string=id_data_string, show_tooltip=True, show_reset_value=True,
                                     show_node_label=True, docs_url_key="DIFFUSE_GROUP_BACKGROUND")
            from_node = next((i.links[0].from_node for i in diffuse.inputs if i.type == 'RGBA' if i.is_linked),
                             None)
            if from_node:
                col_1.separator()
                draw_panel_sliders_group(world, col_1, from_node,
                                         id_data_string=id_data_string, show_tooltip=True, show_reset_value=True,
                                         show_node_label=True)

        if light:
            col_2 = environment_split.column(align=True)
            col_2.separator()
            # col_2.label(text=light.label, icon='NODETREE')
            draw_panel_sliders_group(world, col_2, light, id_data_string=id_data_string, show_tooltip=True,
                                     show_reset_value=True, show_node_label=True, docs_url_key="LIGHT_GROUP_BACKGROUND")

            from_node = next((i.links[0].from_node for i in light.inputs if i.type == 'RGBA' if i.is_linked), None)
            if from_node:
                col_2.separator()
                draw_panel_sliders_group(world, col_2, from_node, id_data_string=id_data_string, show_tooltip=True,
                                         show_reset_value=True, show_node_label=True)

    if vectors:
        environment_col.separator()
        draw_panel_sliders_group(world, environment_col, nodes_dict['VECTORS'], id_data_string=id_data_string,
                                 show_tooltip=True, show_reset_value=True, show_node_label=True,
                                 docs_url_key='VECTOR_GROUP_BACKGROUND',
                                 show_sync_angle=True,
                                 show_hide_option=True)

    if not diffuse and not light and not complete:
        default_box = layout.box()
        default_col = default_box.column(align=True)
        # Here we want to add 'LIGHT' and 'DIFFUSE' nodes, the user can choose which one to add
        title_row = default_col.row(align=True)
        light_ops = title_row.operator(Exa.ops_name + "addremovegroups", text="", icon='ADD')
        light_ops.options = 'ADD'
        light_ops.node_task = 'DIFFUSE'
        light_ops.invoke_browser = True if is_import_tools() else False
        light_ops.is_from_asset_browser = False

        center_row = title_row.row()
        center_row.alignment = 'CENTER'
        center_row.label(text="Default", icon='NODETREE')
        light_ops = title_row.operator(Exa.ops_name + "addremovegroups", text="", icon='ADD')
        light_ops.options = 'ADD'
        light_ops.node_task = 'LIGHT'
        light_ops.invoke_browser = True if is_import_tools() else False
        light_ops.is_from_asset_browser = False

        default_col.separator()
        panel_node_draw(default_col, world, 'Surface')
        row = default_col.row(align=True)
        row.prop(scn.render, 'film_transparent', text="Transparent Background")
        sr_row = row.row()
        sr_row.alignment = 'RIGHT'
        docs_url_key = "CONVERT_WORLD_TO_HDRI_MAKER_WORLD"
        show_helps_v2(sr_row, docs_key=docs_url_key, icon='QUESTION', emboss=False)

        # Qui mettiamo un bottone per convertire il world attuale in un HDRi Maker World, per permettere il controllo tramite interfaccia
        # Funzionerà solo se nel world è presente una immagine HDR/EXR
        default_col.separator()
        default_col.operator(Exa.ops_name + "convert_world", text="Try to convert", icon='WORLD')

    if environment_col:
        environment_col.prop(scn.render, 'film_transparent', text="Transparent Background")

    layout.operator(Exa.ops_name + "solvenodesproblem", text="Solve Nodes Problem",
                    icon='NODETREE').options = 'SOLVE_WORLD_NODES_PROBLEM'


def draw_hooks_menu(self, context, layout):
    scn = context.scene
    scnProp = get_scnprop(scn)

    dome_objects_dict = get_dome_objects()
    hooks = dome_objects_dict.get('DOME_HOOK')
    dome_handler = dome_objects_dict.get('DOME_HANDLER')

    col = layout.column(align=True)

    hooks_box = col.box()
    hooks_col = hooks_box.column(align=True)
    row = hooks_col.row(align=True)
    row.label(text="", icon='HOOK')
    row.prop(scnProp, 'show_hooks_menu', text="Hooks",
             icon='DOWNARROW_HLT' if scnProp.show_hooks_menu else 'RIGHTARROW', emboss=False)
    row.label(text="", icon='NONE')
    show_helps_v2(row, docs_key='DOME_PROJECTION_HOOKS')

    if scnProp.show_hooks_menu:
        hooks_col.separator()
        domehooks_row = hooks_col.row(align=True)
        domehooks_row.operator(Exa.ops_name + "domehooks", text="Add Hooks", icon='ADD').options = 'ADD'

        if hooks:
            domehooks_row.operator(Exa.ops_name + "domehooks", text="Remove Hooks", icon='REMOVE').options = 'REMOVE'
            hooks_col.separator()
            row = hooks_col.row(align=True)
            row.prop(scnProp, 'hide_hooks', text="Hide Hooks")

            hooks_col.prop(scnProp, 'hooks_display_size', text="Hooks Size")
            hooks_col.prop(get_objprop(dome_handler), 'expand_hooks', text="Expand Hooks")
            hooks_col.separator()
            hooks_col.prop(scnProp, 'hooks_display_type', text="Hooks Type")


def draw_sun_studio(self, context, layout):
    scn = context.scene
    scnProp = get_scnprop(scn)

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.label(text="", icon='LIGHT_SUN')
    row.prop(scnProp, 'show_sun_studio', text="Sun", icon='DOWNARROW_HLT' if scnProp.show_sun_studio else 'RIGHTARROW',
             emboss=False)

    row.label(text="", icon='NONE')
    show_helps_v2(row, docs_key='SUN_STUDIO_MENU')

    if not scnProp.show_sun_studio:
        return

    col.separator()
    sun_objects_dict = get_sun_objects()
    sun = sun_objects_dict.get('HDRI_MAKER_SUN')
    sun_handler = sun_objects_dict.get('HDRI_MAKER_SUN_HANDLER')
    sun_studio_collection = sun_objects_dict.get('collection')

    row = col.row(align=True)
    row.scale_y = 1.5
    if sun or sun_handler:
        icon = 'FILE_REFRESH'
    else:
        icon = 'ADD'

    row.operator(Exa.ops_name + "sun_maker", text="Add", icon=icon).options = 'ADD'
    if sun_studio_collection:
        row.operator(Exa.ops_name + "sun_maker", text="Remove Sun", icon='REMOVE').options = 'REMOVE'

    if not sun_objects_dict:
        return
    col.separator()

    if sun:
        col.prop(sun, 'location', index=2, text="Sun Height")
    if sun_handler:
        col.prop(sun_handler, 'rotation_euler', index=2, text="Rotation", invert_checkbox=True)
        col.separator()
        row = col.row(align=True)
        sync_sun = row.operator(Exa.ops_name + "sync_sun", text="Sync Sun", icon='DRIVER')
        sync_sun.options = 'SYNC'

        sync_sun = row.operator(Exa.ops_name + "sync_sun", text="Un-Sync Sun", icon='UNLINKED')
        sync_sun.options = 'UNSYNC'

    if sun:
        col.label(text="Sun Color:")
        split = col.split(factor=0.6, align=True)
        split.prop(sun.data, 'color', text="")
        split.operator(Exa.ops_name + "color_lab", text="Color Lab", icon='COLOR').options = 'HDRI_MAKER_SUN'
        col.separator()
        col.prop(sun.data, 'energy', text="Strength")
        if 'EEVEE' in scn.render.engine:
            col.prop(sun.data, 'diffuse_factor', text="Diffuse")
            col.prop(sun.data, 'specular_factor', text="Specular")
            col.prop(sun.data, 'volume_factor', text="Volume")
            col.prop(sun.data, 'angle', text="Angle")

            col.prop(sun.data, 'use_shadow', text=" Shadow")
            if sun.data.use_shadow:
                col.prop(sun.data, 'shadow_buffer_bias', text="Bias")
                col.separator()
                col.prop(sun.data, "shadow_cascade_count", text="Count")
                col.prop(sun.data, "shadow_cascade_fade", text="Fade")

                col.prop(sun.data, "shadow_cascade_max_distance", text="Max Distance")
                col.prop(sun.data, "shadow_cascade_exponent", text="Distribution")

                col.separator()
                col.prop(sun.data, 'use_contact_shadow', text="Contact Shadow")
                if sun.data.use_contact_shadow:
                    col.prop(sun.data, 'contact_shadow_distance', text="Distance")
                    col.prop(sun.data, 'contact_shadow_bias', text="Bias")
                    col.prop(sun.data, 'contact_shadow_thickness', text="Thickness")

        if scn.render.engine == 'CYCLES':
            col.prop(sun.data, 'angle', text="Angle")
            col.prop(sun.data.cycles, 'max_bounces', text="Max Bounces")
            if bpy.app.version < (4, 2, 0):
                col.prop(sun.data.cycles, 'cast_shadow', text="Cast Shadow")
            else:
                col.prop(sun.data.cycles, 'use_shadow', text="Use Shadow")

            col.prop(sun.data.cycles, 'use_multiple_importance_sampling', text="Multiple Importance")
            col.prop(sun.data.cycles, 'is_caustics_light', text="Shadow Caustics")


def draw_wrap_menu(self, context, layout):
    context_ob = context.object
    scnProp = get_scnprop(context.scene)
    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.label(text="", icon='MOD_WARP')
    row.prop(scnProp, 'show_wrap_menu', text='Wrap', icon='DOWNARROW_HLT' if scnProp.show_wrap_menu else 'RIGHTARROW',
             emboss=False)
    row.label(text="", icon='NONE')
    show_helps_v2(row, docs_key='DOME_PROJECTION_WRAP')

    if not scnProp.show_wrap_menu:
        return

    dome_objects_dict = get_dome_objects()
    dome_handler = dome_objects_dict.get('DOME_HANDLER')
    dome_ground = dome_objects_dict.get('HDRI_MAKER_DOME_GROUND')

    col.separator()

    row = col.row(align=True)
    shrinkwrap = row.operator(Exa.ops_name + "shrinkwrap", text='Wrap', icon='ADD')
    shrinkwrap.options = 'ADD'
    shrinkwrap.target = "SELECTED_OBJECT"

    # shrinkwrap = row.operator(Exa.ops_name + "shrinkwrap", text='Un-Wrap', icon='REMOVE')
    # shrinkwrap.options = 'REMOVE'
    # shrinkwrap.target = "SELECTED_OBJECT"

    shrinkwrap_mod = [o for o in dome_ground.modifiers if o.type == 'SHRINKWRAP']

    if shrinkwrap_mod:
        col.separator()
        sub_box = col.box()

        split = sub_box.split(factor=0.95, align=False)
        col_1 = split.column(align=True)
        active_obj = None
        for mod in shrinkwrap_mod:
            obj = mod.target
            if obj is None:
                # In this case the target is deleted from the scene but the modifier is still there
                continue

            is_active_obj = obj == context_ob and obj.select_get()

            if not active_obj:
                active_obj = is_active_obj

            sub_col = col_1.column(align=True)
            # Check if obj is into a valid dome_ground modifier shrinkwrap:
            if not mod.target:
                sub_col.alert = True

            row = sub_col.row(align=True)

            select_object = row.operator(Exa.ops_name + "select_object", text="", icon='RESTRICT_SELECT_OFF',
                                         emboss=True if is_active_obj else False,
                                         depress=True if is_active_obj else False)
            select_object.target = obj.name

            row.separator()

            shrinkwrap = row.operator(Exa.ops_name + "shrinkwrap", text="", icon='UNLINKED')
            shrinkwrap.options = 'REMOVE'
            shrinkwrap.target = obj.name


            row.prop(obj, 'name', text="", icon='OBJECT_DATA')
            row.prop(mod, 'use_negative_direction', text="", icon='TRIA_DOWN')
            row.prop(mod, 'use_positive_direction', text="", icon='TRIA_UP')

            display_type = 'TEXTURED' if obj.display_type == 'BOUNDS' else 'BOUNDS'
            setobjectview = row.operator(Exa.ops_name + "setobjectview", text='', icon='MOD_WIREFRAME',
                                         depress=False if display_type == 'BOUNDS' else True)
            setobjectview.display_type = display_type
            setobjectview.object_name = obj.name


            is_hidden_wrap_object = is_hidden_object(obj, get='VIEWPORT')
            toggle_hide_object = row.operator(Exa.ops_name + "toggle_hide_object", text='', icon='HIDE_ON' if is_hidden_wrap_object else 'HIDE_OFF',
                                             depress=is_hidden_wrap_object)
            toggle_hide_object.options = 'UNHIDE' if is_hidden_wrap_object else 'HIDE'
            toggle_hide_object.repr_object = repr(obj)

            if not mod:
                shrinkwrap = row.operator(Exa.ops_name + "shrinkwrap", text='', icon='FILE_REFRESH')
                shrinkwrap.options = 'ADD'
                shrinkwrap.target = obj.name

        if len(shrinkwrap_mod) > 1 and active_obj:
            col_2 = split.column(align=True)
            sub_col = col_2.column(align=True)
            row = sub_col.row(align=True)
            row.alignment = 'RIGHT'
            move_up = row.operator(Exa.ops_name + "move_wrap", text="", icon='TRIA_UP')
            move_up.options = 'UP'
            row = sub_col.row(align=True)
            row.alignment = 'RIGHT'
            move_down = row.operator(Exa.ops_name + "move_wrap", text="", icon='TRIA_DOWN')
            move_down.options = 'DOWN'

        subdivide = next((m for m in dome_ground.modifiers if m.type == 'SUBSURF'), None)
        smooth = next((m for m in dome_ground.modifiers if m.type == 'CORRECTIVE_SMOOTH'), None)
        if subdivide or smooth:
            sub_box = col.box()

        if subdivide:
            objProp = get_objprop(dome_ground)
            sub_box.prop(objProp, 'subdivision', text='Subdivision Levels')

        if smooth:
            sub_box.prop(smooth, 'factor', text='Smooth Factor')
            sub_box.prop(smooth, 'iterations', text='Smooth Iterations')

        if subdivide or smooth:
            shrinkwrap = sub_box.operator(Exa.ops_name + "shrinkwrap", text='Un-Wrap All', icon='UNLINKED')
            shrinkwrap.target = ""
            shrinkwrap.options = 'REMOVE_ALL'


def draw_ground_menu(self, context, layout):
    context_ob = context.object
    scnProp = get_scnprop(context.scene)
    box = layout.box()
    col = box.column(align=True)

    row = col.row(align=True)
    row.label(text="", icon='MATERIAL')
    row.prop(scnProp, 'show_ground_menu', text='Ground',
             icon='DOWNARROW_HLT' if scnProp.show_ground_menu else 'RIGHTARROW', emboss=False)
    row.label(text="", icon='NONE')
    show_helps_v2(row, docs_key='DOME_PROJECTION_GROUND_MATERIAL')

    if not scnProp.show_ground_menu:
        return

    col.separator()
    row = col.row(align=True)
    assign_mat_ground = row.operator(Exa.ops_name + "assign_mat_ground", text='Add Ground', icon='ADD')
    assign_mat_ground.options = 'ADD'
    assign_mat_ground.target = "ACTIVE_OBJECT"

    col.separator()

    dome_dict = get_dome_objects()
    dome_handler = dome_dict.get('DOME_HANDLER')
    if not dome_handler:
        return

    grounded = [o for o in dome_handler.children_recursive if get_objprop(o).object_id_name == 'HDRI_MAKER_GROUND']

    if not grounded:
        return

    g_box = col.box()
    for idx, obj in enumerate(grounded):
        objProp = get_objprop(obj)
        g_col = g_box.column(align=True)
        g_row = g_col.row(align=True)

        select_object = g_row.operator(Exa.ops_name + "select_object", text="", icon='RESTRICT_SELECT_OFF',
                                       emboss=True if obj == context_ob and obj.select_get() else False,
                                       depress=True if obj == context_ob and obj.select_get() else False)

        select_object.target = obj.name

        g_row.separator()

        assign_mat_ground = g_row.operator(Exa.ops_name + "assign_mat_ground", text="", icon='UNLINKED')
        assign_mat_ground.options = 'REMOVE'
        assign_mat_ground.target = obj.name

        g_row.prop(obj, 'name', text="", icon='OBJECT_DATA')

        material_selector = g_row.operator(Exa.ops_name + "material_selector", text='', icon='GRID',
                                           depress=True if objProp.ground_object_type == 'GROUND' else False)
        material_selector.options = 'GROUND'
        material_selector.target = obj.name

        material_selector = g_row.operator(Exa.ops_name + "material_selector", text='', icon='SPHERECURVE',
                                           depress=True if objProp.ground_object_type == 'SKY' else False)
        material_selector.options = 'SKY'
        material_selector.target = obj.name

        flip_normals = g_row.operator(Exa.ops_name + "flip_normals", text='', icon='ORIENTATION_NORMAL')
        flip_normals.target = obj.name

    if grounded:
        g_box = col.box()
        g_col = g_box.column(align=True)
        g_row = g_col.row(align=True)
        assign_mat_ground = g_row.operator(Exa.ops_name + "assign_mat_ground", text='Remove All', icon='UNLINKED')
        assign_mat_ground.options = 'REMOVE_ALL'


def draw_dome_submenu(self, context, layout):
    scnProp = get_scnprop(context.scene)

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.label(text="", icon='SPHERECURVE')
    row.prop(scnProp, 'show_dome_menu', text='Dome Properties',
             icon='DOWNARROW_HLT' if scnProp.show_dome_menu else 'RIGHTARROW',
             emboss=False)
    row.label(text="", icon='NONE')
    show_helps_v2(row, 'DOME_PROJECTION_PROPERTIES')

    if not scnProp.show_dome_menu:
        return

    col.separator()

    dome_objects_dict = get_dome_objects()
    reflection_plane = dome_objects_dict.get('DOME_REFLECTION_PLANE')
    dome = dome_objects_dict.get('HDRI_MAKER_DOME_SKY')
    dome_handler = dome_objects_dict.get('DOME_HANDLER')


    prop_row = col.row(align=True)
    prop_row.prop(scnProp, 'hide_dome', text="Hide Dome")

    if reflection_plane:
        prop_row.prop(get_objprop(reflection_plane), 'hide_full', text="Hide Reflection Plane")

    prop_row = col.row(align=True)
    prop_row.prop(scnProp, 'show_dome_wireframe', text="Display Wire")


    prop_row.prop(get_objprop(dome_handler), 'un_lock_dome_handler', text="Enable manually")

    if scnProp.hide_dome:
        text = "The dome is hidden, make it visible to continue working on it"
        wrap_text(col, string=text, text_length=(context.region.width * .15), center=True)

    if dome_handler:
        enable = True
        if get_objprop(dome_handler).un_lock_dome_handler:
            enable = False
            row = col.row(align=True)
            row.label(text="Handler Display Type:")
            row.prop(dome_handler, 'empty_display_type', text="")
            col.separator()
            col.prop(dome_handler, 'empty_display_size', text="Handler Display Size")

            reset_rotation_z = True if dome_handler.rotation_euler[2] != 0 else False
            reset_location = True if sum(dome_handler.location[:]) != 0 else False
            reset_inclination = True if dome_handler.rotation_euler[0] != 0 or dome_handler.rotation_euler[1] != 0 else False
            reset_scale = True if sum(dome_handler.scale[:]) != 3 else False

            if reset_rotation_z or reset_location or reset_inclination or reset_scale:
                col.separator()
                box = col.box()
                b_col = box.column(align=True)
                b_col.label(text="Reset Handler:")
                row = b_col.row(align=True)
                if reset_inclination:
                    row.operator(Exa.ops_name + "dome", text="Tilt", icon='DRIVER_ROTATIONAL_DIFFERENCE').options = 'RESET_LEVEL'
                if reset_location:
                    row.operator(Exa.ops_name + "dome", text="Loc", icon='EMPTY_AXIS').options = 'RESET_LOCATION'
                if reset_rotation_z:
                    row.operator(Exa.ops_name + "dome", text="Rot", icon='CON_ROTLIKE').options = 'RESET_ROTATION'
                if reset_scale:
                    row.operator(Exa.ops_name + "dome", text="Scale", icon='FIXED_SIZE').options = 'RESET_SCALE'

        if enable:
            row = col.row(align=True)
            row.enabled = enable
            aprox_size = "(" + str(round(dome.dimensions[0], 1)) + " , " + str(
                round(dome.dimensions[1], 1)) + " , " + str(round(dome.dimensions[2], 1)) + ")"
            row.label(text="穹顶大小 " + str(aprox_size))
            row = col.row()
            row.enabled = enable
            row.prop(get_objprop(dome_handler), 'scale_dome_handler', text="Scale Dome")
            row = col.row()
            row.enabled = enable
            row.prop(dome_handler, 'rotation_euler', text="Rotate Dome", index=2)
        # col.label(text="Translate Dome:")
        # row = col.row(align=True)
        # row.prop(get_objprop(dome_handler), 'locationX', text="X")
        # row.prop(get_objprop(dome_handler), 'locationY', text="Y")
        # row.prop(get_objprop(dome_handler), 'locationZ', text="Z")


def draw_hdri_dome_menu(self, context, layout, hide_drop=False):
    scn = context.scene
    scnProp = scn.hdri_prop_scn

    id_data_string = "bpy.data.materials"

    # layout.prop(scnProp, 'hdri_projected_menu', text='Dome',
    #             icon_value=get_icon('Menu open' if scnProp.hdri_projected_menu else 'Menu close'))
    #
    # if not scnProp.hdri_projected_menu:
    #     return

    dome_objects_dict = get_dome_objects()
    dome = dome_objects_dict.get('HDRI_MAKER_DOME_SKY')
    dome_handler = dome_objects_dict.get('DOME_HANDLER')

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)

    if dome:
        row.operator(Exa.ops_name + "centerview", text="", icon='CURSOR').options = 'CENTER_VIEW'
    else:
        row.label(text="", icon='NONE')

    row.separator()
    row.label(text="Dome Type:")
    row.prop(scnProp, 'dome_types', text="")
    row.separator()

    show_helps_v2(row, docs_key='DOME_PROJECTION_ADD_REMOVE')

    col.separator()

    import_row = col.row(align=True)
    import_row.scale_y = 1.5
    dome_ops = import_row.operator(Exa.ops_name + "dome", text="Add Dome", icon='ADD')
    dome_ops.options = 'ADD'

    if not dome:
        return

    reload_image = import_row.operator(Exa.ops_name + "dome", text="", icon='FILE_REFRESH')
    reload_image.options = 'RELOAD'

    dome_ops = import_row.operator(Exa.ops_name + "dome", text="Remove Dome", icon='REMOVE')
    dome_ops.options = 'REMOVE'


    if not dome_handler:
        text = "No dome handler found, please add a dome again (probably it was manually deleted)"
        wrap_text(col, string=text, text_length=(context.region.width * .10), center=True)

        row = col.row(align=True)
        row.scale_y = 1.5
        reload_dome_handler = row.operator(Exa.ops_name + "dome", text="Reload Dome Handler", icon='FILE_REFRESH')
        reload_dome_handler.options = 'RELOAD_DOME_HANDLER'
        return

    if get_objprop(dome_handler).un_lock_dome_handler and is_hidden_object(dome_handler):
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.5
        show_handler = row.operator(Exa.ops_name + "dome", text="Show Dome Handler", icon='RESTRICT_SELECT_OFF')
        show_handler.options = 'SHOW_HANDLER'


    draw_dome_submenu(self, context, layout)
    draw_hooks_menu(self, context, layout)
    draw_wrap_menu(self, context, layout)
    draw_ground_menu(self, context, layout)

    if not dome:
        return

    dome_mat = dome.active_material if dome.active_material and dome.active_material.hdri_prop_mat.mat_id_name == 'DOME_MATERIAL' else None
    if not dome_mat:
        return

    nodes_dict = get_nodes_dict(dome_mat.node_tree)
    if not nodes_dict:
        return

    if nodes_dict.get('MIXER'):
        box = layout.box()
        col = box.column(align=True)
        draw_panel_sliders_group(dome_mat, col, nodes_dict['MIXER'],
                                 id_data_string=id_data_string, show_hide_option=True, show_reset_value=True,
                                 show_tooltip=True, show_socket_color=SocketColor.color, show_node_label=True,
                                 group_icon='NODETREE', docs_url_key='DOME_PROJECTION_MIXER_NODE')

    if nodes_dict.get('VECTORS'):
        box = layout.box()
        col = box.column(align=True)
        draw_panel_sliders_group(dome_mat, col, nodes_dict['VECTORS'],
                                 id_data_string=id_data_string, show_hide_option=True, show_reset_value=True,
                                 show_tooltip=True, show_socket_color=SocketColor.vector, show_node_label=True,
                                 group_icon='NODETREE', docs_url_key='DOME_PROJECTION_VECTORS_NODE',
                                 show_sync_angle=True)

    # row = layout.row(align=True)
    # row.operator(Exa.ops_name + "subdividedomeground", text='Subdivide ( ' + str(get_objprop(dome).subdivision_step) + ' )', icon='ADD').options = 'SUBDIVIDE'
    # row.operator(Exa.ops_name + "subdividedomeground", text='Un-Subdivide', icon='REMOVE').options = 'UNSUBDIVIDE'

    # gm = next((m for m in dome.modifiers if m.type == 'NODES'), None)
    # if gm:
    #     draw_geonode_inputs(layout, gm)


def draw_volumetric_menu(self, context, layout, hide_drop=False):
    volume = volume_is_linked = None

    scn = context.scene
    scnProp = get_scnprop(scn)
    world = scn.world
    if has_nodetree(world):
        nodes_dict = get_nodes_dict(world.node_tree)
        volume = nodes_dict.get('VOLUMETRIC')
        if volume:
            volume_is_linked = True if [o for o in volume.outputs if o.name == 'Volume' and o.is_linked] else False

    box = layout.box()
    col = box.column(align=True)
    col.separator()
    row = col.row(align=True)
    row.label(text="Volume:", icon='VOLUME_DATA')
    row.prop(scnProp, 'volumetric_groups', text="")
    row.separator()
    show_helps_v2(row, docs_key='VOLUMETRIC_MENU')
    col.separator()

    row = col.row(align=True)
    row.scale_y = 1.5
    row.operator(Exa.ops_name + "load_volumes", text="Add", icon='ADD').options = 'ADD'
    if volume:
        row.operator(Exa.ops_name + "load_volumes", text="Remove", icon='REMOVE').options = 'REMOVE'

        if volume_is_linked:
            icon = "LINKED"
        else:
            icon = "UNLINKED"

        col.separator()
        col.operator(Exa.ops_name + "volumetric_on_off", text="Unlink Volume", icon=icon,
                     depress=False if volume_is_linked else True)

        col.separator()
        mat_box = col.box()
        mat_col = mat_box.column(align=True)
        if not volume_is_linked:
            mat_col.enabled = False
        draw_panel_sliders_group(world, mat_col, volume,
                                 id_data_string="bpy.data.worlds", show_hide_option=True, show_reset_value=True,
                                 show_tooltip=True, show_node_label=True,
                                 group_icon='OUTLINER_OB_VOLUME', docs_url_key='VOLUME_NODE_GROUP')

        col.separator()
        col.prop(scn.eevee, 'volumetric_end', text="Visibility distance")
        col.separator()
        row = col.row(align=True)
        row.prop(scnProp, 'volumetric_detail', text="Detail")


def draw_shadow_catcher_menu(self, context, layout):
    scn = context.scene
    scnProp = get_scnprop(scn)
    engine = scn.render.engine

    sc_dict = get_shadow_catcher_objects()
    sc_collection = sc_dict.get('collection')
    sc_eevee_plane = sc_dict.get('eevee_plane')
    sc_cycles_plane = sc_dict.get('cycles_plane')
    sc_eevee_material = sc_dict.get('eevee_material')
    sc_eevee_node = sc_dict.get('eevee_node')
    sc_exist = sc_dict.get('exist')
    sc_light_probe = sc_dict.get('light_probe')
    sc_normal_node = sc_dict.get('sc_normal')

    box = layout.box()
    col_box = box.column(align=True)

    row = col_box.row(align=True)
    row.scale_y = 1.5
    if sc_exist:
        row.operator(Exa.ops_name + "shadowcatcher", text='Remove Shadow Catcher',
                     icon='REMOVE').options = 'REMOVE'
    else:
        row.operator(Exa.ops_name + "shadowcatcher", text='Add Shadow Catcher',
                     icon='ADD').options = 'ADD'

    col_box.separator()

    row = col_box.row()
    row.alignment = 'CENTER'
    if 'EEVEE' in engine:
        text = "The shadow catcher (in Eevee render) only works if you add a light into the scene and if are in render mode"
        wrap_text(row, string=text, text_length=(context.region.width * .1), center=True)

    if sc_eevee_material and sc_eevee_node:
        node_box = col_box.box()
        node_col = node_box.column(align=True)
        draw_panel_sliders_group(sc_eevee_material, node_col, sc_eevee_node,
                                 id_data_string="bpy.data.materials", show_tooltip=True, show_reset_value=True,
                                 show_node_label=True, group_icon='NODETREE', docs_url_key='SHADOW_CATCHER_NODE')

    if sc_eevee_material:
        matProp = get_matprop(sc_eevee_material)
        col_box.separator()
        col_box.prop(matProp, 'enum_fc_normals', text='Normals')
        col_box.separator()
        if sc_normal_node:
            node_box = col_box.box()
            node_col = node_box.column(align=True)
            draw_panel_sliders_group(sc_eevee_material, node_col, sc_normal_node,
                                     id_data_string="bpy.data.materials", show_tooltip=True, show_reset_value=True,
                                     show_node_label=True, group_icon='NODETREE',
                                     docs_url_key='SHADOW_CATCHER_NORMAL_NODE')


    row = col_box.row(align=True)
    row.prop(scn.render, 'film_transparent', text='Film Transparent')
    sub = row.row(align=True)
    sub.alignment = 'RIGHT'
    show_helps_v2(row, 'SHADOW_CATCHER_MENU')

    if sc_light_probe:
        objProp = get_objprop(sc_light_probe)
        col_box.prop(objProp, 'hide_full', text='Hide Reflection Plane')

    if sc_cycles_plane:
        objProp = get_objprop(sc_cycles_plane)
        col_box.prop(objProp, 'hide_full', text='Hide Cycles SC')

    if bpy.app.version < (4, 2, 0):
        if 'EEVEE' in engine:
            row = col_box.row(align=True)
            row.label(text="Eevee Shadow Detail:")
            row.prop(scnProp, 'shadow_detail', text="")
            col_box.separator()




def draw_save_menu(self, context, layout, hide_drop=False):
    """This is the Layout dedicated to save the backgrounds and the HDRIs"""

    scn = context.scene
    scnProp = scn.hdri_prop_scn
    # If the user is in the save menu, the drop down menu is hidden if the library is different from the user library
    if scnProp.libraries_selector != 'USER':
        box = layout.box()
        col = box.column(align=True)

        text = "To show the save menu, switch to the user library"
        wrap_text(layout=col, string=text, enum=False, text_length=(context.region.width / 6.5),
                  center=True, icon="")
        col.separator()
        col.prop(scnProp, 'libraries_selector', text='Library')

    if not hide_drop:
        layout.prop(scnProp, 'save_menu', text='Save menu',
                    icon_value=get_icon('Menu open' if scnProp.save_menu else 'Menu close'))
        if not scnProp.save_menu:
            return

    if scnProp.libraries_selector == 'USER':

        hdr_name = get_winman_main_preview()
        # hdr_name = bpy.data.window_managers["WinMan"].hdri_category
        preferences = get_addon_preferences()

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.alignment = 'RIGHT'
        show_helps_v2(row, 'SAVE_MENU')
        col.separator()
        col.operator(Exa.ops_name + "exporthdr", text='Export image', icon='EXPORT')

        col = box.column(align=True)
        col.prop(scnProp, 'save_type', text='Save type')

        if scnProp.save_type == 'CURRENT':
            col = box.column(align=True)
            col.scale_y = 2
            col.operator(Exa.ops_name + "savecurrentbackground", text='Save background', icon='RENDER_STILL')

        if scnProp.save_type == 'PANORAMA':
            camera_sphere = next((o for o in bpy.data.objects if o.hdri_prop_obj.object_id_name == '360_CAMERA_SPHERE'),
                                 None)

            if camera_sphere:

                col = box.column(align=True)
                col.scale_y = 2
                col.operator(Exa.ops_name + "panoramasave", text='Panorama Save',
                             icon='RENDER_STILL')

                row = box.row(align=True)
                row.operator(Exa.ops_name + "putcamera", text='360 Cam on cursor',
                             icon='CURSOR')
                row.operator(Exa.ops_name + "centerview", text='Find Camera',
                             icon='VIEWZOOM').options = 'FIND_BALL_CAMERA'

            else:

                col = box.column(align=True)
                col.scale_y = 2
                col.operator(Exa.ops_name + "addcamerasphere", text='Add 360 Cam on cursor', icon='SPHERE')

        if scnProp.save_type == 'BATCH':
            col = box.column(align=True)
            col.label(text='Choose the source folder:')
            choosepath = col.operator(Exa.ops_name + "choosepath", text=preferences.from_batch_path,
                                      icon='FILE_FOLDER')
            choosepath.options = 'BATCH_FROM_PATH'
            col = box.column(align=True)
            col.scale_y = 2
            col.operator(Exa.ops_name + "batchmodal", text='Batch Save', icon='RENDER_STILL')

        col = box.column(align=False)
        if scnProp.libraries_selector == 'DEFAULT':
            pass  # TODO: Obsoleta
        else:
            col.prop(scnProp, 'up_category', text='Save to Cat')

        col = box.column()
        sub_box = col.box()
        sub_col = sub_box.column(align=True)
        row = sub_col.row(align=True)
        row.prop(scnProp, 'collection_management',
                 text='Library Tools',
                 icon='DOWNARROW_HLT' if scnProp.collection_management else 'RIGHTARROW',
                 emboss=False)
        show_helps_v2(row, 'SAVE_LIBRARY_TOOLS')

        if scnProp.collection_management:
            sub_col.separator()
            sub_col.operator(Exa.ops_name + "addbackgroundcategory", text='Add New Category', icon='NEWFOLDER')
            sub_col.separator()

            sub_col.operator(Exa.ops_name + "tocat", text='Move Background to Category', icon_value=get_icon("right"))
            sub_col.separator()
            sub_col.operator(Exa.ops_name + "rename_lib_tool", text='Rename Background',
                             icon_value=get_icon("rename")).options = 'MATERIAL'

            sub_col.separator()

            sub_col.operator(Exa.ops_name + "rename_lib_tool", text='Rename Category',
                             icon_value=get_icon('rename')).options = 'CATEGORY'
            sub_col.separator()

            preview_mat_name = get_winman_main_preview()
            open_path = os.path.join(preferences.addon_user_library, scnProp.up_category, preview_mat_name)
            if not os.path.exists(open_path):
                open_path = os.path.join(preferences.addon_user_library, scnProp.up_category)
            if not os.path.exists(open_path):
                open_path = preferences.addon_user_library

            pyops = sub_col.operator(Exa.ops_name + "pythonops", text='Open Current Folder', icon='FILE_FOLDER')
            pyops.options = 'OPEN_FOLDER'
            pyops.open_path = open_path

            sub_col.separator()

            if scnProp.up_category != 'Empty Collection...' or hdr_name != 'Empty':

                row = sub_col.row(align=True)
                row.prop(scnProp, 'safety_delete', text='',
                         icon='DOWNARROW_HLT' if scnProp.safety_delete else 'RIGHTARROW', emboss=False)
                row.label(text="Danger Zone:", icon_value=get_icon('danger'))
                # row.label(text="", icon_value=get_icon('danger'))
                show_helps_v2(row, 'SAVE_DANGER_ZONE')
                if scnProp.safety_delete:
                    sub_col.separator()
                    if scnProp.up_category != 'Empty Collection...':
                        remove = sub_col.operator(Exa.ops_name + "remove_lib_tool", text="Delete category",
                                                  icon_value=get_icon('danger'))
                        remove.options = 'REMOVE_CATEGORY'
                        sub_col.separator()

                    if hdr_name != 'Empty':
                        if scnProp.libraries_selector == 'USER':
                            remove = sub_col.operator(Exa.ops_name + "remove_lib_tool", text="Delete background",
                                                      icon_value=get_icon('danger'))
                            remove.options = 'REMOVE_MATERIAL'
    else:
        col = box.column()
        box = col.box()
        col = box.column()
        col.label(text='Switch to User Library for more options', icon_value=get_icon('info'))

    # col.separator()
    # asset_b_maker = col.operator(Exa.ops_name + "make_asset_browser", text='Make Asset Browser', icon='FILE_FOLDER')
    # asset_b_maker.library_path = scnProp.libraries_selector
    # TODO: Questo è da integrare in futuro, mancano troppe API in Asset Browser per ora.


def draw_options_menu(self, context, layout):
    scn = context.scene
    scnProp = scn.hdri_prop_scn

    # --- General Options Box---

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.alignment = 'LEFT'
    row.label(text='General Options:', icon='SETTINGS')
    col.separator()
    row = col.row()
    row.prop(self, 'show_labels', text="Show material popup label")
    row = col.row()
    row.prop(self, "icons_preview_size", text='Icon preview dimension')
    row.prop(self, "icons_popup_size", text='Icons popup size')
    col = box.column(align=True)
    row = col.row(align=True)
    row.label(text="Check update frequency:")
    row.prop(self, 'check_update_frequency_control', text="")

    # --- Fix Options Box---
    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.alignment = 'LEFT'
    row.label(text="Fix Options:", icon='LIBRARY_DATA_BROKEN')
    col.separator()

    split = col.split(factor=0.4)
    col_sx = split.column(align=False)
    snp = col_sx.operator(Exa.ops_name + "solvenodesproblem", text='Try to Fix Unknow Nodes', icon="LOOP_BACK")
    snp.options = 'RETROCOMPATIBILITY'

    col_sx.operator(Exa.ops_name + "findlostfiles", text='Find Lost Images', icon="FILE_FOLDER")
    col_sx.operator(Exa.ops_name + "purge_cache", text="Purge ExtremeAddons Cache", icon='TRASH').options = 'PURGE_EXA_CACHE'

    col_dx = split.column(align=True)


    col.separator()
    col.operator(Exa.ops_name + "restore_all_icons_patch", text='Regenerate Previews and Icons', icon="FILE_IMAGE")

    # --- Properties Box---
    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.alignment = 'LEFT'
    row.label(text='Experimental Options:', icon='EXPERIMENTAL')
    col.separator()

    row = col.row(align=True)
    row.label(text="Color Space:")
    row.prop(scnProp, 'materials_colorspace', text="")
    col.separator()

    row = col.row(align=True)
    row.prop(self, 'show_creator_utility', text="Show Creator Utility")

    col.separator()
    col.label(text="Volumetric Detail:")
    row = col.row(align=True)
    row.prop(scnProp, 'volumetric_detail', expand=True)

    if bpy.app.version < (4, 2, 0):
        col.separator()
        col.label(text="Shadow Detail:")
        row = col.row(align=True)
        row.prop(scnProp, 'shadow_detail', expand=True)


def mini_api_hide(module):
    # pointerprop è l'equivalente di var.extremepbr_scene_prop o qualsiasi altra pointerprop , serve per far funzionare la funzione
    # anche in hdri maker e extreme pbn visto che cambiano solo le pointerproperty ma non le properties condivise

    # Allora, questa seconda mini_api, ha il compito di fare una lista di tutti quelle proprietà che hanno
    # il compito di nascondere altre proprietà una volta raggiunto il valore massimo di se stesse
    # Questo accade previa status prop , se quest'ultima sarà attiva (E cioè il valore massimo della proprietà), nasconderà la proprietà desiderata
    # solo se l'utente lo desidera, restituisce una lista numerica , il cui numero corrisponderà al numero in sequenza da 0 delle proprietà
    # Questo perch risparmiare caratteri , siccome i nomi delle proprietà dei gruppi è di 63 caratteri, usare i numeri è piu conveniente
    hide_prop_list = []

    for idx, inp in enumerate(get_ng_inputs(module.node_tree)):
        sckProp = get_sckprop(inp)

        if sckProp.api_boolean and sckProp.api_hide_prop_if_min:
            if module.inputs[idx].default_value == inp.min_value:
                for hdIdx in sckProp.api_hide_prop_if_min.split(","):
                    if hdIdx.isdigit():
                        if int(hdIdx) != idx:
                            hide_prop_list.append(int(hdIdx))

        if sckProp.api_boolean and sckProp.api_hide_prop_if_max:
            if module.inputs[idx].default_value == inp.max_value:
                for hdIdx in sckProp.api_hide_prop_if_max.split(","):
                    if hdIdx.isdigit():
                        if int(hdIdx) != idx:
                            hide_prop_list.append(int(hdIdx))

    return hide_prop_list


def draw_panel_sliders_group(mat, col, module, check_if_linked=True, id_data_string='bpy.data.materials',
                             show_node_label=False,
                             show_hide_option=False, show_reset_value=False, show_tooltip=True, show_socket_color=(),
                             group_icon='NONE', docs_url_key="", show_sync_angle=False):


    ngProp = get_ngprop(module.node_tree)
    ndProp = get_ndprop(module)

    scn = bpy.context.scene

    if not module.inputs[:]:
        return

    nodes = module.node_tree.nodes
    row = None  # Sicurezza perchè c'è una casistica in cui row può non esistere

    avoid_mix_max = ['RGBA']  # Evita la chiave min max se la proprietà non la supporta:

    if not module.node_tree:
        return

    nGinput, nGoutput = get_in_out_group(module.node_tree)
    if not nGinput:
        return

    label_row = None
    if group_icon != 'NONE':
        label_row = col.row(align=True)
        label_row.label(text="", icon=group_icon)

    if show_hide_option:
        if not label_row:
            label_row = col.row(align=True)
        label_row.prop(ndProp, 'hide', text="", icon='RIGHTARROW' if ndProp.hide else 'DOWNARROW_HLT', emboss=False)
        # label_split.label(text=module.name + ":")

    if show_socket_color:
        if not label_row:
            label_row = col.row(align=True)
        label_row.template_node_socket(color=show_socket_color)

    if show_node_label:
        if not label_row:
            label_row = col.row(align=True)
        # label_split.alignment = 'CENTER'
        label_row.label(text=module.label)

    if not label_row:
        label_row = col.row(align=True)

    label_row.prop(ngProp, 'show_lock_prop', text="", icon='LOCKED' if ngProp.show_lock_prop else 'UNLOCKED',
                   emboss=False)

    if show_reset_value:
        if not label_row:
            label_row = col.row(align=True)
        else:
            label_row.separator()
        restore_node_value = label_row.operator(Exa.ops_name + "restore_node_value", text="", icon='LOOP_BACK',
                                              emboss=False)
        restore_node_value.repr_node = repr(module)

    if show_tooltip:
        if not label_row:
            label_row = col.row(align=True)
        label_row.prop(ngProp, 'ng_show_tips', text="", icon='INFO', emboss=False)

    if docs_url_key:
        if not label_row:
            label_row = col.row(align=True)
        show_helps_v2(label_row, docs_key=docs_url_key, icon='QUESTION', emboss=False)

    if show_hide_option:
        if ndProp.hide:
            return

    if label_row:
        col.separator()

    tagged_nodes = [n for n in nodes if get_ndprop(n).node_tag != ""]

    # Tutte le proprietà di tipo Socket,
    hide_prop_list = mini_api_hide(module)  # Lista di eventuali proprietà da nascondere
    for idx, n_input in enumerate(module.inputs):
        if n_input.is_linked:
            continue

        ng_input = get_ng_inputs(module.node_tree, idx)
        sckProp = get_sckprop(ng_input)
        if n_input.hide_value:
            continue

        if n_input.type == 'SHADER':
            continue

        if n_input.bl_idname in socket_forbidden():
            col.label(text="Invalid Socket type" + " ( " + n_input.name + " )", icon='ERROR')
            continue

        if sckProp.is_system_socket:
            continue

        if sckProp.api_hide_from_panel:
            continue

        # If the socket is linked it will be hidden from the panel
        if check_if_linked:
            if module.inputs[idx].is_linked:
                continue

        # Solo se 1 o piu socket del gruppo input interno è linkato
        if not [n for n in nGinput if n.outputs[idx].is_linked] and not sckProp.is_fake_socket:
            continue

        if idx in hide_prop_list:
            # Se la max default value è al massimo, e coincide con il valore corrente dell'input value
            # allora la proprietà verrà nascosta
            continue

        ico_false = sckProp.api_icon_false if sckProp.api_icon_false in get_blender_icons() else "NONE"
        ico_true = sckProp.api_icon_true if sckProp.api_icon_true in get_blender_icons() else "NONE"
        ico = "NONE"
        if n_input.type not in avoid_mix_max:
            if hasattr(n_input, 'default_value'):
                if n_input.default_value == ng_input.min_value:
                    ico = ico_false
                elif n_input.default_value == ng_input.max_value:
                    ico = ico_true

        if sckProp.api_col_separator:
            col.separator()

        previous_socket = get_ng_inputs(module.node_tree, index=idx - 1)
        if (sckProp.api_row_2 and get_sckprop(previous_socket).api_row_1) or (
                sckProp.api_row_3 and get_sckprop(previous_socket).api_row_2) \
                or (sckProp.api_row_4 and get_sckprop(previous_socket).api_row_3):
            # if pos and pos > 1 and len(pos_list) > 0 and pos_list[-1] != None:

            if sckProp.api_row_1 and sckProp.api_row_2 and sckProp.api_row_3:  # Solo se l'utente inavvertitamente attiva i 3 row sullo stesso socket
                row = col.row(align=True)
            else:
                # Casistica per cui abbiamo dato row = None all'inizio del for loop
                if row:
                    row = row.row(align=True)
                else:
                    row = col.row(align=True)
            row.scale_x = sckProp.api_scale_x
            row.scale_y = sckProp.api_scale_y
        else:
            row = col.row(align=True)
            row.scale_x = sckProp.api_scale_x
            row.scale_y = sckProp.api_scale_y

        # Se l'utente inserisce "lbl" crea un testo in testa
        if sckProp.api_label_on_top:
            if sckProp.api_top_label_text:
                row.label(text=sckProp.api_top_label_text)
            else:
                row.label(text=n_input.name)
            row = col.row(align=True)

        # if ngProp.shader_maker_type != "":
        node = None
        # Se il tag Del Node corrisponde al tag Dell'input, mostra quello che deve mostrare:
        # La lista è in node_tag
        if sckProp.tag_socket != "":
            if sckProp.tag_socket == 'NORMAL' and ngProp.use_normal_generator:
                node = next((n for n in tagged_nodes if get_ndprop(n).node_tag == 'NORMAL_GENERATOR'), None)
            else:
                node = next((n for n in tagged_nodes if sckProp.tag_socket == get_ndprop(n).node_tag), None)

            # elif not node and sckProp.tag_socket == 'BUMP':
            #     node = next((n for n in nodes if 'BUMP' in get_ndprop(n).node_tag if n.type == 'TEX_IMAGE'), None)
            #
            # elif not node and sckProp.tag_socket == 'NORMAL':
            #     node = next((n for n in nodes if 'X_PBR_Utility_Translate' in n.name if n.type == 'GROUP' if n.node_tree), None)

        if node:
            # if ngProp.shader_maker_type in ['PBR','VIDEO']:
            # In questo passaggio recupera anche le immagini del materiale
            if node.type == 'TEX_IMAGE' and node.image:
                if not node.image.packed_file:
                    if not image_has_data(node.image):
                        row.alert = True
                        try:
                            node.image.update()
                        except:
                            pass

                if sckProp.tag_socket != 'NORMAL':
                    icon = 'HIDE_ON' if node.mute else (
                        'IMAGE_DATA' if node.image.frame_duration == 1 else 'RENDER_ANIMATION')
                else:
                    if ngProp.use_normal_generator:
                        icon = 'IMAGE_DATA'
                    elif node.mute:
                        icon = 'HIDE_ON'
                    else:
                        icon = 'IMAGE_DATA'

            elif node.type == 'TEX_IMAGE' and not node.image:
                if sckProp.tag_socket == 'MASK' and ngProp.group_id_name == 'FX':
                    row.alert = True
                icon = 'IMPORT'
            # TODO:
            # elif node.type != 'TEX_IMAGE':
            #     icon = 'NODE_SEL'
            #     if node.inputs[:] and node.inputs[0].is_linked:
            #         from_node = node.inputs[0].links[0].from_node
            #         if from_node.type == 'TEX_IMAGE' and from_node.image:
            #             images_count.append(image)

            if ngProp.shader_maker_type != 'PAINTER':
                row.scale_x = 1.2 if not ngProp.ng_show_tips else 1
                row.scale_y = sckProp.api_scale_y
                easypanel = row.operator(Exa.ops_name + "texturemanagerpanelops", text="", icon=icon,
                                         depress=True if icon == 'HIDE_ON' else False)
                easypanel.options = 'TEXTURE_MANAGER'
                easypanel.mat = mat.name
                easypanel.node_groups = module.node_tree.name
                easypanel.node = node.name
                easypanel.group_inputs_idx = idx
                easypanel.description = "Texture Manager: " + sckProp.tag_socket

                row = row.row(align=True)

            # if sckProp.tag_socket == 'VIDEO':
            #     draw_video_ctrl(col, mat, module.node_tree, node)
            #     col.separator()

            # if node.type == 'TEX_IMAGE':
            #     if ngProp.shader_maker_type == 'PAINTER':
            #         # Accende il pulsante che è registrato come attivo:
            #         depresStat = False
            #         if scnProp.active_shadermaker_paint != "":
            #             node_tree_name = scnProp.active_shadermaker_paint.split("'SpLiT'")[0]
            #             socket_name = scnProp.active_shadermaker_paint.split("'SpLiT'")[1]
            #             if module.node_tree.name == node_tree_name and input.name == socket_name and scnProp.painting_time:
            #                 depresStat = True
            #
            #         tag_socket_text = "Paint " + sckProp.tag_socket.replace("_", " ").title()
            #         paintRow = col.row(align=True)
            #         paintRow.scale_y = 1.5
            #         icon = 'color_brush' if sckProp.tag_socket in ['DIFFUSE', 'EMISSION',
            #                                                        'SUBSURFACE'] else 'noncolor_brush'
            #
            #         paintRow.prop(node, 'mute', text="", icon='HIDE_ON' if node.mute else 'HIDE_OFF')
            #         conRow = paintRow.row(align=True)
            #         conRow.enabled = False if node.mute else True
            #         easypanel = conRow.operator(Exa.ops_name+"texturemanagerpanelops", text=tag_socket_text,
            #                                     icon_value=get_icon(icon), depress=depresStat)
            #         easypanel.options = 'SHADER_MAKER_PAINT'
            #         easypanel.mat = mat.name
            #         easypanel.node_groups = module.node_tree.name
            #         easypanel.node = node.name
            #         easypanel.group_inputs_idx = idx

        if sckProp.api_row_separator:
            row = row.row()

        if sckProp.api_boolean:
            row.scale_x = sckProp.api_scale_x
            row.scale_y = sckProp.api_scale_y
            draw_api_boolean_button(row, module, idx, mat, ico, sckProp)

        elif sckProp.is_api_enum:
            if sckProp.api_enum_direction == 'HORIZONTAL':
                row = row.row()
            else:
                row = row.column(align=True)
            row.prop(sckProp, 'api_enum_items', expand=True)

        else:
            if not sckProp.is_fake_socket:
                row.scale_x = sckProp.api_scale_x
                row.scale_y = sckProp.api_scale_y

                if sckProp.api_hide_text:
                    text = ""
                elif sckProp.api_label_on_top and not sckProp.api_top_label_text:
                    text = ""
                else:
                    text = n_input.name

                if n_input.type == 'VECTOR':
                    v_col = row.column(align=True)
                    v_col.prop(n_input, 'default_value', text="")


                else:
                    row.prop(n_input, 'default_value', text=text, icon=ico)
                    if show_sync_angle and n_input.name.lower() == "angle":

                        ops = HDRIMAKER_OT_sync_node_background_rotation
                        sync_from_background_is_active = ops.sync_from_background_is_active
                        sync_from_dome_is_active = ops.sync_from_dome_is_active

                        depress = False
                        if id_data_string == 'bpy.data.worlds' and sync_from_background_is_active:
                            depress = True
                        elif id_data_string == 'bpy.data.materials' and sync_from_dome_is_active:
                            depress = True

                        sync = row.operator(Exa.ops_name + "sync_node_background_rotation", text="", icon='LINKED', depress=depress)
                        sync.options = 'SYNC_FROM_BACKGROUND' if id_data_string == 'bpy.data.worlds' else 'SYNC_FROM_DOME'


                        unsync = row.operator(Exa.ops_name + "sync_node_background_rotation", text="", icon='UNLINKED')
                        unsync.options = 'UN_SYNC'

                # The property in this case is stored into the Input Node Socket, not in the internal socket of the group
                if ngProp.show_lock_prop:
                    row.prop(sckProp, 'lock_prop', text="", icon='LOCKED' if sckProp.lock_prop else 'UNLOCKED')

                if ngProp.ng_show_tips:
                    if sckProp.api_bool_description:
                        show_tips = row.operator(Exa.ops_name + "show_tips", text="", icon='QUESTION')
                        show_tips.repr_socket = repr(ng_input)

        # -------------------- Subsurface
        # if sckProp.api_sss_translucency:
        #     is_active = False
        #     if mat.use_sss_translucency: is_active = True
        #     if mat.use_screen_refraction: is_active = False
        #     row = row.row(align=True)
        #     # row=row.row(align=True)
        #     row.scale_x = 0.75
        #     # Rimosso in Blender 4.2 e non serve in HDRi Maker
        #     # op = row.operator(Exa.ops_name + "togglematerialsettings", text="Translucency",
        #     #                   icon='HIDE_OFF' if is_active else 'HIDE_ON',
        #     #                   depress=is_active)
        #     # op.options = 'TOGGLE_TRANSLUCENCY'
        #     # op.mat = mat.name
        #     # op.is_from_node_group = True
        #     # op.from_node_tree = module.node_tree.name

        # --------------------------------------------------------------------------------------------------------------

        if n_input.type == 'RGBA' and sckProp.api_add_color_lab:
            row = row.row(align=True)
            row.scale_x = 0.75
            colorlab = row.operator(Exa.ops_name + "color_lab", icon='COLOR')
            colorlab.options = 'ASSIGN_TO_SOCKET'
            colorlab.repr_n_socket = repr(n_input)

        if sckProp.api_double_rgb_operator:
            if len(module.inputs) > (idx + 1):
                next_input = module.inputs[idx + 1]
                if n_input.type == 'RGBA' and next_input.type == 'RGBA':
                    row = col.row(align=True)

                    colorutility = row.operator(Exa.ops_name + "colorutility", text='↑ Flip ↓')
                    colorutility.options = 'FLIP'
                    colorutility.mat = mat.name
                    colorutility.node = module.name
                    colorutility.node_groups = module.node_tree.name
                    colorutility.group_inputs_idx = idx
                    colorutility.id_data = str(module.id_data)

                    colorutility = row.operator(Exa.ops_name + "colorutility", text='↓ Assign ↓')
                    colorutility.options = 'ASSIGN_NEXT'
                    colorutility.mat = mat.name
                    colorutility.node = module.name
                    colorutility.node_groups = module.node_tree.name
                    colorutility.group_inputs_idx = idx
                    colorutility.id_data = str(module.id_data)

        if Exa.product == 'EXTREME_PBR':
            if sckProp.api_transparent_operator:
                row = row.row(align=True)
                row.scale_x = 0.75
                if bpy.app.version < (4, 2, 0):
                    blend_method = mat.blend_method
                else:
                    blend_method = mat.surface_render_method

                toggleops = row.operator(Exa.ops_name + "togglematerialsettings", text="Is " + blend_method,
                                         icon='RADIOBUT_ON')
                toggleops.mat = mat.name
                toggleops.is_from_node_group = True
                toggleops.from_node_tree = module.node_tree.name
                toggleops.options = 'TOGGLE_TRANSPARENT_MODE'

    return col


def draw_api_boolean_button(row, module, idx, mat, ico, sckProp):
    input = module.inputs[idx]

    ng_input = get_ng_inputs(module.node_tree, index=idx)

    # Se trova status, trasforma lo slider in un bottone, che setta il valore Min e Max a pressione toggle
    min, max = (ng_input.min_value, ng_input.max_value)
    depresStat = True if module.inputs[idx].default_value == max else False

    if depresStat:
        text = sckProp.api_text_if_true if sckProp.api_text_if_true != "" else (
            input.name if not sckProp.api_text_if_false else "")
    else:
        text = sckProp.api_text_if_false if sckProp.api_text_if_false != "" else (
            input.name if not sckProp.api_text_if_true else "")

    if sckProp.api_bool_invert:
        depresStat = False if module.inputs[idx].default_value == max else True

    boolops = row.operator(Exa.ops_name + "boolean_socket", text=text if not sckProp.api_hide_text else "",
                           depress=depresStat,
                           icon=ico)
    boolops.options = 'BOOL'
    boolops.repr_node_tree = repr(mat.node_tree)
    boolops.node = module.name
    boolops.id_data = str(module.id_data)
    boolops.node_groups = module.node_tree.name
    boolops.group_inputs_idx = idx
    boolops.description = sckProp.api_bool_description
    boolops.docs_key = sckProp.docs_key

    ngProp = get_ngprop(module.node_tree)
    if ngProp.show_lock_prop:
        row.prop(sckProp, 'lock_prop', text="", icon='LOCKED' if sckProp.lock_prop else 'UNLOCKED')


def draw_add_remove_import(self, context, layout):
    scn = context.scene

    row = layout.row(align=True)
    row.scale_y = 2

    if is_import_tools():
        import_ops = row.operator(Exa.ops_name + "addbackground", text='Import', icon_value=get_icon('import'))
        import_ops.environment = 'COMPLETE'
        import_ops.invoke_browser = True
        import_ops.is_from_asset_browser = False
        import_ops.make_relative_path = False
        import_ops.hide_info_popup = False

    elif is_assemble_studio():
        studio_ops = row.operator(Exa.ops_name + "assemble_studio", text='Studio', icon_value=get_icon('Aggiungi'))
    else:
        add_ops = row.operator(Exa.ops_name + "addbackground", text='Add', icon_value=get_icon('Aggiungi'))
        add_ops.environment = 'COMPLETE'
        add_ops.invoke_browser = False
        add_ops.is_from_asset_browser = False
        add_ops.make_relative_path = False
        add_ops.hide_info_popup = False

    if scn.world:
        row.operator(Exa.ops_name + "remove_background", text="Remove", icon_value=get_icon('Remove'))


def draw_box_utility(self, context, layout):
    dome_objects = get_dome_objects()
    dome_handler = dome_objects.get('DOME_HANDLER')
    if dome_handler:
        objProp = get_objprop(dome_handler)
        box = layout.box()
        row = box.row(align=False)
        row.prop(objProp, 'un_lock_dome_handler', text="", icon='HIDE_OFF' if objProp.un_lock_dome_handler else 'HIDE_ON')


def draw_default_user_lib(self, context, layout):
    preferences = get_addon_preferences()

    col = layout.column(align=True)

    text = 'Enter the path to the Default Library (' + get_default_library_folder_name() + ')'
    wrap_text(col, string=text, text_length=(context.region.width / 6.5), center=True)

    if preferences.addon_default_library and os.path.isdir(preferences.addon_default_library):
        default_lib_text = preferences.addon_default_library
        default_lib_exist = True
    else:
        default_lib_text = "Choose the path"
        default_lib_exist = False

    row = col.row(align=True)

    from .ui_v2.main_ui_v2 import Polling

    row.alert = os.path.isdir(preferences.addon_default_library) == False

    if Polling.is_new_default_lib:
        choosepath = row.operator(Exa.ops_name + "choosepath",
                                  text=default_lib_text,
                                  icon_value=get_icon('mark_check'))
    else:
        choosepath = row.operator(Exa.ops_name + "choosepath",
                                  text=default_lib_text,
                                  icon='FILE_FOLDER')

    choosepath.options = 'LINK_DEFAULT_LIB'
    # choosepath.directory = preferences.addon_default_library if os.path.isdir(preferences.addon_default_library) else ""

    if default_lib_exist:
        row.operator(Exa.ops_name + "resetlibpath", text="", icon='UNLINKED').options = 'RESET_DEFAULT_LIB_PATH'

    text = 'Enter the path of the User Library (' + get_user_library_folder_name() + ')'
    wrap_text(col, string=text, text_length=(context.region.width / 6.5), center=True)

    if preferences.addon_user_library and os.path.isdir(preferences.addon_user_library):
        user_lib_text = preferences.addon_user_library
        user_lib_exist = True
    else:
        user_lib_text = "Choose The Path"
        user_lib_exist = False

    row = col.row(align=True)
    row.alert = os.path.isdir(preferences.addon_user_library) == False

    if Polling.is_new_user_lib:
        choosepath = row.operator(Exa.ops_name + "choosepath",
                                  text=user_lib_text,
                                  icon_value=get_icon('mark_check'))
    else:
        choosepath = row.operator(Exa.ops_name + "choosepath",
                                  text=user_lib_text,
                                  icon='FILE_FOLDER')

    choosepath.options = 'LINK_USER_LIB'
    # choosepath.directory = preferences.addon_user_library if os.path.isdir(preferences.addon_user_library) else ""

    if user_lib_exist:
        row.operator(Exa.ops_name + "resetlibpath", text="", icon='UNLINKED').options = 'RESET_USER_LIB_PATH'
    else:
        if Polling.is_new_default_lib:
            row.operator(Exa.ops_name + "make_user_library", text="Make User Library", icon='NEWFOLDER')


def library_missing(self, context, layout):
    addon_prefs = get_addon_preferences()
    scnProp = get_scnprop(context.scene)

    col = layout.column()
    # row = col.row()
    # row.alignment = 'CENTER'
    # row.label(text=str(addon_prefs.exa_license))
    row = col.row()
    row.scale_y = 1
    row.label(text="", icon_value=get_icon("extreme_addons_32"))

    open_pref = col.operator(Exa.ops_name + "open_preferences", text="Open Help",
                             icon_value=get_icon("extreme_addons_32"))
    open_pref.options = 'HELPS'

    write_with_icons(row, "HORIZONTAL", 'Welcome', True, 1.2)
    row.label(text="", icon_value=get_icon("pastrokkio"))
    box = col.box()
    colbox = box.column(align=True)
    center = colbox.row()
    center.alignment = 'CENTER'
    center.label(text='Libraries are not currently linked or installed')
    colbox.operator(Exa.ops_name + "open_preferences", text="Go to install",
                    icon='OPTIONS').options = 'LIBRARY_INSTALL'

    col.label(text="Other options:")
    box = col.box()
    col = box.column()
    text = "Did you already work on HDRi Maker and you already installed the libraries? If so, indicate the paths below"

    wrap_text(col, text, None, (context.region.width / 6.5), True, "")

    box = col.box()
    draw_default_user_lib(addon_prefs, context, box)


def draw_all_custom_props(prop_class, layout, hide_list=[]):
    col = layout.column(align=True)
    for prop in get_annotations(prop_class):
        if prop in hide_list:
            continue
        row = col.row()
        row.prop(prop_class, prop)


def draw_light_studio(self, context, layout):
    scn = context.scene
    scnProp = get_scnprop(scn)

    light_studio_dict = get_light_studio_objects()

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    row.label(text="", icon='OUTLINER_OB_LIGHT')

    row.prop(scnProp,
             'show_light_studio',
             text="Lamps",
             icon='DOWNARROW_HLT' if scnProp.show_light_studio else 'RIGHTARROW',
             emboss=False)

    row.label(text="")
    show_helps_v2(row, "LIGHT_STUDIO_MENU")

    if not scnProp.show_light_studio:
        return

    col.separator()

    row = col.row(align=True)

    if light_studio_dict:
        text = "Reload"
        icon = 'FILE_REFRESH'
    else:
        text = "Add"
        icon = 'ADD'

    row.scale_y = 1.5
    row.operator(Exa.ops_name + "create_light_studio", text=text, icon=icon).options = 'ADD'
    if light_studio_dict:
        row.operator(Exa.ops_name + "create_light_studio", text="Remove", icon='REMOVE').options = 'REMOVE'

    if not light_studio_dict:
        return

    col.separator()
    col.prop(scnProp, 'light_studio_count', text="Light Count")
    col.separator()

    # area = get_view_3d_area()
    # row = col.row(align=True)
    # row.prop(area.overlay, 'show_extras', text="Extras")
    # row.prop(area.overlay, 'show_relationship_lines', text="Relationship Lines")

    lamp_holders = light_studio_dict.get('LAMP_HOLDERS')
    if lamp_holders:
        col.separator()
        row = col.row(align=True)
        row.prop(lamp_holders, 'location', text="Lamps")
        parent_target = row.operator(Exa.ops_name + "parent_target",
                                     text="",
                                     icon='LINKED' if lamp_holders.parent else 'UNLINKED',
                                     depress=True if lamp_holders.parent else False)
        parent_target.options = 'UNPARENT' if lamp_holders.parent else 'PARENT'
        parent_target.object_name = lamp_holders.name
        parent_target.target_to_object = False

    target = light_studio_dict.get('LIGHT_TARGET')
    if target:
        col.separator()
        row = col.row(align=True)
        row.prop(target, 'location', text="Target")
        parent_target = row.operator(Exa.ops_name + "parent_target",
                                     text="",
                                     icon='LINKED' if target.parent else 'UNLINKED',
                                     depress=True if target.parent else False)
        parent_target.options = 'UNPARENT' if target.parent else 'PARENT'
        parent_target.object_name = target.name
        parent_target.target_to_object = True

        col.separator()

    row = col.row(align=True)
    row.label(text="Light type:")
    row.prop(scnProp, 'light_type', text="")
    if scnProp.light_type == 'AREA':
        row = col.row(align=True)
        row.label(text="Area Shape:")
        row.prop(scnProp, 'light_shape', text="")

    lights_holder = light_studio_dict.get('LIGHT_HOLDER')
    if lights_holder:
        col.separator()
        sub_box = col.box()
        sub_col = sub_box.column(align=True)
        row = sub_col.row(align=True)
        row.label(text="Lights", icon='LIGHT')
        row.operator(Exa.ops_name + "random_light_color", text="Random Color", icon='COLOR_RED', emboss=False)

        sub_col.separator()

        row = sub_col.row(align=True)
        row.label(text="Energy")
        row.operator(Exa.ops_name + "color_lab", text="Color Lab", icon='COLOR',
                     emboss=False).options = 'LIGHT_STUDIO'

        if scnProp.light_type == 'POINT':
            row.label(text="Shadow S.size")

        if scnProp.light_type == 'SPOT':
            row.label(text="Cone Angle")
            row.label(text="Blend")
            row.label(text="Shadow S.size")

            # row.label(text="Show")

        if scnProp.light_type == 'AREA':
            if scnProp.light_shape in ['RECTANGLE', 'ELLIPSE']:
                row.label(text="Size X")
                row.label(text="Size Y")
            else:
                row.label(text="Size")

        col.separator()

        for idx, light in enumerate(reversed(lights_holder)):
            data = light.data
            sub_row = sub_col.row(align=True)
            # sub_row.label(text=str(idx+1))
            sub_row.prop(data, 'energy', text="")
            sub_row.prop(data, 'color', text="")

            if data.type == 'SPOT':
                sub_row.prop(data, 'spot_size', text="")
                sub_row.prop(data, 'spot_blend', text="")
                # sub_row.prop(data, 'show_cone', text="Cone", toggle=True)

            if data.type in ['SPOT', 'POINT']:
                sub_row.prop(data, 'shadow_soft_size', text="")

            if scnProp.light_type == 'AREA':
                sub_row.prop(data, 'size', text="")
                if scnProp.light_shape in ['RECTANGLE', 'ELLIPSE']:
                    sub_row.prop(data, 'size_y', text="")


# def draw_socials_buttons(layout, text="Social Links:", center=False):
#     json_file = os.path.join(risorse_lib(), "online_utility", "exa_social.json")
#
#     if not json_file:
#         return
#
#     row = layout.row(align=True)
#     row.scale_x = 2
#     row.scale_y = 2
#     if text:
#         row.label(text=text)
#     if center:
#         row.alignment = 'CENTER'
#
#     openbrowser = row.operator(Exa.ops_name + "open_web_browser", text="",
#                                icon_value=get_icon('extreme_addons_32'))
#     openbrowser.options = 'GET_URL_KEY'
#     openbrowser.description = "extreme-addons"
#     openbrowser.json_dictionary = 'exa_social.json'
#     openbrowser.url_key = "extreme-addons"
#
#     openbrowser = row.operator(Exa.ops_name + "open_web_browser", text="", icon_value=get_icon('youtube'))
#     openbrowser.options = 'GET_URL_KEY'
#     openbrowser.description = "youtube"
#     openbrowser.json_dictionary = 'exa_social.json'
#     openbrowser.url_key = "youtube"
#
#     # openbrowser = row.operator(Exa.ops_name + "open_web_browser", text="", icon_value=get_icon('facebook'))
#     # openbrowser.options = 'GET_URL_KEY'
#     # openbrowser.description = "facebook"
#     # openbrowser.json_dictionary = 'exa_social.json'
#     # openbrowser.url_key = "facebook"
#
#     openbrowser = row.operator(Exa.ops_name + "open_web_browser", text="", icon_value=get_icon('twitter'))
#     openbrowser.options = 'GET_URL_KEY'
#     openbrowser.description = "twitter"
#     openbrowser.json_dictionary = 'exa_social.json'
#     openbrowser.url_key = "twitter"
#
#     # openbrowser = row.operator(Exa.ops_name + "open_web_browser", text="", icon_value=get_icon('instagram'))
#     # openbrowser.options = 'GET_URL_KEY'
#     # openbrowser.description = "instagram"
#     # openbrowser.json_dictionary = 'exa_social.json'
#     # openbrowser.url_key = "instagram"
#
#     # openbrowser = row.operator(Exa.ops_name + "open_web_browser", text="",
#     #                            icon_value=get_icon('patreon'))
#     # openbrowser.options = 'GET_URL_KEY'
#     # openbrowser.description = "patreon"
#     # openbrowser.json_dictionary = 'exa_social.json'
#     # openbrowser.url_key = "patreon"


def socials_buttons(layout, text="Socials:", center=False):
    row = layout.row(align=True)
    row.scale_x = 2
    row.scale_y = 2
    if text:
        row.label(text=text)

    if center:
        row.alignment = 'CENTER'

    # Temporaneamente disabilitato
    # open_web_browser = row.operator(Exa.ops_name + "open_web_browser", text="",
    #                                 icon_value=get_icon('extreme_addons_32'))
    # open_web_browser.options = 'GET_URL_KEY'
    # open_web_browser.description = "extreme-addons"
    # open_web_browser.json_dictionary = 'exa_social.json'
    # open_web_browser.docs_key = "extreme-addons"

    open_web_browser = row.operator(Exa.ops_name + "open_web_browser", text="", icon_value=get_icon('youtube'))
    open_web_browser.options = 'GET_URL_KEY'
    open_web_browser.description = "youtube"
    open_web_browser.json_dictionary = 'exa_social.json'
    open_web_browser.docs_key = "youtube"

    open_web_browser = row.operator(Exa.ops_name + "open_web_browser", text="", icon_value=get_icon('twitter'))
    open_web_browser.options = 'GET_URL_KEY'
    open_web_browser.description = "twitter"
    open_web_browser.json_dictionary = 'exa_social.json'
    open_web_browser.docs_key = "twitter"

    open_web_browser = row.operator(Exa.ops_name + "open_web_browser", text="",
                                    icon_value=get_icon('blender_market_logo'))
    open_web_browser.options = 'GET_URL_KEY'
    open_web_browser.description = "blender_market"
    open_web_browser.json_dictionary = 'exa_social.json'
    open_web_browser.docs_key = "blender_market"

    open_web_browser = row.operator(Exa.ops_name + "open_web_browser", text="", icon_value=get_icon('gumroad_logo'))
    open_web_browser.options = 'GET_URL_KEY'
    open_web_browser.description = "gumroad"
    open_web_browser.json_dictionary = 'exa_social.json'
    open_web_browser.docs_key = "gumroad"


def draw_alert_experimental_version(self, context, layout):
    if not LibraryUtility.is_official_version:
        experimental = next((spl for spl in bpy.app.version_string.lower().split() if spl in ["beta", "alpha"]),
                            None)
        if experimental:
            text = ""

            wrap_text(layout, text, None, (context.region.width / 6.5), True, "")
        else:
            LibraryUtility.is_official_version = True

        # layout.operator(Exa.ops_name + "confirm_non_official_version", text="OK! I got it", icon='INFO')
