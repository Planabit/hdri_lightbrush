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

from ..bpy_data_libraries_load.data_lib_loads import load_libraries_world, load_libraries_node_group
from ..exaconv import get_ngprop, get_sckprop, get_wrlprop, get_ndprop, get_imgprop
from ..exaproduct import Exa
from ..library_manager.get_library_utils import risorse_lib
from ..ops_and_fcs.create_tools import create_node_utility
from ..standard_utils import StandardUtils
from ..utility.copy_node_tree import create_group_from_node_tree, get_links_dict
from ..utility.fc_utils import purgeOldImage
from ..utility.text_utils import draw_info
from ..utility.utility import has_nodetree, get_in_out_group, \
    get_nodes_ranges_xy, purge_all_group_names
from ..utility.utility_4 import new_ng_socket, get_internal_socket
from ..utility.utility_dependencies import align_node_xy


def create_basic_world(scene):
    world = bpy.data.worlds.new(name='World')
    world.use_nodes = True
    scene.world = world
    wrlProp = get_wrlprop(world)
    wrlProp.world_id_name = 'BASIC_WORLD'
    set_world_goodies(world)


def assign_image_to_background_node(image, world=None, environment='COMPLETE'):
    if not world:
        world = bpy.context.scene.world
    if not world or not world.use_nodes:
        return

    node_tree = world.node_tree
    nodes = node_tree.nodes

    label_name = image.name.replace("_", " ").split(".")[0].title()

    img_prop = get_imgprop(image)
    if not img_prop.image_id_name:
        img_prop.image_id_name = image.name

    mixer = None
    for n in nodes:
        if not has_nodetree(n):
            continue
        ngProp = get_ngprop(n.node_tree)
        if ngProp.group_id_name == 'MIXER':
            mixer = n
            break

    if not mixer:
        complete_node_group = next(
            (n for n in nodes if has_nodetree(n) if get_ngprop(n.node_tree).group_id_name == 'COMPLETE'),
            None)
        if not complete_node_group:
            complete_node_group = load_background_node(node_tree, rename=label_name, node_task='COMPLETE')
        for n in complete_node_group.node_tree.nodes:
            if n.type == 'TEX_ENVIRONMENT':
                n.image = image

        complete_node_group.name = complete_node_group.label = complete_node_group.node_tree.name = label_name
        return complete_node_group

    diffuse, light = get_diffuse_and_light_nodes(mixer)

    if environment == 'DIFFUSE':
        if not diffuse:
            diffuse = load_background_node(node_tree, rename=label_name, node_task='DIFFUSE')

        for n in diffuse.node_tree.nodes:
            if n.type == 'TEX_ENVIRONMENT':
                n.image = image

        diffuse.name = diffuse.label = diffuse.node_tree.name = label_name

        return diffuse

    if environment in ['LIGHT']:
        if not light:
            light = load_background_node(node_tree, rename=label_name, node_task='LIGHT')

        for n in light.node_tree.nodes:
            if n.type == 'TEX_ENVIRONMENT':
                n.image = image

        light.name = light.label = light.node_tree.name = label_name

        return light


def get_nodes_dict(node_tree):
    """Get the [MIXER, VECTOR, COMPLETE, DIFFUSE, LIGHT, OUTPUT_WORLD/OUTPUT_MATERIAL] nodes from the node tree
    :return: dict of nodes with these keys: [MIXER, VECTOR, COMPLETE, DIFFUSE, LIGHT, OUTPUT_WORLD/OUTPUT_MATERIAL]"""

    nodes = node_tree.nodes
    nodes_dict = {}
    for n in nodes:
        if has_nodetree(n):
            ngProp = get_ngprop(n.node_tree)

            if ngProp.group_id_name in ['MIXER', 'VECTORS', 'COMPLETE', 'DIFFUSE', 'LIGHT', 'VOLUMETRIC']:
                nodes_dict[ngProp.group_id_name] = n

        # Get the world output node, important to know if the node tree is a background node complete or not
        elif n.type in ['OUTPUT_WORLD', 'OUTPUT_MATERIAL']:
            # if node_tree.active_output == n: <-- this seems too fussy
            if n.inputs[0].is_linked or n.inputs[1].is_linked:
                nodes_dict['OUTPUT_WORLD'] = n

    return nodes_dict


