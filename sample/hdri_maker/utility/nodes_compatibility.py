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
import time

import bpy

from ..exaconv import get_ndprop
from ..utility.utility import retrieve_nodes, get_all_blender_shadernodes, copy_attributes

def change_mix_node_status(mix_node, data_type = 'RGBA'):
    """Il nuovo mix node è veramente assurdo, quindi ogni inputs, cambia in base a se data_type è RGBA"""
    links = mix_node.id_data.links

    # Get links inputs links
    inputs = {}
    idx = -1
    for i in mix_node.inputs:
        if not i.enabled:  # Questo riconosce i socket che sono realmente mostrati nella UI
            continue
        if i.is_linked:
            idx += 1
            inputs[idx] = i.links[0].from_socket

    # Get links outputs links
    outputs = {}
    idx = -1
    for o in mix_node.outputs:
        if not o.enabled:
            continue
        if o.is_linked:
            idx += 1
            outputs[idx] = o.links[0].to_socket

    mix_node.data_type = data_type

    # Restore links
    for i in mix_node.inputs:
        if not i.enabled:
            continue

        if idx in inputs:
            links.new(inputs[idx], i)

    for o in mix_node.outputs:
        if not o.enabled:
            continue

        if idx in outputs:
            links.new(o, outputs[idx])


def repair_unrecognized_nodes(node_tree, mix_node_ad_mix_rgb=False):
    """Repair unrecognized nodes"""
    # Get the unrecognized nodes:
    time_start = time.time()
    node_list = retrieve_nodes(node_tree)
    unrecognized = []
    mix_rgb = []
    for n in node_list:
        if n.type == 'GROUP':
            continue
        if n.type == '' or n.bl_idname.lower() == 'nodeundefined':
            # In this case the node is not recognized, so we have to replace it with the same node type, by input and output
            unrecognized.append(n)
        if bpy.app.version > (3, 3, 0):
            # Qui per un pasticcio precedente, veniva rimpiazzato il nodo Mix RGB con il nuovo nodo Mix, ma non veniva
            # settato il parametro "data_type" a "RGBA", quindi nel caso non ci siano node_attributes nel nodo, significa
            # che non essendo stati memorizzati attributi, il nodo è ancora di vecchio stampo, quindi sicuro va messo a Mix RGBA
            if get_ndprop(n).node_attributes != "":
                # In questo caso ci sono gli attributi, quindi non c'è bisogno di fare nulla
                continue
            if n.bl_idname == "ShaderNodeMix" and n.data_type != "RGBA":
                # Sistemiamo il pasticcio del Mix RGB causato da Extreme PBR patch
                change_mix_node_status(n, data_type='RGBA')

    if not unrecognized:
        return

    unrecognized = list(set(unrecognized))

    for n in unrecognized:
        # Tutti i nodi in cui abbiamo registrato le proprietà prima di rilasciare la versione dell'addon, possono essere
        # Retro-compatibili con le versioni precedenti.
        result = restore_node_attributes_if_node_unknow(n)
        if result:
            continue

        if is_separate_rgb(n, replace=True):
            continue

        if is_combine_rgb(n, replace=True):
            continue

        if is_new_mix_rgb(n, replace=True):
            continue

    print("Repair unrecognized nodes: %s seconds" % (time.time() - time_start))



def store_node_attributes_into_node_tree(node_tree, node=None):
    """We store the data, because Blender changes the nodes suddenly, so between the versions, there may be problems of
    retro-compatibility imminent (See MixRGB node version 3.4 and previous)"""

    node_list = retrieve_nodes(node_tree)
    # Make node_list without duplicates:
    node_list = list(set(node_list))

    # Ora facciamo lo store degli attributi per ogni nodo e li mettiamo in node_attributes: StringProperty()
    # Solo se il node bl_idname è diverso da ""

    for n in node_list:
        if node:
            if n != node:
                continue

        if n.type == '' or n.bl_idname.lower() == 'nodeundefined':
            continue

        # Store the node attributes:
        string_attr = ""
        for key in n.bl_rna.properties.keys():
            attribute = getattr(n, key)
            if key == "":
                continue
            if "bpy_struct" in str(attribute):
                continue
            if "bpy_prop_collection" in str(attribute):
                continue

            if "bpy_collection" in str(attribute):
                continue

            if key in ["location" , "width", "width_hidden", "height=", "dimensions"]:
                continue

            if key in ['bl_height_max', 'bl_height_min', 'bl_icon', 'bl_width_default',
                       'bl_width_max', 'bl_width_min', 'bl_static_type', 'bl_height_default']:
                # Questi attributi non servono
                continue

            string_attr += str(key) + "==" + str(attribute) + "&&" + str(type(attribute)) + "++"

        ndProp = get_ndprop(n)
        ndProp.node_attributes = string_attr

    return node_list


