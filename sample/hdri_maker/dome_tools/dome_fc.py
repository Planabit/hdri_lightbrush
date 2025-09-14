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
from mathutils import Vector

from ..bpy_data_libraries_load.data_lib_loads import load_libraries_object, load_libraries_material
from ..collections_scene.collection_fc import get_dome_collection, get_collection_by_id_name, \
    move_ob_from_to_collection, remove_hdrimaker_tools_collection
from ..exaconv import get_scnprop, get_objprop, get_ngprop, ItemsVersion, get_matprop, get_meshprop, \
    get_ndprop
from ..library_manager.get_library_utils import risorse_lib
from ..shadow_catcher.shadow_catcher_fc import remove_all_bounds_objects
from ..utility.constraints import limit_location_constraints, limit_scale_constraints, limit_rotation_constraints
from ..utility.modifiers import add_hook_modifier, move_modifier_index
from ..utility.utility import has_nodetree, hide_object, lock_object, get_filename_from_path, Mtrx, show_overlays, \
    purge_all_group_names, override_view_3d_context, un_parent, make_parent, select_objects, store_attributes, \
    restore_attributes, retrieve_nodes, use_temp_override


class DomeUtil:
    domes = []

    def enum_domes(self, context):
        if DomeUtil.domes:
            return DomeUtil.domes

        domes_path = os.path.join(risorse_lib(), "blendfiles", "domes")
        for fn in os.listdir(domes_path):
            if not fn.endswith('.blend'):
                continue
            filepath = os.path.join(domes_path, fn)
            filename = fn.replace("_", "").replace(".blend", "").title()
            DomeUtil.domes.append((filepath, filename, ""))

        # Set "Dome" at the first position if exists
        dome = next((d for d in DomeUtil.domes if d[1].lower() == "dome"), None)
        if dome:
            DomeUtil.domes.remove(dome)
            DomeUtil.domes.insert(0, dome)

        return DomeUtil.domes


