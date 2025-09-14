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
import math

import bpy

from ..collections_scene.collection_fc import get_light_studio_collection, get_hdri_maker_tools_collection, \
    get_collection_by_id_name
from ..dome_tools.dome_fc import get_dome_objects
from ..exaconv import get_objprop
from ..utility.constraints import damper_track_constraints, limit_scale_constraints
from ..utility.utility import create_circle_mesh, create_empty_object, get_edge_vertex_location_divided, create_light, \
    make_parent_v2, apply_object_scale, copy_attributes, set_object_mode, make_parent


def update_lights_studio_count(self, context):

    # Check if Dome is in the scene:
    dome_objects = get_dome_objects()
    dome_handler = dome_objects.get('DOME_HANDLER')
    dome_sky = dome_objects.get('HDRI_MAKER_DOME_SKY')

    if dome_sky:
        dome_size_z = dome_sky.dimensions.z
        dome_size_x = dome_sky.dimensions.x

    # Check if Light Studio Collection is in the scene:
    light_studio_collection = get_light_studio_collection()

    # First Step - Create Circle Curve with 4 points
    # Check if the lamp_holders is in the scene:
    # We need to check if the lamp_holders is the original and not a copy, The original probably have the Light children
    lp_h = [obj for obj in context.scene.objects if get_objprop(obj).object_id_name == 'LAMP_HOLDERS']

    if len(lp_h) > 1:
        lamp_holders = next((obj for obj in lp_h if obj.children_recursive), lp_h[0])
        for obj in lp_h:
            if obj != lamp_holders:
                bpy.data.objects.remove(obj)
    else:
        lamp_holders = next((obj for obj in lp_h), None)

    if dome_sky:
        location = (0, 0, dome_size_z * 0.5)
        radius = dome_size_x * 0.25
    else:
        location = (0, 0, 5)
        radius = 5

    if not lamp_holders:
        lamp_holders = create_circle_mesh(name='Lamp holders', location=location, radius=radius, vertices=512,
                                          collection=light_studio_collection)
        get_objprop(lamp_holders).object_id_name = 'LAMP_HOLDERS'

    set_object_mode(lamp_holders)

    apply_object_scale(lamp_holders)

    context.scene.collection.update_tag()

    # Create Empty Sphere on the bottom (0,0,0)
    # Check if the sphere is in the scene:
    light_target = next((obj for obj in context.scene.objects if get_objprop(obj).object_id_name == 'LIGHT_TARGET'),
                        None)
    if not light_target:
        light_target = create_empty_object(name="Light Target", empty_display_type='SPHERE',
                                           collection=light_studio_collection, location=(location[0], location[1], 0))
        get_objprop(light_target).object_id_name = 'LIGHT_TARGET'


    # Create lights and locate them on the lamp_holders vertices, and parent them to the lamp_holders
    # Check if the lights are in the scene:
    lights = [obj for obj in context.scene.objects if get_objprop(obj).object_id_name == 'LIGHT_HOLDER']

    vertex_location_list = get_edge_vertex_location_divided(lamp_holders, self.light_studio_count)

    # if the number of lights is different from the number of vertex_location_list, create or delete lights
    # We need to redistribute the lights on the vertices if some lights are present
    if len(lights) != len(vertex_location_list):
        if len(lights) > len(vertex_location_list):
            # Delete lights
            for i in range(len(lights) - len(vertex_location_list)):
                # Remove data.light
                bpy.data.lights.remove(lights[i].data)
                # Update lights list, we need to remove lights[i] from the list
                lights = [obj for obj in context.scene.objects if get_objprop(obj).object_id_name == 'LIGHT_HOLDER']
        else:
            # Create lights
            for i in range(len(vertex_location_list) - len(lights)):

                light = create_light(name='Light holder',
                                     location=(0, 0, 0),
                                     light_type=self.light_type,
                                     collection=light_studio_collection,
                                     rotation=(0, 0, 0),
                                     energy=400,
                                     light_color=(0.904661, 1, 0.955973))  # Default light color "Standard Fluorescent"

                get_objprop(light).object_id_name = 'LIGHT_HOLDER'
                # Bisogna prendere e copiare i parametri di una luce se presente e applicarli alla light appena creata:
                if lights:
                    copy_attributes(lights[0].data, light.data)

                lights.append(light)

    # Update lights location and parent
    for i in range(len(lights)):
        lights[i].location = vertex_location_list[i]
        lights[i].data.type = self.light_type
        if lights[i].data.type == 'AREA':
            lights[i].data.shape = self.light_shape
        # Rotate the light on Y axis 90 degrees and make it pointing to the light_target center
        rot_z = math.atan2(lights[i].location.y, lights[i].location.x)
        lights[i].rotation_euler = (0, math.radians(90), rot_z)
        # Make unselectable
        lights[i].hide_select = True

    limit_scale_constraints(lights)
    damper_track_constraints(lights, target=light_target)
    make_parent_v2(lamp_holders, lights)

    if dome_handler and lamp_holders and light_target:
        if not lamp_holders.parent and not light_target.parent:
            # In questo caso riportiamo l'handler a (0,0,0) e lo ruotiamo a (0,0,0) per evitare problemi di posizionamento
            # in quanto creare un parent fuori dal centro del mondo fa si che tutte le coordinate dei figli vengano
            # spostate di conseguenza quindi l'asse Z non è poi in relazione all'altezza del dome
            dome_handler_location = dome_handler.location[:]
            dome_handler_rotation = dome_handler.rotation_euler[:]
            dome_handler.location = (0, 0, 0)
            dome_handler.rotation_euler = (0, 0, 0)

            # Update the object location:
            context.view_layer.depsgraph.update()


            make_parent(dome_handler, [lamp_holders, light_target])

            dome_handler.location = dome_handler_location
            dome_handler.rotation_euler = dome_handler_rotation

            context.view_layer.depsgraph.update()


def remove_light_studio_objects():
    for ob in bpy.context.scene.objects:
        objProp = get_objprop(ob)
        if objProp.object_id_name in ['LAMP_HOLDERS', 'LIGHT_TARGET', 'LIGHT_HOLDER']:
            if ob.type == 'MESH':
                bpy.data.meshes.remove(ob.data)
            elif ob.type == 'LIGHT':
                bpy.data.lights.remove(ob.data)
            else:
                bpy.data.objects.remove(ob)

    # Remove light studio collection if exists
    light_studio_collection = get_light_studio_collection()
    if light_studio_collection:
        bpy.data.collections.remove(light_studio_collection)
    # Remove Hdri Maker Tools collection if exists and empty
    hdri_maker_tools_collection = get_hdri_maker_tools_collection(bpy.context.scene)
    if hdri_maker_tools_collection and not hdri_maker_tools_collection.objects:
        # Check if collection not have children collections
        if not hdri_maker_tools_collection.children:
            bpy.data.collections.remove(hdri_maker_tools_collection)


def get_light_studio_objects():
    objects_dict = {}

    light_studio_collection = get_collection_by_id_name('LIGHT_STUDIO')
    if not light_studio_collection:
        return objects_dict

    lamp_holders = []
    for ob in light_studio_collection.objects:
        objProp = get_objprop(ob)
        if objProp.object_id_name == 'LIGHT_HOLDER':
            lamp_holders.append(ob)
        elif objProp.object_id_name == 'LIGHT_TARGET':
            objects_dict['LIGHT_TARGET'] = ob
        elif objProp.object_id_name == 'LAMP_HOLDERS':
            objects_dict['LAMP_HOLDERS'] = ob

    objects_dict['LIGHT_HOLDER'] = lamp_holders

    return objects_dict


