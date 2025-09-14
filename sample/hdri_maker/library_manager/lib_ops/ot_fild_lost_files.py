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
from bpy.props import StringProperty
from bpy.types import Operator

from ...exaproduct import Exa


class HDRIMAKER_OT_FindLostFiles(Operator):
    bl_idname = Exa.ops_name+"findlostfiles"
    bl_label = "Search Missing Files"


    directory: StringProperty(subtype='DIR_PATH')
    # files: CollectionProperty(type=bpy.types.PropertyGroup)

    filter_glob: StringProperty(
        default="*.png;*.jpg;*.bm;*.sgi;*.rgb;*.bw;*.jpeg;*.jp2;*.j2c;*.tga;*.cin;*.dpx;*.exr;*.hdr;*.tif;*.tiff;*.mov;*.mpg;*.mpeg;*.dvd;*.vob;*.mp4;*.avi;*.dv;*.ogg;*.ogv;*.mkv;*.flv",
        options={'HIDDEN'},
    )

    @classmethod
    def description(cls, context, properties):
        return "Find lost environment images"

    def invoke(self, context, event):

        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scn = context.scene
        world = scn.world

        from ...utility.utility import has_nodetree
        from ...utility.utility import retrieve_nodes

        images = []
        if world and has_nodetree(world):
            node_list = retrieve_nodes(world.node_tree)
            w_images = [node.image for node in node_list if node.type in ['TEX_ENVIRONMENT', 'TEX_IMAGE'] and node.image]
            images.extend(w_images)

        # Get the images from dome
        from ...dome_tools.dome_fc import get_dome_objects
        dome_dict = get_dome_objects()
        dome_material = dome_dict.get('DOME_MATERIAL')
        if dome_material and has_nodetree(dome_material):
            node_list = retrieve_nodes(dome_material.node_tree)
            d_images = [node.image for node in node_list if node.type in ['TEX_ENVIRONMENT', 'TEX_IMAGE'] and node.image]
            images.extend(d_images)

        # Remove duplicates from the list
        images = list(set(images))
        from ...ops_and_fcs.material_utility import find_lost_image_path
        text = find_lost_image_path(images, self.directory)
        if type(text) == str:
            from ...utility.text_utils import draw_info
            draw_info(text, title="Info", icon='INFO')
            self.report({'INFO'}, text)
        return {'FINISHED'}