# /‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾
# Hooks:
#
class Hooks:

    def __init__(self, context, dome_parts={}, parent=None):
        dome_parts = find_current_dome_version(context) if not dome_parts else dome_parts
        self.dome_ground = dome_parts.get('dome_ground')
        self.dome_sky = dome_parts.get('dome_sky')
        self.parent = parent if parent else next(
            (o for o in context.scene.objects if o.hdri_prop_obj.object_id_name == 'DOME_HANDLER'), None)
        self.scale = self.parent.scale[:] if self.parent else 1
        self.context = context

        self.store_handler_rotation = None
        self.store_handler_location = None

    def start(self):
        self.store_handler_properties()
        self.remove_dome_hooks()
        self.reset_scale()
        self.create_vertices_hooks()
        self.set_scale()
        self.restore_handler_properties()

    def store_handler_properties(self):
        if self.parent:
            print("self.parent: ", self.parent)
            self.store_handler_rotation = self.parent.rotation_euler.copy()
            self.store_handler_location = self.parent.location.copy()
            self.parent.rotation_euler = (0, 0, 0)
            self.parent.location = (0, 0, 0)

    def restore_handler_properties(self):
        if self.store_handler_rotation:
            self.parent.rotation_euler = self.store_handler_rotation
        if self.store_handler_location:
            self.parent.location = self.store_handler_location

    def reset_scale(self):
        self.parent.scale = (1, 1, 1)
        get_objprop(self.parent).expand_hooks = 1
        self.context.view_layer.update()

    def make_empty_hook(self, name, location):
        scnProp = get_scnprop(self.context.scene)
        override = override_view_3d_context()
        if use_temp_override():
            with bpy.context.temp_override(**override):
                bpy.ops.object.empty_add(location=self.parent.matrix_world @ Vector(location))

        else:
            bpy.ops.object.empty_add(override, location=self.parent.matrix_world @ Vector(location))

        empty = bpy.context.object
        empty.name = name
        empty.empty_display_type = scnProp.hooks_display_type if scnProp.hooks_display_type else 'SPHERE'
        empty.empty_display_size = scnProp.hooks_display_size if scnProp.hooks_display_size else 1
        objProp = get_objprop(empty)
        objProp.object_id_name = 'DOME_HOOK'

        return empty

    def create_vertices_hooks(self):
        if self.dome_sky.type != 'MESH' or self.dome_ground.type != 'MESH':
            return

        groups = {}
        # TODO: Dome Sky/ Dome Ground
        # Qui bisogna mettere gli hooks sia al ground che allo sky
        # Gli hook devono essere in totale 16 tanti quanti sono i vertici del ground
        for idx, vertex_group in enumerate(self.dome_ground.vertex_groups):
            vg_name = self.dome_ground.vertex_groups[idx].name
            if vg_name.lower() in ["ground", "sky"]:
                # This avoids to iterate and create the hook on the vertex_group
                continue

            vs = [v for v in self.dome_ground.data.vertices if idx in [vg.group for vg in v.groups]]
            groups[self.dome_ground.vertex_groups[idx].name] = vs

        for name, vertices in groups.items():
            groups[name] = sorted(vertices, key=lambda x: x.co[2])

        top_is_ready = False
        dome_collection = get_dome_collection(create=False)

        empty_objs = []
        for name, vertices in groups.items():
            # Try to get vertices[0] with get method
            # If it fails, it means that the list is empty
            if not vertices:
                continue
            lower_vertex = vertices[0]
            if name == "Top":
                # questo per cattare il punto centrale della parte top del cubo
                # Lower vertex, sarà in realtà il vertice centrale del coperchio del cubo:
                lower_vertex = next((v for v in vertices if (v.co[0], v.co[1]) == (0, 0)), None)
                if not lower_vertex:
                    continue

            # Get the Global coordinates of the lower vertex
            lower_vertex_global = self.dome_ground.matrix_world @ lower_vertex.co
            empty = self.make_empty_hook(name, lower_vertex_global)
            # empty = self.make_empty_hook(name, lower_vertex.co)

            mod = add_hook_modifier(self.dome_ground, empty, name=name, vertices=vertices[:],
                                    center=self.parent.matrix_world @ lower_vertex.co)
            move_modifier_index(mod, to_index=0)
            # dome_collection = get_dome_collection(create=False)
            move_ob_from_to_collection(empty, dome_collection)
            empty.parent = self.parent
            empty_objs.append(empty)

            lock_object(empty, location=(False, False, True))
            limit_location_constraints(empty, use_min_z=True, use_max_z=True, min_z=0, max_z=0, owner_space='LOCAL')
            # limit_scale_constraints(empty)
            limit_rotation_constraints(empty, use_limit_x=True, use_limit_y=True, use_limit_z=False,
                                       owner_space='LOCAL')

        # Now with the hooks already created, you have to attach the vertical row and the top of the dome_sky, since it is a separate object
        # top_v_list = []
        for empty_index, empty in enumerate(empty_objs):
            # Create vert_list (as the list of the vertices of the dome_sky in the same x/y position of the empty)
            verts_list = []
            for idx, vertex in enumerate(self.dome_sky.data.vertices):
                # get vertex groups from vertex if name of vertex group is "Top":
                # if "Top" in [self.dome_sky.vertex_groups[vg.group].name for vg in vertex.groups]:
                #     top_v_list.append(vertex)

                if (vertex.co[0], vertex.co[1]) == (empty.location[0], empty.location[1]):
                    verts_list.append(vertex)

            # Now we can create the hook modifier on the dome_sky
            mod = add_hook_modifier(self.dome_sky, empty, name=empty.name, vertices=list(set(verts_list)),
                                    center=self.parent.matrix_world @ empty.location)
            move_modifier_index(mod, to_index=0)

        top_v_list = []
        for idx, vertex in enumerate(self.dome_sky.data.vertices):
            # get vertex groups from vertex if name of vertex group is "Top":
            if "Top" in [self.dome_sky.vertex_groups[vg.group].name for vg in vertex.groups]:
                top_v_list.append(vertex)

        if top_v_list:
            max_top_v = max(top_v_list, key=lambda x: x.co[2])
            empty_top_location = (0, 0, max_top_v.co[2])

            # Global coordinates of the empty_top
            empty_top_global = self.dome_sky.matrix_world @ Vector(empty_top_location)
            empty_top = self.make_empty_hook("Top", empty_top_global)
            # empty_top = self.make_empty_hook("Top", empty_top_location)
            empty_top.parent = self.parent

            mod = add_hook_modifier(self.dome_sky, empty_top, name="Top", vertices=list(set(top_v_list)),
                                    center=self.parent.matrix_world @ empty_top.location)
            move_modifier_index(mod, to_index=0)

            move_ob_from_to_collection(empty_top, dome_collection)

            lock_object(empty_top, location=(True, True, False))
            limit_location_constraints(empty_top, use_min_x=True, use_max_x=True, use_min_y=True, use_max_y=True,
                                       min_x=0, min_y=0, max_x=0, max_y=0, owner_space='LOCAL')
            limit_rotation_constraints(empty_top, use_limit_x=True, use_limit_y=True, use_limit_z=True,
                                       owner_space='LOCAL')

        show_overlays()

    def remove_dome_hooks(self):
        for ob in self.context.scene.objects:
            objProp = get_objprop(ob)
            if objProp.object_id_name == 'DOME_HOOK':
                bpy.data.objects.remove(ob)

        if not self.dome_ground:
            return
        if not self.dome_sky:
            return

        for mod in self.dome_ground.modifiers:
            if mod.type == 'HOOK':
                self.dome_ground.modifiers.remove(mod)
        for mod in self.dome_sky.modifiers:
            if mod.type == 'HOOK':
                self.dome_sky.modifiers.remove(mod)

    def set_scale(self):
        self.parent.scale = self.scale