def flip_diffuse_to_light(self, context):
    """Flip the diffuse and light nodes in the mixer node, so the light node change to diffuse and vice versa"""
    world = context.scene.world
    if not world or not world.use_nodes:
        return

    node_tree = world.node_tree
    links = node_tree.links
    node_dict = get_nodes_dict(node_tree)
    mixer = node_dict.get("MIXER")
    if not mixer:
        return
    # First try to get the diffuse and light nodes from the mixer node and their links
    diffuse, light = get_diffuse_and_light_nodes(mixer)

    # Try to get the diffuse and light nodes from the node tree by the group_id_name:
    if not diffuse or not light:
        # TODO: Qui ci soffermiamo a creare una funzione "Solve Node Problem" che risolve i problemi di nodi nel caso l'utente abbia pasticciato con i nodi
        diffuse = node_dict.get("DIFFUSE")
        light = node_dict.get("LIGHT")
        mixer = node_dict.get("MIXER")
        links.new(diffuse.outputs[0], mixer.inputs[0])
        links.new(light.outputs[0], mixer.inputs[1])

    if diffuse and light:
        # TODO: Riflettere sul fatto che i nodi LIGHT e DIFFUSE possano essere anche di tipo Nodo Standard e non gruppo
        if has_nodetree(diffuse):
            get_ngprop(diffuse.node_tree).group_id_name = 'LIGHT'
        else:
            get_ndprop(diffuse).node_id_name = 'LIGHT'
        if has_nodetree(light):
            get_ngprop(light.node_tree).group_id_name = 'DIFFUSE'
        else:
            get_ndprop(light).node_id_name = 'DIFFUSE'

        diffuse_location = diffuse.location[:]
        light_location = light.location[:]

        from_diffuse = diffuse.outputs[0]
        to_diffuse = diffuse.outputs[0].links[0].to_socket

        from_light = light.outputs[0]
        to_light = light.outputs[0].links[0].to_socket

        if to_diffuse.name == 'Diffuse':
            links.new(from_diffuse, to_light)
            links.new(from_light, to_diffuse)

        diffuse.location = light_location
        light.location = diffuse_location

    align_hdri_maker_nodes(node_tree)


def import_hdri_maker_world(context, world_name="HDRi Maker World", rename="", add_to_current_scene=True, reuse=False):
    """Import the HDRi Maker World (3.x Series) base structure in the current project"""
    scn = context.scene
    tools_version = StandardUtils.hdri_maker_tools_version

    if reuse:
        if scn.world:
            if context.scene.world.hdri_prop_world.world_hdri_maker_version == tools_version:
                scn.world.name = rename
                return scn.world

    blend_world_path = os.path.join(risorse_lib(), "blendfiles", "worlds", "hdri_standard_world.blend")
    world = load_libraries_world(blend_world_path, world_name=world_name, rename=rename)

    wrlProp = world.hdri_prop_world
    wrlProp.world_hdri_maker = True
    wrlProp.world_hdri_maker_version = tools_version
    if add_to_current_scene:
        context.scene.world = world

    # for w in bpy.data.worlds:
    #     if w != world:
    #         wrlProp = get_wrlprop(w)
    #         if wrlProp.world_id_name:
    #             bpy.data.worlds.remove(w)

    set_world_goodies(world)

    return world


def delete_world(self, context):
    """Delete the current scene.world"""
    scn = context.scene
    if scn.world:
        bpy.data.worlds.remove(scn.world)
    purgeOldImage()


def get_diffuse_and_light_nodes(mixer):
    """Get the Diffuse and Light nodes from the mixer node"""
    n1 = n2 = None
    for idx, input in enumerate(mixer.inputs):
        if not input.is_linked:
            continue
        if input.name == 'Diffuse':
            n1 = input.links[0].from_node
        elif input.name == 'Light':
            n2 = input.links[0].from_node

    return n1, n2


def load_mixer(node_tree, create_node=True, mixer_type='LIGHT_MIXER'):
    nodes = node_tree.nodes
    links = node_tree.links

    # Il nome del mixer sarà esattamente il nome del tipo, e dovrà chiamare sempre il nome del file esempio:
    # LIGHT_MIXER = Light Mixer.blend oppure Z_MIXER = Z Mixer.blend e i nomi saranno di conseguenza Light Mixer e Z Mixer
    mixer_name = mixer_type.replace("_", " ").title()
    mixer_filename = mixer_name + ".blend"

    output_node = node_tree.get_output_node('ALL')
    if not output_node:
        output_node = create_node_utility(nodes, 0, 0, "Light Mixer", "Light Mixer",
                                          'ShaderNodeOutputWorld', None,
                                          150, False)

    mixer_path = os.path.join(risorse_lib(), "node_groups", "world_node_utility", mixer_filename)
    mixer_nodetree = load_libraries_node_group(mixer_path, mixer_name, mixer_name)
    get_ngprop(mixer_nodetree).group_id_name = 'MIXER'
    get_ngprop(mixer_nodetree).mixer_type = mixer_type

    if create_node:
        mixer_node = create_node_utility(nodes, output_node.location.x - 350, output_node.location.y, mixer_name,
                                         mixer_name, 'ShaderNodeGroup', None,
                                         150, False)

        mixer_node.node_tree = mixer_nodetree
        return mixer_node

    else:
        return mixer_nodetree


