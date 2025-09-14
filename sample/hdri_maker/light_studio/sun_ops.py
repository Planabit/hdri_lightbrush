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
from bpy.props import EnumProperty
from bpy.types import Operator

from ..exaproduct import Exa


class HDRIMAKER_OT_SunMaker(Operator):
    bl_idname = Exa.ops_name + "sun_maker"
    bl_label = "Sun Maker"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('ADD', "Add", ""), ('REMOVE', "Remove", "")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ADD':
            desc = "Add sun"
        elif properties.options == 'REMOVE':
            desc = "Remove sun"
        return desc

    def execute(self, context):

        from ..utility.utility import create_empty_object
        from ..collections_scene.collection_fc import get_sun_studio_collection
        from ..utility.utility import hide_object
        from ..exaconv import get_objprop
        from ..collections_scene.collection_fc import move_ob_from_to_collection
        from ..utility.constraints import limit_location_constraints
        from ..utility.constraints import limit_scale_constraints
        from ..utility.constraints import limit_rotation_constraints
        from ..utility.constraints import damper_track_constraints
        from ..dome_tools.dome_fc import get_sun_objects
        from ..collections_scene.collection_fc import get_collection_by_id_name

        dome_objects_dict = get_sun_objects()
        sun_handler = dome_objects_dict.get('HDRI_MAKER_SUN_HANDLER')
        hdri_maker_sun = dome_objects_dict.get('HDRI_MAKER_SUN')

        if self.options == 'REMOVE':
            if sun_handler:
                bpy.data.objects.remove(sun_handler)
            if hdri_maker_sun:
                bpy.data.lights.remove(hdri_maker_sun.data)

            sun_studio_collection = get_collection_by_id_name('SUN_STUDIO')
            if sun_studio_collection:
                # Check if the collection is empty:
                if len(sun_studio_collection.objects) == 0:
                    bpy.data.collections.remove(sun_studio_collection)

            bpy.ops.hdrimaker.sync_sun(options='UNSYNC')

            return {'FINISHED'}

        if self.options == 'ADD':
            sun_studio_collection = get_sun_studio_collection(create=True)
            if not sun_handler:
                sun_handler = create_empty_object(name="Sun Handler", collection=sun_studio_collection,
                                                  empty_display_type='CUBE', size=1, location=(0, 0, 0),
                                                  rotation=(0, 0, 0))
                objProp = get_objprop(sun_handler)
                objProp.object_id_name = 'HDRI_MAKER_SUN_HANDLER'

            hide_object(sun_handler, hide=True)

            if not hdri_maker_sun:
                # Check if a sun exists in the scene:
                sun = next((obj for obj in context.scene.objects if obj.type == 'LIGHT' and obj.data.type == 'SUN'),
                           None)
                if sun:
                    hdri_maker_sun = sun
                    objProp = get_objprop(sun)
                    objProp.object_id_name = 'HDRI_MAKER_SUN'
                    move_ob_from_to_collection(hdri_maker_sun, sun_studio_collection)


                else:
                    hdri_maker_sun = bpy.data.objects.new(name="HDRI Maker Sun",
                                                          object_data=bpy.data.lights.new(name="HDRI Maker Sun",
                                                                                          type='SUN'))
                    objProp = get_objprop(hdri_maker_sun)
                    objProp.object_id_name = 'HDRI_MAKER_SUN'
                    sun_studio_collection.objects.link(hdri_maker_sun)

                hdri_maker_sun.location = (8, 0, 8)
                hdri_maker_sun.data.energy = 1

            # Limit Location, rotation and scale of the sun handler:

            limit_location_constraints(sun_handler, use_min_x=True, use_max_x=True, use_min_y=True, use_max_y=True,
                                       use_min_z=True, use_max_z=True,
                                       min_x=0, max_x=0, min_y=0, max_y=0, min_z=0, max_z=0)
            limit_scale_constraints(sun_handler, use_min_x=True, use_max_x=True, use_min_y=True, use_max_y=True,
                                    use_min_z=True, use_max_z=True,
                                    min_x=1, max_x=1, min_y=1, max_y=1, min_z=1, max_z=1)
            limit_rotation_constraints(sun_handler, use_limit_x=True, use_limit_y=True, use_limit_z=False, min_x=0,
                                       max_x=0, min_y=0, max_y=0)

            damper_track_constraints(hdri_maker_sun, target=sun_handler, track_axis='TRACK_NEGATIVE_Z')

            from ..utility.utility import make_parent
            make_parent(sun_handler, hdri_maker_sun)

            hdri_maker_sun.data.use_shadow = True
            hdri_maker_sun.data.use_contact_shadow = True
            hdri_maker_sun.data.shadow_cascade_max_distance = 500

        return {'FINISHED'}


