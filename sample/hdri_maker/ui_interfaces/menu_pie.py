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
from bpy.types import Menu

from ..ui_interfaces.draw_functions import draw_save_menu, preview_menu


class HDRIMAKER_MT_PIE_Main(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "HDRi Maker Main Menu"
    bl_idname = "HDRIMAKER_MT_PIE_Main"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        preview_menu(self, context, pie)
        draw_save_menu(self, context, pie)

