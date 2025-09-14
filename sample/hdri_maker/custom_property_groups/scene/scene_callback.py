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

from ...collections_scene.collection_fc import get_dome_collection
from ...dome_tools.dome_fc import get_dome_objects
from ...exaconv import get_scnprop, get_objprop
from ...library_manager.get_library_utils import risorse_lib
from ...utility.utility import hide_object, get_view_3d_area, has_nodetree, retrieve_nodes


def update_materials_colorspace(self, context):
    """Search All HDRi Maker Materials/World nodes in the context.scene and change the colorspace in the TEX_IMAGE/TEX_ENVIRONMENT nodes"""
    scn = context.scene
    world = scn.world
    color_space = self.materials_colorspace

    mat_list = [] # List of materials to update

    # Get the dome material if exists
    dome_objects_dict = get_dome_objects()
    dome_material = dome_objects_dict.get('DOME_MATERIAL')
    if dome_material:
        mat_list.append(dome_material)

    # Get the world material if exists:
    if world and has_nodetree(world):
        mat_list.append(world)

    for mat in mat_list:
        nodes = retrieve_nodes(mat.node_tree)

        for n in nodes:
            if n.type in ['TEX_IMAGE', 'TEX_ENVIRONMENT']:
                if not n.image:
                    continue
                try:
                    n.image.colorspace_settings.name = color_space
                except:
                    print("Error: Can't change the colorspace of the node: ", n.name, "In the material: ", mat.name)
                    pass


def update_dome_wireframe(self, context):
    scn = context.scene
    for ob in scn.objects:
        if ob.hdri_prop_obj.object_id_name in ['HDRI_MAKER_DOME_GROUND', 'HDRI_MAKER_DOME_SKY']:
            ob.show_wire = self.show_dome_wireframe

    if self.show_dome_wireframe:
        area = get_view_3d_area()
        if area:
            area.overlay.show_overlays = True

def update_hide_hooks(self, context):
    tools_col = get_dome_collection(create=False)
    if not tools_col:
        return

    for ob in tools_col.objects:
        objProp = get_objprop(ob)
        if objProp.object_id_name == 'DOME_HOOK':
            hide_object(ob, self.hide_hooks)

    if not self.hide_hooks:
        area = get_view_3d_area()
        if area:
            area.overlay.show_overlays = True



def hide_unide_dome(self, context):
    scn = context.scene
    tools_col = get_dome_collection(create=False)
    if not tools_col:
        return
    for ob in tools_col.objects:
        hide_object(ob, self.hide_dome)

def update_empty_type(self, context):
    for o in context.scene.objects:
        if o.hdri_prop_obj.object_id_name != 'DOME_HOOK':
            continue

        if o.type == 'EMPTY':
            o.empty_display_type = self.hooks_display_type


def update_hooks_type(self, context):
    for ob in context.scene.objects:
        objProp = get_objprop(ob)
        if objProp.object_id_name == 'DOME_HOOK':
            ob.empty_display_type = self.hooks_display_type


def update_hooks_display_size(self, context):
    for ob in context.scene.objects:
        objProp = get_objprop(ob)
        if objProp.object_id_name == 'DOME_HOOK':
            ob.empty_display_size = self.hooks_display_size


def update_fog_details(self, context):
    scn = context.scene
    scnProp = scn.hdri_prop_scn

    listaOpzioni = scnProp.fog_detail.split('_')
    scn.eevee.volumetric_tile_size = listaOpzioni[0]
    scn.eevee.volumetric_samples = int(listaOpzioni[1])
    scn.cycles.volume_max_steps = int(listaOpzioni[2])
    scn.eevee.use_volumetric_lights = True
    scn.eevee.use_volumetric_shadows = True



def updatebackground(self, context):
    # TODO: Obsoleta
    return


class ScnCall:
    utils_list = []
    shader_type = ""


def enum_node_utility(self, context):
    shader_type = context.space_data.shader_type
    if shader_type == 'OBJECT':
        nodes_folder = 'material_node_utility'
    elif shader_type == 'WORLD':
        nodes_folder = 'world_node_utility'
    else:
        ScnCall.utils_list = [("CONTEXT_ERROR", "Context Error", "")]
        return

    if shader_type == ScnCall.shader_type:
        return ScnCall.utils_list

    ScnCall.utils_list.clear()

    node_utils_directory = os.path.join(risorse_lib(), "node_groups", nodes_folder)
    dirListing = os.listdir(node_utils_directory)
    dirListing.sort()

    for idx, item in enumerate(dirListing):
        if item.lower().endswith('.blend') and not item.startswith("."):
            path_to_blend = os.path.join(node_utils_directory, item)
            name = item[:-6]
            # name = item.replace("X_PBR_Utility_", "").replace("_", " ")
            ScnCall.utils_list.append((path_to_blend, name, "", idx))

    utils_list = sorted(ScnCall.utils_list, key=lambda x: x[1])

    return utils_list


