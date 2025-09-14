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


from bpy.types import Operator

from ..exaproduct import Exa
from ..utility.text_utils import draw_info


class HDRIMAKER_OT_ConvertWorld(Operator):


    bl_idname = Exa.ops_name+"convert_world"
    bl_label = "Convert World"
    bl_description = "Converts the current world to an environment"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    def execute(self, context):

        scn = context.scene

        world = scn.world

        if not world:
            self.report({'ERROR'}, "No world to convert")
            return {'CANCELLED'}

        if not world.use_nodes:
            self.report({'ERROR'}, "World is not using nodes, so it cannot be converted")
            return {'CANCELLED'}

        from ..dome_tools.dome_fc import get_environment_from_world
        result = get_environment_from_world(world)

        image = result.get('image')
        if not image:
            from ..exaconv import get_wrlprop
            wrlProp = get_wrlprop(world)
            if wrlProp.world_id_name == 'BASIC_WORLD':
                text = "Default world of HDRi Maker cannot be converted, no HDR/EXR image in this world"
                draw_info(text, "Info", 'INFO')
                self.report({'INFO'}, text)
                return {'CANCELLED'}

            text = "The current world cannot be converted to an HDRi Maker World, since no HDR/EXR image was found in it"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        from ..background_tools.background_fc import import_hdri_maker_world
        from ..utility.utility import purge_all_group_names
        from ..background_tools.background_fc import assign_image_to_background_node

        new_world = import_hdri_maker_world(context, rename=world.name)

        assign_image_to_background_node(image, environment='COMPLETE')

        purge_all_group_names(new_world.node_tree)


        return {'FINISHED'}