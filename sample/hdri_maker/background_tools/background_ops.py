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
from itertools import chain

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from .background_fc import delete_world, flip_diffuse_to_light, create_basic_world, solve_nodes_problem, \
    link_and_fix_node_tree, align_hdri_maker_nodes, get_nodes_dict
from ..dome_tools.dome_fc import remove_mat_ground, AssembleDome, un_parent_light_studio_from_dome
from ..exaconv import get_wrlprop, get_matprop, get_ngprop, get_objprop
from ..exaproduct import Exa
from ..shadow_catcher.shadow_catcher_fc import remove_all_bounds_objects
from ..utility.text_utils import draw_info
from ..utility.utility import get_addon_preferences, has_nodetree, purge_all_group_names


class HDRIMAKER_OT_RemoveMaterial(Operator):

    """Delete all ground hdri active"""
    bl_idname = Exa.ops_name + "remove_background"
    bl_label = "Remove Background"
    bl_options = {'INTERNAL', 'UNDO'}

    remove_all = False

    @classmethod
    def description(cls, context, properties):
        desc = """Remove the world from the scene, remove the dome and remove all the attached materials. Ctrl+Click or Shift+Click to also remove the default world"""
        return desc

    def invoke(self, context, event):
        self.remove_all = False
        if event.ctrl or event.shift:
            self.remove_all = True
        return self.execute(context)

    def execute(self, context):

        world_id_name = ""

        scn = context.scene
        world = scn.world

        if world:
            wrlProp = get_wrlprop(world)
            world_id_name = wrlProp.world_id_name

        # Find Old Dome if Exists remove it
        for obj in scn.objects:
            if obj.type != 'MESH':
                continue
            objProp = get_objprop(obj)
            if objProp.object_id_name == 'HDRi_Maker_Dome':
                bpy.data.objects.remove(obj)

        # Remove all shinkwrap Objects:

        un_parent_light_studio_from_dome()

        remove_all_bounds_objects(restore_object_id_name=True)

        delete_world(self, context)
        from ..dome_tools.dome_fc import Hooks
        Hooks(context).remove_dome_hooks()
        from ..dome_tools.dome_fc import delete_dome
        delete_dome(self, context)
        from ..dome_tools.dome_fc import remove_dome_handler
        remove_dome_handler()
        from ..collections_scene.collection_fc import remove_hdrimaker_tools_collection
        remove_hdrimaker_tools_collection(scn)

        if not self.remove_all:
            create_basic_world(scn)

        # if self.remove_all:
        #     remove_light_studio_objects()

        remove_all_bounds_objects()
        remove_mat_ground(scn.objects[:])

        return {'FINISHED'}


class HDRIMAKER_OT_SolveNodesProblem(Operator):
    bl_idname = Exa.ops_name + "solvenodesproblem"
    bl_label = "Solve Material Problem"
    bl_options = {'INTERNAL', 'UNDO'}

    options: StringProperty()

    @classmethod
    def description(cls, context, properties):
        if properties.options == "SOLVE_WORLD_NODES_PROBLEM":
            return "Solve the problem with the world node tree"
        elif properties.options == "SOLVE_DOME_NODES_PROBLEM":
            return "Solve the problem with the dome node tree"
        elif properties.options == "RETROCOMPATIBILITY":
            return "It search in all project for unrecognized nodes and repair them (Only works with node_tree created with HDRIMaker to avoid problems)"

    def invoke(self, context, event):
        self.scn = context.scene
        self.world = self.scn.world

        if not self.world:
            return {'CANCELLED'}
        if not has_nodetree(self.world):
            return {'CANCELLED'}
        self.node_tree = self.world.node_tree

        if self.options == 'SOLVE_WORLD_NODES_PROBLEM':
            return self.solve_world(context)
        elif self.options == 'RETROCOMPATIBILITY':
            return self.solve_all_retrocompatibility(context)
        else:
            return {'CANCELLED'}

    def solve_all_retrocompatibility(self, context):
        from ..utility.nodes_compatibility import repair_unrecognized_nodes
        for w in bpy.data.worlds:
            if get_wrlprop(w).world_id_name != "":
                if has_nodetree(w):
                    repair_unrecognized_nodes(w.node_tree)

        for m in bpy.data.materials:
            if get_matprop(m).mat_id_name != "":
                if has_nodetree(m):
                    repair_unrecognized_nodes(m.node_tree)

        for group in bpy.data.node_groups:
            if get_ngprop(group).group_id_name != "":
                repair_unrecognized_nodes(group)

        text = "The operation of searching for incompatible nodes on all HDRi Maker nodes has been completed, " \
               "it is not always guaranteed that it can work at 100%, try to check if the problem has been solved"
        draw_info(text, "Info", 'INFO')

        self.report({'INFO'}, "Retrocompatibility Operation Completed")

        return {'FINISHED'}

    def solve_world(self, context):
        from ..utility.nodes_compatibility import repair_unrecognized_nodes
        repair_unrecognized_nodes(self.node_tree)
        solve_nodes_problem(self.node_tree)
        link_and_fix_node_tree(self.node_tree)
        align_hdri_maker_nodes(self.node_tree)
        purge_all_group_names(self.node_tree)

        node_dict = get_nodes_dict(self.node_tree)

        diffuse = node_dict.get("DIFFUSE")
        light = node_dict.get("LIGHT")
        complete = node_dict.get("COMPLETE")
        vectors = node_dict.get("VECTORS")
        mixer = node_dict.get("MIXER")

        if not diffuse and not light and not complete and not vectors and not mixer:
            text = "This World was not created with HDRi Maker, it is not possible to solve the problem. (This cleaner was created to solve " \
                     "the problems with the nodes created with HDRi Maker)"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}
        return {'FINISHED'}


