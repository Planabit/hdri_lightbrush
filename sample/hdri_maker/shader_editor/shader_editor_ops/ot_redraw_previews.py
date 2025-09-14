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
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ...exaproduct import Exa


class HDRIMAKER_OT_RedrawAllPreviews(Operator):

    bl_idname = Exa.ops_name+"redraw_all_previews"
    bl_label = "Redraw All Previews"
    bl_description = "Redraw all previews"
    bl_options = {'INTERNAL', 'UNDO'}

    confirm: EnumProperty(default='NO', items=(('YES', 'Yes', 'Confirm the action'), ('NO', 'No', 'Cancel the action')))

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        from ...exaconv import get_scnprop
        from ...library_manager.main_pcoll import enum_material_previews
        from ...library_manager.main_pcoll_attributes import set_winman_main_preview
        from ...library_manager.categories_enum import MatDict
        from ...library_manager.main_pcoll_attributes import get_winman_main_preview

        scn = context.scene
        scnProp = get_scnprop(scn)

        total_idx = -1

        for cat in MatDict.mats_categories["categories"]:
            if cat[0].lower() in ['empty...', 'tools']:
                continue

            scnProp.up_category = cat[0]
            # Iterate over the materials into the category:

            preview_image_list = [(N, idx) for (N, n, d, id_n, idx) in enum_material_previews(self, context)]
            for preview_name, idx in preview_image_list:
                set_winman_main_preview(preview_name)
                preview_mat_name = get_winman_main_preview()

                bpy.ops.hdrimaker.redrawpreview()

                total_idx += 1
                print(total_idx, "Redrawing preview", preview_mat_name)

        self.report({'INFO'}, "All previews redrawn")
        print("All previews redrawn")

        return {'FINISHED'}
