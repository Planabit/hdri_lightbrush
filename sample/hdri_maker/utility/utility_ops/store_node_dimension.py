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
import os

import bpy
from bpy.types import Operator

from ...exaproduct import Exa

class NodeDimensions:
    store_node_dimensions = {}


def calculate_node_group_dimensions(node):
    """In base al numero d'inputs e outputs del node group calcola le dimensioni, tiene conto se il nodo è espanso o meno e se ha le proprietà esposte"""

    show_options = False
    if hasattr(node, 'show_options') and node.show_options:
        show_options = True

    total_y_dimension = 0
    # Check if the node options are expanded
    if show_options and node.hide is False:
        total_y_dimension += 55
    else:
        total_y_dimension += 40

    if hasattr(node, 'show_preview') and node.show_preview:
        total_y_dimension += 172  # Approssimativo di default

    for n_input in node.inputs:
        # Check if input is hide or not, if is linked is not hide
        if not n_input.hide_value and not n_input.is_linked:
            if not node.hide:
                total_y_dimension += 15

    for output in node.outputs:
        # Check if output is hide or not, if is linked is not hide
        if not output.hide_value and not output.is_linked:
            if not node.hide:
                total_y_dimension += 15

    if node.hide:
        len_inputs = len([i for i in node.inputs if not i.hide_value and not i.is_linked])
        len_outputs = len([o for o in node.outputs if not o.hide_value and not o.is_linked])

        # Get the max between inputs and outputs
        max_len = max(len_inputs, len_outputs)

        if max_len < 5:
            total_y_dimension += 30

        else:
            # Se superiore a 4 il nodo diventa effettivamente piu alto di 30 ogni input in piu vale 10
            total_y_dimension += 30 + (max_len - 4) * 10

    # Per quanto riguarda la dimensione di larghezza, non sappiamo effettivamente calcolarla prima che esso venga disegnato

    node_dimensions = (node.width, total_y_dimension)

    return node_dimensions


def get_node_dimensions(node):
    """Questa funzione serve per leggere la dimensions del nodo, di default prova a vedere se la dimensione del
    nodo esiste già altrimenti la cerca nel file json che contiene le dimensioni dei nodi. Se non la trova allora, restiruisce una dimensione approssimativa.
    se il nodo è di tipo group, calcola le dimensioni in base al numero d'input e output e alle proprietà esposte."""

    # node.width è sempre aggiornato alla reale dimensione della larghezza del nodo a differenza di node.height che è sempre 100,
    # Questo sembra un comportamento strano, ma è cosi. Quindi per la larghezza del nodo possiamo usare node.width

    approx_dimensions = (node.width, 250)

    if node.dimensions[:] != (0.0, 0.0):
        # In questo caso il nodo ha già le dimensioni
        return node.dimensions[:]

    if node.type == 'GROUP':
        # Se il nodo è di tipo group allora calcoliamo le dimensioni in base al numero di input e output e alle proprietà esposte
        return calculate_node_group_dimensions(node)

    if not NodeDimensions.store_node_dimensions:
        # Proviamo a leggere il file json che contiene le dimensioni dei nodi:
        from ...library_manager.get_library_utils import risorse_lib
        json_file = os.path.join(risorse_lib(), 'json_utility', "node_dimensions.json")

        json_data = None
        if os.path.isfile(json_file):
            from ...utility.json_functions import get_json_data
            json_data = get_json_data(json_file, remove_if_invalid=False)
            NodeDimensions.store_node_dimensions = json_data
    else:
        json_data = NodeDimensions.store_node_dimensions

    if json_data:
        # In questo caso estremo non abbiamo il file json. Quindi niente da fare
        return approx_dimensions

    blender_version_string = bpy.app.version_string

    # Proviamo a ottenere la chiave della versione nel json:
    version = json_data.get(blender_version_string)
    if not version:
        # In questo caso potrebbe essere che Blender ha il terzo numero diverso per esempio 3.5.1 e il json ha 3.5.3
        # Quindi a vedere se nel json c'è una versione che corrisponde alla versione di Blender senza il terzo numero
        # Per esempio 3.5.1 diventa 3.5

        v_key = next((v for v in json_data.keys() if v.startswith(blender_version_string[:-2])), None)
        if v_key:
            version = json_data[v_key]
        else:
            # In questo caso non abbiamo trovato nessuna versione che corrisponde a quella di Blender quindi esaminiamo
            # tutte le versioni json e vediamo se il nodo è presente in una di quelle versioni, estremo arazzo
            for key, value in json_data.items():
                bl_idname = value.get('bl_idname')
                if bl_idname == node.bl_idname:
                    node_dimensions = value.get('dimensions')
                    if node_dimensions:
                        return node_dimensions
                    else:
                        return approx_dimensions

    node_dimensions = version.get(node.bl_idname)
    if node_dimensions:
        return node_dimensions
    else:
        return approx_dimensions


