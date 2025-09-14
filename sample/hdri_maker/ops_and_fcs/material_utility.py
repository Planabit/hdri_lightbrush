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
import os

import bpy

from .node_tree_utils import restore_color_ramps_props
from ..exaconv import get_ndprop, get_ngprop, get_imgprop, get_matprop, get_sckprop
from ..utility.utility import image_has_data, sub_nodes, retrieve_nodes, has_nodetree
from ..utility.utility_4 import get_ng_inputs
from ..utility.utility_dependencies import set_colorspace_name


# Functions with low dependence

def restore_node_inputs_default_value(node):
    """Callback from BoolProperty Restore the node inputs to default value"""

    if not has_nodetree(node):
        return

    node_tree = node.node_tree
    ngProp = get_ngprop(node_tree)
    for iDx, inp in enumerate(node.inputs):
        try:
            # if ngProp.show_lock_prop:  <-- Questo per ora serve solo in HDRi Maker, in Extreme PBR risulta confuso per via dei troppi bottoni nel pannello
            socket_internal = get_ng_inputs(node.node_tree, index=iDx)
            sckProp = get_sckprop(socket_internal)
            if sckProp.lock_prop:
                # If the socket is locked (by the user) do not restore the default value
                continue
            internal_socket = get_ng_inputs(node.node_tree, index=iDx)
            inp.default_value = internal_socket.default_value
        except:
            print("Error: Can't restore the default value of the node: ", node.name, "Input name", inp.name)
            continue

    restore_color_ramps_props(node.node_tree.nodes)

    try:
        # A volte capita che i materiali abbiano attivo il Show tips, quindi importandoli si deve disattivare
        node_tree = node.node_tree
        ngProp = get_ngprop(node_tree)
        ngProp.ng_show_tips = False

    except Exception as e:
        print("Can't restore the default value of the node: ", node.name)
        pass



def get_node_from_self(self, context):
    node_tree = self.id_data
    nodes = node_tree.nodes
    for n in nodes:
        ndProp = get_ndprop(n)
        ndProp.self_id_name = n.name
    self_node = next((n for n in nodes if get_ndprop(n).self_id_name == self.self_id_name), None)
    return node_tree, self_node


def force_driver_nodes(mat):
    # Forza la riattivazione dei driver imporati da Node utility.
    # Per sicurezza va eseguito , altrimenti l'animazione potrebbe non partire
    if mat is not None and mat.use_nodes:
        if mat.node_tree.animation_data:
            for d in mat.node_tree.animation_data.drivers:
                d.driver.expression = d.driver.expression

        for n in mat.node_tree.nodes:
            for g in sub_nodes(n):
                if g.type == "GROUP" and g.node_tree and g.node_tree.animation_data:
                    for d in g.node_tree.animation_data.drivers:
                        d.driver.expression = d.driver.expression



def assign_node_texture(node_tex, imageDIr, colorSpace, mute_node):
    # Questa funzione per convenienza, può avere un input di tipo bpy.data.images oppure il filepath del file immagine
    if os.path.isfile(imageDIr):
        image_exist = bpy.data.images.get(ntpath.basename(imageDIr))
    else:
        image_exist = bpy.data.images.get(imageDIr)

    if image_exist:
        # Controllo ulteriore per capire se l'immagine esiste veramente e non è "Purple" ma ci sono problemi perchè
        # has_data non si aggiorna correttamente, penso finchè non si liberi dal ciclo for
        try:
            if image_has_data(image_exist):
                node_tex.image = image_exist
            else:
                node_tex.image = bpy.data.images.load(imageDIr)

        except:
            node_tex.image = bpy.data.images.load(imageDIr)

    else:
        node_tex.image = bpy.data.images.load(imageDIr)

    set_colorspace_name(node_tex.image, colorSpace)
    # node_tex.image.colorspace_settings.name = colorSpace
    imgProp = get_imgprop(node_tex.image)
    imgProp.self_tag = True

    if mute_node:
        node_tex.extremepbr_node_prop.mute_node = mute_node if mute_node is not None else False

    return node_tex.image


def return_if_exa_node_group(mat):
    # Per ora inutilizzata#
    # Questa funzione serve per capire se il materiale appeso è già gruppato o no
    # molto importate per capire se creare un nuovo gruppo in automatico dai materiali utenti
    is_exa_node_group = False
    for n in mat.node_tree.nodes:
        if n.type == 'GROUP':
            if n.node_tree:
                if get_ngprop(n.node_tree).group_id_name != "":
                    is_exa_node_group = True
    return is_exa_node_group


def eevee_default_settings(context):
    scn = context.scene
    if not scn.eevee.use_ssr:
        scn.eevee.use_ssr = True
    if not scn.eevee.use_ssr_refraction:
        scn.eevee.use_ssr_refraction = True



