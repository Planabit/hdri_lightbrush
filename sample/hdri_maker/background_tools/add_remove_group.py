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
import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from .background_fc import load_background_diffuse_or_light, analyse_blend_world_and_get_node_group, \
    is_hdri_maker_studio_world, convert_world_to_node_group, align_hdri_maker_nodes
from ..bpy_data_libraries_load.data_lib_loads import load_libraries_world
from ..exaproduct import Exa
from ..library_manager.tools import get_file_source
from ..ops_and_fcs.create_tools import create_node_utility
from ..utility.text_utils import draw_info
from ..utility.utility import remove_nodes, make_local, has_nodetree, retrieve_nodes


class HDRIMAKET_OT_AddRemoveGroups(Operator, ImportHelper):
    bl_idname = Exa.ops_name + "addremovegroups"
    bl_label = "Add Remove Groups"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(options={'HIDDEN'}, items=(('ADD', "Add", ""), ('REMOVE', "Remove", "")))
    node_task: EnumProperty(options={'HIDDEN'}, items=(('DIFFUSE', "Diffuse", ""), ('LIGHT', "Light", "")))
    invoke_browser: BoolProperty(options={'HIDDEN'}, name="Invoke Browser", default=False)
    filepath: StringProperty(options={'HIDDEN'}, subtype="FILE_PATH")
    filter_glob: StringProperty(options={'HIDDEN'}, default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.hdr;*.exr;*.blend')
    is_from_asset_browser: BoolProperty(options={'HIDDEN'}, name="Is From Asset Browser", default=False)

    @classmethod
    def description(cls, context, properties):
        if properties.options == 'ADD':
            if properties.invoke_browser:
                return "Import a background image or from file.blend for the " + properties.node_task.lower() + " (Tips: Ctrl or Shift + Click to invoke the file browser)"
            else:
                return "Add a new background as " + properties.node_task.lower()
        elif properties.options == 'REMOVE':
            return "Remove the background " + properties.node_task.lower()
        return ""

    def invoke(self, context, event):
        if self.options == 'REMOVE':
            return self.execute(context)

        # For file search if the library manager is on the Import Tools
        if self.invoke_browser or (event.ctrl or event.shift):
            self.invoke_browser = True
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            return self.execute(context)

    def execute(self, context):
        from ..dome_tools.dome_fc import AssembleDome
        from ..dome_tools.dome_fc import get_environment_from_world

        scn = context.scene
        world = scn.world
        node_tree = world.node_tree

        from ..light_studio.sun_ops import get_sun_sinc_driver
        sun_driver = get_sun_sinc_driver(node_tree)

        make_local(world)

        node_list = retrieve_nodes(node_tree)
        for n in node_list:
            if has_nodetree(n):
                # Any node_tree from asset_browser is not local, and it is not editable. So we try to make it local:
                # TODO: This does not seem to work well on group nodes. I don't really understand why.
                make_local(n.node_tree)

        image = None

        if self.options == 'REMOVE':
            load_background_diffuse_or_light(node_tree, node_task=self.node_task, action=self.options)
            # In this case, the image has been removed from Diffuse, so the Dome need to be updated with the Light image
            # as now the complete image
            if self.node_task == 'DIFFUSE':
                image_dict = get_environment_from_world(world)
                image = image_dict.get('image')
                if image:
                    A_Dome = AssembleDome(context, image=image, dome_name="DOME_" + world.name)
                    A_Dome.asign_image_to_dome()

            return {'FINISHED'}

        if self.is_from_asset_browser:
            if len(context.selected_asset_files[:]) > 1:
                text = "You have selected more than one asset. Please select only one asset"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}
            elif len(context.selected_asset_files[:]) == 0:
                text = "You have not selected any asset. Please select one asset"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}
            # In this case, the operator is called from the asset browser!
            from ..asset_browser.asset_functions import get_asset_browser_world
            dictionary_file = get_asset_browser_world(self, context)

        else:
            if self.invoke_browser:
                dictionary_file = get_file_source(self.filepath)
            else:
                dictionary_file = get_file_source()


        if not dictionary_file:
            text = "The selected file does not exist or is empty, check if you are importing from the library the right file or if it is in 'Empty' state " \
                     "If you want to import a file to use as a background, you can use the Shift + Click button to open the file browser"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if not is_hdri_maker_studio_world(world):

            node_tree = world.node_tree
            nodes = node_tree.nodes
            node_group = convert_world_to_node_group(world, group_id_name='COMPLETE')
            if node_group:
                remove_nodes(node_tree, keep_output=True)
                n = create_node_utility(nodes, nodeName=node_group.name, label=node_group.name,
                                        nodeType="ShaderNodeGroup")
                n.node_tree = node_group
            else:
                text = "With the current world node configuration, it is not possible to convert it into a node group" \
                       " you can also add a new background with the standard add operator in the main ui panel"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

        file_type = dictionary_file.get("file_type")
        filepath = dictionary_file.get("filepath")
        filename = dictionary_file.get("filename")

        if file_type == 'IMAGE':
            # In this case we have an image from the library manager
            image = bpy.data.images.load(filepath)
            image.name = filename
            load_background_diffuse_or_light(node_tree=node_tree, image=image, node_task=self.node_task,
                                             action=self.options)

            align_hdri_maker_nodes(world.node_tree)

        elif file_type == 'BLENDER_FILE':
            world = load_libraries_world(path_to_world=filepath, world_index=0)
            world_info_dict = analyse_blend_world_and_get_node_group(world, group_id_name=self.node_task)

            # if world_info_dict contains an image, we have an old hdri maker world, and we need to get the image
            image = world_info_dict.get("image")
            if image:
                load_background_diffuse_or_light(node_tree=node_tree, image=image, node_task=self.node_task,
                                                 action=self.options)
            else:
                node_group = world_info_dict.get("node_group")

                if node_group:
                    load_background_diffuse_or_light(node_tree=node_tree, node_group=node_group,
                                                     node_task=self.node_task,
                                                     action=self.options)

            align_hdri_maker_nodes(world.node_tree)


        if image and self.node_task == 'DIFFUSE':
            A_Dome = AssembleDome(context, image=image, dome_name="DOME_" + world.name)
            A_Dome.asign_image_to_dome()

        if sun_driver:
            from ..light_studio.sun_ops import sync_sun
            sync_sun(context, options="SYNC")

        return {'FINISHED'}
