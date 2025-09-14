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
from ..exaconv import get_matprop, get_ndprop
from ..utility.utility import retrieve_nodes


def purge_module_group(node_tree):
    nodes = node_tree.nodes
    links = node_tree.links
    for n in nodes:
        if n.type == 'TEX_IMAGE' and not n.image:
            nodes.remove(n)
    for n in nodes:
        if n.type == 'GROUP' and n.extremepbr_node_prop.node_tag == 'MAP_CTRL_POST':
            if not n.inputs[0].is_linked:
                nodes.remove(n)

    for n in nodes:
        if n.outputs[:]:
            if not [out for out in n.outputs if out.is_linked]:
                nodes.remove(n)


def is_old_extreme_pbr_material(mat):
    if not mat.use_nodes:
        return
    matProp = get_matprop(mat)
    if "#xtm_pbr#" not in matProp.mat_id_name:
        # Questo vuol dire che non è nemmeno un Evo o Combo Materiale
        return

    if matProp.mat_version:
        # mat_version è stato aggiunto solo con l'avvento di Nexus Versione
        return

    return True


def node_tree_statistics(node_tree):
    retrieve = retrieve_nodes(node_tree)
    full_nodes = []
    groups = []
    images = []
    mute_images = []

    for n in retrieve:
        if n.type not in ['GROUP_INPUT', 'GROUP_OUTPUT', 'FRAME', 'REROUTE']:
            full_nodes.append(n)
        if n.type == 'GROUP':
            groups.append(n)
        if n.type == 'TEX_IMAGE':
            if n.image:
                images.append(n.image)
                if n.mute:
                    mute_images.append(n)

    data_images = [n.image for n in mute_images]
    univoque_mute_images = set(data_images)

    univoque_groups = [n.node_tree for n in groups]
    univoque_groups = set(univoque_groups)

    return full_nodes, groups, images, univoque_mute_images, univoque_groups




def store_color_ramps_props(nodes, store_method='CUSTOM_PROP'):
    """Memorizza le proprietà delle ColorRamp in un Custom Property Group che è un dizzionario trasformato in stringa"""

    for n in nodes:
        if n.type != 'VALTORGB':  # Quindi ColorRamp
            continue

        ndProp = get_ndprop(n)
        if store_method == 'CUSTOM_PROP':
            if ndProp.color_ramp_props:
                # Per sicurezza, se possiede già le proprietà color_ramp_props non le sovrascrive
                continue

        color_ramp = n.color_ramp

        props = {}
        for key in color_ramp.bl_rna.properties.keys():
            if not color_ramp.is_property_readonly(key):
                # Qui dobbiamo salvare la proprietà in formato stringa, quindi dobbiamo accedere a tutti i valori
                # Se la proprietà è una classe, lasciamo stare:
                if color_ramp.bl_rna.properties[key].type == 'POINTER':
                    continue
                value = getattr(color_ramp, key)
                props[key] = str(value)

        elements = {}
        for idx, element in enumerate(color_ramp.elements):
            elements[idx] = {}
            try:
                elements[idx]['position'] = element.position
            except:
                print("Unable to store position from ColorRamp element")
                pass
            try:
                elements[idx]['color'] = element.color[:]
            except:
                print("Unable to store color from ColorRamp element")
                pass
            try:
                elements[idx]['alpha'] = element.alpha
            except:
                print("Unable to store alpha from ColorRamp element")
                pass

        color_ramp_props = {'props': props, 'elements': elements}

        # Convert to json string:

        if store_method == 'CUSTOM_PROP':
            import json
            color_ramp_props = json.dumps(color_ramp_props)
            ndProp.color_ramp_props = color_ramp_props
        elif store_method == 'JSON_DATA':
            return color_ramp_props


def restore_color_ramps_props(nodes, preset_data=None):
    """Ripristina le proprietà delle ColorRamp se in essa sono memorizzate le proprietà personalizzate
      :param preset_data: se None, ripristina tutte le ColorRamp, altrimenti ripristina solo la ColorRamp passata
      :param nodes: nodes to enumerate or single node into a list
      :param color_ramp: if None, restore all color_ramps, else restore only the color_ramp passed"""

    for n in nodes:
        if n.type != 'VALTORGB':
            continue

        ndProp = get_ndprop(n)
        if not preset_data:
            if not ndProp.color_ramp_props:
                continue

        # Remove all elements:
        color_ramp = n.color_ramp
        while color_ramp.elements:
            to_remove = next((element for element in color_ramp.elements))
            color_ramp.elements.remove(to_remove)
            if len(color_ramp.elements[:]) == 1:
                # Un elemento deve esistere sempre, quindi se ne rimane solo uno interrompiamo il ciclo
                break

        if preset_data:
            color_ramp_prop = preset_data
        else:
            import json
            color_ramp_prop = json.loads(ndProp.color_ramp_props)

        props = color_ramp_prop.get('props')
        if props:
            for key, value in props.items():
                try:
                    setattr(color_ramp, key, value)
                except:
                    pass

        elements = color_ramp_prop.get('elements')
        if elements:
            for idx, element in elements.items():
                if len(color_ramp.elements) == len([i for i in elements.keys()]):
                    break
                try:
                    color_ramp.elements.new(int(idx))
                except:
                    print("Unable to create new ColorRamp element", idx)
                    pass

        for idx, real_element in enumerate(color_ramp.elements):
            str_idx = str(idx)
            try:
                real_element.position = elements[str_idx]['position']
            except Exception as e:
                print("Unable to restore position from ColorRamp element", idx, "Error:", e)
                pass
            try:
                real_element.color = elements[str_idx]['color']
            except Exception as e:
                print("Unable to restore color from ColorRamp element", idx, "Error:", e)
                pass
            try:
                real_element.alpha = elements[str_idx]['alpha']
            except Exception as e:
                print("Unable to restore alpha from ColorRamp element", idx, "Error:", e)
                pass












