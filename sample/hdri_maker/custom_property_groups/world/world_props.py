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
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty
from bpy.types import PropertyGroup

from ...background_tools.background_fc import get_nodes_dict
from ...utility.utility import has_nodetree

light_path = []


def enum_light_path(self, context):
    scn = context.scene
    world = scn.world

    light_path.clear()

    if not world or not has_nodetree(world):
        light_path.append(('NONE', "None", ""))
        return light_path

    nodes_dict = get_nodes_dict(world.node_tree)
    mixer = nodes_dict.get('MIXER')
    if not mixer or not has_nodetree(mixer):
        light_path.append(('NONE', "None", ""))
        return light_path

    node_light_path = next((node for node in mixer.node_tree.nodes if node.type == 'LIGHT_PATH'), None)
    if not node_light_path:
        light_path.append(('NONE', "None", ""))
        return light_path

    light_path.append(('Is Camera Ray', "Is Camera Ray", "Defautl value"))
    light_path.append(('Is Reflection Ray', "Is Reflection Ray", "Show only reflection rays"))

    return light_path


def update_light_path(self, context):
    scn = context.scene
    world = scn.world

    if self.light_path == 'NONE':
        return

    if not world or not has_nodetree(world):
        return

    nodes_dict = get_nodes_dict(world.node_tree)
    mixer = nodes_dict.get('MIXER')
    if not mixer or not has_nodetree(mixer):
        return

    node_light_path = next((n for n in mixer.node_tree.nodes if n.type == 'LIGHT_PATH'), None)
    if not node_light_path:
        return

    # Get the linked output
    link = None
    for output in node_light_path.outputs:
        if output.is_linked:
            link = output.links[0]
            break

    # Connect from self.light_path to the linked output
    if link:
        to_socket = link.to_socket
        try:
            mixer.node_tree.links.new(node_light_path.outputs[self.light_path], to_socket)
        except Exception as e:
            text = "From function update_light_path: " + str(e)
            from ...utility.text_utils import draw_info
            draw_info(text, "Info", 'INFO')
            pass


class HdriMakerWorldProperty(PropertyGroup):
    world_id_name: StringProperty()
    world_id_base_name: StringProperty()
    world_id_savename: StringProperty()
    world_user: BoolProperty(default=False)
    world_hdri_maker: BoolProperty(default=False)
    world_nome_preview: StringProperty()

    self_tag: BoolProperty(default=False)
    world_hdri_maker_version: IntProperty(default=-1)

    light_path: EnumProperty(name="Light Path", items=enum_light_path, update=update_light_path)
