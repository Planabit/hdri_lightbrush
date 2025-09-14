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
from bpy.props import EnumProperty, BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from ..background_tools.background_fc import import_hdri_maker_world, assign_image_to_background_node, \
    analyse_blend_world_and_get_node_group, is_hdri_maker_studio_world, \
    load_background_complete, get_nodes_dict
from ..bpy_data_libraries_load.data_lib_loads import load_libraries_world
from ..dome_tools.dome_fc import find_current_dome_version, AssembleDome
from ..exaconv import get_scnprop
from ..exaproduct import Exa
from ..library_manager.main_pcoll_attributes import get_winman_main_preview
from ..library_manager.tools import get_file_source, get_volume_name_by_folder_name
from ..utility.text_utils import draw_info
from ..utility.utility import set_object_mode, purge_all_group_names, has_nodetree


class HDRIMAKER_OT_AddBackground(Operator, ImportHelper):
    """Create new world from current preview"""

    bl_idname = Exa.ops_name + "addbackground"
    bl_label = "Add Background"
    bl_options = {'INTERNAL', 'UNDO'}

    is_from_asset_browser: BoolProperty(default=False, options={'HIDDEN'})
    make_relative_path: BoolProperty(default=False)

    environment: EnumProperty(options={'HIDDEN'}, default='COMPLETE',
                              items=(('COMPLETE', "Complete", ""), ('DIFFUSE', "Diffuse", ""), ('LIGHT', "Light", "")))

    invoke_browser: BoolProperty(options={'HIDDEN'}, default=False)
    filepath: StringProperty(options={'HIDDEN'}, subtype='FILE_PATH')
    filter_glob: StringProperty(options={'HIDDEN'}, default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.hdr;*.exr;*.blend')
    hide_info_popup: BoolProperty(options={'HIDDEN'}, default=False)
    use_script: BoolProperty(options={'HIDDEN'}, default=False)

    _lost_files_from_exapack = None  # Keep track outside the class of the lost files from exapack

    @classmethod
    def description(cls, context, properties):
        desc = "Add or import a world background and assign it to the current scene. (Tips: Ctrl+Click or Shift+Click to invoke the file browser)"
        return desc

    def invoke(self, context, event):
        # With ctrl or shift click invoke the file browser, only on ADD option
        from ..utility.utility import set_object_mode
        set_object_mode(context.object)

        self.filepath = ""
        if self.invoke_browser or event.ctrl or event.shift:
            self.invoke_browser = True
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

        return self.execute(context)

    def execute(self, context):

        scn = context.scene
        scnProp = get_scnprop(scn)
        cat = scnProp.up_category
        preview = get_winman_main_preview()

        if bpy.app.version >= (4, 2, 0):
            scn.eevee.use_raytracing = True

        cls = self.__class__
        cls._lost_files_from_exapack = None  # Remember to reset this variable!!! è utilizzata durante la creazione dell'asset browser per tenere traccia dei file persi e da dove vengono

        replace_sun_driver = False

        def restore_volume():
            # Restore Volumetric node if present
            if volume and new_world and has_nodetree(new_world):
                from ..volumetric.volumetric_fc import MemorizeNodeGroup
                MemorizeNodeGroup.restore_node_group_from_memory(new_world.node_tree)

            if replace_sun_driver:
                from ..light_studio.sun_ops import sync_sun
                sync_sun(context, options="SYNC")

        if not self.is_from_asset_browser:
            set_object_mode(context.view_layer.objects.active)

        if not self.is_from_asset_browser and not self.invoke_browser:
            if scnProp.up_category == 'Empty Collection...':
                if self.hide_info_popup:
                    return {'CANCELLED'}
                text = "This category is empty"
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}

            if preview in ['Empty...', '']:
                if self.hide_info_popup:
                    return {'CANCELLED'}
                text = "This Background is empty"
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}

        if self.is_from_asset_browser:
            if len(context.selected_asset_files[:]) > 1:
                if self.hide_info_popup:
                    return {'CANCELLED'}

                text = "You have selected more than one asset. Please select only one asset"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}
            elif len(context.selected_asset_files[:]) == 0:
                if self.hide_info_popup:
                    return {'CANCELLED'}

                text = "You have not selected any asset. Please select one asset"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            # In this case, the operator is called from the asset browser!
            from ..asset_browser.asset_functions import get_asset_browser_world
            dictionary_file = get_asset_browser_world(self, context)
        elif self.use_script:
            dictionary_file = get_file_source(self.filepath)
        else:
            dictionary_file = get_file_source(self.filepath) if self.invoke_browser else get_file_source()

        if not dictionary_file:
            message = ""
            from ..library_manager.get_library_utils import current_lib
            folder_path = os.path.join(current_lib(), scnProp.up_category, get_winman_main_preview(), scnProp.k_size)
            from_exapack = get_volume_name_by_folder_name(current_lib(), folder_path)

            cls._lost_files_from_exapack = {"preview_name": get_winman_main_preview(),
                                            "category": scnProp.up_category,
                                            "k_size": scnProp.k_size,
                                            "exapack": from_exapack}

            if self.hide_info_popup:
                return {'CANCELLED'}
            # Qui dobbiamo anche dire all'utente in quale libreria exapack si trova il file

            if from_exapack:
                message = "The missing file is also part of the Exapack library: {} try to reinstall this exapack library".format(
                    from_exapack)
            text = "No valid file found in the selected library, the file may have been moved or deleted {}".format(
                message)

            self.report({'INFO'}, text)
            draw_info(text, "Info", 'INFO')

            return {'FINISHED'}

        # Memorize Volumetric node if present
        volume = None
        world = scn.world
        if world and has_nodetree(world):
            from ..volumetric.volumetric_fc import MemorizeNodeGroup
            nodes_dict = get_nodes_dict(world.node_tree)
            volume = nodes_dict.get('VOLUMETRIC')
            if volume:
                MemorizeNodeGroup.keep_node_group_in_memory(volume)

            # We need to check if the sun driver is present, and memorize it if present, at the end we will restore it
            from ..light_studio.sun_ops import get_sun_sinc_driver
            replace_sun_driver = get_sun_sinc_driver(world.node_tree)

        file_type = dictionary_file.get("file_type")
        filepath = dictionary_file.get("filepath")
        filename = dictionary_file.get("filename")

        dome_parts = find_current_dome_version(context)
        dome_ground = dome_parts.get("dome_ground")
        dome_sky = dome_parts.get("dome_sky")

        new_world = None
        if file_type == 'IMAGE':
            image = bpy.data.images.load(filepath)
            if self.make_relative_path:
                # Questo per ora serve solo se si sta creando un Asset per l'Asset Browser
                # Il percorso deve essere relativo alla stessa cartella da cui proviene l'immagine esempio:
                # /home/utente/immagine.jpg -> ../immagine.jpg
                image.filepath_raw = "//" + filename

            new_world = import_hdri_maker_world(context, rename=filename.split(".")[0].replace("_", " ").title(),
                                                reuse=True)
            assign_image_to_background_node(image, environment=self.environment)
            purge_all_group_names(new_world.node_tree)

            if dome_ground and dome_sky:
                A_Dome = AssembleDome(context, image=image, dome_name="DOME_" + new_world.name)
                A_Dome.asign_image_to_dome()

        elif file_type == 'BLENDER_FILE':
            new_world = load_libraries_world(path_to_world=filepath, world_index=0)
            if not new_world:
                if self.hide_info_popup:
                    return {'CANCELLED'}
                text = "Unable to load world from the file ( " + filename + " ) form this path: " + filepath + " Make sure the file.blend have a world in it"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if is_hdri_maker_studio_world(new_world):
                # In this case is a complete world made with hdri maker studio (3.x series), so can be loaded as is
                context.scene.world = new_world
                restore_volume()
                return {'FINISHED'}

            world_info_dict = analyse_blend_world_and_get_node_group(new_world, group_id_name=self.environment)
            # if world_info_dict contains a image, we have an old hdri maker world, and we need to get the image
            image = world_info_dict.get("image")
            if image:
                # If image from in the world, if probably is an old hdri maker world, so, remove the old world and create a new one
                # with the image grabbed from the old world
                bpy.data.worlds.remove(new_world)
                new_world = import_hdri_maker_world(context, rename=filename.split(".")[0].replace("_", " ").title())

                load_background_complete(node_tree=new_world.node_tree, image=image)

                if dome_ground and dome_sky:
                    A_Dome = AssembleDome(context, image=image, dome_name="DOME_" + new_world.name)
                    A_Dome.asign_image_to_dome()
                # load_background_diffuse_or_light(node_tree=new_world.node_tree, image=image, node_task=self.environment, action='ADD')
            else:
                # If image is not in the world, we have a different world, so, we need to convert it to a hdri maker world
                node_group = world_info_dict.get("node_group")

                if node_group:
                    # If node_group is in the world, or it's been created by the analyse_blend_world_and_get_node_group function,
                    # we have a complete world, so, we need to convert it to a hdri maker world
                    bpy.data.worlds.remove(new_world)
                    new_world = import_hdri_maker_world(context,
                                                        rename=filename.split(".")[0].replace("_", " ").title())
                    load_background_complete(node_tree=new_world.node_tree, node_group=node_group)
                    # load_background_diffuse_or_light(node_tree=world.node_tree, node_group=node_group,
                    #                                  node_task=self.environment,
                    #                                  action='ADD')

            if new_world:
                context.scene.world = new_world

        restore_volume()

        return {'FINISHED'}
