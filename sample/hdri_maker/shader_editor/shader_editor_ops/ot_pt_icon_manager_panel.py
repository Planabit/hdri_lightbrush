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

from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from ...exaconv import get_sckprop
from ...exaproduct import Exa
from ...utility.enum_blender_native import get_blender_icons
from ...utility.utility import wima, safety_eval


def reset_icon_search(self, context):
    if self.clear_search:
        self.icon_search = ""
        self.clear_search = False


class HDRIMAKER_OT_icon_manager_panel(Operator):
    bl_idname = Exa.ops_name + "icon_manager_panel"
    bl_label = "Icon Manager Panel"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(default='ICON_TRUE',
                          items=(('ICON_TRUE', 'Icon True', 'Icon True'),
                                 ('ICON_FALSE', 'Icon False', 'Icon False'),
                                 ('ADD_ICON_TO_ENUM_SOCKET', 'Add Icon to Enum Socket', 'Add Icon to Enum Socket'))
                          )
    icon_search: StringProperty()
    clear_search: BoolProperty(default=False, update=reset_icon_search)
    socket_enum_idx: IntProperty()
    repr_socket: StringProperty()

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ICON_TRUE':
            desc = "Choose the icon for when the button is True"
        elif properties.options == 'ICON_FALSE':
            desc = "Choose the icon for when the button is False"
        elif properties.options == 'ADD_ICON_TO_ENUM_SOCKET':
            desc = "Choose the icon for this Enum Property"
        return desc

    def invoke(self, context, event):
        return wima().invoke_props_dialog(self, width=500)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        ob = context.object
        socket = safety_eval(self.repr_socket)
        sckProp = get_sckprop(socket)

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, 'icon_search', text="Search", icon='VIEWZOOM')
        if self.icon_search:
            row.prop(self, 'clear_search', text="", icon='X')

        col.separator(factor=0.5)

        row = col.row(align=True)
        row.alignment = 'CENTER'
        for idx, icon in enumerate(get_blender_icons()):
            if self.icon_search.lower() in icon.lower():
                if idx % 28 == 0:
                    row = col.row(align=True)
                    row.alignment = 'CENTER'

                depressStat = False
                if self.options in ['ICON_TRUE', 'ICON_FALSE']:
                    if self.options == 'ICON_TRUE':
                        depressStat = True if sckProp.api_icon_true == icon else False
                    if self.options == 'ICON_FALSE':
                        depressStat = True if sckProp.api_icon_false == icon else False

                elif self.options == 'ADD_ICON_TO_ENUM_SOCKET':
                    depressStat = True if sckProp.api_collection_idx[self.socket_enum_idx].icon == icon else False

                icon_button = row.operator(Exa.ops_name + "icon_button", text="", icon=icon, depress=depressStat)
                icon_button.options = self.options
                icon_button.repr_socket = repr(socket)
                icon_button.icon = icon
                icon_button.socket_enum_idx = self.socket_enum_idx