def load_vector_node(node_tree, create_node=True):
    nodes = node_tree.nodes
    links = node_tree.links

    vector_path = os.path.join(risorse_lib(), "node_groups", "world_node_utility", "HDRi_Maker_World_Vector_v1.blend")
    vector_nodetree = load_libraries_node_group(vector_path, "HDRi_Maker_World_Vector_v1", "HDRi_Maker_World_Vector_v1")
    get_ngprop(vector_nodetree).group_id_name = 'VECTORS'

    if create_node:
        vector_node = create_node_utility(nodes, - 1000, 0, "Vector",
                                          "Vector", 'ShaderNodeGroup', None,
                                          150, False)
        vector_node.node_tree = vector_nodetree

        return vector_node
    else:
        return vector_nodetree


def load_background_node(node_tree, rename="", node_task='COMPLETE'):
    nodes = node_tree.nodes
    links = node_tree.links

    background_path = os.path.join(risorse_lib(), "node_groups", "world_node_utility", "BackGround.blend")

    background_nodetree = load_libraries_node_group(background_path, "BackGround", rename)

    background_node = create_node_utility(nodes, - 1000, 0, rename,
                                          rename, 'ShaderNodeGroup', None,
                                          150, False)

    background_node.node_tree = background_nodetree

    get_ngprop(background_nodetree).group_id_name = node_task
    get_ngprop(background_nodetree).environment_type = 'TEXTURE_BACKGROUND'

    return background_node


def is_hdri_texture_node(node):
    if not has_nodetree(node):
        return False

    ngProp = get_ngprop(node.node_tree)
    if ngProp.environment_type == 'TEXTURE_BACKGROUND':
        return True


def load_background_diffuse_or_light(node_tree, image=None, node_group=None, node_task='DIFFUSE', action='ADD'):
    """
    Function dedicated to load the background node and the diffuse/light/Complete node with the task specified.

    :node_tree: (Never None) = context.node_tree
    :image: the bpy.data.images (Optional)
    :node_groups: the bpy.data.groups to asign (Optional)
    :node_task: The function of the node enum in 'DIFFUSE', 'LIGHT', 'COMPLETE'
    :action: Enum in ADD/REMOVE
    """
    nodes = node_tree.nodes
    nodes_dict = get_nodes_dict(node_tree)

    mixer_node = nodes_dict.get('MIXER')
    diffuse = nodes_dict.get('DIFFUSE')
    light = nodes_dict.get('LIGHT')
    complete = nodes_dict.get('COMPLETE')
    vectors = nodes_dict.get('VECTORS')

    if action == 'ADD':
        # --------------------------------------------------------------------------------------------------------------
        # ADD means that we have to create the node and link it to the mixer
        #
        if not mixer_node:
            mixer_node = load_mixer(node_tree)
        if not vectors:
            vectors = load_vector_node(node_tree)

        # Case 1 - Ci sono già tutti e DUE i nodi standard di HDRI Maker:
        if diffuse and light:
            if node_task == 'DIFFUSE':
                if not is_hdri_texture_node(diffuse):
                    nodes.remove(diffuse)
                if image:
                    assign_image_to_background_node(image, environment='DIFFUSE')
                elif node_group:
                    if diffuse:
                        # This is because the light node is already present, and needs to be removed (and replaced with the new one)
                        nodes.remove(diffuse)
                    diffuse = create_node_utility(nodes, nodeName=node_group.name, label=node_group.name,
                                                  nodeType='ShaderNodeGroup')
                    diffuse.node_tree = node_group
                    get_ngprop(node_group).group_id_name = 'DIFFUSE'

            elif node_task == 'LIGHT':
                if not is_hdri_texture_node(light):
                    nodes.remove(light)
                if image:
                    assign_image_to_background_node(image, environment='LIGHT')
                elif node_group:
                    if light:
                        # This is because the light node is already present, and needs to be removed (and replaced with the new one)
                        nodes.remove(light)

                    light = create_node_utility(nodes, nodeName=node_group.name, label=node_group.name,
                                                nodeType='ShaderNodeGroup')
                    light.node_tree = node_group
                    get_ngprop(node_group).group_id_name = 'LIGHT'

        # Case 2 - C'è Solo il nodo COMPLETE:
        elif complete:
            if node_task == 'DIFFUSE':
                if image:
                    diffuse = assign_image_to_background_node(image, environment='DIFFUSE')
                elif node_group:
                    diffuse = create_node_utility(nodes, nodeName=node_group.name, label=node_group.name,
                                                  nodeType='ShaderNodeGroup')
                    diffuse.node_tree = node_group
                    get_ngprop(node_group).group_id_name = 'DIFFUSE'
                # Qui il nodo complete, cambia funzione, diventa il nodo LIGHT
                get_ngprop(complete.node_tree).group_id_name = 'LIGHT'

            elif node_task == 'LIGHT':
                if image:
                    light = assign_image_to_background_node(image, environment='LIGHT')
                elif node_group:

                    light = create_node_utility(nodes, nodeName=node_group.name, label=node_group.name,
                                                nodeType='ShaderNodeGroup')
                    light.node_tree = node_group
                    get_ngprop(node_group).group_id_name = 'LIGHT'
                # Qui il nodo complete, cambia funzione, diventa il nodo DIFFUSE
                get_ngprop(complete.node_tree).group_id_name = 'DIFFUSE'
            # else:
            #     pass
        #
        #
        # --------------------------------------------------------------------------------------------------------------

    if action == 'REMOVE':
        # REMOVE means that we have to remove the node and link the mixer to the other node
        if node_task == 'DIFFUSE':
            if diffuse:
                nodes.remove(diffuse)
            if light:
                get_ngprop(light.node_tree).group_id_name = 'COMPLETE'

        if node_task == 'LIGHT':
            if light:
                nodes.remove(light)
            if diffuse:
                get_ngprop(diffuse.node_tree).group_id_name = 'COMPLETE'

        if mixer_node:
            nodes.remove(mixer_node)

    link_and_fix_node_tree(node_tree)
    align_hdri_maker_nodes(node_tree)


