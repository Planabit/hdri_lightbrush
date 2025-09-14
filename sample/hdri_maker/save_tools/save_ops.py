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
import shutil

import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

from .save_fcs import write_some_data
from ..bpy_data_libraries_load.data_lib_loads import load_libraries_object
from ..exaconv import get_objprop, get_scnprop
from ..exaproduct import Exa
from ..library_manager.categories_enum import enum_up_category
from ..library_manager.get_library_utils import risorse_lib, current_lib
from ..library_manager.main_pcoll_attributes import get_winman_main_preview
from ..utility.fc_utils import remove_scene_by_scene_id_name
from ..utility.text_utils import draw_info
from ..utility.utility import get_addon_preferences, center_view, replace_forbidden_characters, has_nodetree, \
    retrieve_nodes, is_subfolder_and_files_in_use, image_has_data


class HDRIMAKER_OT_AddPanoramaCamera(Operator):
    """Import 360 camera"""

    bl_idname = Exa.ops_name + "addcamerasphere"
    bl_label = "Add panorama sphere"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        # sphere 360 filepath:
        blender_filepath = os.path.join(risorse_lib(), 'blendfiles', 'objects', 'HDRi_Maker_Cam360.blend')

        # Load the blend file with the function:
        camera_360 = load_libraries_object(blender_filepath, 'HDRi_Maker_Cam360', 'HDRi_Maker_Cam360')
        objProp = get_objprop(camera_360)
        # 360_CAMERA_SPHERE is the object_id_name of the 360 camera sphere, is the object, not the real camera
        objProp.object_id_name = '360_CAMERA_SPHERE'

        # Set the camera on blender 3D Cursor location:
        camera_360.location = scn.cursor.location

        # Deselect all objects in the scene
        for ob in context.scene.objects:
            ob.select_set(state=False)

        # Link camera to current scene
        scn.collection.objects.link(camera_360)

        # Make the camera active and select it
        context.view_layer.objects.active = camera_360
        camera_360.select_set(state=True)
        camera_360.hide_render = True

        return {'FINISHED'}


class HDRIMAKER_OT_FileToCat(Operator):
    """Transfer the selected material from the left to the right category"""

    bl_idname = Exa.ops_name + "tocat"
    bl_label = "Move to category"
    bl_options = {'INTERNAL'}

    to_category: EnumProperty(items=enum_up_category)
    confirm: EnumProperty(default='NO', items=(('YES', 'Yes', 'Yes'), ('NO', 'No', 'No')), name='Confirm',
                          description='Confirm the operation')

    @classmethod
    def description(cls, context, properties):
        return "Move current background to another category"

    def draw(self, context):
        preview_mat_name = get_winman_main_preview()
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Move current background {}".format(preview_mat_name))
        col.separator()
        col.prop(self, 'to_category', text='To category')
        col.separator()
        row = col.row(align=True)
        row.prop(self, 'confirm', text='Confirm', expand=True)
        col.separator()

    def invoke(self, context, event):
        self.confirm = 'NO'
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        if self.confirm == 'NO':
            return {'CANCELLED'}

        # Check if the category folder exists:
        dir_path = os.path.join(current_lib(), self.to_category)
        if not os.path.isdir(dir_path):
            text = "The category {} does not exist".format(self.to_category)
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        # Check if the material folder already exists into the self.to_category folder:
        preview_mat_name = get_winman_main_preview()
        dir_path = os.path.join(current_lib(), self.to_category, preview_mat_name)
        if os.path.isdir(dir_path):
            text = "The background {} already exists into the category {} so it will not be moved".format(
                preview_mat_name, self.to_category)
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        # Move the material folder to the self.to_category folder:
        scnProp = get_scnprop(context.scene)
        old_dir_path = os.path.join(current_lib(), scnProp.up_category, preview_mat_name)
        # Try to move:
        try:
            shutil.move(old_dir_path, dir_path)
        except Exception as e:
            text = "Error moving the background {} to the category {}: {}".format(preview_mat_name, self.to_category, e)
            draw_info(text, "Error", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}

        # Reload the preview collection:
        from ..library_manager.main_pcoll import reload_main_previews_collection
        reload_main_previews_collection()

        return {'FINISHED'}


