# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Copyright 2024(C) Andrea Donati
#
import bpy
from .exaproduct import Exa


class ItemsVersion:
    # Qui ci vanno
    dome_version = 2.0


def get_default_library_folder_name():
    """Return the default library folder name"""
    if Exa.product == 'EXTREME_PBR':
        return 'EXTREME_PBR_DEFAULT_LIB'
    elif Exa.product == 'HDRI_MAKER':
        return 'HDRI_MAKER_DEFAULT_LIB'


def get_user_library_folder_name():
    """Return the user library folder name"""
    if Exa.product == 'EXTREME_PBR':
        return "EXTREME_PBR_USER_LIB"
    elif Exa.product == 'HDRI_MAKER':
        return "HDRI_MAKER_USER_LIB"


def k_size_base(minimum=1, maximum=18):

    k_strings = []
    for n in range(minimum, maximum):
        k_strings.append(str(n) + "k")
    return k_strings


def get_wimaprop():
    """Get the window manager 'extremepbr_wima_prop' property"""
    wimaProp = None
    if Exa.product == 'EXTREME_PBR':
        wimaProp = bpy.context.window_manager.extremepbr_wima_prop
    elif Exa.product == 'HDRI_MAKER':
        wimaProp = bpy.context.window_manager.hdrimaker_wima_prop

    return wimaProp


def get_scnprop(scn):
    """Get the scene 'extremepbr_scene_prop' property if the addon is extreme pbr, otherwise return the 'hdri_prop_scene' property"""
    scnProp = None
    if Exa.product == 'EXTREME_PBR':
        scnProp = scn.extremepbr_scene_prop
    elif Exa.product == 'HDRI_MAKER':
        scnProp = scn.hdri_prop_scn
    return scnProp


def get_matprop(mat):
    """Get the material 'extremepbr_material_prop' property if the addon is extreme pbr, otherwise return the 'hdri_prop_mat' property"""
    matProp = None
    if Exa.product == 'EXTREME_PBR':
        matProp = mat.extremepbr_material_prop
    elif Exa.product == 'HDRI_MAKER':
        matProp = mat.hdri_prop_mat
    return matProp


def get_objprop(ob):
    """Get the object 'extremepbr_object_prop' property if the addon is extreme pbr, otherwise return the 'hdri_prop_obj' property"""
    objProp = None
    if Exa.product == 'EXTREME_PBR':
        objProp = ob.extremepbr_object_prop
    elif Exa.product == 'HDRI_MAKER':
        objProp = ob.hdri_prop_obj
    return objProp


def get_ngprop(node_tree):
    """Get the node tree 'extremepbr_node_tree_prop' property if the addon is extreme pbr, otherwise return the 'hdri_prop_node_tree' property"""
    ngProp = None
    if Exa.product == 'EXTREME_PBR':
        ngProp = node_tree.extremepbr_ngroup_prop
    elif Exa.product == 'HDRI_MAKER':
        ngProp = node_tree.hdri_prop_nodetree
    return ngProp


def get_imgprop(image):
    """Get the image 'extremepbr_image_prop' property if the addon is extreme pbr, otherwise return the 'hdri_prop_image' property"""
    imgProp = None
    if Exa.product == 'EXTREME_PBR':
        imgProp = image.extremepbr_image_prop
    elif Exa.product == 'HDRI_MAKER':
        imgProp = image.hdri_prop_image
    return imgProp


def get_txrprop(texture):
    txrProp = None
    if Exa.product == 'EXTREME_PBR':
        txrProp = texture.extremepbr_textures_prop
    elif Exa.product == 'HDRI_MAKER':
        txrProp = texture.hdri_prop_texture
    return txrProp


def get_wrlprop(world):
    wrlProp = None
    if Exa.product == 'EXTREME_PBR':
        wrlProp = world.extremepbr_world_prop
    elif Exa.product == 'HDRI_MAKER':
        wrlProp = world.hdri_prop_world
    return wrlProp


def get_brsprop(brush):
    brsProp = None
    if Exa.product == 'EXTREME_PBR':
        brsProp = brush.extremepbr_brush_prop
    elif Exa.product == 'HDRI_MAKER':
        brsProp = brush.hdri_prop_brush
    return brsProp


def get_sckprop(socket):
    sckProp = None
    if Exa.product == 'EXTREME_PBR':
        sckProp = socket.extremepbr_socket_prop
    elif Exa.product == 'HDRI_MAKER':
        sckProp = socket.hdri_prop_socket
    return sckProp


def get_ndprop(node):
    ndProp = None
    if Exa.product == 'EXTREME_PBR':
        ndProp = node.extremepbr_node_prop
    elif Exa.product == 'HDRI_MAKER':
        ndProp = node.hdri_prop_nodes
    return ndProp

def get_colprop(collection):
    colProp = None
    if Exa.product == 'EXTREME_PBR':
        colProp = collection.extremepbr_node_prop
    elif Exa.product == 'HDRI_MAKER':
        colProp = collection.hdri_prop_collection

    return colProp


def get_meshprop(ob_data):
    meshProp = None
    if Exa.product == 'EXTREME_PBR':
        meshProp = ob_data.extremepbr_mesh_prop
    elif Exa.product == 'HDRI_MAKER':
        meshProp = ob_data.hdri_prop_mesh
    return meshProp