def load_background_complete(node_tree, image=None, node_group=None):
    """
    Function dedicated to load the Complete node with the task specified.
    :node_tree: (Never None) = context.node_tree
    :image: the bpy.data.images (Optional)
    :node_groups: the bpy.data.groups to asign (Optional)
    """
    nodes = node_tree.nodes
    nodes_dict = get_nodes_dict(node_tree)

    complete = nodes_dict.get('COMPLETE')
    if complete:
        nodes.remove(complete)

    if image:
        assign_image_to_background_node(image, environment='COMPLETE')
    elif node_group:
        complete = create_node_utility(nodes, nodeName=node_group.name, label=node_group.name,
                                       nodeType='ShaderNodeGroup')
        complete.node_tree = node_group
        get_ngprop(node_group).group_id_name = 'COMPLETE'

    link_and_fix_node_tree(node_tree)
    align_hdri_maker_nodes(node_tree)


def link_and_fix_node_tree(node_tree):
    nodes = node_tree.nodes
    links = node_tree.links

    output = node_tree.get_output_node('ALL')
    if not output:
        output = create_node_utility(nodes, 0, 0, "World Output", "", 'ShaderNodeOutputWorld', None, 150, False)

    nodes_dict = get_nodes_dict(node_tree)
    diffuse = nodes_dict.get('DIFFUSE')
    light = nodes_dict.get('LIGHT')
    complete = nodes_dict.get('COMPLETE')
    mixer = nodes_dict.get('MIXER')
    vectors = nodes_dict.get('VECTORS')

    oriz_dist = 200

    if diffuse and light:
        if not mixer:
            mixer = load_mixer(node_tree, mixer_type='LIGHT_MIXER')
        if not vectors:
            vectors = load_vector_node(node_tree)

    if mixer:
        links.new(mixer.outputs[0], output.inputs[0])
        if diffuse and light:
            # Connect the diffuse and light to the mixer
            links.new(diffuse.outputs[0], mixer.inputs[0])
            links.new(light.outputs[0], mixer.inputs[1])

    if vectors:
        # Connect the vectors to background nodes if the nodes have the inputs "Vector" or "Vector Fx"
        if diffuse and light:
            for idx, inp in enumerate(diffuse.inputs):
                if inp.name.lower() == 'vector':
                    links.new(vectors.outputs[0], diffuse.inputs[idx])
                elif inp.name.lower() == 'vector fx':
                    links.new(vectors.outputs[1], diffuse.inputs[idx])

            for idx, inp in enumerate(light.inputs):
                if inp.name.lower() == 'vector':
                    links.new(vectors.outputs[0], light.inputs[idx])
                elif inp.name.lower() == 'vector fx':
                    links.new(vectors.outputs[1], light.inputs[idx])

        elif complete:
            for idx, inp in enumerate(complete.inputs):
                if inp.name.lower() == 'vector':
                    links.new(vectors.outputs[0], complete.inputs[idx])
                elif inp.name.lower() == 'vector fx':
                    links.new(vectors.outputs[1], complete.inputs[idx])

            links.new(complete.outputs[0], output.inputs[0])

    # In this case if vectors node and mixer node are present but no links are present, we have to remove the nodes
    if vectors:
        # No inputs or outputs are linked
        if not [i for i in vectors.inputs if i.is_linked] + [o for o in vectors.outputs if o.is_linked]:
            nodes.remove(vectors)
    if mixer:
        # No inputs or outputs are linked
        if not [i for i in mixer.inputs if i.is_linked] + [o for o in mixer.outputs if o.is_linked]:
            nodes.remove(mixer)


