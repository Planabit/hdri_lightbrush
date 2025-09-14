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
import ntpath

import bpy

from ..exaconv import get_ndprop, get_imgprop, get_txrprop, get_scnprop
from ..utility.utility import copy_attributes


def create_empty_world(name, scn, scnProp, use_now):
    new_world = bpy.data.worlds.new(name)
    new_world.use_nodes = True
    nodes = new_world.node_tree.nodes
    for n in nodes:
        nodes.remove(n)
    if use_now:
        scn.world = new_world

    from ..background_tools.background_fc import set_world_goodies
    set_world_goodies(new_world)

    return new_world


def create_node_utility(nodes, loc_x=None, loc_y=None, nodeName=None, label=None, nodeType=None, use_custom_color=None,
                        width=None, hide=False):

    """This function creates a node and positions it in the node tree, loc_x and loc_y are the coordinates of the node in the node tree"""

    node = nodes.new(type=nodeType)
    if nodeName:
        node.name = nodeName
    if label:
        node.label = label
    if loc_x:
        node.location[0] = loc_x
    if loc_y:
        node.location[1] = loc_y

    if use_custom_color:
        node.use_custom_color = True
        node.color = use_custom_color
    if width:
        node.width = width

    node.hide = hide

    ndProp = get_ndprop(node)
    ndProp.self_tag = True

    if nodeName:
        ndProp.node_id_name = nodeName

    return node


def create_data_texture(id_name, textureImage):
    reload_texture = bpy.data.textures.get(id_name)
    heightTex = reload_texture if reload_texture else bpy.data.textures.new(id_name, type='IMAGE')

    reload_image = bpy.data.images.get(ntpath.basename(textureImage))
    heightTex.image = reload_image if reload_image else bpy.data.images.load(textureImage)

    imgProp = get_imgprop(heightTex.image)
    imgProp.self_tag = True

    txrProp = get_txrprop(heightTex)
    txrProp.self_tag = True

    return heightTex


def create_scene(scene_from, scene_name="", scene_id_name="", copy_attr=False, copy_exa_attr=False, got_to_scene=True, recycle=True):

    new_scene = None
    if recycle:
        new_scene = bpy.data.scenes.get(scene_name)
        if new_scene and scene_id_name:
            if not new_scene.extremepbr_scene_prop.scene_id_name == scene_id_name:
                new_scene = None

    if not new_scene:
        new_scene = bpy.data.scenes.new(scene_name)
    if copy_attr:
        copy_attributes(scene_from, new_scene)
        copy_attributes(scene_from.render.bake, new_scene.render.bake)
    if copy_exa_attr:
        copy_attributes(scene_from.extremepbr_scene_prop, new_scene.extremepbr_scene_prop)

    scnProp = get_scnprop(new_scene)
    scnProp.scene_id_name = scene_id_name
    scnProp.self_tag = True
    if got_to_scene:
        bpy.context.window.scene = new_scene

    return new_scene