def add_driver_to_sun_driver_z(sun_driver_z, sun_handler):
    driver = sun_driver_z.outputs[0].driver_add('default_value')
    driver.driver.type = 'SUM'
    # Add the object to the driver:
    driver.driver.variables.new()
    driver.driver.variables[0].name = 'sun'
    driver.driver.variables[0].type = 'TRANSFORMS'
    # Put the sun_handler as the target:
    driver.driver.variables[0].targets[0].id = sun_handler
    driver.driver.variables[0].targets[0].transform_type = 'ROT_Z'


def sync_sun(context, options="SYNC"):
    from ..exaconv import get_scnprop
    from ..background_tools.background_fc import get_nodes_dict
    from ..utility.utility import has_nodetree
    from ..dome_tools.dome_fc import get_sun_objects
    from ..dome_tools.dome_fc import get_dome_objects

    scn = context.scene
    scnProp = get_scnprop(scn)

    sun_objects_dict = get_sun_objects()
    sun = sun_objects_dict.get('HDRI_MAKER_SUN')
    sun_handler = sun_objects_dict.get('HDRI_MAKER_SUN_HANDLER')

    world = scn.world
    if world:
        if has_nodetree(world):
            nodes_dict = get_nodes_dict(world.node_tree)
            vectors = nodes_dict.get('VECTORS')
            if vectors:
                sun_driver_z = next(
                    (n for n in vectors.node_tree.nodes if n.name == 'SUN_DRIVER_Z' if n.type == 'VALUE'), None)
                if sun_driver_z:
                    # Remove the driver:
                    sun_driver_z.outputs[0].driver_remove('default_value')
                    if options == 'SYNC':
                        # Add Driver to the value input
                        add_driver_to_sun_driver_z(sun_driver_z, sun_handler)
                    else:
                        # Restore default value: to 0
                        sun_driver_z.outputs[0].default_value = 0

    dome_objects_list = get_dome_objects()
    dome_material = dome_objects_list.get('DOME_MATERIAL')
    if dome_material:
        nodes_dict = get_nodes_dict(dome_material.node_tree)
        vectors = nodes_dict.get('VECTORS')
        if vectors:
            sun_driver_z = next(
                (n for n in vectors.node_tree.nodes if n.name == 'SUN_DRIVER_Z' if n.type == 'VALUE'), None)
            if sun_driver_z:
                # Remove the driver:
                sun_driver_z.outputs[0].driver_remove('default_value')
                if options == 'SYNC':
                    # Add Driver to the value input
                    add_driver_to_sun_driver_z(sun_driver_z, sun_handler)
                else:
                    # Restore default value: to 0
                    sun_driver_z.outputs[0].default_value = 0

def get_sun_sinc_driver(node_tree):
    # Checking by get the driver into the defaut_value input:

    from ..background_tools.background_fc import get_nodes_dict
    nodes_dict = get_nodes_dict(node_tree)
    vectors = nodes_dict.get('VECTORS')
    if not vectors:
        return None

    sun_driver_z = next((n for n in vectors.node_tree.nodes if n.name == 'SUN_DRIVER_Z' if n.type == 'VALUE'), None)

    if sun_driver_z:
        return sun_driver_z


class HDRIMAKER_OT_SyncSun(Operator):
    bl_idname = Exa.ops_name + "sync_sun"
    bl_label = "Sync Sun"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('SYNC', "Sync", ""), ('UNSYNC', "Un-Sync", "")),
                          options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'SYNC':
            desc = "Try to Sync the sun rotation with the Background and the Dome"
        elif properties.options == 'UNSYNC':
            desc = "Unsync the sun rotation from the Background and the Dome"
        return desc

    def execute(self, context):
        sync_sun(context, self.options)

        return {'FINISHED'}