def generate_all_compositing_node():
    previous_area = next((area for area in bpy.context.screen.areas if area != bpy.context.area), bpy.context.area)
    previous_area_type = previous_area.type
    previous_area_ui_type = previous_area.ui_type

    previous_area.type = 'NODE_EDITOR'
    previous_area.ui_type = 'CompositorNodeTree'

    scn = bpy.context.scene
    scn.use_nodes = True
    node_tree = scn.node_tree
    nodes = node_tree.nodes


    # Remove all nodes
    for node in nodes:
        nodes.remove(node)

    bl_nodes = [n for n in bpy.types.CompositorNode.__subclasses__()]

    new_nodes = []
    for node in bl_nodes:
        new_node = nodes.new(node.bl_rna.identifier)
        new_nodes.append(new_node)

    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    # Wait 3 seconds (to be sure that the node editor is redrawn):
    import time
    time.sleep(5)

    nodes_dimensions = {}
    for n in new_nodes:
        nodes_dimensions[n.bl_rna.identifier] = {'dimensions': n.dimensions[:]}

    # Restore previous area:
    previous_area.type = previous_area_type
    previous_area.ui_type = previous_area_ui_type

    return nodes_dimensions


def generate_all_geometry_nodes():

    # TODO: per ora i nodi Geometrici sono enumerati in bpy.types.GeometryNode..... Ogni nodo è un types separato,
    #  troppo presto per fare una funzione che li genera tutti

    previous_area = next((area for area in bpy.context.screen.areas if area != bpy.context.area), bpy.context.area)
    previous_area_type = previous_area.type
    previous_area_ui_type = previous_area.ui_type

    previous_area.type = 'NODE_EDITOR'
    previous_area.ui_type = 'GeometryNodeTree'

    scn = bpy.context.scene
    node_tree = scn.node_tree
    nodes = node_tree.nodes

    name = "Make GEONODES Dimensions Temp"
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

    data = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, data)
    scn.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.modifiers.new("Geometry Nodes", 'NODES')

    # Remove all nodes
    for node in nodes:
        nodes.remove(node)

    bl_nodes = [n for n in bpy.types.GeometryNode.__subclasses__()]

    new_nodes = []
    for node in bl_nodes:
        print("Creating node: ", node.bl_rna.identifier)
        new_node = nodes.new(node.bl_rna.identifier)
        new_nodes.append(new_node)

    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    # Wait 3 seconds (to be sure that the node editor is redrawn):
    import time
    time.sleep(5)

    nodes_dimensions = {}
    for n in new_nodes:

        nodes_dimensions[n.bl_rna.identifier] = {'dimensions': n.dimensions[:]}

    bpy.data.objects.remove(obj, do_unlink=True)

    # Restore previous area:
    previous_area.type = previous_area_type
    previous_area.ui_type = previous_area_ui_type


    return nodes_dimensions


def generate_shader_node_dimensions():

    name = "Make SHADERNODES Dimensions Temp"
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

    data = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    mat = bpy.data.materials.get(name)
    if mat:
        bpy.data.materials.remove(mat, do_unlink=True)

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node_tree = mat.node_tree
    nodes = node_tree.nodes

    # Remove all nodes
    for node in nodes:
        nodes.remove(node)

    # Remove all obj materials
    for slot in obj.material_slots:
        obj.material_slots.remove(slot)

    obj.data.materials.append(mat)
    obj.active_material = mat

    # Select the material slot:


    previous_area = next((area for area in bpy.context.screen.areas if area != bpy.context.area), bpy.context.area)
    previous_area_type = previous_area.type
    previous_area_ui_type = previous_area.ui_type

    previous_area.type = 'NODE_EDITOR'
    previous_area.ui_type = 'ShaderNodeTree'

    shader_nodes = [n for n in bpy.types.ShaderNode.__subclasses__()]


    nodes_dimensions = {}
    for node in shader_nodes:
        new_node = nodes.new(node.bl_rna.identifier)

    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    # Wait 3 seconds (to be sure that the node editor is redrawn):
    import time
    time.sleep(5)

    for n in nodes:
        nodes_dimensions[n.bl_rna.identifier] = {'dimensions': n.dimensions[:]}


    # Restore previous area:
    previous_area.type = previous_area_type
    previous_area.ui_type = previous_area_ui_type

    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.materials.remove(mat, do_unlink=True)

    return nodes_dimensions


class HDRIMAKER_OT_NodePropsDimensions(Operator):
    """Store Shader Node Properties"""
    bl_idname = Exa.ops_name + "store_node_props_dim"
    bl_label = "Store Shader Node Properties"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        shader_nodes_dimensions = generate_shader_node_dimensions()
        compo_nodes_dimensions = generate_all_compositing_node()
        # geo_nodes_dimensions = generate_all_geometry_nodes()  # Per ora non serve ed è rischioso inutilmente.
        # Se serve faremo una funzione che genera tutti i nodi geometrici

        from ...library_manager.get_library_utils import risorse_lib

        json_file = os.path.join(risorse_lib(), 'json_utility', "node_dimensions.json")

        json_data = None
        if os.path.isfile(json_file):
            from ...utility.json_functions import get_json_data
            json_data = get_json_data(json_file, remove_if_invalid=False)

        if not json_data:
            json_data = {}

        blender_version = bpy.app.version_string.split(" ")[0]
        version = json_data.get(blender_version)
        if not version:
            json_data[blender_version] = {}

        # merge the dictionary with the compositor nodes dimensions
        json_data[blender_version].update(shader_nodes_dimensions)
        json_data[blender_version].update(compo_nodes_dimensions)

        # Save the json file:
        from ...utility.json_functions import save_json
        save_json(json_file, json_data)

        return {'FINISHED'}
