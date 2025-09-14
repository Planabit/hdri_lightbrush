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
from bpy.types import Operator

from ...exaproduct import Exa


class HDRIMAKER_OT_ConfirmNonOfficialVersion(Operator):
    """Close"""
    bl_idname = Exa.ops_name+"confirm_non_official_version"
    bl_label = "Close"
    bl_options = {'INTERNAL'}

    def execute(self, context):

        from ...utility.classes_utils import LibraryUtility
        LibraryUtility.is_official_version = True

        return {'FINISHED'}

