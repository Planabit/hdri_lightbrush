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


import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from ...exaproduct import Exa


class HDRIMAKER_OT_ResetLibPath(Operator):
    """Reset paths"""
    bl_idname = Exa.ops_name + "resetlibpath"
    bl_label = "Choose path"
    bl_options = {'INTERNAL'}

    options: StringProperty(options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        desc = properties.options.replace("_", " ").title()
        return desc

    def execute(self, context):
        from ...ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        from ...utility.utility import get_addon_preferences
        from ...utility.classes_utils import LibraryUtility
        from ...library_manager.get_library_utils import libraries_ready
        from ...installer_tools.check_tools import get_info_library_bar

        addon_prefs = get_addon_preferences()

        if self.options == 'RESET_DEFAULT_LIB_PATH':
            addon_prefs.addon_default_library = ""
        elif self.options == 'RESET_USER_LIB_PATH':
            addon_prefs.addon_user_library = ""

        get_info_library_bar()

        LibraryUtility.libraries_ready = libraries_ready()
        bpy.ops.wm.save_userpref()

        refresh_interface()

        return {'FINISHED'}