#
#
# /‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾
# Assemble dome
#
class AssembleDome:

    def __init__(self, context, image=None, dome_name="", reuse_image=True):
        self.subdivide_modifier_attributes = None
        self.reuse_image = reuse_image
        self.image = image
        self.dome_collection = get_dome_collection()
        self.dome_material = None
        self.reflection_plane = None
        self.dome_name = dome_name
        self.context = context
        self.scale = None
        self.wrapped = None
        # Attrubutes modidier:
        self.subdivide_modifier_attributes = None
        self.smooth_modifier_attributes = None
        self.dome_ground = None
        self.hdri_maker_ground_objects = [o for o in bpy.context.scene.objects if
                                          get_objprop(o).object_id_name == 'HDRI_MAKER_GROUND']
        self.dome_handler = None

    def start(self):
        self.memorize_old_status()
        self.remove_old_dome()
        self.add_dome_handler()
        self.load_dome()
        self.add_reflection_plane()
        self.make_dome_child()
        self.asign_dome_material()
        self.asign_image_to_dome()
        # self.create_import_geometry_node()
        self.asign_dome_ob_to_dome_material_coordinates()
        self.adjust()
        self.scale = 1

    def memorize_old_status(self):
        dome_parts = get_dome_objects()
        dome_handler = dome_parts.get('DOME_HANDLER')
        dome_ground = dome_parts.get('HDRI_MAKER_DOME_GROUND')
        if not dome_ground:
            return

        self.dome_material = dome_parts.get('DOME_MATERIAL')
        if dome_handler:
            self.scale = get_objprop(dome_handler).scale_dome_handler

        self.wrapped = [ob for ob in self.context.scene.objects if get_objprop(ob).is_shrinkwrap if ob.type == 'MESH']

        subdivide_modifier = next((mod for mod in dome_ground.modifiers if mod.type == 'SUBSURF'), None)
        smooth_modifier = next((mod for mod in dome_ground.modifiers if mod.type == 'CORRECTIVE_SMOOTH'), None)

        if subdivide_modifier:
            self.subdivide_modifier_attributes = store_attributes(subdivide_modifier)
        if smooth_modifier:
            self.smooth_modifier_attributes = store_attributes(smooth_modifier)

        if self.wrapped:
            un_parent(self.wrapped)

    def remove_old_dome(self):
        """Only in the case the old dome exists, remove it"""
        Hooks(self.context).remove_dome_hooks()
        # remove_dome_handler()
        for o in self.context.scene.objects:
            objProp = get_objprop(o)
            if objProp.object_id_name in ['HDRI_MAKER_DOME_GROUND', 'HDRI_MAKER_DOME_SKY']:
                bpy.data.objects.remove(o)

    def remove_all(self):
        """Every time you start the dome, it removes the old one, but keeping the many properties of the last dome, by the memorize_old_status() function"""
        # Funzione da chiamare solo per rimuovere il dome
        un_parent_light_studio_from_dome()

        remove_all_bounds_objects()
        Hooks(self.context).remove_dome_hooks()
        remove_dome_handler()
        delete_dome(self, self.context)
        remove_hdrimaker_tools_collection(self.context.scene)

    def add_dome_handler(self):
        """The dome handler is the empty that will be used link all the dome objects together, it is used to scale the
        dome and all its children objects"""

        self.dome_handler = next((o for o in self.context.scene.objects if o.type == 'EMPTY' if
                                  get_objprop(o).object_id_name == 'DOME_HANDLER'), None)

        if self.dome_handler:
            return

        active_object = self.context.active_object
        selected_object = self.context.selected_objects[:]

        # If the dome does not exist, it need to be created
        override = override_view_3d_context()
        if use_temp_override():
            with bpy.context.temp_override(**override):
                bpy.ops.object.empty_add(location=(0, 0, 0))
        else:
            bpy.ops.object.empty_add(override, location=(0, 0, 0))

        self.dome_handler = self.context.object
        self.dome_handler.name = "Dome Handler"
        # The object_id_name is used to identify the object as a dome handler
        get_objprop(self.dome_handler).object_id_name = 'DOME_HANDLER'

        # The dome_handler location need to be at the center of the scene (x, y, z = 0, 0, 0)
        self.dome_handler.location = (0, 0, 0)
        # The dome_handler need to be hidden and unselectable, in addition it need to be locked in the scene
        hide_object(self.dome_handler, hide=True)
        lock_object(self.dome_handler, hide_select=True, scale=(False, False, False))

        move_ob_from_to_collection(self.dome_handler, self.dome_collection)

        if active_object:
            self.context.view_layer.objects.active = active_object
        if selected_object:
            for o in selected_object:
                o.select_set(True)

        # The dome_handler need for security to be limited in all the axis location and rotation,
        # but not in the scale axis, because it will be used to scale the dome
        limit_location_constraints(self.dome_handler, use_min_x=True, use_min_y=True, use_min_z=True, use_max_x=True,
                                   use_max_y=True, use_max_z=True)
        limit_rotation_constraints(self.dome_handler, use_limit_x=True, use_limit_y=True, use_limit_z=False)

        return self.dome_handler

    def load_dome(self):
        """Load the dome object, it is choosen by the user in scnProp.dome_type, if it is not present in scene.objects
        it will be loaded from the library"""

        scn = self.context.scene
        scnProp = get_scnprop(scn)
        # The dome_type is the same name ad the blend file that contains the dome object, only replace the .blend
        dome_type = get_filename_from_path(scnProp.dome_types).replace(".blend", "").upper()

        # In this case the dome object is not present in the scene
        self.dome_ground = load_libraries_object(scnProp.dome_types, "hdri_maker_dome_ground",
                                                 rename=self.dome_name + "_Ground")
        self.dome_sky = load_libraries_object(scnProp.dome_types, "hdri_maker_dome_sky",
                                              rename=self.dome_name + "_Sky")
        self.dome_ground.use_fake_user = True  # Bug In Blender 3.3 su Purge, cancella il dome anche se nella scena
        self.dome_sky.use_fake_user = True  # Bug In Blender 3.3 su Purge, cancella il dome anche se nella scena

        objProp = get_objprop(self.dome_ground)
        objProp.dome_type = dome_type
        objProp.dome_version = ItemsVersion.dome_version
        objProp = get_objprop(self.dome_sky)
        objProp.dome_type = dome_type
        objProp.dome_version = ItemsVersion.dome_version

        meshProp = get_meshprop(self.dome_ground.data)
        meshProp.self_tag = True
        meshProp = get_meshprop(self.dome_sky.data)
        meshProp.self_tag = True

        if self.dome_ground not in scn.objects[:]:
            # in this case the dome object is not present in the scene, so it need to be linked to the scene
            self.dome_collection.objects.link(self.dome_ground)
        if self.dome_sky not in scn.objects[:]:
            # in this case the dome object is not present in the scene, so it need to be linked to the scene
            self.dome_collection.objects.link(self.dome_sky)

        # Dome location is the same location of the dome handler
        self.dome_ground.location = self.dome_sky.location = (0, 0, 0)

        # The dome need to be hidden and unselectable, in addition it need to be locked in the scene, the scale is
        # managed by the dome handler, limit_scale is used to limit the scale of the dome, but with LOCAL it can be
        # scaled by the dome handler
        lock_object([self.dome_ground, self.dome_sky], hide_select=True)
        limit_rotation_constraints([self.dome_ground, self.dome_sky], use_limit_x=True, use_limit_y=True,
                                   use_limit_z=True, owner_space='LOCAL')
        limit_location_constraints([self.dome_ground, self.dome_sky], use_min_x=True, use_min_y=True, use_min_z=True,
                                   use_max_x=True,
                                   use_max_y=True, use_max_z=True, owner_space='LOCAL')
        limit_scale_constraints([self.dome_ground, self.dome_sky], use_min_x=True, use_min_y=True, use_min_z=True,
                                use_max_x=True,
                                use_max_y=True,
                                use_max_z=True, owner_space='LOCAL')

        # object_id_name is used to identify the object as a dome
        objProp = get_objprop(self.dome_ground)
        objProp.object_id_name = 'HDRI_MAKER_DOME_GROUND'

        objProp = get_objprop(self.dome_sky)
        objProp.object_id_name = 'HDRI_MAKER_DOME_SKY'

        self.dome_sky.visible_shadow = False
        self.dome_ground.visible_shadow = False

        return {'dome_ground': self.dome_ground, 'dome_sky': self.dome_sky}

    def add_reflection_plane(self):
        """Add a reflection plane to the dome, it is used to reflect the environment in the dome, it is necessary into
        eevee engine to have a correct reflection in the dome ground"""
        # Check if the reflection plane is already present in the scene
        self.reflection_plane = next(
            (o for o in self.context.scene.objects if get_objprop(o).object_id_name == 'DOME_REFLECTION_PLANE'), None)
        if self.reflection_plane:
            # If the reflection plane is present, need to be linked to the scene if it is not present in the scene
            if not self.reflection_plane in self.context.scene.objects[:]:
                self.dome_collection.objects.link(self.reflection_plane)
            else:
                # In this case need to be moved to the hdri maker tools collection
                move_ob_from_to_collection(self.reflection_plane, self.dome_collection)

        else:
            # In this case the reflection plane is not present in the scene, so it need to be created
            if bpy.app.version >= (4, 1, 0):
                planar_name = 'PLANE'
            else:
                planar_name = 'PLANAR'

            lp = bpy.data.lightprobes.new("Dome Reflection Plane", planar_name)
            self.reflection_plane = bpy.data.objects.new(name="Dome Reflection Plane", object_data=lp)
            objProp = get_objprop(self.reflection_plane)
            # object_id_name is used to identify the object as a reflection plane
            objProp.object_id_name = 'DOME_REFLECTION_PLANE'
            self.dome_collection.objects.link(self.reflection_plane)

        # The reflection plane need to be hidden and unselectable, in addition it need to be locked in the scene
        # The location is managed by the dome handler, like the dome
        self.reflection_plane.location = (0, 0, 0)
        self.reflection_plane.parent = self.dome_handler
        lock_object(self.reflection_plane)
        self.reflection_plane.hide_select = True
        self.reflection_plane.scale = self.dome_handler.scale * 12.5 + Vector((0.5, 0.5, 0.5))
        limit_location_constraints(self.reflection_plane, use_min_x=True, use_min_y=True, use_min_z=True,
                                   use_max_x=True, use_max_y=True, use_max_z=True)
        limit_rotation_constraints(self.reflection_plane, use_limit_x=True, use_limit_y=True, use_limit_z=False)

    def make_dome_child(self):
        """Make dome child of dome handler"""

        if not self.dome_handler:
            self.add_dome_handler()
        if not self.dome_ground or not self.dome_sky:
            self.load_dome()

        self.dome_ground.parent = self.dome_handler
        self.dome_sky.parent = self.dome_handler

    def asign_dome_material(self):
        """Asign the dome material to the dome, the dome material is a special material that is made to work with the dome"""

        if not self.dome_material:
            dome_mat_path = os.path.join(risorse_lib(), "blendfiles", "materials", "HDRi_Maker_Dome.blend")
            self.dome_material = load_libraries_material(dome_mat_path, 'HDRi_Maker_Dome')
            matProp = get_matprop(self.dome_material)
            matProp.mat_id_name = 'DOME_MATERIAL'
            matProp.dome_version = ItemsVersion.dome_version
            # Close the material node groups
            for n in self.dome_material.node_tree.nodes:
                if has_nodetree(n):
                    ndProp = get_ndprop(n)
                    ndProp.hide = True

        while self.dome_ground.data.materials[:]:
            self.dome_ground.data.materials.pop(index=-1)
        if self.dome_material not in self.dome_ground.data.materials[:]:
            self.dome_ground.data.materials.append(self.dome_material)
        while self.dome_sky.data.materials[:]:
            self.dome_sky.data.materials.pop(index=-1)
        if self.dome_material not in self.dome_sky.data.materials[:]:
            self.dome_sky.data.materials.append(self.dome_material)

        purge_all_group_names(self.dome_material.node_tree)

        return self.dome_material

    def asign_image_to_dome(self):
        """Asign the image to the dome material if exist an image"""
        dome_parts = get_dome_objects()
        ground = dome_parts.get('HDRI_MAKER_DOME_GROUND')
        sky = dome_parts.get('HDRI_MAKER_DOME_SKY')
        material = dome_parts.get('DOME_MATERIAL')
        if not material:
            return

        if ground:
            ground.name = self.dome_name + "_Ground"
            ground.data.name = self.dome_name + "_Ground"

        if sky:
            sky.name = self.dome_name + "_Sky"
            sky.data.name = self.dome_name + "_Sky"

        node_tree = material.node_tree
        nodes = node_tree.nodes

        background_node_group = next(
            (n for n in nodes if has_nodetree(n) if n.node_tree.hdri_prop_nodetree.group_id_name == 'COMPLETE'), None)

        if background_node_group:
            for n in background_node_group.node_tree.nodes:
                if n.type == 'TEX_ENVIRONMENT':
                    n.image = self.image

    def create_import_geometry_node(self):
        # geonode_path = os.path.join(risorse_lib(), "blendfiles", "geometry_nodes", "dome.blend")
        # geometry_node = load_libraries_geonodes(geonode_path, geonode_name='dome', rename='HdriMakerDome')
        # ngProp = get_ngprop(geometry_node)
        # ngProp.group_id_name = 'DOME_GEONODE'
        # modifier = self.dome.modifiers.new(name='Dome', type='NODES')
        # modifier.node_group = geometry_node
        #
        # For now we don't want to risk with the geometry nodes, so we use the modifier
        pass

    def asign_dome_ob_to_dome_material_coordinates(self):
        """Asign the dome object to the dome material coordinates into coordinates node, it is necessary to have a correct
        location of the texture material into the dome and into in ground objects"""
        if not self.dome_material:
            self.dome_material = get_dome_material(self.dome_ground)
        if not self.dome_material:
            return

        node_tree = self.dome_material.node_tree
        from ..background_tools.background_fc import get_nodes_dict
        node_dict = get_nodes_dict(node_tree)

        vectors_ng = node_dict.get('VECTORS')

        if not vectors_ng:
            return

        for n in vectors_ng.node_tree.nodes:
            if n.type == 'TEX_COORD':
                n.object = self.dome_ground

    def adjust(self):
        """Adjust the dome to the previous scale size, it is necessary to have a correct scale of the dome and the
        reflection plane"""
        if not get_objprop(self.dome_handler).un_lock_dome_handler:
            get_objprop(self.dome_handler).scale_dome_handler = self.scale if self.scale else 1
        if self.wrapped:
            # In this step, we need to add the old wrap modifier to the dome, because now the dome is New
            make_parent(self.dome_handler, self.wrapped)
            select_objects(self.wrapped)
            bpy.ops.hdrimaker.shrinkwrap(options='ADD', target='SELECTED_OBJECT')
            dome_dict = get_dome_objects()
            dome_ground = dome_dict.get('HDRI_MAKER_DOME_GROUND')

            subdivide = next((m for m in dome_ground.modifiers if m.type == 'SUBSURF'), None)
            if subdivide:
                restore_attributes(subdivide, self.subdivide_modifier_attributes)
            smooth = next((m for m in dome_ground.modifiers if m.type == 'CORRECTIVE_SMOOTH'), None)
            if smooth:
                restore_attributes(smooth, self.smooth_modifier_attributes)

        # Qui resetta la proprietà per scalare gli hooks! importantissimo
        Mtrx.last_scalars.clear()
        get_objprop(self.dome_handler).expand_hooks = 1

        # Re-parent the objects to the dome handler if they are not parented
        for ob in self.hdri_maker_ground_objects:
            if ob.parent != self.dome_handler:
                ob.parent = self.dome_handler


