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
import time

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ...exaproduct import Exa
from ...utility.utility import get_addon_preferences


class HDRIMAKER_OT_remind_me_later(Operator):

    bl_idname = Exa.ops_name+"remind_me_later"
    bl_label = "Remind me later"
    bl_description = "Remind me later"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(default="UPDATE", items=[("UPDATE", "Update", "Update")])
    remind_time: EnumProperty(default="1", items=[("1", "1 day", "1 day"), ("3", "3 days", "3 days"), ("7", "7 days", "7 days"), ("15", "15 days", "15 days")])

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == "UPDATE":
            desc = "Choose when to be reminded to update the addon"
        return desc

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        text = "Choose when to be reminded to update the addon:"
        col.label(text=text)
        row = col.row()
        row.scale_y = 1.5
        row.prop(self, "remind_time", expand=True)
        col.separator()
        col.label(text="Press Ok to confirm, or Esc to cancel")

    def execute(self, context):
        remind_day = int(self.remind_time)
        remind_time = remind_day * 24 * 60 * 60

        preferences = get_addon_preferences()

        # Qui il remind_me_later_update è un int che deve essere settato sul time.time del giorno in cui si vuole essere ricordati
        # Quindi bisogna sommare il remind_time al time.time() attuale
        preferences.remind_me_later_update = int(time.time() + remind_time)

        bpy.ops.wm.save_userpref()

        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        refresh_interface()

        return {'FINISHED'}


