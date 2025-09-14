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
import time

from ..exaproduct import Exa
from ..utility.text_utils import write_with_icons

# def draw_first_message(layout, context):
#     col = layout.column(align=True)
#     data = LibraryUtility.first_message
#
#     changes = data.get("changes")
#     if not changes:
#         return
#     write_with_icons(col, "HORIZONTAL", 'Please read', False, 1.2)
#     col.separator()
#     col.label(text="Important Change:")
#     col.separator()
#
#     for title, description in changes.items():
#         changesCol = col.column(align=True)
#         changesCol.label(text=title, icon='DOT')
#         box = col.box()
#         colBox = box.column(align=True)
#         wrap_text(colBox, description, False, (context.region.width / 6.5), False, False, True)
#
#     col.separator()
#     row = col.row()
#     row.scale_y = 2
#     ops = row.operator(Exa.ops_name+"osremove", text="OK! I got it", icon="CANCEL")
#     ops.options = 'REMOVE_FIRST_MESSAGE'


from ..utility.classes_utils import LibraryUtility


def update_icons_message(layout, addon_prefs, open_preferences=False):

    if not addon_prefs.need_update:
        return

    if time.time() < addon_prefs.remind_me_later_update:
        return

    col = layout.column(align=True)
    if addon_prefs.update_urgency:
        write_with_icons(col, "HORIZONTAL", 'Very Important', False, 1.2)

    # write_with_icons(col, "HORIZONTAL", 'Update required', False, 1.2)
    col.separator()
    row = col.row(align=True)
    row.alignment = 'CENTER'

    row.label(text="", icon="CHECKMARK")
    row.label(text="( Update is now available )")
    row.label(text="", icon="CHECKMARK")

    col.separator()
    row = col.row()
    row.scale_y = 1.5
    row.operator(Exa.ops_name + "remind_me_later", text="Remind me later",
                 icon="TIME").options = "UPDATE"

    col.separator()

    if open_preferences:
        row = col.row()
        # row.operator(Exa.ops_name + "update_menu", text="Check the changes",
        #              icon="QUESTION").options = "CHECK_UPDATE"
        row.operator(Exa.ops_name + "open_preferences", text="Go to update menu",
                     icon='PREFERENCES').options = 'UPDATES'

        col.separator()

