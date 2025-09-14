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

import bpy
from bpy.types import Operator

from ...exaproduct import Exa
from ...library_manager.textures_pcoll_attributes import get_winman_texture_preview
from ...ops_and_fcs.create_tools import create_node_utility
from ...utility.text_utils import draw_info
from ...utility.utility_dependencies import set_colorspace_name


class HDRIMAKER_OT_ImportTexture(Operator):
    bl_idname = Exa.ops_name + "importtexture"
    bl_label = "Import Texture"
    bl_options = {'INTERNAL', 'UNDO'}

    options: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        options = properties.options
        desc = "Import Image into a node"
        return desc

    def execute(self, context):

        node_tree = context.space_data.edit_tree

        nodes = node_tree.nodes

        for n in node_tree.nodes:
            n.select = False

        texture_path = get_winman_texture_preview()
        if not os.path.isfile(texture_path):
            return {'FINISHED'}

        image = bpy.data.images.load(texture_path)
        if self.options == "ADD_TEXTURE":
            node = create_node_utility(nodes, nodeType="ShaderNodeTexEnvironment")
        elif self.options == "REPLACE_TEXTURE":
            node = context.space_data.edit_tree.nodes.active
            if not node:
                text = "No active node selected"
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}
            if node.bl_idname != "ShaderNodeTexImage":
                text = "The selected node is not of type 'Image node'"
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}

        if self.options == 'REPLACE_TEXTURE':
            if node.image:
                try:
                    colorspace = node.image.colorspace_settings.name
                except:
                    pass

        node.image = image
        node.select = True
        nodes.active = node

        if self.options == 'REPLACE_TEXTURE':
            if colorspace:
                set_colorspace_name(node.image, colorspace)
                # try: node.image.colorspace_settings.name = colorspace
                # except: pass

        if self.options == "ADD_TEXTURE":
            return bpy.ops.transform.translate('INVOKE_DEFAULT')
        else:
            return {'FINISHED'}
