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

from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
from bpy.types import PropertyGroup

from .material_callback import enum_fc_normals_items, update_fc_normals_items


class HdriMakerMaterialProperty(PropertyGroup):
    """Property group for material properties"""
    mat_id_name: StringProperty()
    dome_version: FloatProperty(default=0)
    self_tag: BoolProperty(default=False)
    enum_fc_normals: EnumProperty(items=enum_fc_normals_items, update=update_fc_normals_items,
                                  description="Choose the normal map to use into the shadow catcher material")

