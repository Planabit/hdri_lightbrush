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
from bpy.props import EnumProperty, FloatVectorProperty, StringProperty

from .colorlab_func import enum_color_lab_system, update_color_lab_system, enum_color_lab_category, \
    update_color_lab_category, update_color_lab_name, enum_color_lab_name, update_color_lab_example


class HdriMakerColorLabSceneProperties(bpy.types.PropertyGroup):
    color_lab_system: EnumProperty(items=enum_color_lab_system, description="Choose the coloring system",
                                   update=update_color_lab_system)
    color_lab_category: EnumProperty(items=enum_color_lab_category, description='Choose the type of manufacturer',
                                     update=update_color_lab_category)
    color_lab_name: EnumProperty(items=enum_color_lab_name, description='Choose the color by name', default=None,
                                 update=update_color_lab_name)
    color_lab_example: FloatVectorProperty(name="", subtype='COLOR', default=(1, 1, 1, 1), min=0.0, max=1.0, size=4,
                                           description="Diffuse", update=update_color_lab_example)
    color_lab_show_name: StringProperty()

    color_lab_hex: StringProperty()