def hooks_exist(context):
    """Check if the hooks exist, if 1 hook exist, return True
    input: bpy.context"""
    hdri_col = get_collection_by_id_name(collection_id_name='HDRI_MAKER_DOME')
    if hdri_col:
        for ob in hdri_col.objects:
            objProp = get_objprop(ob)
            if objProp.object_id_name == 'DOME_HOOK':
                return True
    else:
        for ob in bpy.data.objects:
            objProp = get_objprop(ob)
            if objProp.object_id_name == 'DOME_HOOK':
                return True


def remove_dome_handler():
    """Remove only the dome handler"""
    for ob in bpy.data.objects:
        objProp = get_objprop(ob)
        if objProp.object_id_name == 'DOME_HANDLER':
            bpy.data.objects.remove(ob)


def find_current_dome_version(context):
    """Return the dome if exist in the scene, if the dome version is the same of the current version of HDRi Maker
    (ItemsVersion.dome_version)
    input: bpy.context"""
    dome_ground = None
    dome_sky = None
    for ob in context.scene.objects:
        if ob.type != 'MESH':
            continue
        objProp = get_objprop(ob)
        if objProp.dome_version == ItemsVersion.dome_version:

            if objProp.object_id_name == 'HDRI_MAKER_DOME_SKY':
                dome_sky = ob
            elif objProp.object_id_name == 'HDRI_MAKER_DOME_GROUND':
                dome_ground = ob

    return {'dome_ground': dome_ground, 'dome_sky': dome_sky}