class HDRIMAKER_OT_RenameLibTool(Operator):
    bl_idname = Exa.ops_name + "rename_lib_tool"
    bl_label = "Rename"
    bl_options = {'INTERNAL', 'UNDO'}

    confirm: EnumProperty(default='NO', items=(('NO', 'NO', 'NO'), ('YES', 'YES', 'YES')))
    options: EnumProperty(default='MATERIAL',
                          items=(('MATERIAL', 'Material', 'Material'), ('CATEGORY', 'Category', 'Category')))
    new_name: StringProperty(name="New name", default="")

    @classmethod
    def description(cls, context, properties):
        if properties.options == 'MATERIAL':
            return "Rename the current material"
        elif properties.options == 'CATEGORY':
            return "Rename the current category"

    def invoke(self, context, event):
        from ..library_manager.main_pcoll_attributes import get_winman_main_preview
        up_category = get_scnprop(context.scene).up_category
        preview_mat_name = get_winman_main_preview()

        self.confirm = 'NO'
        self.new_name = ''

        if preview_mat_name == 'Empty...' and self.options == 'MATERIAL':
            text = "No material present in this category, impossible to rename because it does not exist"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'CANCELLED'}
        if up_category == 'Empty Collection...':
            text = "No category present, impossible to rename because it does not exist"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'FINISHED'}

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        up_category = get_scnprop(context.scene).up_category

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        if self.options == 'MATERIAL':
            from ..library_manager.main_pcoll_attributes import get_winman_main_preview
            preview_mat_name = get_winman_main_preview()
            row.label(text="Rename background name, From:")
            row.label(text=preview_mat_name)
        elif self.options == 'CATEGORY':
            row.label(text="Rename category name, From:")
            row.label(text=up_category)

        col.separator()
        row = col.row(align=True)
        row.alignment = 'CENTER'
        col.prop(self, 'new_name', text="To new name")
        col.separator()

        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.scale_y = 1.5
        row.prop(self, 'confirm', expand=True)

        col.separator()
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Press ESC or 'No' and 'OK' button to cancel")

        col.separator()

    def execute(self, context):

        if self.confirm == 'NO':
            return {'FINISHED'}

        scn = context.scene
        scnProp = get_scnprop(scn)
        addon_preferences = get_addon_preferences()

        from ..library_manager.main_pcoll_attributes import get_winman_main_preview

        self.new_name = replace_forbidden_characters(self.new_name)

        if self.new_name == '':
            text = "Impossible to rename, the new name is empty (or contains only forbidden characters)"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)
            return {'FINISHED'}

        category_folder = os.path.join(addon_preferences.addon_user_library, scnProp.up_category)
        preview_mat_name = get_winman_main_preview()
        current_mat_path = os.path.join(current_lib(), scnProp.up_category, preview_mat_name)

        if scnProp.up_category == 'Empty Collection...':
            return {'FINISHED'}

        if self.options == 'MATERIAL':
            if preview_mat_name == 'Empty...':
                return {'FINISHED'}

            new_mat_path = os.path.join(current_lib(), scnProp.up_category, self.new_name)
            # Check if the new_mat_path already exists:
            if os.path.exists(new_mat_path):
                text = "Impossible to rename, the new name already exists in this category"
                draw_info(text, "Info", 'INFO')
                self.report({'INFO'}, text)
                return {'CANCELLED'}

            is_in_use = is_subfolder_and_files_in_use(current_mat_path)

            if is_in_use:
                text = "Impossible to rename, some files or folders are open or in use on your computer, check well, close the windows and try again"
                draw_info(text, "Info", 'INFO')
                self.report({'INFO'}, text)
                return {'CANCELLED'}

            # In questo caso iteriamo a tutti i file e cartelle contenute nella cartella preview_mat_name e rimpiazziamo
            # il nome del file (Se presente nel filename o nel foldername) con il nuovo nome
            for root, dirs, files in os.walk(current_mat_path):
                for dn in dirs:
                    if preview_mat_name in dn:
                        # Dobbiamo solo rimpiazzare la sottostringa se presente nel foldername
                        new_dn = dn.replace(preview_mat_name, self.new_name)
                        try:
                            os.rename(os.path.join(root, dn), os.path.join(root, new_dn))
                        except OSError as e:
                            return {'CANCELLED'}

                for fn in files:
                    if fn.endswith(".json"):
                        continue
                    # Controlliamo se il nome del materiale con gli underscore è presente nel filename
                    lower_material_name = preview_mat_name.lower().replace(' ', '_')
                    if lower_material_name in fn:
                        # Dobbiamo solo rimpiazzare la sottostringa se presente nel filename
                        new_fn = fn.replace(lower_material_name, self.new_name.lower().replace(' ', '_'))
                        try:
                            print("Trying to rename: ", os.path.join(root, fn), " to: ", os.path.join(root, new_fn))
                            os.rename(os.path.join(root, fn), os.path.join(root, new_fn))
                        except OSError as e:
                            text = "Impossible to rename the file: {}".format(e)
                            self.report({'ERROR'}, text)
                            continue

            # Otteniamo l'eventuale file json "mat_info.json" se esiste nel percorso current_mat_path/data/mat_info.json
            # Lo apriamo e controlliamo se esiste la chiave "material_info" con la relativa chiave "material_name"
            # e rimpiazziamo il nome del materiale con il nuovo nome
            mat_info_path = os.path.join(current_mat_path, 'data', 'mat_info.json')

            if os.path.exists(mat_info_path):
                from ..utility.json_functions import get_json_data

                json_data = get_json_data(mat_info_path)
                if json_data:
                    material_info = json_data.get('material_info')
                    if material_info:
                        material_name = material_info.get('material_name')
                        if material_name:
                            material_info['material_name'] = self.new_name
                            from ..utility.json_functions import save_json
                            save_json(mat_info_path, json_data)

            # Rename the current_mat_path:
            os.rename(current_mat_path, new_mat_path)

            from ..library_manager.main_pcoll import reload_main_previews_collection
            reload_main_previews_collection()

            # Try to set the preview to the new material:
            from ..library_manager.main_pcoll_attributes import set_winman_main_preview
            set_winman_main_preview(self.new_name)

            text = "The replacement of the material name was successful"
            draw_info(text, "Info", 'INFO')
            self.report({'INFO'}, text)

        elif self.options == 'CATEGORY':
            # In questo caso dobbiamo solo cambiare il nome della cartella che sarebbe la up_category
            # e rimpiazzare il nome della cartella con il nuovo nome

            # Se il nome è lo stesso della cartella principale non ci preoccupiamo di nulla perchè potrebbe voler aggiustare le maiuscole
            # O minuscole, quindi non facciamo il controllo se il nome esiste già nella directory
            if scnProp.up_category.lower() != self.new_name.lower():
                # Controlliamo se esiste la cartella con il nuovo nome:
                if os.path.exists(os.path.join(current_lib(), self.new_name)):
                    text = "The category {} already exists".format(self.new_name)
                    draw_info(text, "Info", 'INFO')
                    self.report({'INFO'}, text)
                    return {'FINISHED'}

            try:
                os.rename(category_folder, os.path.join(addon_preferences.addon_user_library, self.new_name))
                from ..library_manager.categories_enum import update_first_cat
                update_first_cat(scnProp, context)
                scnProp.up_category = self.new_name

            except OSError as e:
                text = "From the category rename operation an error occurred: {}".format(e)
                text += "The folder of the category {} is probably open in another program or into the explorer".format(
                    scnProp.up_category)
                draw_info(text, "Error", 'ERROR')
                self.report({'ERROR'}, text)
                return {'FINISHED'}

        return {'FINISHED'}


