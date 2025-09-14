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
from ..background_tools.background_fc import get_nodes_dict
from ..exaproduct import Exa
from ..icons.interfaceicons import get_icon
from ..utility.utility import has_nodetree


def asset_browser_ui(self, context):
    # TODO: Forse inutile se troviamo un handler che intercetti il drag and drop
    return

    world = context.scene.world

    layout = self.layout
    row = layout.row(align=True)
    add = row.operator(Exa.ops_name+"addbackground", text="Add", icon_value=get_icon("Aggiungi"))
    add.is_from_asset_browser = True
    add.environment = 'COMPLETE'
    add.make_relative_path = False
    add.hide_info_popup = False


    if world and has_nodetree(world):
        node_tree = world.node_tree
        nodes_dict = get_nodes_dict(node_tree)
        mixer = nodes_dict.get('MIXER')
        complete = nodes_dict.get('COMPLETE')
        diffuse = nodes_dict.get('DIFFUSE')
        light = nodes_dict.get('LIGHT')
        vectors = nodes_dict.get('VECTORS')

        if complete or diffuse or light:
            s_row = row.row(align=True)
            s_row.scale_x = 0.5
            diffuse = s_row.operator(Exa.ops_name + "addremovegroups", text="Diffuse", icon='ADD')
            diffuse.is_from_asset_browser = True

            light = s_row.operator(Exa.ops_name + "addremovegroups", text="Light", icon='ADD')
            light.is_from_asset_browser = True
