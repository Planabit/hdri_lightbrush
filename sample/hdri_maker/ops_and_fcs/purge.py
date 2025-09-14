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


import bpy

from ..exaconv import get_sckprop, get_ngprop
from ..utility.utility import get_in_out_group
from ..utility.utility import retrieve_nodes
from ..utility.utility_4 import get_ng_inputs, remove_ng_socket


def purge_all():
    count = 0
    orphan_ob = [o for o in bpy.data.objects if not o.users]
    count += len(orphan_ob)
    while orphan_ob:
        bpy.data.objects.remove(orphan_ob.pop())

    orphan_mesh = [m for m in bpy.data.meshes if not m.users]
    count += len(orphan_mesh)
    while orphan_mesh:
        bpy.data.meshes.remove(orphan_mesh.pop())

    orphan_mat = [mat for mat in bpy.data.materials if not mat.users]
    count += len(orphan_mat)
    while orphan_mat:
        bpy.data.materials.remove(orphan_mat.pop())

    count += purge_node_groups(count, bpy.data.node_groups[:])

    orphan_texture = [t for t in bpy.data.textures if not t.users]
    count += len(orphan_texture)
    while orphan_texture:
        bpy.data.textures.remove(orphan_texture.pop())

    orphan_images = [i for i in bpy.data.images if not i.users]
    count += len(orphan_images)
    while orphan_images:
        bpy.data.images.remove(orphan_images.pop())

    return count

def purge_deleted_node_tree(node_tree):
    id_data_string = repr(node_tree)
    is_material = id_data_string.startswith("bpy.data.materials")

    # Questa funzione è mirata ad eliminare il materiale / o nodo, i nodi gruppi in esso contenuti e le immagini
    nodes = retrieve_nodes(node_tree)
    images = []
    groups = []

    for n in nodes:
        if n.type == 'GROUP' and n.node_tree:
            groups.append(n.node_tree)
        elif n.type == 'TEX_IMAGE' and n.image:
            images.append(n.image)

    groups = set(groups)
    images = set(images)

    if is_material:
        mat_name = id_data_string[20:-12]
        mat = bpy.data.materials.get(mat_name)
        if mat and not mat.users:
            bpy.data.materials.remove(mat)

    purge_node_groups(0, groups)

    for i in images:
        if not i.users:
            bpy.data.images.remove(i)

def purge_node_groups(count, lista):
    orphan_node_group = [g for g in lista if not g.users]
    count += len(orphan_node_group)
    for g in orphan_node_group:
        lista.remove(g)
        bpy.data.node_groups.remove(g)

    new_list = [g for g in lista if not g.users]
    if new_list:
        count += purge_node_groups(count, new_list)

    return count

def purge_unused_inputs(node_tree, default='INPUTS'):
    # Rimuove gli inputs inutilizzati, stando attenti a non rimuovere i nodi Taggati con is_system_socket
    # e iterando tutti gli eventuali nodi di tipo 'GROUP_INPUT'
    node_inputs, node_outputs = get_in_out_group(node_tree)

    connected_list = []
    for n in node_inputs:
        for idx, out in enumerate(n.outputs):
            if out.type != 'CUSTOM':
                socket_input = get_ng_inputs(node_tree, idx)
                sckProp = get_sckprop(socket_input)
                if not sckProp.is_system_socket and not sckProp.api_color_ramp:
                    if out.is_linked:
                        connected_list.append((n, idx))

    sockets_to_remove = []
    sockets_inputs = get_ng_inputs(node_tree)
    for idx, i in enumerate(sockets_inputs):
        sckProp = get_sckprop(i)
        if not sckProp.is_system_socket and not sckProp.api_color_ramp:
            if idx not in [index for node, index in connected_list]:
                sockets_to_remove.append(i)

    sockets_to_remove = list(set(sockets_to_remove))
    for s in sockets_to_remove:
        remove_ng_socket(s)

def remove_unused_node_groups(mat):
    # Questa funzione elimina eventuali nodi di tipo exa rimasti scollegati
    # Specialmente il Mask node e il Normals
    # Solo nel node_tree del materiale!
    nodes = mat.node_tree.nodes

    n_groups = [n for n in nodes if n.type == "GROUP" if n.node_tree if get_ngprop(n.node_tree).self_tag]
    n_groups = list(set(n_groups))
    for n in n_groups:
        input_links = [i for i in n.inputs if i.is_linked]
        output_links = [o for o in n.outputs if o.is_linked]
        if not input_links and not output_links:
            nodes.remove(n)





