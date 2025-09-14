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
from bpy.props import BoolProperty, StringProperty, EnumProperty
from bpy.types import PropertyGroup

from ...exaconv import get_sckprop
from ...ops_and_fcs.socket_utility import enum_socket_type
from ...utility.text_utils import draw_info
from ...utility.utility_4 import get_ng_inputs


def update_ng_show_tips(self, context):
    node_group = self.id_data

    if self.ng_show_tips is False:
        return

    tooltips = 0
    ng_inputs = get_ng_inputs(node_group)
    for idx, i in enumerate(ng_inputs):
        sckProp = get_sckprop(i)
        if sckProp.api_bool_description:
            tooltips += 1

    if tooltips == 0:
        text = "No tooltips/descriptions are available for this node group inputs"
        draw_info(text, "Info", 'INFO')
        self.ng_show_tips = False




class HdriMakerNodeTreeProperties(PropertyGroup):
    self_tag: BoolProperty(default=False)

    group_id_name: StringProperty()
    mixer_type: StringProperty(description="Type of Mixer Node Group in use for mix background")

    NodeSocketType: EnumProperty(name="Socket Type", items=enum_socket_type)

    ng_description: StringProperty(
        description="Enter a description if you want, a button will be shown to show it in a popup. Useful to help the user. Enter a minimum of 10 characters to show the description")
    ng_show_tips: BoolProperty(default=False, description="Show tooltip next to values if tips exist",
                               update=update_ng_show_tips)

    environment_type: StringProperty()  # To recognize if Node group type (ONLY FOR HDRi Maker) 'IMAGE_ENV_V1' is for image group
    show_lock_prop: BoolProperty(default=False, name="Show Lock Properties",
                                 description="Show Lock Property, useful for lock the properties if you need to reset the node at the Default Value, but you don't want to lose some properties")


    ng_util = {'last_active_socket': 0, 'len_inputs': 0, 'len_outputs': 0}
