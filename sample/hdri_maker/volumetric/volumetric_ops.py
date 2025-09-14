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

from ..background_tools.background_fc import get_nodes_dict, set_world_goodies
from ..exaproduct import Exa


class HDRIMAKER_OT_VolumetricOnOff(Operator):
    """Turn On/Off The volumetric Node, keep it into node tree, only unlink from Output node"""

    bl_idname = Exa.ops_name + "volumetric_on_off"
    bl_label = "Volumetric On/Off"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Turn On/Off The volumetric Node, keep it into node tree, only unlink from Output node"

    def execute(self, context):
        scn = context.scene
        world = scn.world

        if not world:
            self.report({'ERROR'}, "No World")
            return {'CANCELLED'}

        if not world.node_tree:
            self.report({'ERROR'}, "No Node Tree")
            return {'CANCELLED'}

        from ..background_tools.background_fc import get_nodes_dict
        nodes_dict = get_nodes_dict(world.node_tree)
        volume = nodes_dict.get('VOLUMETRIC')
        node_output = nodes_dict.get('OUTPUT_WORLD')

        if not volume:
            self.report({'ERROR'}, "No Volumetric Node")
            return {'CANCELLED'}

        # Check if node_output have the input socket named "Volume"
        if not node_output.inputs.get('Volume'):
            # Caso raro se qualcosa cambia all'insaputa in Blender e manca un socket al nodo world output
            self.report({'ERROR'}, "No Volume Socket in the Output Node, This should not happen, please report it")
            return {'CANCELLED'}

        if not node_output:
            self.report({'ERROR'}, "No Output Node")
            return {'CANCELLED'}

        # Check if the volume node have the outputs[0] named "Volume"
        volume_output = volume.outputs.get('Volume')
        if not volume_output:
            self.report({'ERROR'}, "No Volume Output in the Volumetric Node Group")
            return {'CANCELLED'}

        links = world.node_tree.links

        # Check if exist the Node Output
        if volume_output.is_linked:
            # Unlink the node
            links.remove(volume_output.links[0])
        else:
            # Link the node
            links.new(volume_output, node_output.inputs['Volume'])

        return {'FINISHED'}


class HDRIMAKER_OT_LoadVolumes(Operator):
    """Load or remove the Volume NodeGroups"""

    bl_idname = Exa.ops_name + "load_volumes"
    bl_label = "Load Volumes"
    bl_options = {'REGISTER', 'UNDO'}

    options: EnumProperty(items=(('ADD', "Add", ""), ('REMOVE', "Remove", "")), options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        if properties.options == 'ADD':
            return "Load the Volume NodeGroups"
        else:
            return "Remove the Volume NodeGroups"

    def execute(self, context):
        scn = context.scene
        world = scn.world

        if not world:
            # Create on the fly a simple world
            world = bpy.data.worlds.new("World")
            world.use_nodes = True
            scn.world = world
            set_world_goodies(world)

        from ..utility.utility import has_nodetree

        if not has_nodetree(world):
            self.report({'ERROR'}, "No Node Tree, please add a World or Activate the Options Use Nodes in this scene world")
            return {'CANCELLED'}

        if self.options == 'ADD':
            from ..volumetric.volumetric_fc import load_volumetric
            load_volumetric(self, context)

        else:
            nodes_dict = get_nodes_dict(world.node_tree)
            volume = nodes_dict.get('VOLUMETRIC')
            if volume:
                world.node_tree.nodes.remove(volume)

        return {'FINISHED'}


