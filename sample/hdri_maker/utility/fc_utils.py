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
import shutil

import bpy

from ..exaconv import get_scnprop
from ..exaproduct import Exa


def show_helps_v2(layout, docs_key='', icon='QUESTION', emboss=False, text=""):
    """This function is used to show the help button in the UI, the button will open the documentation in the browser,
    the key of the input (url_key) is the key of the dictionary in the file exa_manual.json, the value is the url of the documentation
    """
    docs = layout.operator(Exa.ops_name+"docs", text=text, icon=icon, emboss=emboss)
    docs.docs_key = docs_key
    return

def purgeOldImage():
    for wrl in bpy.data.worlds:
        if not wrl.users:
            if wrl.hdri_prop_world.world_hdri_maker:
                bpy.data.worlds.remove(wrl)

    for mat in bpy.data.materials:
        if not mat.users:
            if mat.hdri_prop_mat.mat_id_name == 'EEVEE_SHADOW_CATCHER':
                bpy.data.materials.remove(mat)

    for img in bpy.data.images:
        if not img.users:
            if img.hdri_prop_image.image_tag:
                bpy.data.images.remove(img)
            elif img.hdri_prop_image.image_tag_normal:
                bpy.data.images.remove(img)
            elif img.hdri_prop_image.image_tag_displace:
                bpy.data.images.remove(img)


# def purge_duplicate(scn):
#     def nodeTree(alberoDiNodi):
#         exposure = None
#         nodeGroupToDelete = []
#         for ng in bpy.data.node_groups:
#             if ng.name == 'HDRI_Maker_Exposure':
#                 exposure = ng
#             if 'HDRI_Maker_Exposure' in ng.name:
#                 nodeGroupToDelete.append(ng)
#
#         for n in alberoDiNodi:
#             if exposure:
#                 if n.name == 'HDRI_Maker_Exposure':
#                     if n.node_tree:
#                         if n.node_tree.name[-4] == '.' and n.node_tree.name[-3:].isnumeric():
#                             n.node_tree = exposure
#
#         for ng in nodeGroupToDelete:
#             if not ng.users:
#                 bpy.data.node_groups.remove(ng)
#
#     for m in bpy.data.materials:
#         if m.node_tree:
#             nodeTree(m.node_tree.nodes)
#
#     if scn.world:
#         if scn.world.use_nodes:
#             nodeTree(scn.world.node_tree.nodes)
#
#         if len(scn.world.name) > 4:
#             if scn.world.name[-4] == '.':
#                 if scn.world.name[-3:].isnumeric():
#                     scn.world.name = scn.world.name[:-4]




def remove_scene_by_scene_id_name(scene_id_name, reset_id_name_if_only_one_scene=True):
    if len(bpy.data.scenes) == 1:
        if reset_id_name_if_only_one_scene:
            scnProp = get_scnprop(bpy.data.scenes[0])
            scnProp.scene_id_name = ""
        return

    for scn in bpy.data.scenes:
        scnProp = get_scnprop(scn)
        if scnProp.scene_id_name == scene_id_name:
            bpy.data.scenes.remove(scn)
