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
from bpy.types import Panel

from ..exaproduct import Exa
from ..shader_editor.functions import check_geometry_area_ok


class HDRIMAKER_PT_GeometryNodeTools(Panel):
    bl_label = "HDRi Maker"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Hdri Maker"

    @classmethod
    def poll(self, context):

        return check_geometry_area_ok(context)

    def draw(self, context):
        # Pay attention, node_tree in this case is a bpy.data.node_groups Type 'GEOMETRY'
        node_tree = context.space_data.node_tree

        layout = self.layout
        layout.label(text="This is a test")

        col = layout.column(align=True)
        row = col.row(align=True)
        sgn = row.operator(Exa.ops_name + "save_geometry_nodes", text="Save Geometry Nodes", icon="FILE_TICK")
        sgn.geometry_node = node_tree.name

