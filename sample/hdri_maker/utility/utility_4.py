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


def get_ng_inputs(node_tree, index=None, name=None):
    if bpy.app.version < (4, 0, 0):
        if index is not None:
            if index is not None:
                try:
                    socket_index = node_tree.inputs[index]
                    return socket_index
                except IndexError:
                    return None

        if name is not None:
            if name in node_tree.inputs:
                return node_tree.inputs[name]
            else:
                return None

        return node_tree.inputs

    socket_inputs = []
    for item in node_tree.interface.items_tree:
        if item.item_type != 'SOCKET':
            continue
        if item.in_out == 'INPUT':
            socket_inputs.append(item)

    if index is not None:
        try:
            socket_index = socket_inputs[index]
            return socket_index
        except IndexError:
            return None

    if name is not None:
        for socket in socket_inputs:
            if socket.name == name:
                return socket
        return None

    return socket_inputs


def get_ng_outputs(node_tree, index=None, name=None):
    if bpy.app.version < (4, 0, 0):
        if index is not None:
            try:
                socket_index = node_tree.outputs[index]
                return socket_index
            except IndexError:
                return None

        if name is not None:
            if name in node_tree.outputs:
                return node_tree.outputs[name]
            else:
                return None

        return node_tree.outputs

    socket_outputs = []
    for item in node_tree.interface.items_tree:
        if item.item_type != 'SOCKET':
            continue
        if item.in_out == 'OUTPUT':
            socket_outputs.append(item)

    if index is not None:
        try:
            socket_index = socket_outputs[index]
            return socket_index
        except IndexError:
            return None

    if name is not None:
        for socket in socket_outputs:
            if socket.name == name:
                return socket
        return None

    return socket_outputs


def remove_ng_socket(socket):
    """Remove a socket from a node group, no need to indicate if it is input or output, just the socket itself
    :socket: socket to remove"""

    node_tree = socket.id_data

    if bpy.app.version < (4, 0, 0):
        if socket.is_output:
            node_tree.outputs.remove(socket)
        else:
            node_tree.inputs.remove(socket)
        return

    node_tree.interface.remove(socket)


def set_active_socket(socket):
    """Imposta il socket attivo, non necessita d'indicare se è input od output, solo il socket stesso"""
    node_tree = socket.id_data

    if bpy.app.version < (4, 0, 0):
        index = get_socket_index(socket)
        if socket.is_output:
            node_tree.active_output = index
        else:
            node_tree.active_input = index
        return

    else:
        index = get_socket_index(socket, get_real_index=True)
        node_tree.interface.active_index = index


def get_active_socket(node_tree, input_output='INPUT'):
    """Ritorna il socket attivo (socket, index)
    Nota: In blender 4.0 l'indice attivo sarà solo 1"""
    socket = None
    index = None

    if bpy.app.version < (4, 0, 0):
        if input_output == 'INPUT':
            index = node_tree.active_input
            if index is not None:
                socket = node_tree.inputs[index]
            return socket, index

        if input_output == 'OUTPUT':
            index = node_tree.active_output
            if index is not None:
                socket = node_tree.outputs[index]
            return socket, index

    else:
        socket = node_tree.interface.active
        index = node_tree.interface.active_index
        return socket, index

    return socket, index


def new_ng_socket(node_group, socket_type="NodeSocketFloat", socket_subtype="", socket_name="", in_out='INPUT', parent=None):
    if socket_name == "":
        socket_name = socket_type.title()
    if bpy.app.version < (4, 0, 0):
        if in_out == 'INPUT':
            socket = node_group.inputs.new(socket_type, socket_name)
        else:
            socket = node_group.outputs.new(socket_type, socket_name)
    else:
        s_types = ['NodeSocketVector', 'NodeSocketShader', 'NodeSocketFloat', 'NodeSocketColor']
        if not socket_type in s_types:
            # In questo caso stiamo usando il vecchio sistema di socket a nome unico, ma dobbiamo dividerlo in 2 parti
            # Type e SubType
            # Check if for example "NodeSocketFloatFactor" is in the list, if so, we need to remove the "Factor" part
            father_type = next((s for s in s_types if s in socket_type), None)
            sub_type = socket_type.replace(father_type, "")
            socket_subtype = sub_type

            socket = node_group.interface.new_socket(socket_name, description="", in_out=in_out, socket_type=father_type,
                                                     parent=parent)
        else:
            socket = node_group.interface.new_socket(socket_name, description="", in_out=in_out, socket_type=socket_type,
                                                     parent=parent)

        if socket_subtype:
            socket.subtype = socket_subtype.upper()

    return socket


def is_ng_input(socket):
    if bpy.app.version < (4, 0, 0):
        if socket.identifier.startswith("Input"):
            return True
        else:
            return False

    if socket.item_type == 'SOCKET' and socket.in_out == 'INPUT':
        return True