def align_hdri_maker_nodes(node_tree):
    """This function align the nodes of the HDRI Maker node tree form the version 3.x of the addon"""
    nodes = node_tree.nodes
    links = node_tree.links

    output = node_tree.get_output_node('ALL')
    if not output:
        return

    nodes_dict = get_nodes_dict(node_tree)
    diffuse = nodes_dict.get('DIFFUSE')
    light = nodes_dict.get('LIGHT')
    complete = nodes_dict.get('COMPLETE')
    mixer = nodes_dict.get('MIXER')
    vectors = nodes_dict.get('VECTORS')

    oriz_dist = 200

    if diffuse and light:
        # Connect the diffuse and light to the mixer
        if mixer:
            mixer.location = output.location.x - oriz_dist, output.location.y
            diffuse.location = mixer.location.x - oriz_dist, mixer.location.y + 250
            light.location = mixer.location.x - oriz_dist, mixer.location.y - -250

        align_node_xy(node_tree, [diffuse, light], direction='Y', margin=20, master_node=diffuse)

    if vectors:
        # Connect the vectors to background nodes if the nodes have the inputs "Vector" or "Vector Fx"
        if diffuse and light:
            vectors.location = diffuse.location.x - oriz_dist, output.location.y
        elif complete:
            complete.location = output.location.x - oriz_dist, output.location.y
            vectors.location = complete.location.x - oriz_dist, output.location.y

    if complete and output:
        complete.location = output.location.x - oriz_dist, output.location.y

    for id, node in nodes_dict.items():
        node.width = 150


def is_node_complete(node):
    """This method is used to understand if the node can be used as diffuse/light/complete node"""
    if not has_nodetree(node):
        return False

    # First step: check the outputs and if the node has a shader output and if in the internal node_tree has a "Background"
    # node connected to the shader output
    if not node.outputs:
        return False

    input_nodes, output_nodes = get_in_out_group(node.node_tree)
    for idx, out in enumerate(node.outputs):
        if out.type != 'SHADER':
            continue

        # We are sure that the node has a shader output and that the internal node_tree has a "Background" node connected to the shader output
        # So it can be used as a complete node for HDRI Maker
        interior_output = output_nodes[0].inputs[idx]
        if interior_output.is_linked:
            if interior_output.links[0].from_node.type == 'BACKGROUND':
                return True


def analyse_blend_world_and_get_node_group(world, group_id_name=""):
    """This function is used ONLY when you want to add a Light or Diffuse module to an already existing world."""

    if not world:
        # No world is present into the function parameter
        return {}

    node_tree = world.node_tree
    if not node_tree:
        return {}

    nodes = node_tree.nodes
    links = node_tree.links
    nodes_dict = get_nodes_dict(node_tree)

    diffuse = nodes_dict.get('DIFFUSE')
    light = nodes_dict.get('LIGHT')
    complete = nodes_dict.get('COMPLETE')

    # ------------------------------------------------------------------------------------------------------------------
    # Primi 4 casi in cui tutto è ok e restituisce un nodo gruppo, tutto è praticamente ok
    if diffuse and light:
        # In statement the world is a HDRI Maker world with 2 HDRI procedural node groups (DIFFUSE and LIGHT) not very good situation.
        get_ngprop(diffuse.node_tree).group_id_name = 'COMPLETE'
        complete = diffuse.node_tree
        return {'world_type': 'IS_HDRI_MAKER', 'node_group': complete}

    if diffuse:
        # In statement the world is a HDRI Maker world with 1 HDRI procedural node group (DIFFUSE) not very good situation.
        get_ngprop(diffuse.node_tree).group_id_name = 'COMPLETE'
        complete = diffuse.node_tree
        return {'world_type': 'IS_HDRI_MAKER', 'node_group': complete}

    if light:
        # In statement the world is a HDRI Maker world with 1 HDRI procedural node group (LIGHT) not very good situation.
        get_ngprop(light.node_tree).group_id_name = 'COMPLETE'
        complete = light.node_tree
        return {'world_type': 'IS_HDRI_MAKER', 'node_group': complete}

    if complete:
        if has_nodetree(complete):
            complete = complete.node_tree
        return {'world_type': 'IS_HDRI_MAKER', 'node_group': complete}
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Caso in cui c'è solo un nodo gruppo:
    nodes_list = [n for n in nodes if n.type != 'OUTPUT_WORLD']
    if len(nodes_list) == 1 and nodes_list[0].type == 'GROUP' and is_node_complete(nodes_list[0]):
        complete = nodes_list[0].node_tree
        return {'world_type': 'IS_HDRI_MAKER', 'node_group': complete}

    if is_old_hdrimaker_world(node_tree):
        image = get_image_from_old_hdri_maker_world(node_tree)

        if image:
            return {'world_type': 'IMAGE_FROM_OLD_WORLD', 'node_group': None, 'image': image}
        else:

            # In this case it is an old HDRI Maker world but the image is missing or are modified by the user
            complete = convert_world_to_node_group(world, group_id_name=group_id_name)
            return {'world_type': 'IS_OLD_HDRI_MAKER', 'node_group': complete, 'image': None}

    else:
        # In questo caso c'è un albero di nodi ma non è un HDRI Maker world, quindi si crea un gruppo di tutti i nodi presenti
        complete = convert_world_to_node_group(world, group_id_name=group_id_name)
        return {'world_type': 'UNKNOW', 'node_group': complete, 'image': None}


