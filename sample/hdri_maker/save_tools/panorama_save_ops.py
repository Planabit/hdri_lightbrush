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
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from .render_tools import cycles_render_set_background_360, try_render
from .save_utility import create_batch_scene, render_background_preview
from ..background_tools.background_fc import import_hdri_maker_world, assign_image_to_background_node
from ..exaconv import get_objprop, get_scnprop, get_imgprop
from ..exaproduct import Exa
from ..library_manager.get_library_utils import current_lib, risorse_lib
from ..library_manager.main_pcoll import reload_main_previews_collection
from ..library_manager.main_pcoll_attributes import set_winman_main_preview
from ..library_manager.tools import create_material_folders
from ..utility.fc_utils import remove_scene_by_scene_id_name
from ..utility.utility import is_string_cointain_number, wima, \
    store_attributes, restore_attributes, asign_image_into_render_window, return_name_without_numeric_extension, \
    replace_forbidden_characters, get_image_from_render_window, screen_shading_type
from ..utility.utility_dependencies import create_panoramic_360_camera


def update_k_panorama_size_custom(self, context):
    if self.k_panorama_size_custom == '0':
        self.k_panorama_size_custom = '1'

    if not self.k_panorama_size_custom:
        self.k_panorama_size_custom = '1'

    if not is_string_cointain_number(self.k_panorama_size_custom, skip_dot=True):
        self.k_panorama_size_custom = '1'


def get_resolution(self):
    """Get the resolution of the image by k_panorama_size_custom or k_panorama_size"""
    if self.k_custom_size:
        resolution = (int(float(self.k_panorama_size_custom) * 1024), int(float(self.k_panorama_size_custom) * 512))
    else:
        resolution = (int(self.k_panorama_size) * 1024, int(self.k_panorama_size) * 512)

    return resolution


