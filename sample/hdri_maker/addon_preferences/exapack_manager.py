#   #
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version
#    of the License, or (at your option) any later version.
#   #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#   #
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software Foundation,
#    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#   #
#   Copyright 2024(C) Andrea Donati
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
from bpy.types import PropertyGroup


class HdriMakerExaPackToInstall(PropertyGroup):

    idx: IntProperty()
    name: StringProperty(default="")
    size: StringProperty(default="")
    filepath: StringProperty(subtype='DIR_PATH')
    icon: StringProperty(default='NONE')
    float_bar_percentage: FloatProperty(default=0.0, min=0, max=100, subtype='PERCENTAGE')
    is_good_zip: BoolProperty(default=False)
    is_wrong_product: BoolProperty(default=False)
    product: StringProperty(default="")
    volume_name: StringProperty(default="")
    files_dict = {}

    # This 2, is made for using during the installation process
    unpacked_files: IntProperty(default=0)
    packed_files: IntProperty(default=0)