# ----------------------------------------------------------------------------------------------------------------------
# The following functions are useful to create a node group with all the nodes present in a world.

def convert_world_to_node_group(id_data, group_id_name=""):
    """Create a node group from node_tree.
    :id_data: can be a D.world/D.material/etc.
    In practice, it is a data-block that has a node_tree.
    :node_task: is the function of the node group, it can be 'LIGHT' or 'DIFFUSE' or 'COMPLETE'."""
    # Function that takes all the nodes of the world.node_tree and creates a group with them, all the inputs of
    # all the nodes are connected to the input of the group In order to be able to control them from the HDRI Maker panel
    if not has_nodetree(id_data):
        print("Error from function convert_world_to_node_group():",
              "The data-block" + str(id_data) + "has no node_tree")
        return
    node_group_dict = create_group_from_node_tree(id_data)
    if not node_group_dict:
        return

    nodes_input = node_group_dict.get('nodes_input')
    nodes_output = node_group_dict.get('nodes_output')
    node_group = node_group_dict.get('node_group')


    ngProp = get_ngprop(node_group)
    ngProp.group_id_name = group_id_name

    nodes = node_group.nodes
    links = node_group.links

    # TODO: Assicurati che il shader_nodes_properties.json non serva più
    # # Need to load the json file with the blender nodes properties min_value, max_value, default_value, etc. because
    # # when create a node group from a node tree, the properties are lost.
    # # Example with bpy.ops.node.group_make() the properties are grabbed from the node, but not when create a node group
    # # into low level blender api. Unable for now to find the prop min_value, max_value, default_value, etc. form a standard node
    #
    #
    # # load json file:
    # path = os.path.join(risorse_lib(), "Files", "shader_nodes_properties.json")
    # json_data = get_json_data(path)

    # Create node_tree node input linked to any node in the node_tree with free socket inputs:
    for node_idx, node in enumerate(nodes):

        if node.type in ['VALUE', 'RGB']:
            # In this case we need to remove the node and keep the link to the socket
            output = node.outputs[0]
            if output.is_linked:
                # Here inp is the input of the node to which the node "Value" or "RGB" is connected, this to remove the
                # nodes that do not have input values.
                to_node = output.links[0].to_node
                nodes.remove(node)
                node = to_node

        is_first_free_socket = False
        for socket_idx, inp in enumerate(node.inputs):
            if node in [nodes_input, nodes_output]:
                # The nodes Input/Output inside the node group not need to be considerate
                continue

            if inp.is_linked:
                # If the input is linked to another node, it is not necessary to create an input for the node group
                continue

            if not inp.enabled:
                # In this case the socket is disabled, so it is not necessary to create a node input for it, for example
                # the node "Background" has a socket "Weight" idx=2 that is disabled.
                continue

            # Custom socket is the "Empty" socket at the end of the node into node_group, so that socket grab the values
            # from the link_to_socket in automatic mode

            new_socket = new_ng_socket(node_group, in_out='INPUT', socket_type=inp.bl_idname)

            # Bisogna settare la default_value, min_value, max_value, etc. del socket appena creato (Se esistono)
            if hasattr(inp, 'default_value'):
                new_socket.default_value = inp.default_value

            # custom_socket = next((out for out in nodes_input.outputs if out.type == 'CUSTOM'), None)

            new_internal_socket = get_internal_socket(new_socket)
            links.new(new_internal_socket, inp)

            sckProp = get_sckprop(new_socket)
            # This is now the new socket created in auto by Blender api when the custom_socket is linked to the inp socket:
            if node.type != 'GROUP':
                if node.type in ['MAPPING'] or inp.name.lower() == 'vector':
                    # This statement is necessary to keep the socket name "Original" because HDRi Maker if found Vector inputs
                    # Can be connected from Vectors Node group to the new one group. ( Keep in mind :D )
                    new_socket.name = inp.name
                else:
                    new_socket.name = node.name + " " + inp.name

            is_first_free_socket = True if is_first_free_socket is False else False

            sckProp.api_bool_description = "Value '" + inp.name + "' from node '" + node.name + "' (Created from your node tree by HDRI Maker)"
            if inp.type in ['VECTOR', 'RGBA']:
                sckProp.api_label_on_top = True

    # Get nodes locations:
    ranges = get_nodes_ranges_xy(node_group, exclude_nodes=[nodes_input, nodes_output])
    min_x = ranges.get('min_x')
    max_x = ranges.get('max_x')
    center_y = ranges.get('center_y')

    if min_x is not None:
        nodes_input.location.x = min_x - 300
    if max_x is not None:
        nodes_output.location.x = max_x + 300

    if center_y is not None:
        nodes_input.location.y = center_y
        nodes_output.location.y = center_y

    return node_group


