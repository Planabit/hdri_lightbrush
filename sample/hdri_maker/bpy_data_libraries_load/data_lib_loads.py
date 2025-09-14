import bpy

from ..exaproduct import Exa
from ..utility.utility import get_version_to_int, has_nodetree
from ..utility.utility import sub_nodes


def load_libraries_world(path_to_world, world_name=None, rename=None, world_index=None):
    """This function load a world from a blender file and return it, use only this function to load worlds from blend files"""

    world = None
    with bpy.data.libraries.load(path_to_world, link=False) as (data_from, data_to):
        if world_index is not None:
            # This is a case where you try to load a world from any scene
            # for now load a world based on the index assigned to the function input
            for idx, name in enumerate(data_from.worlds):
                if idx == world_index:
                    data_to.worlds = [name]
                    world_name = name
                    break
        elif world_name:
            data_to.worlds = [name for name in data_from.worlds if name.lower() == world_name.lower()]
        # remove the library (bpy.data.libraries.load(path_to_world)) from blender data:

    if not world_name:
        print("No world name provided into the function load_libraries_world")
        return

    if data_to.worlds:
        world = bpy.data.worlds[world_name]
        if rename:
            world.name = rename
        world.use_nodes = True
        wrlProp = world.hdri_prop_world
        wrlProp.self_tag = True

    if world and has_nodetree(world):
        from ..utility.nodes_compatibility import repair_unrecognized_nodes
        repair_unrecognized_nodes(world.node_tree)
        
    return world

def load_libraries_node_group(path_to_node, node_name, rename, try_to_reuse=False):
    """This function load a node group from a blender file and return it, use only this function to load node groups from blend files"""
    group = None
    if try_to_reuse:
        for nG in bpy.data.node_groups:
            if nG.name == node_name:
                return nG

    with bpy.data.libraries.load(path_to_node, link=False) as (data_from, data_to):
        data_to.node_groups = [name for name in data_from.node_groups if name.lower() == node_name.lower()]
    if data_to.node_groups:
        group = data_to.node_groups[0]  # bpy.data.node_groups[node_name]
        group.name = rename
        for n in group.nodes:
            if has_nodetree(n):
                n.node_tree.hdri_prop_nodetree.self_tag = True
                for sN in sub_nodes(group):
                    if has_nodetree(sN):
                        sN.node_tree.hdri_prop_nodetree.self_tag = True

    if group:
        ngProp = group.hdri_prop_nodetree
        ngProp.self_tag = True
        ngProp.group_version = get_version_to_int(Exa.blender_manifest.get('version'))

    if group:
        from ..utility.nodes_compatibility import repair_unrecognized_nodes
        repair_unrecognized_nodes(group)

    return group

def load_libraries_material(path, mat_name, rename=""):
    """This function load a material from a blender file and return it, use only this function to load materials from blend files"""
    mat = None
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.materials = [name for name in data_from.materials if name == mat_name]
    if len(data_to.materials) > 0:
        mat = data_to.materials[0]
        matProp = mat.hdri_prop_mat
        matProp.self_tag = True
        if rename:
            mat.name = rename

    if mat and has_nodetree(mat):
        from ..utility.nodes_compatibility import repair_unrecognized_nodes
        repair_unrecognized_nodes(mat.node_tree)

    return mat

def load_libraries_object(path, object_name, rename=""):
    """This function load an object from a blender file and return it, use only this function to load objects from blend files"""
    ob = None
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name == object_name]
    if data_to.objects[:]:
        ob = data_to.objects[0]
        if rename:
            ob.name = rename
            if ob.type == 'MESH':
                ob.data.name = rename

        objProp = ob.hdri_prop_obj
        objProp.self_tag = True

    for mat in ob.data.materials:
        if mat and has_nodetree(mat):
            from ..utility.nodes_compatibility import repair_unrecognized_nodes
            repair_unrecognized_nodes(mat.node_tree)

    return ob

def load_libraries_geonodes(path, geonode_name, rename=""):
    """This function load a geonode from a blender file and return it, use only this function to load geonodes from blend files"""
    geonode = None
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.node_groups = [name for name in data_from.node_groups if name == geonode_name]
    if data_to.node_groups[:]:
        geonode = data_to.node_groups[0]
        if rename:
            geonode.name = rename

    return geonode


def get_data_from_blend(filepath, data_type='materials'):
    """Get data from a blend file"""
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_id = getattr(data_from, data_type)
        data_list = [name for name in data_id]

    return data_list
