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

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from ...exaproduct import Exa


# TODO: Operatore che trova da solo le librerie se esistono sul computer


class HDRIMAKER_OT_Findlibraries(Operator, ImportHelper):
    """Automatic Library Finder"""
    bl_idname = Exa.ops_name+"findlibraries"
    bl_label = "Find Libraries"
    bl_options = {'INTERNAL'}

    _timer = None
    directory: StringProperty(options={'HIDDEN'})

    def modal(self, context, event):
        return{'PASS_THROUGH'}

    def execute(self, context):

        root = [f for root, dirs, files in os.walk(self.directory) for f in files]

        return {'FINISHED'}