def is_ng_output(socket):
    if bpy.app.version < (4, 0, 0):
        if socket.identifier.startswith("Output"):
            return True
        else:
            return False

    if socket.item_type == 'SOCKET' and socket.in_out == 'OUTPUT':
        return True


def get_socket_type(socket):
    """Ritorna il tipo di socket
    bl_socket_idname per esempio può ritornare con "NodeSocketFloat" che corrisponde a VALUE"""
    if bpy.app.version < (4, 0, 0):
        return socket.type

    values = {
            'NodeSocketBool': 'BOOL',
            'NodeSocketColor': 'RGBA',
            'NodeSocketFloat': 'VALUE',
            'NodeSocketFloatAngle': 'VALUE',
            'NodeSocketFloatFactor': 'VALUE',
            'NodeSocketFloatUnsigned': 'VALUE',
            'NodeSocketInt': 'INT',
            'NodeSocketShader': 'SHADER',
            'NodeSocketString': 'STRING',
            'NodeSocketVector': 'VECTOR',
            'NodeSocketVectorAcceleration': 'VECTOR',
            'NodeSocketVectorDirection': 'VECTOR',
            'NodeSocketVectorEuler': 'VECTOR',
            'NodeSocketVectorTranslation': 'VECTOR',
            'NodeSocketVectorVelocity': 'VECTOR',
            'NodeSocketVirtual': 'VIRTUAL',
            'NodeSocketVirtualObject': 'VIRTUAL',
            'NodeSocketVirtualTransform': 'VIRTUAL',
            'NodeSocketVirtualVector': 'VIRTUAL',
            'NodeSocketVirtualXYZ': 'VIRTUAL',
        }

    return values.get(socket.bl_idname)


def ng_move_socket(socket, to_index):
    """Questa funzione muove il socket all'indice desiderato, attenzione in Blender 4.0 poichè gli indici fanno riferimento
    a tutti i socket, sia input che output compresi gli altri items_tree, quindi bisogna fare attenzione a non spostare
    un socket input prima di un socket output, altrimenti si creano problemi"""
    node_group = socket.id_data

    if bpy.app.version < (4, 0, 0):
        if socket.is_output:
            node_group.id_data.outputs.move(socket.index, to_index)
        else:
            node_group.id_data.inputs.move(socket.index, to_index)
        return

    else:
        socket_inputs = get_ng_inputs(node_group)
        socket_outputs = get_ng_outputs(node_group)

        if socket.in_out == 'INPUT':
            first_input_socket_fake_index = get_socket_index(socket_inputs[0], get_real_index=True)
            # Se il to_index combacia con il socket_inputs[0] ci fermiamo tenendo presente che il to_index fa riferimento
            # a tutti i socket, sia input che output compresi gli altri items_tree, quindi se il to_index corrisponde al
            # primo socket_inputs o all'ultimo socket_outputs, ci fermiamo
            if to_index == first_input_socket_fake_index -1:
                return

        elif socket.in_out == 'OUTPUT':
            last_output_socket_fake_index = get_socket_index(socket_outputs[-1], get_real_index=True)
            # Se il to_index combacia con il socket_outputs[-1] ci fermiamo tenendo presente che il to_index fa riferimento
            # a tutti i socket, sia input che output compresi gli altri items_tree, quindi se il to_index corrisponde al
            # primo socket_inputs o all'ultimo socket_outputs, ci fermiamo
            if to_index == last_output_socket_fake_index + 1:
                return

        node_group.interface.move(socket, to_index)


def get_socket_index(socket, get_real_index=False):
    """Questa funzione accetta i socket del node_group e di un nodo normale, ritorna l'indice del socket
    indipendentemente dal fatto che sia input o output
    NOTA Importante: In Blender 4.0 Gli indici restituiti fanno fede al conteggio degli inputs o degli outputs e non
    al conteggio totale dei socket (items_tree)
    :socket: socket del node group o del nodo
    :get_real_index: Solo per Blender 4.0, se True ritorna l'indice reale del socket, altrimenti ritorna l'indice Input o Output"""

    if hasattr(socket, 'node'):
        # In questo caso il socket è dal nodo non dal node group
        node = socket.node
        if socket.is_output:
            for idx, sck in enumerate(node.outputs):
                if sck == socket:
                    return idx
        else:
            for idx, sck in enumerate(node.inputs):
                if sck == socket:
                    return idx

    node_tree = socket.id_data

    if bpy.app.version < (4, 0, 0):
        if socket.is_output:
            for idx, sck in enumerate(node_tree.outputs):
                if sck == socket:
                    return idx
        else:
            for idx, sck in enumerate(node_tree.inputs):
                if sck == socket:
                    return idx

    else:

        sockets = []
        if socket.item_type != 'SOCKET':
            return None
        if get_real_index:
            for sck in node_tree.interface.items_tree:
                if sck.item_type != 'SOCKET':
                    continue
                sockets.append(sck)
        else:
            if socket.in_out == 'OUTPUT':
                for sck in node_tree.interface.items_tree:
                    if sck.item_type != 'SOCKET':
                        continue
                    if sck.in_out == 'OUTPUT':
                        sockets.append(sck)
            elif socket.in_out == 'INPUT':
                for sck in node_tree.interface.items_tree:
                    if sck.item_type != 'SOCKET':
                        continue
                    if sck.in_out == 'INPUT':
                        sockets.append(sck)

        for idx, sck in enumerate(sockets):
            if sck == socket:
                return idx


