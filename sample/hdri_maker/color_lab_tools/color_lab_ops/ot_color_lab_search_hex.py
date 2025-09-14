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
import bpy
from bpy.types import Operator

from ..colorlab_func import searchCallback
from ...exaproduct import Exa
from ...utility.utility import wima


class HDRIMAKER_OT_SearchHex(Operator):
    """Search Color Name"""
    bl_idname = Exa.ops_name+"searchhex"
    bl_label = "Search Hex"
    bl_property = "search_hex"
    bl_options = {'INTERNAL', 'UNDO'}

    search_hex: bpy.props.EnumProperty(name="search_hex", description="", items=searchCallback)

    def execute(self, context):

        colabProp = context.scene.hdri_maker_colorlab_scene_prop

        # split separa tramite i simboli aggiunti nel callback per rendere molto piu veloce la ricerca
        system = self.search_hex.split('###')[0]
        category = self.search_hex.split('###')[1]
        name = self.search_hex.split('###')[2]

        colabProp.color_lab_system = system
        colabProp.color_lab_category = category
        colabProp.color_lab_name = name

        return {'FINISHED'}

    def invoke(self, context, event):
        wima().invoke_search_popup(self)
        return {'FINISHED'}
