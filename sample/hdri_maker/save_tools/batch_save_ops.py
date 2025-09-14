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
from bpy.props import EnumProperty, IntProperty, BoolProperty
from bpy.types import Operator

from .save_utility import render_background_preview, save_background_file, create_batch_scene, load_world_to_save
from ..bpy_data_libraries_load.data_lib_loads import get_data_from_blend
from ..exaconv import get_scnprop
from ..exaproduct import Exa
from ..library_manager.get_library_utils import current_lib
from ..library_manager.main_pcoll import reload_main_previews_collection
from ..library_manager.textures_pcoll import reload_textures_prev_icons
from ..library_manager.tools import create_material_folders
from ..save_tools.save_fcs import search_hdr_files
from ..utility.fc_utils import remove_scene_by_scene_id_name
from ..utility.text_utils import draw_info, wrap_text
from ..utility.utility import wima, get_addon_preferences, redraw_all_areas, get_filename_from_path, \
    get_percentage


class HDRIMAKER_OT_RemoveFromColProp(Operator):
    """Remove File From List"""
    bl_idname = Exa.ops_name + "removefromcolprop"
    bl_label = "Remove File From List"
    bl_options = {'INTERNAL'}

    idx: IntProperty()

    def execute(self, context):
        preferences = get_addon_preferences()
        file_list_prop = preferences.file_list_prop
        file_list_prop.remove(self.idx)
        return {'FINISHED'}