def get_image_from_old_hdri_maker_world(node_tree):
    nodes = node_tree.nodes
    links = node_tree.links

    for n in nodes:
        if n.type == 'TEX_ENVIRONMENT':
            if n.name.lower() == "hdri maker background":
                if n.image:
                    return n.image


def is_old_hdrimaker_world(node_tree):
    """This function checks if the node tree is an old version of the HDRI Maker node tree before the update to 3.3"""
    hdri_maker_old_nodes_dict = {'VM_Blurry_1': {'type': 'VECT_MATH'},
                                 'VM_Blurry_2': {'type': 'VECT_MATH'},
                                 'NOISE_Blurry': {'type': 'TEX_NOISE'},
                                 'BLURRY_Value': {'type': 'VALUE'},
                                 'HDRi Maker Background': {'type': 'TEX_ENVIRONMENT'},
                                 'World Rotation': {'type': 'MAPPING'},
                                 'Texture Coordinate': {'type': 'TEX_COORD'},
                                 'HDRI_COLORIZE': {'type': 'RGB'},
                                 'World Output': {'type': 'OUTPUT_WORLD'},
                                 'Background light': {'type': 'BACKGROUND'},
                                 'Hdri hue_sat': {'type': 'HUE_SAT'},
                                 'HDRI_COLORIZE_MIX': {'type': 'MIX_RGB'},
                                 'HDRI_Maker_Exposure': {'type': 'GROUP'},
                                 'MixBlutty_2': {'type': 'MIX_RGB'},
                                 'MixBlutty_1': {'type': 'MIX_RGB'}}

    nodes = node_tree.nodes

    node_list = []
    for n in nodes:
        node_list.append(n.name)

    for key in hdri_maker_old_nodes_dict.keys():
        if key not in node_list:
            return False

    # In this case all the nodes are present, so this is 100% an old HDRI Maker world (before hdri maker 3.0)
    return True


def is_hdri_maker_studio_world(world):
    """This function checks if the world is a HDRI Maker Studio world, (3.X Series) the return value is a boolean"""

    if not has_nodetree(world):
        return False
    node_tree = world.node_tree
    nodes = node_tree.nodes
    node_dict = get_nodes_dict(node_tree)

    output = node_dict.get('OUTPUT_WORLD')
    diffuse = node_dict.get('DIFFUSE')
    light = node_dict.get('LIGHT')
    complete = node_dict.get('COMPLETE')
    vectors = node_dict.get('VECTORS')
    mixer = node_dict.get('MIXER')

    if not diffuse and not light and not complete:
        return False

    if diffuse and light and mixer and output:
        return True

    if complete and output:
        return True


