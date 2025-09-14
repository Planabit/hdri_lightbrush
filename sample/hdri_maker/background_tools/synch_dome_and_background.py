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
from bpy.props import EnumProperty
from bpy.types import Operator

from ..exaproduct import Exa


class HDRIMAKER_OT_sync_node_background_rotation(Operator):
    bl_idname = Exa.ops_name + "sync_node_background_rotation"
    bl_label = "Sync Rotation"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('SYNC_FROM_BACKGROUND', "From Background", "Sync from background"),
                                 ('SYNC_FROM_DOME', "From Dome", "Sync from dome"),
                                 ('UN_SYNC', "Unsync", "Unsync"),
                                 ),
                          name="Sync Options",
                          description="Sync options",
                          default='SYNC_FROM_BACKGROUND',
                          options={'HIDDEN'})

    sync_from_background_is_active = False
    sync_from_dome_is_active = False

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'SYNC_FROM_BACKGROUND':
            desc = "Sync rotation with dome rotation (If the dome is in the scene)"
        elif properties.options == 'SYNC_FROM_DOME':
            desc = "Sync rotation with background rotation"
        elif properties.options == 'UN_SYNC':
            desc = "Unsync rotation if Dome or Background are Synced"
        return desc

    def execute(self, context):
        scn = context.scene
        world = scn.world

        cls = self.__class__

        from ..utility.utility import has_nodetree
        from ..dome_tools.dome_fc import get_dome_objects
        from ..background_tools.background_fc import get_nodes_dict

        world_vectors = None
        dome_vectors = None
        if has_nodetree(world):
            nodes_dict = get_nodes_dict(world.node_tree)
            world_vectors = nodes_dict.get('VECTORS')

        dome_objects_list = get_dome_objects()
        dome_material = dome_objects_list.get('DOME_MATERIAL')
        if dome_material:
            if has_nodetree(dome_material):
                nodes_dict = get_nodes_dict(dome_material.node_tree)
                dome_vectors = nodes_dict.get('VECTORS')

        if self.options in ['SYNC_FROM_BACKGROUND', 'SYNC_FROM_DOME']:
            if not world_vectors:
                self.report({'INFO'}, "No Background Found, the sync is not possible")
                return {'CANCELLED'}
            if not dome_vectors:
                self.report({'INFO'}, "No Dome Found, the sync is not possible")
                return {'CANCELLED'}

        if self.options == 'UN_SYNC':
            cls.sync_from_background_is_active = False
            cls.sync_from_dome_is_active = False

        if world_vectors:
            world_vectors_angle = world_vectors.inputs.get("Angle")
            if world_vectors_angle:
                # Remove driver:
                world_vectors_angle.driver_remove("default_value")
                # Add Driver:
                if self.options == 'SYNC_FROM_DOME':
                    cls.sync_from_background_is_active = False
                    if dome_vectors:
                        driver = world_vectors_angle.driver_add("default_value").driver
                        driver.type = 'SUM'
                        var = driver.variables.new()
                        var.name = "Angle"
                        var.type = 'SINGLE_PROP'
                        # Use Material path to get the variable:
                        var.targets[0].id_type = 'MATERIAL'
                        var.targets[0].id = dome_material
                        var.targets[0].data_path = 'node_tree.nodes["{}"].inputs["Angle"].default_value'.format(
                            dome_vectors.name)
                        cls.sync_from_dome_is_active = True

        if dome_vectors:
            dome_vectors_angle = dome_vectors.inputs.get("Angle")
            if dome_vectors_angle:
                # Remove driver:
                dome_vectors_angle.driver_remove("default_value")
                # Add Driver:
                if self.options == 'SYNC_FROM_BACKGROUND':
                    cls.sync_from_dome_is_active = False
                    if world_vectors:
                        driver = dome_vectors_angle.driver_add("default_value").driver
                        driver.type = 'SUM'
                        var = driver.variables.new()
                        var.name = "Angle"
                        var.type = 'SINGLE_PROP'
                        # Use Material path to get the variable:
                        var.targets[0].id_type = 'WORLD'
                        var.targets[0].id = world
                        var.targets[0].data_path = 'node_tree.nodes["{}"].inputs["Angle"].default_value'.format(
                            world_vectors.name)
                        cls.sync_from_background_is_active = True


        return {'FINISHED'}
