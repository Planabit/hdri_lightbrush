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

from bpy.props import EnumProperty
from bpy.types import Operator

from ..get_library_utils import current_lib
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...utility.json_functions import get_json_data
from ...utility.utility import wima


def search_all_tags(self, context):

    if not os.path.isdir(current_lib()):
        return [('No library', 'No library', "")]

    all_tags = []
    for cat in os.listdir(current_lib()):
        cat_folder = os.path.join(current_lib(), cat)
        if os.path.isdir(cat_folder):
            for mat in os.listdir(cat_folder):
                json_dir = os.path.join(cat_folder, mat, "data", "tags.json")
                if os.path.isfile(json_dir):
                    data = get_json_data(json_dir)
                    for tag in data['tags']:
                        if tag not in all_tags:
                            all_tags.append(tag)

    all_tags = sorted(all_tags)

    return [(tag, tag, "") for tag in all_tags]


class HDRIMAKER_OT_SearchTags(Operator):
    """Searches for all tags used throughout the library"""
    bl_idname = Exa.ops_name+"searchtags"
    bl_label = "Search Tags:"
    bl_property = "search_all_tags"
    bl_options = {'INTERNAL'}

    search_all_tags: EnumProperty(name="search_all_tags", description="", items=search_all_tags)

    def execute(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        scnProp.temp_tag = self.search_all_tags

        return {'FINISHED'}

    def invoke(self, context, event):
        wima().invoke_search_popup(self)
        return {'FINISHED'}
