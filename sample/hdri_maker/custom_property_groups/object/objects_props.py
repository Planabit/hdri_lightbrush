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
from bpy.props import EnumProperty, StringProperty, FloatProperty, BoolProperty, IntProperty
from bpy.types import PropertyGroup

from ...custom_property_groups.object.object_callback import update_alpha, \
    update_scale_dome_handler, update_expand_hooks, \
    update_hide_full, update_subdivision, update_un_lock_dome_handler


class HdriMakerObjectProperty(PropertyGroup):
    object_id_name: StringProperty()

    alpha_mode: EnumProperty(default='BLEND', update=update_alpha, items=(
        ('BLEND', "Blend", "Less impact on performance, but no shadow reflection on other objects"),
        ('HASHED', "Hashed",
         "Shadows reflected on the objects in the scene, but require a large number of samples for an optimal result")))

    # show_wireframe: BoolProperty(default=False, update=update_show_wireframe, description='Show wireframe mesh')
    # hide_wrap: BoolProperty(default=False, update=hide_Wrap_objects, description='Hide the wrapped object')

    # v3:

    dome_version: FloatProperty(default=0)
    dome_type: StringProperty()

    self_tag: BoolProperty(default=False)

    scale_dome_handler: FloatProperty(default=1, min=0.1, description="Scale Dome", update=update_scale_dome_handler)

    expand_hooks: FloatProperty(default=1, min=0.1,
                                description="Expand the hooks from the center (Similar to the Scale)",
                                update=update_expand_hooks)

    hide_full: BoolProperty(default=False, description="Hide Un-hide", update=update_hide_full)
    subdivision_step: IntProperty(default=0, min=0, max=4, description="Subdivision step")

    is_shrinkwrap: BoolProperty(default=False,
                                description="is_shrinkwrap is used for objects to which the shrinkwrap has been applied, "
                                            "so they can be easily recognized")

    ground_object_type: StringProperty(default="",
                                       description="ground_object_type is used to identify the type of object when apply the dome material")

    subdivision: IntProperty(default=1, min=1, max=6, description="Number of subdivision to perform",
                             update=update_subdivision)

    un_lock_dome_handler: BoolProperty(default=False, description="Un-lock the dome handler, to move it freely", update=update_un_lock_dome_handler)

    # locationX: FloatProperty(name="locationX",
    #                          default=0.0,
    #                          subtype='DISTANCE',
    #                          description="Set the location on local z axis",
    #                          get=get_locationX,
    #                          set=set_locationX)
    #
    # locationY: FloatProperty(name="locationY",
    #                          default=0.0,
    #                          subtype='DISTANCE',
    #                          description="Set the location on local z axis",
    #                          get=get_locationY,
    #                          set=set_locationY)
    #
    # locationZ: FloatProperty(name="locationZ",
    #                          default=0.0,
    #                          subtype='DISTANCE',
    #                          description="Set the location on local z axis",
    #                          get=get_locationZ,
    #                          set=set_locationZ)

