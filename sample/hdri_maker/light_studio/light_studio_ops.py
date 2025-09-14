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
from bpy.props import EnumProperty, StringProperty, BoolProperty
from bpy.types import Operator

from ..exaproduct import Exa


class HDRIMAKER_OT_CreateLightStudio(Operator):
    bl_idname = Exa.ops_name + "create_light_studio"
    bl_label = "Create Light Studio"
    bl_description = "Create Light Studio objects"
    bl_options = {'REGISTER', 'UNDO'}

    options: EnumProperty(
        options={'HIDDEN'},
        items=(('ADD', "Add", "Create Light Studio objects"),
               ('REMOVE', "Remove", "Remove Light Studio objects")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ADD':
            desc = "Create Light Studio objects"
        elif properties.options == 'REMOVE':
            desc = "Remove Light Studio objects"
        return desc

    def execute(self, context):

        scn = context.scene

        from ..exaconv import get_scnprop
        scnProp = get_scnprop(scn)

        if self.options == 'ADD':
            from ..utility.utility import set_object_mode
            set_object_mode(context.view_layer.objects.active)
            from ..light_studio.light_studio_fc import update_lights_studio_count
            update_lights_studio_count(scnProp, context)

        elif self.options == 'REMOVE':
            from ..light_studio.light_studio_fc import remove_light_studio_objects
            remove_light_studio_objects()

        return {'FINISHED'}


class HDRIMAKER_OT_RandomLightColor(Operator):
    """Randomize the Light Color"""

    bl_idname = Exa.ops_name + "random_light_color"
    bl_label = "Randomize Light Color"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Randomize the Lights Color"

    def execute(self, context):
        from ..light_studio.light_studio_fc import get_light_studio_objects
        light_studio_dict = get_light_studio_objects()
        lights = light_studio_dict.get('LIGHT_HOLDER')
        if lights:
            from random import random
            for light in lights:
                # Randomize the RGB color of the lights
                light.data.color = (random(), random(), random())

        return {'FINISHED'}


class HDRIMAKER_OT_ParentTarget(Operator):
    """Parent/Unparent The target Object with the selected Object"""

    bl_idname = Exa.ops_name + "parent_target"
    bl_label = "Parent Target"
    bl_options = {'REGISTER', 'UNDO'}

    options: EnumProperty(
        items=(
            ('PARENT', "Parent", "Parent the target object with the selected object"),
            ('UNPARENT', "Un-parent", "Un-parent the target object")
        )
    )

    object_name: StringProperty()
    target_to_object: BoolProperty(default=False)

    @classmethod
    def description(cls, context, properties):
        return "Parent/Unparent The target Object with the selected Object"

    def execute(self, context):
        scn = context.scene
        from ..light_studio.light_studio_fc import get_light_studio_objects
        objects_list = get_light_studio_objects()
        object = bpy.data.objects.get(self.object_name)

        if not object:
            return {'CANCELLED'}

        father = context.view_layer.objects.active
        if not father:
            from ..utility.text_utils import draw_info
            text = "Please select the object you want to parent the target to"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if self.options == 'PARENT':

            if self.target_to_object:
                object.location = father.location

            from ..utility.utility import make_parent_v2
            make_parent_v2(father, object)

        elif self.options == 'UNPARENT':
            from ..utility.utility import un_parent
            un_parent(object)

        return {'FINISHED'}