def get_environment_from_world(world):
    """Return the environment image from the world if exist, if not return None,
    input: bpy.world
    return {'node_group': node_group, 'image': image}"""

    node_tree = world.node_tree
    nodes = node_tree.nodes

    image = None

    for n in nodes:
        # Nel caso della versione precedente alla 3 in cui i nodi erano senza gruppi
        if n.type == 'TEX_ENVIRONMENT':
            if 'HDRi Maker Background' in n.name:
                if n.image:
                    image = n.image
                    break
    if image:
        return {'image': image}

    for n in nodes:
        if not has_nodetree(n):
            continue
        ngProp = get_ngprop(n.node_tree)
        if ngProp.environment_type == 'TEXTURE_BACKGROUND':
            for tbn in n.node_tree.nodes:
                if tbn.type == 'TEX_ENVIRONMENT':
                    if tbn.image:
                        return {'node_group': None, 'image': tbn.image}

    # Second case, the image not exist in the world, but i want to try to find the node group in the world, if the node
    # group have the Vector inputs it can be used into the dome

    from ..background_tools.background_fc import get_nodes_dict
    node_dict = get_nodes_dict(node_tree)
    diffuse = node_dict.get("DIFFUSE")
    light = node_dict.get("LIGHT")
    complete = node_dict.get("COMPLETE")

    if complete:
        if complete.inputs.get("Vector"):
            return {'node_group': complete, 'image': None}
    elif diffuse:
        if diffuse.inputs.get("Vector"):
            return {'node_group': diffuse, 'image': None}
    elif light:
        if light.inputs.get("Vector"):
            return {'node_group': light, 'image': None}

    # In this last case we try to retrieve all nodes and subnodes, and the first node with the image is returned

    retrieve = retrieve_nodes(node_tree)
    for n in retrieve:
        if n.type == 'TEX_ENVIRONMENT':
            if n.image:
                return {'node_group': n.id_data, 'image': n.image}

    return {}


