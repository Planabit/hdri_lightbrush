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
from bpy.types import Operator

from ...exaproduct import Exa


class HDRIMAKER_OT_GetLibraryUpdates(Operator):
    bl_idname = Exa.ops_name + "get_library_updates"
    bl_label = "Get Library Updates"
    bl_description = "Get the latest updates for the library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ...web_tools.webservice import get_json_online
        json_data = get_json_online(urls=Exa.urls_exa_libraries_volumes,
                                    save_name="exa_library_volumes.json")
        if not json_data:
            self.report({'ERROR'}, "Failed to get the latest updates for the library, please try again later")
            return {'CANCELLED'}
        else:
            from ...utility.text_utils import draw_info
            text = "Check libraries updates done!"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'FINISHED'}