class HDRIMAKER_OT_FlipDiffuseLight(Operator):
    """Flip Diffuse and Light"""
    bl_idname = Exa.ops_name + "flipdiffuselight"
    bl_label = "Flip Diffuse and Light"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(default="SWITCH",
                          items=(('SWITCH', "Switch", ""), ('SET_1', "Set 1", ""), ('SET_2', "Set 2", "")))

    def execute(self, context):
        scn = context.scene
        world = scn.world
        if not world:
            return {'CANCELLED'}
        if not has_nodetree(world):
            return {'CANCELLED'}

        if self.options == 'SWITCH':
            flip_diffuse_to_light(self, context)

        nodes_dict = get_nodes_dict(world.node_tree)
        diffuse = nodes_dict.get('DIFFUSE')
        if not diffuse:
            return {'CANCELLED'}

        image = None
        for n in diffuse.node_tree.nodes:
            if hasattr(n, 'image'):
                if n.image:
                    image = n.image

        if image:
            A_Dome = AssembleDome(context, image=image, dome_name="DOME_" + world.name)
            A_Dome.asign_image_to_dome()

        # TODO: Qui, bisogna attendere di decidere se il world è di tipo estraneo e cosa fare nel caso

        return {'FINISHED'}


class HDRIMAKET_OT_SearchCurrentWorld(Operator):
    """Look for the preview of the current world"""

    bl_idname = Exa.ops_name + "searchcurrentworld"
    bl_label = "Search Current Background"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        try:
            scn = context.scene
            scnProp = scn.hdri_prop_scn

            idWorld = scn.world.hdri_prop_world.world_id_name

            addon_preferences = get_addon_preferences()

            dir = (
                os.path.join(addon_preferences.addon_default_library, "preview_hdri"),
                addon_preferences.addon_user_library)

            if idWorld != '':
                for subdir, dirs, files in chain.from_iterable(os.walk(path) for path in dir):
                    for f in files:
                        if not f.startswith("."):
                            if f == idWorld + '.png':
                                try:
                                    scnProp.libraries_selector = 'DEFAULT'
                                    scnProp.up_category = subdir.split(os.path.sep)[-1]
                                except:
                                    scnProp.libraries_selector = 'USER'
                                    scnProp.up_category = subdir.split(os.path.sep)[-1]

                bpy.data.window_managers["WinMan"].hdri_category = idWorld
        except:
            pass

        return {'FINISHED'}

class HDRIMAKER_OT_MakeLocal(Operator):
    """Make Local"""
    bl_idname = Exa.ops_name + "make_local"
    bl_label = "Make Local"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Make Local"

    def execute(self, context):
        scn = context.scene
        world = scn.world

        if world.library:
            world.make_local()


        return {'FINISHED'}
