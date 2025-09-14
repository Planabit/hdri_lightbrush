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
import os

import bpy
from bpy.types import Operator

from ..exaproduct import Exa
from ..library_manager.get_library_utils import current_lib
from ..library_manager.tools import create_json_material_library_register
from ..utility.utility_dependencies import open_folder


class HDRIMAKER_OT_PythonOps(Operator):
    bl_idname = Exa.ops_name+"pythonops"
    bl_label = "Ops"
    bl_options = {'INTERNAL'}

    options: bpy.props.StringProperty()
    open_path: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        return properties.options.title().replace("_", " ")

    def execute(self, context):

        options = self.options

        if options == 'CREATE_LIBRARY_REGISTER':
            if current_lib():
                register_filepath = os.path.join(current_lib(), "._data")
                create_json_material_library_register(current_lib(), register_filepath)

        elif options == 'OPEN_FOLDER':
            open_folder(self.open_path)

        return {'FINISHED'}
