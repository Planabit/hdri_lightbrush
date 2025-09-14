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
import shutil

import bpy

from .render_tools import try_render, cycles_render_set_preview
from ..background_tools.background_fc import import_hdri_maker_world, assign_image_to_background_node
from ..bpy_data_libraries_load.data_lib_loads import load_libraries_world
from ..exaconv import get_objprop, get_scnprop
from ..utility.utility import get_filename_from_path, create_camera_and_place


def create_batch_scene(context):
    batch_scene = next((scn for scn in bpy.data.scenes if get_scnprop(scn).scene_id_name == 'BATCH_SCENE'), None)

    if not batch_scene:
        batch_scene = bpy.data.scenes.new('Batch scene')
        get_scnprop(batch_scene).scene_id_name = 'BATCH_SCENE'

    context.window.scene = batch_scene

    return batch_scene


def load_world_to_save(context, scene, from_filepath, world_name):
    filename = get_filename_from_path(from_filepath)

    if filename.split(".")[-1] not in ['hdr', 'exr', 'blend']:
        return

    clean_filename = filename.replace(".hdr", "").replace(".exr", "").replace("_", " ").replace(".blend", "").title()

    if filename.endswith('.blend'):
        world = load_libraries_world(from_filepath, world_name=world_name, rename=clean_filename)
        if not world:
            return

        world.name = clean_filename
    else:
        world = import_hdri_maker_world(context, rename=clean_filename)
        image = bpy.data.images.load(from_filepath)
        assign_image_to_background_node(image)

    scene.world = world

    return world


def render_background_preview(scene, render_filepath, lens=12, camera_loc=[0, 0, 0], camera_rotation=[0, 0, 0], file_format='PNG'):
    """This function renders a preview of the background in the scene"""
    camera = next((o for o in bpy.data.objects if get_objprop(o).object_id_name == 'CAMERA_RENDER'), None)
    if camera:
        bpy.data.objects.remove(camera)
    camera = create_camera_and_place(scene, name="Camera Batch Save", camera_id_name='CAMERA_RENDER',
                                     lens=lens,
                                     location=camera_loc,
                                     rotation_in_degrees=camera_rotation)

    cycles_render_set_preview(scene)
    try_render(scene, render_filepath, file_format, (512, 512))
    bpy.data.objects.remove(camera)


def save_background_file(scene, filepath, to_variant_folderpath):

    filename = get_filename_from_path(filepath)
    if filepath.endswith(".blend"):
        world = scene.world
        data_blocks = {world}
        write_path = os.path.join(to_variant_folderpath, filename)

        try:
            bpy.data.libraries.write(write_path, data_blocks)
        except:
            pass

    else:
        to_filepath = os.path.join(to_variant_folderpath, filename)
        shutil.copyfile(filepath, to_filepath)




