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
from bpy.props import EnumProperty
from bpy.types import Operator

from ..categories_enum import enum_up_category
from ...exaconv import get_scnprop
from ...exaproduct import Exa
from ...utility.utility import wima


class HDRIMAKER_OT_SearchCategories(Operator):
    """Search Categories"""
    bl_idname = Exa.ops_name+"searchcategories"
    bl_label = "Search:"
    bl_property = "search_cat"
    bl_options = {'INTERNAL'}

    # Qui si fa riferimento alla funzione per la popolazione della lista delle categorie
    search_cat: EnumProperty(name="search_cat", description="",
                             items=enum_up_category)

    def execute(self, context):

        scn = context.scene
        scnProp = get_scnprop(scn)
        scnProp.up_category = self.search_cat
        return {'FINISHED'}

    def invoke(self, context, event):
        wima().invoke_search_popup(self)
        return {'FINISHED'}