def restore_node_attributes_if_node_unknow(node):
    """Qui in sostanza, deve analizzare i vecchi attributi se esistono, e modificare il nodo con quelli vecchi o con quelli nuovi"""

    if not node.type == '' or not node.bl_idname.lower() == 'nodeundefined':
        # Se il nodo è riconosciuto, non facciamo nulla
        return

    nd_prop = get_ndprop(node)
    if not nd_prop.node_attributes:
        # Se non ci sono attributi, non facciamo nulla
        return

    # Se ci sono attributi, li analizziamo:

    attr_dict = {}
    attributes = nd_prop.node_attributes.split("++")
    for a in attributes:
        if a == "":
            continue

        if not "==" in a or not "&&" in a:
            continue
        attr_type = a.split("&&")[-1]
        key_value = a.split("&&")[0]

        key = key_value.split("==")[0]
        value = key_value.split("==")[1]
        attr_dict[key] = value

    # ShaderNodeMix Is the new MixRGB from 3.4 version
    # ShaderNodeMixRGB is the old MixRGB from previous versions
    # If the user save the project into 3.4 version, and then open it into previous versions, the node is not recognized
    bl_idname = attr_dict.get("bl_idname")

    new_node = False
    if bpy.app.version < (3, 4, 0):
        if bl_idname == 'ShaderNodeMix':
            # Creiamo un nuovo nodo MixRGB nella versione precedente
            new_node = node.id_data.nodes.new('ShaderNodeMixRGB')
            # Mi servono gli attributi Blend_type, Fac, Color1, Color2
            blend_type = attr_dict.get("blend_type")
            if blend_type and hasattr(new_node, "blend_type"):
                new_node.blend_type = blend_type

    if bpy.app.version < (3, 3, 0):
        if bl_idname == 'ShaderNodeSeparateColor':
            new_node = node.id_data.nodes.new('ShaderNodeSeparateRGB')
        elif bl_idname == 'ShaderNodeCombineColor':
            new_node = node.id_data.nodes.new('ShaderNodeCombineRGB')

    if new_node:
        # Try to copy many attributes:
        node_tree = node.id_data
        store_node_attributes_into_node_tree(node_tree, node = new_node) # Visto che il nuovo nodo non avrà gli attributi, li aggiungiamo
        copy_attributes(node, new_node)
        copy_location(node, new_node)
        restore_links_by_old_node(old_node=node, new_node=new_node, remove_old_node=True)
        return True


def restore_links_by_old_node(old_node, new_node, remove_old_node=False):
    """Ristora i Links"""
    # Copiamo i link:
    nodes = old_node.id_data.nodes
    links = old_node.id_data.links

    idx = -1
    for i in old_node.inputs:
        if not i.enabled:  # Questo riconosce i socket che sono realmente mostrati nella UI
            continue
        # Real index:
        idx += 1
        if not i.is_linked:
            continue
        for l in i.links:
            links.new(l.from_socket, new_node.inputs[idx])

    idx = -1
    for o in old_node.outputs:
        if not o.enabled:
            continue
        idx += 1
        if not o.is_linked:
            continue
        for l in o.links:
            links.new(new_node.outputs[idx], l.to_socket)

    if remove_old_node:
        nodes.remove(old_node)
    nodes.update()


def copy_location(node, new_node):
    # Se il nodo node è parentato con un frame, allora il nuovo nodo deve essere parentato con lo stesso frame e deve trovarsi nella posizione del frame e non in quella del nodo
    if node.parent:
        new_node.parent = node.parent

    new_node.location = node.location


def is_new_mix_rgb(node, replace=False):
    """Check if the node is a new mix rgb node (From 3.4 version) is not retro-compatible with previous versions"""
    actual_inputs_name = [i.name.upper() for i in node.inputs]
    if bpy.app.version < (3, 4, 0):
        new_mix_rgb_inputs = ['FAC', 'COLOR1', 'COLOR2']
    elif bpy.app.version >= (3, 4, 0) and bpy.app.version < (4, 0, 0):
        new_mix_rgb_inputs = ['FACTOR', 'FACTOR', 'A', 'B', 'A', 'B', 'A', 'B']
    elif bpy.app.version >= (4, 0, 0):
        new_mix_rgb_inputs = ['FACTOR', 'FACTOR', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']

    # Controlla le liste ma senza controllare l'ordine
    if sorted(actual_inputs_name) != sorted(new_mix_rgb_inputs) and not replace:
        return False

    if not replace:
        return True

    if replace:
        # Replace the node with the old mix rgb node

        old_mix_rgb = node.id_data.nodes.new('ShaderNodeMixRGB')
        copy_attributes(node, old_mix_rgb)
        copy_location(node, old_mix_rgb)
        restore_links_by_old_node(old_node=node, new_node=old_mix_rgb, remove_old_node=True)
        return True


def is_separate_rgb(n, replace=False):
    """Check if the unknown node is a separate RGB node"""

    # Len inputs:
    if len(n.inputs) != 1:
        return False
    # Len outputs:
    if len(n.outputs) != 3:
        return False

    if n.inputs[0].type != 'RGBA':
        return False

    # Check if all outputs are VALUE type:
    for output in n.outputs:
        if output.type != 'VALUE':
            return False

    if not replace:
        return True

    if bpy.app.version < (3, 3, 0):
        # Create a new node:
        new_node = n.id_data.nodes.new('ShaderNodeSeparateRGB')
        copy_location(n, new_node)
        restore_links_by_old_node(n, new_node, remove_old_node=True)


def is_combine_rgb(n, replace=False):
    """Check if the unknown node is a combine RGB node"""
    # Len inputs:
    if len(n.inputs) != 3:
        return False
    # Len outputs:
    if len(n.outputs) != 1:
        return False

    if n.outputs[0].type != 'RGBA':
        return False

    # Check if all inputs are VALUE type:
    for n_input in n.inputs:
        if n_input.type != 'VALUE':
            return False

    if not replace:
        return True

    if bpy.app.version < (3, 3, 0):
        # Create a new node:
        new_node = n.id_data.nodes.new('ShaderNodeCombineRGB')
        copy_location(n, new_node)
        restore_links_by_old_node(n, new_node, remove_old_node=True)