def set_switchs_to_existent(node_tree, update_non_color, use_custom_color=True):
    # Questa funzione, da chiamare con attenzione, aggiusta gli switch dei nodi utility, utile per Shader Maker
    # Imposta semplicemente 0-1 se presente o no un nodo texture con una texture inserita.
    # Cosi da non dove cancellare nessun nodo durante lo shader maker
    nodes = node_tree.nodes
    links = node_tree.links

    def set_exist(node, map_socket, map_exist, non_color_socket):

        if update_non_color:
            if non_color_socket: non_color_socket.default_value = 0.454

        if map_exist: map_exist_socket.default_value = 0
        if map_socket.is_linked:
            tex_node = map_socket.links[0].from_node
            if tex_node.type == 'TEX_IMAGE':
                if tex_node.image:
                    if not tex_node.mute and map_exist_socket:
                        map_exist_socket.default_value = 1
                    if tex_node.image.colorspace_settings.name == 'Non-Color':
                        if non_color_socket:
                            non_color_socket.default_value = 1

            elif tex_node.type != 'TEX_IMAGE':
                map_exist_socket.default_value = 1

    for n in nodes:
        if n.type == 'TEX_IMAGE':
            n.use_custom_color = use_custom_color
            if n.image:
                n.color = 0, 0.3, 0
            else:
                n.color = 0.7, 0, 0

        ndProp = get_ndprop(n)
        if ndProp.node_tag == 'MAP_CTRL_POST':
            if n.type == 'GROUP' and n.node_tree:
                map_exist_socket = n.inputs.get("Map Exist")
                non_color_socket = n.inputs.get("Non-Color") if update_non_color else None
                map_socket = n.inputs.get("Input Map")
                set_exist(n, map_socket, map_exist_socket, non_color_socket)
                n.use_custom_color = use_custom_color

                if not map_exist_socket:
                    return

                if map_exist_socket.default_value > 0:
                    n.color = 0, 0.3, 0
                else:
                    n.color = 0.7, 0, 0


def find_lost_image_path(image_list, search_path):
    # Funzione specializzata sulla ricerca di immagini e video perduti
    extreme_pbr_system_images = ['']

    lost_images = []
    for img in image_list:
        try:
            img.update()  # Forzare aggiornamento, altrimenti has_data sarrà sempre false
        except:
            pass
        if not image_has_data(
                img):  # Teniamo conto che le immagini create direttamente in Blender non hanno filepath, quindi sono tecnicamente presenti
            lost_images.append(img)

    if not lost_images:
        text = "No lost images found"
        return text

    lost_images = set(lost_images)
    for root, dirs, files in os.walk(search_path):
        for fn in files:
            for image in lost_images:
                if fn == ntpath.basename(image.filepath):
                    image.filepath_raw = os.path.join(root, fn)
                    lost_images.remove(image)
                    bpy.data.images[image.name].reload()
                    image.reload()
                    break

    # Restituisce una lista dei nomi delle immagini impossibili da trovare in quel percorso:
    if lost_images:
        lost_images_name = ""
        for i in lost_images:
            lost_images_name += "Image name: " + i.name + " File name: " + ntpath.basename(i.filepath)

        text = "These images were not found: " + lost_images_name + " Try searching in another location"
        return text

    else:
        text = "All images have been found"
        return text


def return_image_list(nodes):
    imageList = []
    for n in nodes:
        if n.type == 'TEX_IMAGE':
            if n.image:
                if n.image not in imageList:
                    imageList.append(n.image.id_data)
        if n.type == 'GROUP':
            if n.node_tree:
                for sN in sub_nodes(n):
                    if sN.type == 'TEX_IMAGE':
                        if sN.image:
                            if sN.image not in imageList:
                                imageList.append(sN.image.id_data)

    return imageList


def remove_nodegroup_by_group_id_name(mat, group_id_name):
    nodes = mat.node_tree.nodes
    nodes_to_remove = []
    for n in nodes:
        if n.type == 'GROUP':
            if n.node_tree:
                if get_ngprop(n.node_tree).group_id_name == group_id_name:
                    if n not in nodes_to_remove: nodes_to_remove.append(n)

    for n in nodes_to_remove:
        nodes.remove(n)


def get_images_into_material(mat, use_alert):
    # Funzione che restituisce le immagini univoche utilizzate in un materiale
    # Utile da chiamare per evitare il sorpassamento di 24 immagini in eevee quindi il limite di esso
    matProp = get_matprop(mat)

    node_with_images = []
    images = []
    images_in_use = []

    nodes = retrieve_nodes(mat.node_tree)
    for n in nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            node_with_images.append(n)
            images.append(n.image)
            if not n.mute and [o for o in n.outputs if o.is_linked]:
                # Se il nodo è connesso e non è in muto
                images_in_use.append(n.image)

    images_in_use = list(set(images_in_use))  # lista immagini univoche realmente utilizzate
    images = list(set(images))  # Lista immagini univoche non per forza in uso

    if use_alert:
        matProp.texture_alert = True if len(images_in_use) > 24 else False
        matProp.texture_in_use = 0
        for img in images_in_use:
            matProp.texture_in_use += 1

    return images_in_use, node_with_images, images












