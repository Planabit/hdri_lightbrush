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
import bpy

from ..exaconv import get_colprop

def get_light_studio_collection(create=True):
    """Return the collection of the light studio if exist in the scene, if the collection id name is the same of the collection_id_name.
    Inputs
    :create: default = True, create or search"""
    tools_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_TOOLS')
    if not tools_collection:
        if create:
            tools_collection = create_collection_and_link_it(collection_id_name='HDRI_MAKER_TOOLS')

    light_studio_collection = get_collection_by_id_name(collection_id_name='LIGHT_STUDIO')
    if create:
        if not light_studio_collection:
            light_studio_collection = create_collection_and_link_it(collection_id_name='LIGHT_STUDIO',
                                                                   collection_father=tools_collection,
                                                                   color_tag='COLOR_03')
    return light_studio_collection

def get_sun_studio_collection(create=True):
    """Return the collection of the sun studio if exist in the scene, if the collection id name is the same of the collection_id_name.
    Inputs
    :create: default = True, create or search"""
    tools_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_TOOLS')
    if not tools_collection:
        if create:
            tools_collection = create_collection_and_link_it(collection_id_name='HDRI_MAKER_TOOLS')

    sun_studio_collection = get_collection_by_id_name(collection_id_name='SUN_STUDIO')
    if create:
        if not sun_studio_collection:
            sun_studio_collection = create_collection_and_link_it(collection_id_name='SUN_STUDIO',
                                                                  collection_father=tools_collection,
                                                                  color_tag='COLOR_02')
    return sun_studio_collection

def get_shadow_catcher_collection(create=True):
    """Return the collection of the shadow catcher if exist in the scene, if the collection id name is the same of the collection_id_name.
    input: bpy.context"""
    tools_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_TOOLS')
    if not tools_collection:
        tools_collection = create_collection_and_link_it(collection_id_name='HDRI_MAKER_TOOLS')

    shadow_catcher_collection = get_collection_by_id_name(collection_id_name='SHADOW_CATCHER')
    if create:
        if not shadow_catcher_collection:
            shadow_catcher_collection = create_collection_and_link_it(collection_id_name='SHADOW_CATCHER',
                                                                      collection_father=tools_collection,
                                                                      color_tag='COLOR_04')
    return shadow_catcher_collection


def get_hdri_maker_tools_collection(scn):
    """Return the collection of the hdri maker tools if not exist return the HDRI_MAKER_TOOLS collection"""
    for col in get_scene_collections(scn.collection):
        colProp = get_colprop(col)
        if colProp.collection_id_name == 'HDRI_MAKER_TOOLS':
            return col


def remove_hdrimaker_tools_collection(scn):
    """Remove only the empty collection of the hdri maker tools, no objects inside=Remove collection
    it checks also if the children collections_scene is empty, it remove the tools collection"""

    hdri_maker_tools_collection = get_hdri_maker_tools_collection(scn)
    if hdri_maker_tools_collection:
        collection_children = hdri_maker_tools_collection.children_recursive
        for col in reversed(collection_children):
            if not col.objects:
                bpy.data.collections.remove(col)

        if len(hdri_maker_tools_collection.children_recursive) == 0:
            if not hdri_maker_tools_collection.objects:
                bpy.data.collections.remove(hdri_maker_tools_collection)


def get_dome_collection(create=True):
    """Return the collection of the dome if exist in the scene, if the collection id name is the same of the collection_id_name.
    Inputs
    :create: default = True, create or search"""
    tools_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_TOOLS')
    if not tools_collection:
        if create:
            tools_collection = create_collection_and_link_it(collection_id_name='HDRI_MAKER_TOOLS')

    dome_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_DOME')
    if create:
        if not dome_collection:
            dome_collection = create_collection_and_link_it(collection_id_name='HDRI_MAKER_DOME',
                                                            collection_father=tools_collection,
                                                            color_tag='COLOR_07')
    return dome_collection


def create_collection_and_link_it(collection_id_name,
                                  collection_father=None, color_tag='COLOR_05'):
    """Create or get the collection with the name and the collection_id_name specified in the input.
    :collection_id_name: str
    :collection_father: bpy.types.Collection
    :color_tag: str
    """
    if collection_father is None:
        collection_father = bpy.context.scene.collection

    collection = get_collection_by_id_name(collection_id_name=collection_id_name)
    name = collection_id_name.replace('_', ' ').title()
    if not collection:
        collection = bpy.data.collections.new(name)
        colProp = get_colprop(collection)
        colProp.collection_id_name = collection_id_name
        try:
            # Not sure about eventual api changes about COLOR_05, So try
            collection.color_tag = color_tag
        except:
            pass

    if collection not in collection_father.children[:]:
        collection_father.children.link(collection)

    return collection


def get_collection_by_id_name(collection_id_name=''):
    """
    Return the collection if exist in the scene, if the collection id name is the same of the collection_id_name.

    :input: bpy.context,
    :collection_id_name: str
    """
    scene_collections = get_scene_collections(bpy.context.scene.collection)
    collection = next(
        (col for col in scene_collections if get_colprop(col).collection_id_name == collection_id_name),
        None)

    return collection


def get_scene_collections(scene_collection):
    """Return a list of all the collections_scene in a scene"""
    yield scene_collection
    for child in scene_collection.children:
        yield from get_scene_collections(child)


def move_ob_from_to_collection(ob, to_col):
    """Move an object from one blender collection to another"""

    if ob not in to_col.objects[:]:
        to_col.objects.link(ob)
    for col in ob.users_collection:
        if col != to_col:
            col.objects.unlink(ob)


def unlink_ob_from_scene_collections(ob):
    """Unlink an object from all the collections_scene in a scene"""
    for col in get_scene_collections(bpy.context.scene.collection):
        if ob in col.objects:
            col.objects.unlink(ob)

def get_collection_and_childrens(collection):
    """Return a list of all the collections_scene in a scene"""
    childrens = collection.children_recursive
    childrens.append(collection)
    return childrens

def get_all_objects_in_children_collection(collection):
    """Return a list of all the objects in the childrens collections_scene of a collection"""
    childrens = get_collection_and_childrens(collection)

    objects = []
    for col in childrens:
        for ob in col.objects:
            if ob not in objects:
                objects.append(ob)

    return objects


def make_active_collection(collection):
    """Make active a collection"""
    children_recursive = bpy.context.scene.collection.children_recursive
    for col in children_recursive:
        if col.name == collection.name:
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[col.name]
            break