class HDRIMAKER_OT_ExportHdr(Operator, ExportHelper):
    """Note: the image file exporter only works if the image has been assigned to the background, via HDRi Maker"""

    bl_idname = Exa.ops_name + "exporthdr"
    bl_label = "Export"
    bl_options = {'INTERNAL'}

    filename_ext = ".hdr"
    filter_glob: StringProperty(
        default="*.hdr;*.png;*.hdr;*.jpg;*.jpeg;*.bmp;*.exr;",
        options={'HIDDEN'},
        maxlen=255,
    )

    image_extension = [".hdr", ".png", ".jpg", ".jpeg", ".bmp", ".exr"]
    directory: StringProperty(options={'HIDDEN'})

    # Folderpath:

    @classmethod
    def description(cls, context, properties):
        return "Export the world background image if exists"

    def execute(self, context):

        if self.directory == '':
            text = "Please select a valid path to export and save the image"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        if not os.path.exists(self.directory):
            text = "The selected path {} does not exist, please retry with a valid path".format(self.directory)
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        scn = context.scene
        world = scn.world
        if not world:
            text = "No world found, so no image(s) exists to export"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        if not has_nodetree(world):
            text = "No node tree found, so no image(s) exists to export"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        node_list = retrieve_nodes(world.node_tree)

        first_images = [n.image for n in node_list if n.type == 'TEX_ENVIRONMENT' if n.image]
        second_images = list(set(first_images))
        if not second_images:
            text = "No image(s) {} found into the current world node tree, so no image(s) exists to export. " \
                   "Make sure the world is not completely procedural. In case you want to export it as an image," \
                   "you must use the 'Panorama 360°' type of saving"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        images = [i for i in second_images if image_has_data(i)]

        if not images:
            text = "Sorry, but the image(s) has not data, so it cannot be exported. Images with data are: {}".format(
                second_images)
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        # Get blender project name if it is saved:
        if bpy.data.filepath:
            project_name = os.path.basename(bpy.data.filepath)
            # Remove the extension:
            project_name = os.path.splitext(project_name)[0]
        else:
            project_name = "HDRi Maker Images from unsaved project"

        save_path = os.path.join(self.directory, project_name)
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

        for img in images:
            filepath = os.path.join(save_path, img.name)
            if not filepath.endswith(tuple(self.image_extension)):
                filepath += ".hdr"

            write_some_data(filepath, img)

            text = "The image {} was exported successfully at the path {}".format(img.name, filepath)
            self.report({'INFO'}, text)

        text = "The following images have been exported successfully: {}".format(", ".join([i.name for i in images]))
        draw_info(text, "Info", 'INFO')
        self.report({'INFO'}, text)

        # Try to open the folder where the images are saved:
        from ..utility.utility_dependencies import open_folder
        open_folder(save_path)

        return {'FINISHED'}


