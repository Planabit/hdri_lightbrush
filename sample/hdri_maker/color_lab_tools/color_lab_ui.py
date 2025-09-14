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
from ..exaproduct import Exa
from ..icons.interfaceicons import get_icon


def colorlab_panel(self, context):
    colabProp = context.scene.hdri_maker_colorlab_scene_prop
    layout = self.layout
    box = layout.box()
    col = box.column(align=True)
    col.label(text="Color System:")
    row = col.row(align=True)
    row.prop(colabProp, 'color_lab_system', text='System', expand=True)
    col.template_icon(icon_value=get_icon('color_chart'), scale=2)

    col.prop(colabProp, 'color_lab_category', text='Category')
    col.separator()
    col.prop(colabProp, 'color_lab_name', text='Name')
    col.separator()
    col.operator(Exa.ops_name+"searchhex", text='Search color name', icon='VIEWZOOM')

    col.separator()
    row = col.row(align=True)
    row.label(text='Color Sample: ' + colabProp.color_lab_show_name, icon='COLOR')

    col.separator()
    row = col.row(align=True)
    row.scale_y = 4
    # row.scale_x=0.1
    row.operator(Exa.ops_name+"colorlabscroll", text='', icon='TRIA_LEFT').options = 'PREVIUOS'
    # row.scale_x=1
    row.prop(colabProp, 'color_lab_example')
    # row.scale_x=0.1
    row.operator(Exa.ops_name+"colorlabscroll", text='', icon='TRIA_RIGHT').options = 'NEXT'

    # row = col.row()
    # row.alignment = 'CENTER'
    # row.prop(colabProp, 'color_lab_hex', text="HEX:")
    # row.label(text="Press OK to confirm")
