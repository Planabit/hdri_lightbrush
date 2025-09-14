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

from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy.types import Operator

from .save_utility import create_batch_scene, render_background_preview, save_background_file
from ..exaconv import get_scnprop
from ..exaproduct import Exa
from ..library_manager.get_library_utils import current_lib, set_material_preview
from ..library_manager.main_pcoll import reload_main_previews_collection
from ..library_manager.tools import create_material_folders
from ..save_tools.save_fcs import check_if_name_exist_in_category
from ..utility.fc_utils import remove_scene_by_scene_id_name
from ..utility.text_utils import draw_info
from ..utility.utility import replace_forbidden_characters, wima, get_addon_preferences, \
    return_name_without_numeric_extension, get_output_node


class HDRIMAKER_OT_SaveCurrentBackground(Operator):
    bl_idname = Exa.ops_name + "savecurrentbackground"
    bl_label = "Save Current Background"
    bl_options = {'INTERNAL'}

    override_save_name: BoolProperty(default=False, description='Overwrite the name if the name is present in this category')
    world_save_name: StringProperty()
    confirm: EnumProperty(items=[('YES', 'Yes', 'Yes'), ('NO', 'No', 'No')], default='NO')

    @classmethod
    def description(cls, context, properties):
        desc = "Save the current world in the selected category"
        return desc

    def draw(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        world = scn.world

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.alignment = 'CENTER'
        row.label(text="Save Current Background")
        col.separator()

        row = col.row()
        row.prop(self, "world_save_name", text="Background Name")
        col.separator()
        row = col.row()
        row.prop(self, "override_save_name", text="Override if name exist")
        col.separator()

        col.prop(scnProp, 'up_category', text="Save Into Category")
        col.separator()

        row = col.row(align=True)
        row.scale_y = 2
        row.prop(self, "confirm", expand=True)

        col.separator()

    def invoke(self, context, event):
        scn = context.scene
        scnProp = get_scnprop(scn)
        world = scn.world

        if not world:
            text = "This scene contains no world, so nothing can be saved, if you want to save a world, please create one " \
                   "If you want to batch render an external images choose the 'Batch Render'"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if not world:
            text = "This scene contains no world, so nothing can be saved"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if scnProp.libraries_selector != 'USER':
            text = "Please, before proceeding, go to your user library and select or create a category before proceeding"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if scnProp.up_category in ["Empty Collection...", ""]:
            text = "Please add a new category with a custom name of your choice"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if not world.node_tree:
            text = "This world contains no node tree, so nothing can be saved, if you want to save a world, please create one"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if not get_output_node(world.node_tree):
            text = "This world contains no output node, or the output node is not connected, so nothing can be saved, please check the node tree"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}


        scnProp = get_scnprop(scn)
        if scnProp.libraries_selector != 'USER':
            scnProp.libraries_selector = 'USER'

        self.confirm = 'NO'
        self.world_save_name = world.name

        return wima().invoke_props_dialog(self, width=450)

    def execute(self, context):

        if self.confirm == 'NO':
            text="You have choosen not to save the current world, if you want to save it, please click on 'Yes'"
            draw_info(text, "Info", 'INFO')
            return {'FINISHED'}

        scn = context.scene
        scnProp = get_scnprop(scn)
        addon_preferences = get_addon_preferences()
        world = scn.world


        remove_scene_by_scene_id_name('BATCH_SCENE')

        libraries_selector = scnProp.libraries_selector
        up_category = scnProp.up_category


        cat_path = os.path.join(current_lib(), get_scnprop(context.scene).up_category)

        # Get filename from world.name
        file_name_clean = replace_forbidden_characters(self.world_save_name)
        file_name_clean = replace_forbidden_characters(file_name_clean)
        file_name_clean = return_name_without_numeric_extension(file_name_clean)

        if self.override_save_name is False:
            exist = check_if_name_exist_in_category(addon_preferences.addon_user_library, up_category, file_name_clean)
            if exist:
                return {'FINISHED'}

        mat_folders_dict = create_material_folders(cat_path, file_name_clean, mat_variant_folder_names=[file_name_clean])

        batch_scene = create_batch_scene(context)

        batch_scene.world = world

        render_filepath = os.path.join(mat_folders_dict['default'], file_name_clean + '.png')

        render_background_preview(batch_scene,
                                  render_filepath,
                                  lens=12,
                                  camera_loc=[0, 0, 0],
                                  camera_rotation=[0, 0, 0])


        # Here we save the world into the library, as a .blend file
        blend_filename = file_name_clean + '.blend'
        save_background_file(batch_scene, blend_filename, mat_folders_dict['variant_paths'][0])

        remove_scene_by_scene_id_name('BATCH_SCENE')

        reload_main_previews_collection()

        set_material_preview(libraries_selector, up_category, file_name_clean)

        return {'FINISHED'}