def get_dome_material(dome):
    """Return the dome material if exist, if not, return None"""
    material = next(
        (m for m in dome.data.materials if has_nodetree(m) if get_matprop(m).mat_id_name == 'DOME_MATERIAL'),
        None)

    return material


def asign_vcol_to_node_attribute(dome_material, v_col_name='HDRI_MAKER_GROUND'):
    """Asign the vertex color to the node attribute, it is necessary to have a vertex color with the name specified in
    the input
    : dome_material: bpy.data.materials, v_col_name: str"""

    node_tree = dome_material.node_tree
    nodes = node_tree.nodes

    for n in nodes:
        if not has_nodetree(n):
            continue
        ngProp = get_ngprop(n.node_tree)
        if ngProp.group_id_name == 'VECTORS':
            for sn in n.node_tree.nodes:
                if sn.type == 'VERTEX_COLOR':
                    sn.layer_name = v_col_name


#
#
# /‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾

def delete_dome(self, context):
    """Delete the dome from the scene"""
    remove_from_data = []

    scn = context.scene
    for ob in scn.objects:
        objProp = get_objprop(ob)
        if objProp.object_id_name in ['HDRI_MAKER_DOME_SKY', 'HDRI_MAKER_DOME_GROUND', 'HDRi_CenterPoint',
                                      'hdri_fog_box', 'DOME_REFLECTION_PLANE']:
            remove_from_data.append(ob)

    for ob in remove_from_data:
        if ob.type == 'MESH':
            mesh = ob.data
            bpy.data.meshes.remove(mesh)
            continue
        elif ob.type == 'LIGHT_PROBE':
            probe = ob.data
            bpy.data.lightprobes.remove(probe, do_unlink=True)
            continue

        bpy.data.objects.remove(ob, do_unlink=True)


