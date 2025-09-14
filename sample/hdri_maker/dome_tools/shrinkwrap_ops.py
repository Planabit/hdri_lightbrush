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
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from ..collections_scene.collection_fc import get_collection_by_id_name, get_dome_collection, \
    get_shadow_catcher_collection
from ..dome_tools.dome_fc import find_current_dome_version, get_dome_objects
from ..exaconv import get_objprop
from ..exaproduct import Exa
from ..utility.modifiers import remove_empty_shrinkwrap_modifiers, add_subdivision_surface, add_corrective_smooth, \
    move_modifier_index, add_shrinkwrap
from ..utility.text_utils import draw_info
from ..utility.utility import make_parent, set_object_bounds, un_parent


class HDRIMAKER_OT_Shrinkwrap(Operator):
    """Assign/remove Shrinkwrap to object(s)"""

    bl_idname = Exa.ops_name + "shrinkwrap"
    bl_label = "Shrinkwrap"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('ADD', "Add", ""), ('REMOVE', "Remove", ""), ("REMOVE_ALL", "Remove All", "")))
    target: StringProperty()

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ADD':
            desc = "Assign Shrinkwrap to the selected object(s)"
        elif properties.options == 'REMOVE':
            desc = "Remove Shrinkwrap from the selected object"
        return desc

    def execute(self, context):
        scn = context.scene

        tool_collection = get_collection_by_id_name(collection_id_name='HDRI_MAKER_TOOLS')
        dome_collection = get_dome_collection(create=False)
        sc_collection = get_shadow_catcher_collection(create=False)

        forbidden_objs = []
        if tool_collection:
            forbidden_objs.extend(tool_collection.objects)
        if dome_collection:
            forbidden_objs.extend(dome_collection.objects)
        if sc_collection:
            forbidden_objs.extend(sc_collection.objects)

        if self.target == 'SELECTED_OBJECT':
            targets = [o for o in context.selected_objects if o.type == 'MESH' and o not in forbidden_objs]
        else:
            targets = [o for o in bpy.data.objects if o.name == self.target]

        dome_parts = find_current_dome_version(context)
        dome_ground = dome_parts.get('dome_ground')
        dome_sky = dome_parts.get('dome_sky')

        if not dome_sky or not dome_ground:
            text = "Dome is not present in the current scene, so it is not possible to assign the shrinkwrap modifier."
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        remove_empty_shrinkwrap_modifiers(dome_ground)

        dome_dict = get_dome_objects()
        dome_handler = dome_dict.get('DOME_HANDLER')

        ss = next((mod for mod in dome_ground.modifiers if mod.type == 'SUBSURF'), None)
        cs = next((mod for mod in dome_ground.modifiers if mod.type == 'CORRECTIVE_SMOOTH'), None)

        if self.options == 'ADD':
            if not targets:
                text = "No object selected Or object(s) are not 'MEHS' type. To make the shrinkwrap, select the object(s) to which you want to apply the shrinkwrap." \
                       "the object(s) must be of type 'MESH'."
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            # Since there may be Hook modifiers, you have to count them and put them right after them the modifiers
            # dedicated to shrinkwrap, otherwise they don't work.
            # To do this, you count the Hook modifiers, and you put them right after them the Shrinkwrap modifiers.

            # First of all, the Hook modifiers are counted
            hooks_count = 0
            for mod in dome_ground.modifiers:
                if mod.type == 'HOOK':
                    hooks_count += 1

            if targets:
                if not ss:
                    ss = add_subdivision_surface(dome_ground, name=dome_ground.name + "_SS")
                if not cs:
                    # cs modifier need to be always at the end of the modifiers list
                    cs = add_corrective_smooth(dome_ground, name=dome_ground.name + "_CS", vertex_group="Ground")

            # The ss modifier must be right after the hooks, otherwise it doesn't work. hooks_count is the number of hooks present.
            # We use the move_modifier_to_index function to move the ss modifier to the hooks_count position.
            move_modifier_index(ss, to_index=hooks_count)

            for obj in targets:
                # Check if the object has already shrinkwrap modifier as target
                if next((mod for mod in dome_ground.modifiers if mod.type == 'SHRINKWRAP' and mod.target == obj), None):
                    # If the object has already shrinkwrap modifier as target, then it is skipped
                    continue

                objProp = get_objprop(obj)
                objProp.is_shrinkwrap = True

                shrinkwrap = add_shrinkwrap(dome_ground, obj, name=obj.name + "_SW", vertex_group="Ground")
                move_modifier_index(shrinkwrap, to_index=-1)
                # The obj need to be children of the dome handler, so that the dome handler can move the obj and scale it
                # when the dome is moved or scaled.
                if dome_handler:
                    make_parent(dome_handler, obj)

            move_modifier_index(cs, to_index=-1)

            from ..custom_property_groups.object.object_callback import update_subdivision
            objProp = get_objprop(dome_ground)
            update_subdivision(objProp, context)

        elif self.options in ['REMOVE', 'REMOVE_ALL']:

            if self.options == 'REMOVE_ALL':
                targets = [o for o in scn.objects if o.type == 'MESH' if get_objprop(o).is_shrinkwrap]

            for obj in targets:
                if obj.type != 'MESH':
                    continue

                objProp = get_objprop(obj)
                objProp.is_shrinkwrap = True
                for mod in dome_ground.modifiers:
                    if mod.type == 'SHRINKWRAP':
                        if mod.target == obj:
                            dome_ground.modifiers.remove(mod)

                set_object_bounds(obj, 'TEXTURED')
                objProp.is_shrinkwrap = False

                if objProp.object_id_name != 'HDRI_MAKER_GROUND':
                    un_parent(obj)

            # Rimuoviamo eventuali shrinkwrap rimasti senza target
            remove_empty_shrinkwrap_modifiers(dome_ground)

            # Remove the cc and ss modifiers if no shrinkwrap is present
            shrinkwrap = next((mod for mod in dome_ground.modifiers if mod.type == 'SHRINKWRAP'), None)

            if not shrinkwrap:
                if cs:
                    dome_ground.modifiers.remove(cs)
                if ss:
                    dome_ground.modifiers.remove(ss)

        return {'FINISHED'}
