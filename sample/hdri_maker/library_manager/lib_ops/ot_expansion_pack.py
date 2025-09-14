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
from bpy.types import Operator

from ..libraries_enum import StoreLibraries
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...utility.utility import get_addon_preferences


class HDRIMAKER_OT_ExpansionPack(Operator):
    """Expansion Manager"""

    bl_idname = Exa.ops_name+"expansionpack"
    bl_label = "Expansion Manager"
    bl_options = {'INTERNAL'}

    options: bpy.props.StringProperty()
    idx: bpy.props.IntProperty()

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ADD':
            desc = "Add a path to another library (Only if you have third party libraries)"
        elif properties.options == 'REMOVE':
            desc = "Remove the path to this library"
        return desc

    def execute(self, context):

        addon_prefs = get_addon_preferences()
        scnProp = get_scnprop(context.scene)

        if self.options == 'ADD':
            for idx in range(1, 1000):
                prefix = "0" + str(idx) + "-"
                if not [exp for exp in addon_prefs.expansion_filepaths if exp.name and exp.name.startswith(prefix)]:
                    break

            item = addon_prefs.expansion_filepaths.add()
            item.name = prefix + item.name
            item.display = True

        if self.options == 'REMOVE':
            addon_prefs.expansion_filepaths.remove(self.idx)
            try: scnProp.libraries_selector = StoreLibraries.libraries[0][0]
            except: pass

        StoreLibraries.libraries = []

        bpy.ops.wm.save_userpref()

        return {'FINISHED'}
