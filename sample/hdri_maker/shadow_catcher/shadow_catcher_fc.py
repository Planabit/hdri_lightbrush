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

from ..exaconv import get_matprop, get_ngprop, get_objprop
from ..utility.utility import has_nodetree, get_shading_engine, un_parent, hide_object
from ..utility.utility import set_object_bounds

class MemorizeShadowCatcher:
    sc_cycles_plane = None
    sc_light_probe = None

def update_shadow_catcher():
    """This Function adjust the shadow catcher situation, in order to make it work into Eevee and Cycles"""
    context_engine = get_shading_engine()

    if not context_engine:
        # Durante la fase di rendering, c'è un momento in cui il context_engine è None
        return

    sc_dict = get_shadow_catcher_objects()
    sc_cycles_plane = sc_dict.get('cycles_plane')
    sc_light_probe = sc_dict.get('light_probe')

    if sc_cycles_plane:
        get_objprop(sc_cycles_plane).hide_full = False if context_engine == 'CYCLES' else True
    if sc_light_probe:
        get_objprop(sc_light_probe).hide_full = True if context_engine == 'CYCLES' else False


def add_probe_funct(plane, object_id_name='LIGHT_PROBE_PLANE'):
    if bpy.app.version >= (4, 1, 0):
        planar_name = 'PLANE'
    else:
        planar_name = 'PLANAR'

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.lightprobe_add(type=planar_name, enter_editmode=False, align='WORLD')
    light_probe = bpy.context.active_object
    # Matrix world è la miglior soluzione perchè bypassa il problema di posizione se l'oggetto è figlio
    light_probe.matrix_world = plane.matrix_world
    light_probe.name = 'LIGHT_PROBE_PLANE'
    light_probe.hdri_prop_obj.object_id_name = object_id_name
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = plane
    plane.select_set(state=True)
    light_probe.parent = plane
    light_probe.matrix_parent_inverse = plane.matrix_world.inverted()
    light_probe.hide_select = True
    light_probe.scale = plane.scale

    return light_probe


def get_shadow_catcher_objects():
    """Get and return into a dict the shadow catcher object inside the collection of the shadow catcher if exist"""
    sc_objects = {}

    from ..collections_scene.collection_fc import get_collection_by_id_name
    collection = get_collection_by_id_name('SHADOW_CATCHER')
    if collection:
        sc_objects['collection'] = collection
    else:
        return {}

    for o in collection.objects:
        objProp = get_objprop(o)
        if objProp.object_id_name == 'CYCLES_SHADOW_CATCHER':
            sc_objects['cycles_plane'] = o
        elif objProp.object_id_name == 'EEVEE_SHADOW_CATCHER':
            sc_objects['eevee_plane'] = o
            if o.data.materials:
                sc_material = o.data.materials[0]
                if sc_material is not None:
                    matProp = get_matprop(sc_material)
                    if matProp.mat_id_name == 'EEVEE_SHADOW_CATCHER':
                        if has_nodetree(sc_material):
                            sc_objects['eevee_material'] = o.data.materials[0]
                            for n in sc_material.node_tree.nodes:
                                if has_nodetree(n):
                                    ngProp = get_ngprop(n.node_tree)
                                    if ngProp.group_id_name == 'EEVEE_SHADOW_CATCHER':
                                        sc_objects['eevee_node'] = n
                                    elif ngProp.group_id_name == 'SC_NORMAL':
                                        sc_objects['sc_normal'] = n

        elif objProp.object_id_name == 'SC_LIGHT_PROBE_PLANE':
            sc_objects['light_probe'] = o

    if sc_objects:
        sc_objects['exist'] = True

    return sc_objects


def remove_all_bounds_objects(restore_object_id_name=True):
    """Restore all objects if object is BOUNDS and objProp.is_shrinkwrap"""
    for ob in bpy.context.scene.objects:
        objProp = get_objprop(ob)
        if objProp.is_shrinkwrap:
            un_parent(ob)
            hide_object(ob, hide=False)
            set_object_bounds(ob, display_type='TEXTURED')
            if restore_object_id_name:
                objProp.is_shrinkwrap = False