def update_shadow_preferences(self, context):
    scn = context.scene
    eevee = scn.eevee

    shadow_detail = self.shadow_detail

    if shadow_detail == 'VERY_LOW':
        shadow_cube_size, shadow_cascade_size, use_shadow_high_bitdepth, use_soft_shadows = '64', '64', False, False
    elif shadow_detail == 'LOW':
        shadow_cube_size, shadow_cascade_size, use_shadow_high_bitdepth, use_soft_shadows = '256', '512', False, True
    elif shadow_detail == 'DEFAULT':
        shadow_cube_size, shadow_cascade_size, use_shadow_high_bitdepth, use_soft_shadows = '512', '1024', False, True
    elif shadow_detail == 'HIGH':
        if eevee.taa_render_samples < 32:
            eevee.taa_render_samples = 32
        if eevee.taa_samples < 32:
            eevee.taa_samples = 32
        shadow_cube_size, shadow_cascade_size, use_shadow_high_bitdepth, use_soft_shadows = '1024', '2048', False, True
    elif shadow_detail == 'VERY_HIGH':
        if eevee.taa_render_samples < 64:
            eevee.taa_render_samples = 64
        if eevee.taa_samples < 64:
            eevee.taa_samples = 64
        shadow_cube_size, shadow_cascade_size, use_shadow_high_bitdepth, use_soft_shadows = '2048', '2048', True, True
    elif shadow_detail == 'ULTRA':
        if eevee.taa_render_samples < 128:
            eevee.taa_render_samples = 128
        if eevee.taa_samples < 128:
            eevee.taa_samples = 128
        shadow_cube_size, shadow_cascade_size, use_shadow_high_bitdepth, use_soft_shadows = '4096', '4096', True, True

    if bpy.app.version < (4, 2, 0):
        # Deprecated in Blender 4.2 https://developer.blender.org/docs/release_notes/4.2/python_api/
        eevee.shadow_cube_size = shadow_cube_size
        eevee.shadow_cascade_size = shadow_cascade_size

    eevee.use_shadow_high_bitdepth = use_shadow_high_bitdepth
    eevee.use_soft_shadows = use_soft_shadows

def update_volumetric_preferences(self, context):
    volumetric_detail = self.volumetric_detail

    if volumetric_detail == 'VERY_LOW':
        # First row is Cycles render, second row is Eevee render
        volume_step_rate, volume_preview_step_rate, volume_max_steps = 4.0, 4.0, 32
        volumetric_tile_size, volumetric_samples, volumetric_sample_distribution, use_volumetric_shadows = '16', 16, 0.6, False
    elif volumetric_detail == 'LOW':
        volume_step_rate, volume_preview_step_rate, volume_max_steps = 2.0, 2.0, 64
        volumetric_tile_size, volumetric_samples, volumetric_sample_distribution, use_volumetric_shadows = '8', 32, 0.7, False
    elif volumetric_detail == 'DEFAULT':
        volume_step_rate, volume_preview_step_rate, volume_max_steps = 2.0, 2.0, 128
        volumetric_tile_size, volumetric_samples, volumetric_sample_distribution, use_volumetric_shadows = '8', 64, 0.8, False
    elif volumetric_detail == 'HIGH':
        volume_step_rate, volume_preview_step_rate, volume_max_steps = 1.0, 1.0, 256
        volumetric_tile_size, volumetric_samples, volumetric_sample_distribution, use_volumetric_shadows = '4', 128, 0.9, False
    elif volumetric_detail == 'VERY_HIGH':
        volume_step_rate, volume_preview_step_rate, volume_max_steps = 0.5, 0.5, 1024
        volumetric_tile_size, volumetric_samples, volumetric_sample_distribution, use_volumetric_shadows = '2', 128, 1.0, False
    elif volumetric_detail == 'ULTRA':
        volume_step_rate, volume_preview_step_rate, volume_max_steps = 0.1, 0.1, 1024
        volumetric_tile_size, volumetric_samples, volumetric_sample_distribution, use_volumetric_shadows = '2', 256, 1.0, True

    scn = context.scene
    eevee = scn.eevee
    cycles = scn.cycles

    eevee.use_volumetric_lights = True
    eevee.use_volumetric_shadows = use_volumetric_shadows
    eevee.volumetric_tile_size = volumetric_tile_size
    eevee.volumetric_samples = volumetric_samples
    eevee.volumetric_sample_distribution = volumetric_sample_distribution

    cycles.volume_step_rate = volume_step_rate
    cycles.volume_preview_step_rate = volume_preview_step_rate
    cycles.volume_max_steps = volume_max_steps


