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
from bpy.props import StringProperty, BoolProperty


class HdriMakerNodeProperty(bpy.types.PropertyGroup):
    node_id_name: StringProperty()
    node_to_delete: BoolProperty(default=False)

    self_tag: BoolProperty(default=False)

    node_tag: StringProperty(
        description="Tag nodes of type TEX_IMAGE to make the workflow on this addon easier. The whole interface,"
                    " especially the functions, will recognize these tags, and will be fundamental for many operations")

    hide: BoolProperty(default=False, description="Open Or Close from UI panel")

    node_attributes: StringProperty()





