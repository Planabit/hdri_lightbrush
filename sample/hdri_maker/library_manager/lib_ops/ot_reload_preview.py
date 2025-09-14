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

from ..textures_pcoll import reload_textures_prev_icons
from ...exaproduct import Exa
from ...library_manager.main_pcoll import reload_main_previews_collection


class HDRIMAKER_OT_ReloadPreviewIcons(Operator):
    bl_idname = Exa.ops_name+"reloadpreviewicons"
    bl_label = "Reload Previews"
    bl_options = {'INTERNAL'}

    @classmethod
    def description(cls, context, properties):
        desc = "Force reload of preview icons, Useful in case the preview icons have not been loaded correctly"
        return desc

    def execute(self, context):
        reload_main_previews_collection()
        reload_textures_prev_icons()
        return{'FINISHED'}
