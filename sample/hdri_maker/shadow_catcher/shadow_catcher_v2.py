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
from bpy.props import EnumProperty
from bpy.types import Operator

from .shadow_catcher_fc import add_probe_funct, update_shadow_catcher
from ..bpy_data_libraries_load.data_lib_loads import load_libraries_material
from ..collections_scene.collection_fc import get_shadow_catcher_collection, remove_hdrimaker_tools_collection, \
    move_ob_from_to_collection
from ..exaconv import get_objprop, get_matprop
from ..exaproduct import Exa
from ..library_manager.get_library_utils import risorse_lib
from ..utility.constraints import copy_scale_constraints
from ..utility.utility import bmesh_create_object, set_active_object, purge_all_group_names, make_parent


class HDRIMAKER_OT_AddShadowCatcher(Operator):
    """Add Shadow Catcher plane"""

    bl_idname = Exa.ops_name + "shadowcatcher"
    bl_label = "Add shadow catcher"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(default='ADD', items=(
        ('ADD', "Add", "Add Shadow Catcher"),
        ('REMOVE', "Remove", "Remove Shadow Catcher")
    ))

    def invoke(self, context, event):
        return self.execute(context)

    @staticmethod
    def remove(context):
        scn = context.scene
        for o in scn.objects:
            objProp = get_objprop(o)
            if o.type == 'MESH':
                if objProp.object_id_name in ["EEVEE_SHADOW_CATCHER", "CYCLES_SHADOW_CATCHER"]:
                    bpy.data.meshes.remove(o.data)
            elif o.type == 'LIGHT_PROBE':
                if objProp.object_id_name == "SC_LIGHT_PROBE_PLANE":
                    bpy.data.objects.remove(o)

        remove_hdrimaker_tools_collection(scn)

    def execute(self, context):

        self.remove(context)

        scn = context.scene

        if self.options == 'ADD':
            if bpy.app.version >= (4, 2, 0):
                scn.eevee.use_raytracing = True

            shadow_catcher_collection = get_shadow_catcher_collection()

            # Eevee Shadow Catcher
            data = bpy.data.meshes.new("Eevee Shadow Catcher")
            eevee_plane = bpy.data.objects.new("Eevee Shadow Catcher", data)
            bmesh_create_object(data, 'PLANE')
            eevee_plane.location = context.scene.cursor.location
            objProp = get_objprop(eevee_plane)
            objProp.object_id_name = "EEVEE_SHADOW_CATCHER"
            shadow_catcher_collection.objects.link(eevee_plane)
            eevee_plane.visible_shadow = False
            # ----------------------------------------------------------------------------------------------------------

            # Cycles Shadow Catcher:
            data = bpy.data.meshes.new("Cycles Shadow Catcher")
            cycles_plane = bpy.data.objects.new("Cycles Shadow Catcher", data)
            bmesh_create_object(data, 'PLANE')
            objProp = get_objprop(cycles_plane)
            objProp.object_id_name = "CYCLES_SHADOW_CATCHER"

            shadow_catcher_collection.objects.link(cycles_plane)

            # cycles_plane.location = eevee_plane.location
            cycles_plane.location.z -= 0.005

            make_parent(eevee_plane, cycles_plane)

            copy_scale_constraints(cycles_plane, target=eevee_plane, target_space='CUSTOM', owner_space='CUSTOM')


            cycles_plane.hide_select = True
            cycles_plane.visible_glossy = False
            cycles_plane.is_shadow_catcher = True



            # --------------------------------------------------------------

            # Plane need to be selected and active object
            set_active_object(eevee_plane)

            # Add material:
            material_path = os.path.join(risorse_lib(), "blendfiles", "materials", "Shadow Catcher.blend")
            material = load_libraries_material(material_path, "Shadow Catcher", rename="Shadow Catcher")
            purge_all_group_names(material.node_tree)

            matProp = get_matprop(material)
            matProp.mat_id_name = "EEVEE_SHADOW_CATCHER"

            eevee_plane.data.materials.append(material)

            # Add reflection plane probe:
            reflection_plane = add_probe_funct(eevee_plane, object_id_name='SC_LIGHT_PROBE_PLANE')
            move_ob_from_to_collection(reflection_plane, shadow_catcher_collection)

            # Important to update the shadow catcher and their materials and objects
            update_shadow_catcher()

        return {'FINISHED'}
