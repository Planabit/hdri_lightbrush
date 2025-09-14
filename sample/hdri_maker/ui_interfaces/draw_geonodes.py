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


def draw_geonode_inputs(layout, gm):
    """Try to draw the geonode inputs, not easy in this version of Blender"""
    if gm.type != 'NODES':
        return
    if gm.node_group is None:
        return

    # Get the node group
    node_group = gm.node_group

    col = layout.column(align=True)


    for ng_input in gm.node_group.inputs:
        if ng_input.type in ['VALUE', 'INT']:
            row = col.row(align=True)
            identifier = '["' + str(ng_input.identifier) + '"]'
            row.prop(gm, identifier, text=ng_input.name)
            # row.prop(input.identifier, 'default_value', text='X')
            # row.prop(input, 'name', text='X')
            # row.prop(input, 'type', text=str(input.type))

