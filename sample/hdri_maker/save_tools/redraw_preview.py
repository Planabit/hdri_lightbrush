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
from bpy.props import FloatProperty, IntProperty
from bpy.types import Operator

from ..background_tools.background_fc import import_hdri_maker_world, assign_image_to_background_node, get_nodes_dict
from ..bpy_data_libraries_load.data_lib_loads import load_libraries_world
from ..exaconv import get_scnprop
from ..exaproduct import Exa
from ..library_manager.main_pcoll import reload_main_previews_collection
from ..library_manager.main_pcoll_attributes import get_winman_main_preview, set_winman_main_preview
from ..library_manager.tools import get_file_source
from ..save_tools.save_utility import create_batch_scene, render_background_preview
from ..utility.fc_utils import remove_scene_by_scene_id_name
from ..utility.text_utils import draw_info
from ..utility.utility import purge_all_group_names


class HDRIMAKER_OT_RedrawPreview(Operator):
    """Redraw the current preview"""
    bl_idname = Exa.ops_name + "redrawpreview"
    bl_label = "Redraw Preview"
    bl_options = {'INTERNAL'}

    cam_rot_x: FloatProperty(default=0.0, min=-360.0, max=360.0, subtype='ANGLE',
                             description="Camera Inclination")
    cam_rot_y: FloatProperty(default=0.0, min=-360.0, max=360.0, subtype='ANGLE',
                             description="Camera Rotation Y")
    cam_rot_z: FloatProperty(default=0.0, min=-360.0, max=360.0, subtype='ANGLE',
                             description="Camera Rotation Z")
    cam_lens: IntProperty(default=12, min=1, max=50, description="Focal Length")
    emission: FloatProperty(default=1.0, min=0.0, description="Background Light Strength")
    saturation: FloatProperty(default=1.0, min=0.0, max=2.0, description="Background Saturation")


    def invoke(self, context, event):
        # Check if project is saved:
        if not os.path.isfile(bpy.data.filepath):
            text = "Please Save your project before proceeding"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.separator()
        col.label(text="Camera Rotation", icon='CAMERA_DATA')
        col.separator()
        row = col.row(align=True)
        row.prop(self, "cam_rot_x", text="Rotation X")
        row.prop(self, "cam_rot_y", text="Rotation Y")
        row.prop(self, "cam_rot_z", text="Rotation Z")
        col.separator()
        col.prop(self, "emission", text="Emission")
        col.prop(self, "saturation", text="Saturation")
        col.separator()

        row = col.row(align=True)
        row.label(text="Camera Lens")
        row.prop(self, "cam_lens", text="mm")

    def execute(self, context):
        time_start = time.time()

        scn = context.scene
        scnProp = get_scnprop(scn)

        libraries_selector = scnProp.libraries_selector
        up_category = scnProp.up_category
        preview = get_winman_main_preview()

        # Remove batch scene
        remove_scene_by_scene_id_name('BATCH_SCENE')

        if libraries_selector != 'USER':
            text = "Only User Library Can Be Rendered"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if up_category in ['Empty Collection...', '']:
            text = "This Category Is Empty, please add a new one"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if preview in ['Empty...', '']:
            text = "No Preview To Render"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        # Check if exists a k size bigger max size of the backgound (material folder version are contained into the k size folder)
        from ..library_manager.k_size_enum import get_k_size_list
        k_list = ["1k", "2k", "4k", "6k", "8k", "10k", "12k", "16k", "20k", "24k", "32k"]
        gks = get_k_size_list()
        if gks:
            k_tuples = gks.get('list')
            if k_tuples:
                k_sizes = [k[0] for k in k_tuples]
                if any(k in k_sizes for k in k_list):
                    # convert k_sizes string into int
                    k_sizes = [int(k_size[:-1]) for k_size in k_sizes]
                    # get the max k_size
                    max_k_size = max(k_sizes)
                    # Now set the scnProp.k_size to the max_k_size
                    scnProp.k_size = str(max_k_size) + "k"

        # Import world like to background operator
        dictionary_file = get_file_source()
        if not dictionary_file:
            text = "No File Found"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        file_type = dictionary_file.get("file_type")
        filepath = dictionary_file.get("filepath")
        filename = dictionary_file.get("filename")
        preview_filepath = dictionary_file.get("preview_filepath")

        image = None
        if file_type == 'IMAGE':
            world = import_hdri_maker_world(context, rename=filename.split(".")[0].replace("_", " ").title(), add_to_current_scene=False)
            image = bpy.data.images.load(filepath)
            assign_image_to_background_node(image, world=world, environment='COMPLETE')
            purge_all_group_names(world.node_tree)

        elif file_type == 'BLENDER_FILE':
            world = load_libraries_world(filepath, world_index=0)
            if not world:
                text = "This blend file does not contain any world ( " + filepath + " )"
                draw_info(text, "Info", 'INFO', text_wrap=False)
                return {'CANCELLED'}

        # Create batch scene
        batch_scene = create_batch_scene(context)
        batch_scene.world = world

        # Get the Color Nodegroup (If exists)
        nodes_dict = get_nodes_dict(world.node_tree)
        complete = nodes_dict.get('COMPLETE')
        if complete:
            emission = complete.inputs.get("Emission")
            if emission:
                emission.default_value = self.emission
            saturation = complete.inputs.get("Saturation")
            if saturation:
                saturation.default_value = self.saturation

        render_background_preview(batch_scene,
                                  preview_filepath, lens=self.cam_lens,
                                  camera_rotation=(self.cam_rot_x, self.cam_rot_y, self.cam_rot_z))


        # Remove world
        # Se rimuoviamo, mentre ha uno sfondo uguale. Lo sfondo viene rimosso.
        # if world:
        #     bpy.data.worlds.remove(batch_scene.world, do_unlink=True)
        # Remove image if exists
        # if image:
        #     bpy.data.images.remove(image, do_unlink=True)


        # Remove batch scene
        remove_scene_by_scene_id_name('BATCH_SCENE')

        reload_main_previews_collection()

        scnProp.libraries_selector = libraries_selector
        scnProp.up_category = up_category
        set_winman_main_preview(preview)

        # Calc time:
        time_end = time.time() - time_start

        # Print render time as time_end:
        text = filename + " Preview Rendered in" + " " + str(round(time_end, 2)) + " " + "seconds"
        self.report({'INFO'}, text)

        return {'FINISHED'}