class HDRIMAKER_OT_BatchModal(Operator):
    """Batch save"""
    bl_idname = Exa.ops_name + "batchmodal"
    bl_label = "Redraw Preview/Create Library"
    bl_options = {'INTERNAL'}

    _timer = None
    _handler = None
    hdr_list = []
    user_scene = None
    batch_scene = None
    from_batch_path = None
    libraries_selector = None
    up_category = ''
    progress_percentage = 0
    tot_files = 0

    free_cycle = 0

    show_files: BoolProperty(default=False)
    confirm: EnumProperty(default="NO", items=(('NO', "No", ""), ('YES', "Yes", "")))

    @classmethod
    def progress(cls):
        return cls.progress_percentage

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    def draw(self, context):
        preferences = get_addon_preferences()
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        file_number = str(len(preferences.file_list_prop))
        if file_number != 0:
            text = "This path you have chosen contains " + file_number + " background files, do you want to proceed to create a library?"
            wrap_text(layout=col, string=text, enum=False, text_length=(context.region.width / 30),
                      center=True, icon="")

            col.separator()
            col.prop(self, 'show_files', text="Show file list:",
                     icon='DOWNARROW_HLT' if self.show_files else 'RIGHTARROW')
            if self.show_files:
                col.separator()
                for idx, prop in enumerate(preferences.file_list_prop):
                    row = col.row(align=True)
                    space = "0" if idx < 10 else ""
                    row.label(text=space + str(idx) + " - " + prop.name)
                    row.label(text=prop.world_name)
                    row.operator(Exa.ops_name + "removefromcolprop", text="", icon='CANCEL').idx = idx

        col.separator()

        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="Choose Yes and press OK button to start")

        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="Choose No or press Esc (Key) to abort")

        col.separator()
        row = col.row()
        row.scale_y = 2
        row.prop(self, 'confirm', expand=True)
        col.separator()

    def invoke(self, context, event):
        self.tot_files = 0
        self.progress_percentage = 0
        self.free_cycle = 0

        self.confirm = 'NO'

        preferences = get_addon_preferences()
        remove_scene_by_scene_id_name('BATCH_SCENE')
        self.user_scene = context.scene
        scnProp = get_scnprop(self.user_scene)
        if scnProp.scene_id_name != 'BATCH_SCENE':
            scnProp.scene_id_name = 'USER_SCENE'

        self.libraries_selector = scnProp.libraries_selector
        self.up_category = scnProp.up_category

        preferences.file_list_prop.clear()

        addon_preferences = get_addon_preferences()

        self.from_batch_path = bpy.path.abspath(addon_preferences.from_batch_path)

        if not os.path.exists(self.from_batch_path):
            text = "Attention Enter a path that contains .hdr files"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        file_list = search_hdr_files(self.from_batch_path, use_blend=True, only_hdr=False)

        if not file_list:
            text = "Attention: This directory does not contain any .hdr/.exr/.blend files Choose a directory that contains at least 1 of these formats"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        idx = -1
        for filepath in file_list:
            # This operator can save the world from .blend file, but need to check if blend file contain at least 1 world
            fn = get_filename_from_path(filepath)
            if fn and fn.endswith('.blend'):
                worlds_list = get_data_from_blend(filepath, 'worlds')
                if not worlds_list:
                    continue
                for w_name in worlds_list:
                    idx += 1
                    item = preferences.file_list_prop.add()
                    item.idx = idx
                    item.name = fn
                    item.world_name = w_name
                    item.filepath = filepath
                    item.filetype = 'BLEND'
            else:
                idx += 1
                item = preferences.file_list_prop.add()
                item.idx = idx
                item.name = fn
                item.world_name = ""
                item.filepath = filepath
                item.filetype = 'IMAGE'

        return wima().invoke_props_dialog(self, width=550)

    def modal(self, context, event):
        redraw_all_areas()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if self.free_cycle != 30:
            self.free_cycle += 1
            # This to leave the processor free for 20 cycles and be able to interact with the Blender interface for
            # About 3 seconds. In order not to completely freeze the interface
            return {'PASS_THROUGH'}
        else:
            self.free_cycle = 0

        if event.type == 'TIMER':
            preferences = get_addon_preferences()
            if preferences.file_list_prop:
                # -----------------------------------
                prop = preferences.file_list_prop[0]
                filepath = prop.filepath
                # -----------------------------------

                scnProp = get_scnprop(context.scene)
                scnProp.libraries_selector = self.libraries_selector
                scnProp.up_category = self.up_category

                if prop.filetype == 'BLEND':
                    filename = prop.world_name
                else:
                    filename = get_filename_from_path(filepath)

                file_name_clean = filename.split(".")[0].replace("_", " ").title()

                cat_path = os.path.join(current_lib(), get_scnprop(context.scene).up_category)
                mat_folders_dict = create_material_folders(cat_path, file_name_clean,
                                                           mat_variant_folder_names=[file_name_clean])
                ####
                batch_scene = create_batch_scene(context)
                world = load_world_to_save(context, batch_scene, filepath, file_name_clean)
                if not world:
                    preferences.file_list_prop.remove(0)
                    return {'PASS_THROUGH'}

                render_filepath = os.path.join(mat_folders_dict['default'], file_name_clean + ".png")
                render_background_preview(batch_scene,
                                          render_filepath,
                                          lens=12,
                                          )

                save_background_file(batch_scene, filepath, mat_folders_dict['variant_paths'][0])

                # ------------------------------------------------------------------------------------------------------

                preferences.file_list_prop.remove(0)
                cls = self.__class__
                cls.progress_percentage = get_percentage(self.tot_files - len(preferences.file_list_prop),
                                                         self.tot_files, decimal=2)
            else:
                self.cancel(context)
                redraw_all_areas()
                return {'FINISHED'}

        redraw_all_areas()



        return {'PASS_THROUGH'}

    def execute(self, context):

        if self.confirm == 'NO':
            return {'CANCELLED'}

        remove_scene_by_scene_id_name('BATCH_SCENE')
        context.window.scene = self.user_scene

        cls = self.__class__
        cls._handler = self
        preferences = get_addon_preferences()
        self.tot_files = len(preferences.file_list_prop)
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        remove_scene_by_scene_id_name('BATCH_SCENE')
        cls = self.__class__
        cls._handler = None
        redraw_all_areas()
        if self._timer:
            wima().event_timer_remove(self._timer)

        reload_main_previews_collection()
        reload_textures_prev_icons()

        redraw_all_areas()
