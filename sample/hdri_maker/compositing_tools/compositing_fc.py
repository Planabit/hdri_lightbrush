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


def redo_last_compo_node(self):
    for s in bpy.data.scenes:
        if s.hdri_prop_scn.scene_id_name == 'USER_SCENE':

            for n in s.node_tree.nodes:
                if n.hdri_prop_nodes.node_to_delete == True:
                    s.node_tree.nodes.remove(n)

            if mem_nod_out.nodo_output == None:
                return

            link = s.node_tree.links
            if mem_nod_out.nodo_zero_out is not None:
                link.new(mem_nod_out.nodo_zero_out, mem_nod_out.nodo_output.inputs[0])
            if mem_nod_out.nodo_uno_out is not None:
                link.new(mem_nod_out.nodo_uno_out, mem_nod_out.nodo_output.inputs[1])
            if mem_nod_out.nodo_due_out is not None:
                link.new(mem_nod_out.nodo_due_out, mem_nod_out.nodo_output.inputs[2])

def mem_nod_out(self, context):
    scn = context.scene
    scn.use_nodes = True

    mem_nod_out.nodo_output = None

    mem_nod_out.nodo_zero_out = None
    mem_nod_out.nodo_uno_out = None
    mem_nod_out.nodo_due_out = None

    for n in scn.node_tree.nodes:
        if n.type == 'COMPOSITE':
            for inp in n.inputs:

                if inp.name == 'Image':
                    if inp.is_linked:
                        mem_nod_out.nodo_output = n

                        mem_nod_out.nodo_zero_out = inp.links[0].from_socket
                        scn.node_tree.links.remove(n.inputs[0].links[0])


                elif inp.name == 'Alpha':
                    if inp.is_linked:
                        mem_nod_out.nodo_uno_out = inp.links[0].from_socket
                        scn.node_tree.links.remove(n.inputs[1].links[0])

                elif inp.name == 'Z':
                    if inp.is_linked:
                        mem_nod_out.nodo_due_out = inp.links[0].from_socket
                        scn.node_tree.links.remove(n.inputs[2].links[0])
