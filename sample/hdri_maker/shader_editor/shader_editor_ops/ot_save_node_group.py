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
from bpy.props import EnumProperty, StringProperty, BoolProperty
from bpy.types import Operator

from ...background_tools.background_fc import set_world_goodies
from ...exaproduct import Exa


class HDRIMAKER_OT_SaveNodeGroup(Operator):
    """Save the group node, in the indicated directory"""
    bl_idname = Exa.ops_name + "savenodegroup"
    bl_label = "Save Node Group"
    bl_options = {'INTERNAL', 'UNDO'}

    path: StringProperty(subtype='DIR_PATH')
    save_type: EnumProperty(default='MATERIALS', items=(('MATERIALS', "Materials", ""), ('WORLDS', "Worlds", "")))
    full: BoolProperty(default=False, description="Save full Node_tree as material or world")

    def execute(self, context):
        from ...utility.nodes_compatibility import store_node_attributes_into_node_tree
        from ...custom_property_groups.scene.scene_callback import ScnCall
        from ...exaconv import get_scnprop
        from ...ops_and_fcs.create_tools import create_node_utility, create_scene
        from ...utility.text_utils import draw_info
        from ...utility.utility import retrieve_nodes
        from ...utility.utility import return_name_without_numeric_extension, bmesh_create_object
        from ...utility.utility_dependencies import open_folder

        scn = context.scene

        path = self.path
        if not os.path.isdir(self.path):
            text = "This path does not exist, please enter a valid path or check into "
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if not self.full:
            node_group = context.space_data.edit_tree.nodes.active.node_tree
            name = return_name_without_numeric_extension(node_group.name)
            node_group.name = name

        save_scene = create_scene(bpy.context.scene, "HDRIMAKER_RenderScene", "SAVE_MATERIAL")

        if self.save_type == 'WORLDS':
            if self.full:
                data_id = scn.world
            else:
                data_id = bpy.data.worlds.new(name)
                set_world_goodies(data_id)
            save_scene.world = data_id

        elif self.save_type == 'MATERIALS':
            if self.full:
                mat_node_tree = context.space_data.edit_tree.original
                data_id = next((m for m in bpy.data.materials if m.node_tree if m.node_tree == mat_node_tree), None)
                name = return_name_without_numeric_extension(data_id.name)
            else:
                data_id = bpy.data.materials.new(name)

            data = bpy.data.meshes.new(name)
            ob = bpy.data.objects.new(name, data)
            bmesh_create_object(data, 'CUBE')
            data.name = return_name_without_numeric_extension(data.name)
            ob.name = return_name_without_numeric_extension(ob.name)
            ob.location = (0, 0, 0)
            ob.data.materials.append(data_id)
            save_scene.collection.objects.link(ob)

        if not self.full:
            data_id.use_nodes = True
            nodes = data_id.node_tree.nodes
            for n in nodes:
                nodes.remove(n)

            node = create_node_utility(nodes, -125, 100, node_group.name, node_group.name, 'ShaderNodeGroup', None,
                                       150, False)
            node.node_tree = node_group

        unpack = []
        if self.full:
            node_list = retrieve_nodes(data_id.node_tree)
            store_node_attributes_into_node_tree(data_id.node_tree)
        else:
            node_list = retrieve_nodes(node_group)
            store_node_attributes_into_node_tree(node_group)

        for n in node_list:
            if n.type in ['TEX_IMAGE', 'TEX_ENVIRONMENT'] and n.image:
                if not n.image.packed_file:
                    n.image.pack()
                    if n.image not in unpack:
                        unpack.append(n.image)

        data_blocks = {data_id, save_scene}
        if self.full:
            write_path = os.path.join(path, data_id.name + ".blend")
        else:
            write_path = os.path.join(path, node_group.name + ".blend")
        scnProp = get_scnprop(save_scene)
        prev_id_name = scnProp.scene_id_name
        scnProp.scene_id_name = ''
        try:
            bpy.data.libraries.write(write_path, data_blocks)
        except:
            pass

        scnProp.scene_id_name = prev_id_name

        for img in unpack:
            try:
                img.unpack(method='USE_ORIGINAL')
            except:
                continue
        bpy.data.scenes.remove(save_scene)

        if not self.full:
            if self.save_type == 'WORLDS':
                bpy.data.worlds.remove(data_id)
            elif self.save_type == 'MATERIALS':
                bpy.data.objects.remove(ob)
                bpy.data.materials.remove(data_id)

        try:
            open_folder(path)
        except:
            pass

        ScnCall.shader_type = ""  # Refresha l'enum proprietà che elenca i nodi gruppi nell'interfaccia ShaderEditor

        return {'FINISHED'}