def set_reflection_plane_size():
    """This function set the size of the reflection plane, it is necessary to adapt the size of the reflection plane
    in function of the hooks when the hooks are moved"""
    if not bpy.context:
        return

    scn = bpy.context.scene

    tools_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_TOOLS')
    dome_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_DOME')
    shadow_catcher_collection = get_collection_by_id_name(collection_id_name='SHADOW_CATCHER')
    light_sun_collection = get_collection_by_id_name(collection_id_name='SUN_STUDIO')
    light_studio_collection = get_collection_by_id_name(collection_id_name='LIGHT_STUDIO')

    # Avoids to work inside the collection "HDRI_MAKER_TOOLS" and "SHADOW_CATCHER" and "HDRI_MAKER_DOME"
    if bpy.context.collection in [tools_collection, dome_collection, shadow_catcher_collection, light_sun_collection,
                                  light_studio_collection]:
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection

    # Join the collections if exists

    # This function is very light if the collection "HDRI_MAKER_TOOLS" is not present in the scene,
    # the function finish here:
    if not dome_collection:
        return

    dome = None
    reflection_plane = None
    dome_handler = None
    hooks = []
    intruder = []
    for coll in [tools_collection, dome_collection, shadow_catcher_collection]:
        if not coll:
            # The coll can be None if the collection is not present in the scene
            continue

        for ob in coll.objects:
            objProp = get_objprop(ob)
            if objProp.object_id_name == 'DOME_REFLECTION_PLANE' and ob.type == 'LIGHT_PROBE':
                reflection_plane = ob
            elif objProp.object_id_name in ['HDRI_MAKER_DOME_SKY']:
                dome = ob
            elif objProp.object_id_name == 'DOME_HOOK' and ob.type == 'EMPTY':
                hooks.append(ob)
            elif objProp.object_id_name == 'DOME_HANDLER':
                dome_handler = ob
            elif not objProp.object_id_name:
                intruder.append(ob)

    if None in [dome, reflection_plane, dome_handler]:
        return

    # Rimuove eventuali collezioni aggiunte sotto la HDRi Maker Tools
    for coll in [dome_collection, shadow_catcher_collection]:
        if not coll:
            continue

        for child in coll.children:
            coll.children.unlink(child)

    # Sposta qualsiasi oggetto estraneo dalla collezione HDRi Maker tools
    for o in intruder:
        move_ob_from_to_collection(o, scn.collection)

    try:
        if hooks:
            # If the hooks are present, the size of the reflection plane is set in function of the hooks location
            coordinates = []
            for hk in hooks:
                coordinates.extend([abs(hk.location.x), abs(hk.location.y)])

            max_size = max(coordinates)
            scale = max_size + 0.5
            reflection_plane.scale = (scale, scale, scale)

        elif dome:

            reflection_plane.scale = (12.5 + 0.5, 12.5 + 0.5, 12.5 + 0.5)

    except:
        print(
            "Error in set_reflection_plane_size, the context is not valid, do not worry, this is just a warning. It's all ok")
        pass