def get_socket_color(context, socket):
    """Ritorna il colore del socket"""
    if bpy.app.version < (4, 0, 0):
        return socket.draw_color(context)

    # Bisogna ottenere il colore in base al tipo di socket:

    from ..dictionaries.dictionaries import socket_colors
    colors = socket_colors()
    color = colors.get(socket.bl_socket_idname)
    if not color:
        color = (0.63, 0.63, 0.63, 1.0)

    return color


def get_node_socket_from_ng_socket(socket, node):
    """Ritorna il socket del nodo a cui fa riferimento il socket del node group
    :socket: socket del node group (non l'indice!)
    :node: nodo che contiene il node_group che a sua volta contiene il socket
    :return: socket del nodo"""

    node_tree = socket.id_data

    if bpy.app.version < (4, 0, 0):
        if socket.is_output:
            # Otteniamo l'index del socket data la lista di socket
            index = get_socket_index(socket)
            return node.inputs[index]

        else:
            # Otteniamo l'index del socket data la lista di socket
            index = get_socket_index(socket)
            return node.outputs[index]

    else:
        if socket.in_out == 'INPUT':
            # Otteniamo l'index del socket data la lista di socket
            index = get_socket_index(socket)

            return node.inputs[index]
        else:
            # Otteniamo l'index del socket data la lista di socket
            index = get_socket_index(socket)
            return node.outputs[index]


def is_linked_internal(socket):
    """Dato il socket (del node_group) ritorna True se almeno 1 dei nodi "Group Input" o "Group Output" è collegato esattamente sul socket
    a cui fa riferimento il socket del node group.
    Nota: Il socket viene riconosciuto automaticamente se è un input o un output
    :socket: socket del node group
    :return: True se è collegato, False se non è collegato"""

    node_tree = socket.id_data
    nodes = node_tree.nodes

    if bpy.app.version < (4, 0, 0):
        if socket.is_output:
            socket_index = get_socket_index(socket)
            is_linked = next((n for n in nodes if n.type == 'GROUP_OUTPUT' and n.inputs[socket_index].is_linked), None)
            return is_linked

        else:
            socket_index = get_socket_index(socket)
            is_linked = next((n for n in nodes if n.type == 'GROUP_INPUT' and n.outputs[socket_index].is_linked), None)
            return is_linked

    else:
        if socket.item_type != 'SOCKET':
            return False

        if socket.in_out == 'OUTPUT':
            socket_index = get_socket_index(socket)
            is_linked = next((n for n in nodes if n.type == 'GROUP_OUTPUT' and n.inputs[socket_index].is_linked), None)
            return is_linked

        if socket.in_out == 'INPUT':
            socket_index = get_socket_index(socket)
            is_linked = next((n for n in nodes if n.type == 'GROUP_INPUT' and n.outputs[socket_index].is_linked), None)
            return is_linked


def move_socket(socket, index):
    """Sposta il socket del nodo gruppo alla posizione desiderata"""
    node_tree = socket.id_data
    if bpy.app.version < (4, 0, 0):
        if socket.is_output:
            node_tree.outputs.move(socket.index, index)
        else:
            node_tree.inputs.move(socket.index, index)

    else:
        node_tree.interface.move(socket, index)


def copy_socket_description_to_official_description(node_tree):
    """Copia la vecchia descrizione dei socket nel nuovo campo description"""
    ng_inputs = []
    if bpy.app.version < (4, 0, 0):
        for ng_input in node_tree.inputs:
            ng_inputs.append(ng_input)

    else:
        for item in node_tree.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                ng_inputs.append(item)

    from ..exaconv import get_sckprop
    for ng_input in ng_inputs:
        sckProp = get_sckprop(ng_input)
        description = sckProp.api_bool_description
        if description:
            ng_input.description = description
            
            
            
def get_internal_socket(socket):

    """Restituisce il socket interno del node group a cui fa riferimento il socket del node group"""

    from ..utility.utility import get_in_out_group
    node_tree = socket.id_data
    nGinput, nGoutput = get_in_out_group(node_tree)
    nGinput = next((n for n in nGinput), None)
    nGoutput = next((n for n in nGoutput), None)

    index = get_socket_index(socket)

    if bpy.app.version < (4, 0, 0):
        if socket.is_output and nGoutput:
            return nGoutput.inputs[index]
        else:
            return nGinput.outputs[index]
        
    else:
        if socket.in_out == 'OUTPUT' and nGoutput:
            return nGoutput.inputs[index]
        else:
            return nGinput.outputs[index]
            
            