def solve_nodes_problem(node_tree):
    """Risolve eventuali problemi, ad esempio se l'utente ha modificato qualche nodo e ora non funziona più"""
    node_dict = get_nodes_dict(node_tree)

    diffuse = node_dict.get('DIFFUSE')
    light = node_dict.get('LIGHT')
    complete = node_dict.get('COMPLETE')
    vectors = node_dict.get('VECTORS')
    mixer = node_dict.get('MIXER')
    output = node_dict.get('OUTPUT_WORLD')

    nodes = node_tree.nodes
    links = node_tree.links

    if not output:
        output = next((n for n in node_tree.nodes if n.type == 'OUTPUT_WORLD'), None)
        if not output:
            output = node_tree.nodes.new('ShaderNodeOutputWorld')
            output.location = (0, 0)

    def output_exist(node, id_name):
        if not node.outputs:
            text = "The node '" + id_name.title() + "' must have at least one output socket of type 'Shader', please check your world node tree or remove it"
            draw_info(text, "Problem Found", 'INFO')
            return
        return True

    # 1) Check the output node:
    # The diffuse/light/complete node, to be compatible, must have at least one output socket of type 'Shader' and at least one node 'Background' connected to that socket
    # If one of these nodes does not have an output socket of type 'Shader', then it is not compatible with HDRI Maker, so the function must stop and warn the user
    if diffuse:
        if not output_exist(diffuse, 'DIFFUSE'):
            return
    if light:
        if not output_exist(light, 'LIGHT'):
            return
    if complete:
        if not output_exist(complete, 'COMPLETE'):
            return

    # 2) Check the mixer node if is the same of the mixer node of the HDRI Maker Studio world:
    if mixer:
        # Compare mixer node with the mixer node of the HDRI Maker Studio world, so we need to load the HDRI Maker Studio world:
        real_mixer = load_mixer(node_tree, create_node=False)
        if not compare_node_group(real_mixer, mixer.node_tree):
            # If the node is not the same, then we need to replace it with the correct one:
            mixer.node_tree = real_mixer
        else:
            bpy.data.node_groups.remove(real_mixer)

    # 3) Check the vectors node if is the same of the vectors node of the HDRI Maker Studio world:
    if vectors:
        # Compare vectors node with the vectors node of the HDRI Maker Studio world, so we need to load the HDRI Maker Studio world:
        real_vectors = load_vector_node(node_tree, create_node=False)
        if not compare_node_group(real_vectors, vectors.node_tree):
            # If the node is not the same, then we need to replace it with the correct one:
            vectors.node_tree = real_vectors
        else:
            bpy.data.node_groups.remove(real_vectors)

    if diffuse and light and not mixer:
        # If the world is a HDRI Maker Studio world, but the user has deleted the mixer node, then we need to create it again:
        mixer = load_mixer(node_tree, create_node=True)

    if mixer:
        # In this case the mixer exists, but it is not necessary,
        # so we need to convert the node Diffuse or Light in a Complete node and remove the mixer node:
        if not diffuse or not light:
            nodes.remove(mixer)

    if diffuse or light:
        if not diffuse:
            if light:
                if has_nodetree(light):
                    get_ngprop(light.node_tree).group_id_name = 'COMPLETE'
        if not light:
            if diffuse:
                if has_nodetree(diffuse):
                    get_ngprop(diffuse.node_tree).group_id_name = 'COMPLETE'

    purge_all_group_names(node_tree)


def compare_node_group(node_tree_a, node_tree_b):
    """This function compares two node groups and returns True if they are the same, False otherwise"""

    nodes_a = node_tree_a.nodes
    nodes_b = node_tree_b.nodes

    links_a = node_tree_a.links
    links_b = node_tree_b.links

    if len(links_a) != len(links_b):
        # If the number of links is different, then the node groups are different
        return False

    if len(nodes_a) != len(nodes_b):
        # If the number of nodes is different, then the node groups are different
        return False

    links_dict_a = get_links_dict(node_tree_a)
    links_dict_b = get_links_dict(node_tree_b)

    if links_dict_a != links_dict_b:
        # If the links are different, then the node groups are different
        return False

    # Compare the names of the nodes
    node_names_a = [n.name for n in nodes_a]
    node_names_b = [n.name for n in nodes_b]

    if node_names_a != node_names_b:
        # If the names of the nodes are different, then the node groups are different
        return False

    # Compare the types of the nodes in order to check if node.type is the same of the same node in the other node group
    node_types_a = [n.type for n in nodes_a]
    node_types_b = [n.type for n in nodes_b]

    if node_types_a != node_types_b:
        # If the types of the nodes are different, then the node groups are different
        return False

    # Compare the properties of the nodes in order to check if node.property is the same of the same node in the other node group
    for node_a in nodes_a:
        node_b = nodes_b[node_a.name]
        if has_nodetree(node_a):
            # If the node is a node group, then we need to compare the node groups
            if not compare_node_group(node_a.node_tree, node_b.node_tree):
                return False
        # Compare inputs values if the node has inputs
        if node_a.inputs:
            for idx, input_a in enumerate(node_a.inputs):
                input_b = node_b.inputs[idx]
                if hasattr(input_a, 'default_value') and hasattr(input_b, 'default_value'):
                    if input_a.default_value != input_b.default_value:
                        return False

    # I think that the node groups are the same
    return True


def set_world_goodies(world):
    if bpy.app.version < (4, 2, 0):
        return

    if hasattr(world, 'use_sun_shadow'):
        if not world.use_sun_shadow:
            world.use_sun_shadow = True
    else:
        print("Error, rhe world has no attribute 'use_sun_shadow' (If you see this message, please contact the developer)")