class HDRIMAKER_OT_ResnapCamera(Operator):
    """Put camera on 3D Cursor"""

    bl_idname = Exa.ops_name + "putcamera"
    bl_label = "Re-snap Camera"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):

        for o in context.scene.objects:
            objProp = get_objprop(o)
            if objProp.object_id_name == '360_CAMERA_SPHERE':
                o.location = context.scene.cursor.location

        return {'FINISHED'}


class HDRIMAKER_OT_CenterView(Operator):
    bl_idname = Exa.ops_name + "centerview"
    bl_label = "Center View"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(default='CENTER_VIEW',
                          items=(('CENTER_VIEW', "Center View", ""), ('FIND_BALL_CAMERA', "Find Ball Camera", "")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'CENTER_VIEW':
            desc = "Center View in Dome"
        elif properties.options == 'FIND_BALL_CAMERA':
            desc = "Find 360 Ball Camera"
        return desc

    def execute(self, context):
        scn = context.scene
        if self.options == 'CENTER_VIEW':
            dome_handler = next((o for o in scn.objects if o.hdri_prop_obj.object_id_name == 'DOME_HANDLER'), None)
            if not dome_handler:
                return {'CANCELLED'}

            objProp = get_objprop(dome_handler)

            scale = objProp.scale_dome_handler
            position = scale * 2

            loc_x = dome_handler.location.x
            loc_y = dome_handler.location.y
            loc_z = dome_handler.location.z + position

            center_view(view_location=(loc_x, loc_y, loc_z), view_distance=position)
            return {'FINISHED'}

        elif self.options == 'FIND_BALL_CAMERA':
            camSphere = next((ob for ob in scn.objects if ob.hdri_prop_obj.object_id_name == '360_CAMERA_SPHERE'), None)
            if not camSphere:
                text = "No camera 360 in this scene, Add 360 cam and try again"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            x, y, z = camSphere.location
            center_view(view_location=(x, y, z))

        return {'FINISHED'}


class HDRIMAKER_OT_AddCategory(Operator):
    """Add New category to save your background"""

    bl_idname = Exa.ops_name + "addbackgroundcategory"
    bl_label = "Add category"
    bl_options = {'INTERNAL'}

    add_category: StringProperty(name="Category Name", default="")
    confirm: EnumProperty(default='NO', items=(('YES', "Yes", ""), ('NO', "No", "")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.add_category:
            desc = "Add new category"
        return desc

    def invoke(self, context, event):
        self.add_category = ""
        self.confirm = 'NO'
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Add new category")
        col.separator()
        col.prop(self, "add_category", text="Category Name")
        col.separator()
        row = col.row(align=True)
        row.prop(self, "confirm", text="Are you sure?", expand=True)
        col.separator()
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="After your choice, press 'Ok' to confirm, or Esc, to cancel.")

    def execute(self, context):
        if self.confirm == 'NO':
            return {'CANCELLED'}

        scn = context.scene
        scnProp = get_scnprop(scn)

        self.add_category = replace_forbidden_characters(self.add_category)

        addon_preferences = get_addon_preferences()

        savelib = addon_preferences.addon_user_library
        dirName = os.path.join(savelib, self.add_category)

        if self.add_category == '' or 'Empty Collection...' in self.add_category:
            def draw(self, context):
                self.layout.label(text="Attention, enter a valid name!")

            bpy.context.window_manager.popup_menu(draw, title="Name error")
            return {'FINISHED'}

        # controllo maiuscole minuscole se c'è la categoria
        for file in os.listdir(savelib):
            if not file.startswith("."):
                if file.casefold() == self.add_category.casefold():
                    if not os.path.isfile(file):
                        scnProp.libraries_selector = 'USER'
                        scnProp.up_category = file

                        def draw(self, context):
                            self.layout.label(text="Attention, this category already exists, try with another name")

                        bpy.context.window_manager.popup_menu(draw, title="Name error")
                        return {'FINISHED'}

        if not os.path.exists(dirName):
            os.mkdir(dirName)

        scnProp.libraries_selector = 'USER'
        scnProp.up_category = self.add_category

        return {'FINISHED'}


class HDRIMAKER_OT_ConvertToAbsolutePath(Operator):
    """Fix"""

    bl_idname = Exa.ops_name + "absolutepath"
    bl_label = "Fix"
    bl_options = {'INTERNAL'}

    def execute(self, context):

        addon_prefs = get_addon_preferences()
        addon_prefs.addon_default_library = bpy.path.abspath(addon_prefs.addon_default_library)
        addon_prefs.addon_user_library = bpy.path.abspath(addon_prefs.addon_user_library)

        if len(addon_prefs.addon_default_library) > 1:

            if addon_prefs.addon_default_library[-1] != os.sep:
                addon_prefs.addon_default_library = addon_prefs.addon_default_library + os.sep

        if len(addon_prefs.addon_user_library) > 1:
            if addon_prefs.addon_user_library[-1] != os.sep:
                addon_prefs.addon_user_library = addon_prefs.addon_user_library + os.sep

        bpy.ops.wm.save_userpref()
        return {'FINISHED'}


# Remove scene operator
class HDRIMAKER_OT_RemoveScene(Operator):
    """Remove Scene"""

    bl_idname = Exa.ops_name + "removescene"
    bl_label = "Remove Scene"
    bl_options = {'INTERNAL'}

    scene_id_name: StringProperty()

    def execute(self, context):
        remove_scene_by_scene_id_name(self.scene_id_name)
        return {'FINISHED'}
