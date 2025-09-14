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

from ..library_manager.get_library_utils import libraries_ready
from ..utility.utility import get_addon_preferences


def check_shader_area_ok(context):
    addon_prefs = get_addon_preferences()
    ui_type = context.area.ui_type
    show_creator_utility = addon_prefs.show_creator_utility
    shader_type = context.space_data.shader_type
    node_tree = context.space_data.edit_tree

    if node_tree and ui_type == "ShaderNodeTree" and libraries_ready() and show_creator_utility and shader_type in ['WORLD', 'OBJECT']:
        return True

def check_geometry_area_ok(context):
    ui_type = context.area.ui_type
    node_tree = context.space_data.node_tree

    if node_tree and ui_type == "GeometryNodeTree":
        return True
