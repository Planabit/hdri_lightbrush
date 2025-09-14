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
import os

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

from ..exaproduct import Exa
from ..utility.utility import bmesh_create_object
from ..utility.utility_dependencies import open_folder


class HDRIMAKER_OT_SaveGeoNode(Operator, ExportHelper):
    bl_idname = Exa.ops_name + "save_geometry_nodes"
    bl_label = "Save Geometry Nodes"
    bl_description = "Save the geometry nodes of the current world"
    bl_options = {'REGISTER', 'UNDO'}

    geometry_node: StringProperty(options={'HIDDEN'})
    filter_glob: StringProperty(options={'HIDDEN'}, default='*.blend')
    filename_ext = ".blend"

    def invoke(self, context, event):
        node_tree = bpy.data.node_groups[self.geometry_node]
        self.filepath = os.path.join(bpy.path.abspath("//"), node_tree.name)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scn = context.scene
        node_tree = bpy.data.node_groups[self.geometry_node]

        # Create Empty object
        data = bpy.data.meshes.new(node_tree.name)
        ob = bpy.data.objects.new(node_tree.name, data)
        bmesh_create_object(data, 'CUBE')

        # Attention, the saving of the geometry node takes place on a Cube, the cube may not be visible in the
        # scene of the blender file that is saved, because there is indeed applied the geometry node

        fake_scene = bpy.data.scenes.new(node_tree.name)
        # Link object to fake scene
        fake_scene.collection.objects.link(ob)

        # Create Geometry Nodes Modifier
        mod = ob.modifiers.new(node_tree.name, 'NODES')
        mod.node_group = node_tree

        filepath = os.path.join(self.filepath)

        # Save the object
        data_blocks = {ob, fake_scene}
        try:
            bpy.data.libraries.write(filepath, data_blocks)
        except:
            pass

        bpy.data.objects.remove(ob)
        bpy.data.scenes.remove(fake_scene)

        open_folder(os.path.dirname(filepath))

        return {'FINISHED'}