class HDRIMAKER_OT_PanoramaSave(Operator):
    bl_idname = Exa.ops_name + "panoramasave"
    bl_label = "Save Panorama"
    bl_description = "Save the current panorama as a new HDRI"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    # user_cycles_attributes and user_render_attributes are used to store the user scene properties and restore them at the end of the operator
    user_cycles_attributes = None
    user_render_attributes = None
    user_shading_type = None

    libraries_selector = None
    up_category = None
    mat_folders_dict = None
    _on_cancel = None
    _on_finish = None
    background_render_filepath = None
    user_scene = None
    filename_clean = ''

    filename: StringProperty()
    k_custom_size: BoolProperty(default=False)
    k_panorama_size: EnumProperty(default='4', items=(
        ('1', "1k", ""), ('2', "2k", ""), ('4', "4k", ""), ('8', "8k", ""), ('16', "16k", "")))
    k_panorama_size_custom: StringProperty(default="1", update=update_k_panorama_size_custom,
                                           description='The value is expanded in k, so it will automatically correct the aspect ratio. For example, 2 = 2048x1024')
    resolution = (0, 0)

    use_compiled_render_attributes: BoolProperty(
        default=True,
        description="If active, use the best parameters for the precompiled 360 render. If disabled, use the current scene parameters.")

    @staticmethod
    def fc_on_finish(none):
        HDRIMAKER_OT_PanoramaSave._on_finish = True
        bpy.app.handlers.render_complete.remove(HDRIMAKER_OT_PanoramaSave.fc_on_finish)

    @staticmethod
    def fc_on_cancel(none):
        HDRIMAKER_OT_PanoramaSave._on_cancel = True
        bpy.app.handlers.render_cancel.remove(HDRIMAKER_OT_PanoramaSave.fc_on_cancel)

    def invoke(self, context, event):
        scn = context.scene
        update_k_panorama_size_custom(self, context)

        image = get_image_from_render_window(context)
        if image and get_imgprop(image).image_id_name == 'RENDER_FINISHED':
            asign_image_into_render_window(context, None)

        # Important, reset the state of the variables, the modal must start with these variables set to False
        HDRIMAKER_OT_PanoramaSave._on_cancel = False
        HDRIMAKER_OT_PanoramaSave._on_finish = False
        HDRIMAKER_OT_PanoramaSave._timer = None
        # --------------------------------------------------------------------------------------------------------------

        # Store user scene properties into a dictionary to restore them later, if needed
        self.user_cycles_attributes = store_attributes(scn.cycles)
        self.user_render_attributes = store_attributes(scn.render)
        self.user_shading_type = screen_shading_type(get_set='GET')


        return wima().invoke_props_dialog(self, width=450)


    def draw(self, context):
        scn = context.scene
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        if self.filename == '':
            row.alert = True
            row.label(text="Please insert a name:")
        else:
            row.label(text="Background Name:")
        row.prop(self, 'filename', text="")

        col = box.column(align=True)
        if int(self.k_panorama_size_custom) > 16:
            col.alert = True
            col.label(text="WARNING: The value is high, pay attention to the render time!")

        col.separator()
        row = col.row(align=True)
        row.prop(self, 'k_custom_size', text="Custom Size")
        row.prop(self, 'use_compiled_render_attributes', text="Use HDRi Maker Render Attributes")
        col.separator()

        if self.k_custom_size:
            row = col.row()
            row.prop(self, 'k_panorama_size_custom', text='Size in K', expand=True)
            row = col.row()
            row.alignment = 'CENTER'
            row.label(
                text="( " + str(int(float(self.k_panorama_size_custom) * 1024)) + 'x' + str(int(
                    float(self.k_panorama_size_custom) * 512)) + " )")
        else:
            row = col.row()
            row.prop(self, 'k_panorama_size', text='Size in K', expand=True)
            row = col.row()
            row.alignment = 'CENTER'
            row.label(
                text="( " + str(int(float(self.k_panorama_size) * 1024)) + 'x' + str(
                    int(float(self.k_panorama_size) * 512)) + " )")

        col = box.column(align=True)
        # Settings the denoise:
        col.prop(scn.cycles, 'use_denoising', text='Use Denoising')
        if scn.cycles.use_denoising:
            col.prop(scn.cycles, "denoiser", text="Denoiser")
            col.prop(scn.cycles, "denoising_input_passes", text="Passes")
            if scn.cycles.denoiser == 'OPENIMAGEDENOISE':
                col.prop(scn.cycles, "denoising_prefilter", text="Prefilter")

        # Settings the render sampling
        col = box.column(align=True)
        col.prop(scn.cycles, "samples", text="Render Samples")

    def modal(self, context, event):
        if event.type == 'TIMER':
            cls = self.__class__
            if cls._on_finish:
                self.finish(context)

            elif cls._on_cancel:
                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Check if filename contains forbidden characters
        self.filename = replace_forbidden_characters(self.filename, replace_with='')

        # Check if filename contains only white spaces
        if self.filename.strip() == '':
            self.report({'WARNING'}, "The filename is empty")
            return {'CANCELLED'}

        self.user_scene = context.scene
        scnProp = get_scnprop(self.user_scene)
        # Search the 360 camera sphere object
        camera_sphere = next(
            (o for o in self.user_scene.objects if
             o.type == 'MESH' and get_objprop(o).object_id_name == '360_CAMERA_SPHERE'), None)

        # Create real camera at the camera_sphere location
        camera_render = create_panoramic_360_camera(self.user_scene, camera_sphere.location)

        libraries_selector = scnProp.libraries_selector
        self.up_category = scnProp.up_category

        cat_path = os.path.join(current_lib(), self.up_category)

        # Clean the filename from the .001 and .002 etc. Blender adds to the name
        self.filename_clean = return_name_without_numeric_extension(self.filename).replace('_', " ")

        self.mat_folders_dict = create_material_folders(cat_path, self.filename_clean,
                                                        mat_variant_folder_names=[self.filename_clean])

        variant_folder = self.mat_folders_dict["variant_paths"][0]

        # Start the 360 rendering:
        print("Start the 360 rendering...")


        if self.use_compiled_render_attributes:
            # Set render attributes standard and easy to render:
            cycles_render_set_background_360(self.user_scene)

        self.background_render_filepath = os.path.join(variant_folder, self.filename_clean + ".hdr")
        cls = self.__class__
        try_render(self.user_scene, self.background_render_filepath, 'HDR', get_resolution(self),
                   invoke='INVOKE_DEFAULT',
                   fc_on_finish=cls.fc_on_finish,
                   fc_on_cancel=cls.fc_on_cancel)

        # Since you have to wait for the render to finish, you have to start a timer that checks if the render
        # is finished, then the fc_on_finish function will be executed
        self._timer = wima().event_timer_add(1, window=context.window)
        wima().modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        # Save the render image as a HDR file 360 because in the modal function the render is done
        # save_render_image(self.background_render_filepath)
        # This function is called when the render is finished, unfortunately blender at the moment does not provide simpler API to check if the render is finished

        # Create the batch scene from function
        print("Create the batch scene from function...")
        batch_scene = create_batch_scene(context)

        # Add the new world background to the batch scene, using bpy.ops.hdrimaker.addbackground
        print("Add the new world background to the batch scene, using bpy.ops.hdrimaker.addbackground...")
        # bpy.ops.hdrimaker.addbackground(environment='COMPLETE')
        world = import_hdri_maker_world(context, rename=self.filename_clean)
        image = bpy.data.images.load(self.background_render_filepath)
        assign_image_to_background_node(image, environment='COMPLETE')

        # Render the preview from the batch scene
        print("Render the preview from the batch scene...")
        preview_filepath = os.path.join(self.mat_folders_dict['default'], self.filename_clean + ".png")

        render_background_preview(batch_scene,
                                  preview_filepath,
                                  lens=12, camera_loc=[0, 0, 0],
                                  camera_rotation=[0, 0, 0])

        bpy.data.worlds.remove(world)
        # Remove image because it is not needed anymore, and this occupies space in the memory
        bpy.data.images.remove(image)

        # save_render_image(preview_filepath)
        print("The render (Preview Background) is finished and the preview image is saved at the", preview_filepath)
        batchScnProp = get_scnprop(batch_scene)
        batchScnProp.libraries_selector = 'USER'
        batchScnProp.up_category = self.up_category

        # I reload the library to update the preview, otherwise it will not be available in the list of libraries
        reload_main_previews_collection()
        # I set the preview of the library just created in the preview interface
        set_winman_main_preview(self.filename_clean)

        # Delete the batch scene
        remove_scene_by_scene_id_name('BATCH_SCENE')
        print("The scene BATCH_SCENE is deleted")

        # Set the HDRi Maker library preview on the created background
        scnProp = get_scnprop(self.user_scene)
        scnProp.libraries_selector = 'USER'
        scnProp.up_category = self.up_category
        set_winman_main_preview(self.filename_clean)

        # This puts an image in the render window so that the user understands that the render is finished.
        image = next((i for i in bpy.data.images if get_imgprop(i).image_id_name == 'RENDER_FINISHED'), None)
        if not image:
            end_image_path = os.path.join(risorse_lib(), 'Files', 'RENDER_FINISHED.png')
            image = bpy.data.images.load(end_image_path)
            get_imgprop(image).image_id_name = 'RENDER_FINISHED'

        # Assign the Finish Text Image to the render window:
        asign_image_into_render_window(bpy.context, image)

        # Remove 360 camera from data objects
        camera_360 = next(
            (o for o in bpy.data.objects if o.type == 'CAMERA' and get_objprop(o).object_id_name == '360_CAMERA_REAL'),
            None)
        if camera_360:
            bpy.data.objects.remove(camera_360)

        # Restore user scene properties
        restore_attributes(self.user_scene.render, self.user_render_attributes)
        restore_attributes(self.user_scene.cycles, self.user_cycles_attributes)
        screen_shading_type(get_set='SET', shading_type=self.user_shading_type)
        print("The attributes of the user scene are restored")

        if self._timer:
            wima().event_timer_remove(self._timer)

    def cancel(self, context):
        restore_attributes(self.user_scene.render, self.user_render_attributes)
        restore_attributes(self.user_scene.cycles, self.user_cycles_attributes)
        screen_shading_type(get_set='SET', shading_type=self.user_shading_type)

        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