def get_dome_objects():
    """Get all objects that are part of the dome, inside the collection "HDRI_MAKER_TOOLS" """
    tools_objects = {}
    collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_DOME')
    if not collection:
        return tools_objects

    for ob in collection.objects:
        objProp = get_objprop(ob)
        if ob.type == 'EMPTY':
            if objProp.object_id_name in ['DOME_HOOK']:
                if not objProp.object_id_name in tools_objects.keys():
                    tools_objects[objProp.object_id_name] = []
                tools_objects[objProp.object_id_name].append(ob)
            elif objProp.object_id_name == 'DOME_HANDLER':
                tools_objects[objProp.object_id_name] = ob

        elif ob.type == 'LIGHT_PROBE':
            if objProp.object_id_name == 'DOME_REFLECTION_PLANE':
                tools_objects[objProp.object_id_name] = ob

        elif ob.type == 'MESH':
            if objProp.object_id_name in ['HDRI_MAKER_DOME_GROUND', 'HDRI_MAKER_DOME_SKY']:
                tools_objects[objProp.object_id_name] = ob
                for mat in ob.data.materials:
                    if mat is None:
                        continue
                    matProp = get_matprop(mat)
                    if matProp.mat_id_name == 'DOME_MATERIAL':
                        tools_objects[matProp.mat_id_name] = mat

            elif objProp.object_id_name == 'DOME_HANDLER':
                tools_objects[objProp.object_id_name] = ob

            elif objProp.object_id_name == 'DOME_DRIVER':
                tools_objects[objProp.object_id_name] = ob

    return tools_objects


def get_sun_objects():
    """Return a list of sun objects"""
    sun_objects = {}
    collection = get_collection_by_id_name(collection_id_name='SUN_STUDIO')
    if not collection:
        return sun_objects

    for ob in collection.objects:
        objProp = get_objprop(ob)
        if ob.type == 'LIGHT':
            if objProp.object_id_name == 'HDRI_MAKER_SUN':
                sun_objects[objProp.object_id_name] = ob

        elif ob.type == 'EMPTY':
            if objProp.object_id_name == 'HDRI_MAKER_SUN_HANDLER':
                sun_objects[objProp.object_id_name] = ob

    sun_objects['collection'] = collection

    return sun_objects


def remove_mat_ground(objects):
    """Remove the "AddGround" material from the object, input is a list of objects"""
    # Check if objects is a list
    if not isinstance(objects, list):
        objects = [objects]

    for ob in objects:
        if ob.type != 'MESH':
            continue
        objProp = get_objprop(ob)
        if objProp.object_id_name != 'HDRI_MAKER_GROUND':
            continue

        for idx, mat in enumerate(ob.data.materials):
            matProp = get_matprop(mat)
            if matProp.mat_id_name == 'DOME_MATERIAL':
                ob.data.materials.pop(index=idx)

        v_col_to_delete = []
        for idx, v_col in enumerate(ob.data.vertex_colors):
            if 'HDRI_MAKER_GROUND' in v_col.name:
                v_col_to_delete.append(v_col)
        while v_col_to_delete:
            ob.data.vertex_colors.remove(v_col_to_delete.pop())

        # Important! Restore the objProp.object_id_name to ''
        objProp.object_id_name = ''


def un_parent_light_studio_from_dome():
    """Un-parent the Light studio Objects from the dome"""

    dome_objects = get_dome_objects()
    dome_handler = dome_objects.get('DOME_HANDLER')
    if not dome_handler:
        return

    from ..light_studio.light_studio_fc import get_light_studio_objects
    light_objects = get_light_studio_objects()
    lamp_holders = light_objects.get('LAMP_HOLDERS')
    if lamp_holders:
        un_parent(lamp_holders)

    light_target = light_objects.get('LIGHT_TARGET')
    if light_target:
        un_parent(light_target)


def recreate_dome_handler():
    dome_objects = get_dome_objects()
    dome_handler = dome_objects.get('DOME_HANDLER')
    if not dome_handler:
        dome_handler = bpy.data.objects.new('Dome Handler', None)
        objProp = get_objprop(dome_handler)
        objProp.object_id_name = 'DOME_HANDLER'
        dome_handler.empty_display_type = 'PLAIN_AXES'
        dome_handler.location = (0, 0, 0)
        dome_handler.scale = (1, 1, 1)

    # Move the dome handler to the collection "HDRI_MAKER_DOME"
    move_ob_from_to_collection(dome_handler, get_collection_by_id_name(collection_id_name='HDRI_MAKER_DOME'))

    from ..light_studio.light_studio_fc import get_light_studio_objects
    light_studio_objects = get_light_studio_objects()
    lamp_holders = light_studio_objects.get('LAMP_HOLDERS')
    lamp_target = light_studio_objects.get('LIGHT_TARGET')

    if lamp_holders:
        if not lamp_holders.parent:
            lamp_holders.parent = dome_handler

    if lamp_target:
        if not lamp_target.parent:
            lamp_target.parent = dome_handler

    for key, obj in dome_objects.items():
        if key == 'DOME_HANDLER':
            continue
        if hasattr(obj, 'parent') and obj.parent != dome_handler:
            obj.parent = dome_handler

    for ob in bpy.context.scene.objects:
        objProp = get_objprop(ob)
        if objProp.is_shrinkwrap:
            ob.parent = dome_handler

        elif objProp.object_id_name == 'DOME_HOOK':
            if not ob.parent:
                ob.parent = dome_handler

        elif objProp.object_id_name == 'HDRI_MAKER_GROUND':
            if not ob.parent:
                ob.parent = dome_handler

