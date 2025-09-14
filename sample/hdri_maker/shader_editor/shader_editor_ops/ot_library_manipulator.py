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
import datetime
import os

import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator

from ...exaconv import get_scnprop, get_sckprop
from ...exaproduct import Exa
from ...library_manager.get_library_utils import current_lib
from ...library_manager.main_pcoll_attributes import get_winman_main_preview
from ...utility.dictionaries import mat_info_example
from ...utility.json_functions import get_json_data, save_json
from ...utility.text_utils import draw_info
from ...utility.utility import wima


class HDRIMAKER_OT_LibraryManipulator(Operator):
    bl_idname = Exa.ops_name+"librarymanipulator"
    bl_label = "Library Manager"
    bl_options = {'INTERNAL', 'UNDO'}

    options: StringProperty()
    descriptions: StringProperty()
    yes_no: EnumProperty(default="NO", items=(('YES', "Yes", ""), ('NO', "No", "")))
    active_node: StringProperty()

    @classmethod
    def description(cls, context, properties):
        # The description work directly in the shader_editor_ops call
        # Is not a great job...
        return properties.descriptions

    def execute(self, context):

        preview_mat_name = get_winman_main_preview()
        scn = context.scene
        scnProp = get_scnprop(scn)

        if self.yes_no == 'NO':
            return {'FINISHED'}

        if not scnProp.permission:
            text = "Please insert a Permission name or key, It will be used to modify the data file, mark this Permission somewhere. You can also check it from the mat_info.json files. To edit these jsons, you will need to have the same key. "
            draw_info(text, "Info", 'INFO')
            return {'FINISHED'}
        if len(scnProp.permission) < 5:
            text = "Please enter a permission longer than 4 characters"
            draw_info(text, "Info", 'INFO')
            return {'FINISHED'}

        # Atenzione, bisogna controllare lo storage_method poichè potrebbero esserci dei conflitti tra
        # Materiali di tipo .blend, e materiali di tipo TEXTURE_IMAGES

        options = self.options

        if options in ['REPLACE_MATERIAL_INFO', 'REPLACE_GROUP_INPUT_PROPERTIES', 'REPLACE_MATERIAL_SETTINGS']:
            today = datetime.date.today()

            dir = lib_path = current_lib()  # if scnProp.libraries_selector == 'DEFAULT' else user_lib
            json_dir = os.path.join(dir, scnProp.up_category, preview_mat_name, "data", "mat_info.json")
            if not os.path.isfile(json_dir):
                text = "No json file to edit, create a new one with the button 'Create single mat_info.json"
                draw_info(text, "Info", 'INFO')
                return {'FINISHED'}

            json_data = get_json_data(json_dir)

            # Replace only material info:
            if options == 'REPLACE_MATERIAL_INFO':
                storage_info = json_data.get('storage_info')
                if not storage_info:
                    storage_info = json_data['storage_info'] = {}

                storage_info['permission'] = scnProp.permission
                storage_info['json_version'] = 1.0
                storage_info['blender_version'] = bpy.app.version
                storage_info[Exa.product + 'version'] = Exa.blender_manifest['version']

                material_info = json_data.get('material_info')
                if not material_info:
                    material_info = json_data['material_info'] = {}

                material_info["material_name"] = preview_mat_name
                material_info["author"] = scnProp.author
                material_info["website_name"] = scnProp.website_name
                material_info["website_url"] = scnProp.website_url
                material_info["license"] = scnProp.license
                material_info["license_description"] = scnProp.license_description
                material_info["license_link"] = scnProp.license_link

                json_data['storage_info'] = storage_info
                json_data['material_info'] = material_info
                json_data['date'] = str(today.strftime("%d/%m/%Y"))
                save_json(json_dir, json_data)

            # Replace only inpu properties
            if options == 'REPLACE_GROUP_INPUT_PROPERTIES':
                group_inputs_properties = json_data['group_inputs_properties'] = {}
                module_node = context.space_data.edit_tree.nodes.active
                module_data = module_node.node_tree
                # Le proprietà del nodo inputs, vanno settate solo per singolo materiale
                # Non si può farlo in batch (Per fortuna)
                for idx, input in enumerate(module_node.inputs):
                    sckProp = get_sckprop(module_data.inputs[idx])
                    if sckProp.store_property:
                        value = input.default_value
                        if isinstance(value, int) or isinstance(value, float):
                            value = value
                            group_inputs_properties[input.name] = value
                        else:
                            group_inputs_properties[input.name] = value[:]
                json_data['date'] = str(today.strftime("%d/%m/%Y"))
                save_json(json_dir, json_data)

            if options == 'REPLACE_MATERIAL_SETTINGS':
                material_properties = json_data['material_properties'] = {}
                material_properties['use_backface_culling'] = scnProp.use_backface_culling
                material_properties['blend_method'] = scnProp.blend_method
                material_properties['shadow_method'] = scnProp.shadow_method
                material_properties['alpha_threshold'] = scnProp.alpha_threshold
                material_properties['refraction_depth'] = scnProp.refraction_depth
                material_properties['use_screen_refraction'] = scnProp.use_screen_refraction
                material_properties['use_sss_translucency'] = scnProp.use_sss_translucency
                json_data['date'] = str(today.strftime("%d/%m/%Y"))

                json_data['material_properties'] = material_properties
                save_json(json_dir, json_data)

            return {'FINISHED'}

        if options in ['CREATE_BATCH_JSON', 'CREATE_SINGLE_JSON', 'CREATE_BATCH_JSON_CURRENT_CAT']:
            write = False

            lib_path = current_lib()

            mat_info_dict = mat_info_example().copy()

            storage_info = mat_info_dict['storage_info']
            for key, value in storage_info.items():
                if hasattr(scnProp, key):
                    storage_info[key] = getattr(scnProp, key)

            today = datetime.date.today()
            storage_info['date'] = str(today.strftime("%d/%m/%Y"))

            # Qui è un bel casino, in quanto le API sono cambiate in Blender 4.2 quindi quelle memorizzate nel dizionario
            # Seguono le vecchie API,
            material_info = mat_info_dict['material_info']
            for key, value in material_info.items():
                if hasattr(scnProp, key):
                    material_info[key] = getattr(scnProp, key)

            if scnProp.storage_method in ['TEXTURE_IMAGES', 'ENVIRONMENT_IMAGE']:
                material_properties = mat_info_dict['material_properties']
                for key, value in material_properties.items():
                    if hasattr(scnProp, key):
                        material_properties[key] = getattr(scnProp, key)

            # 1
            if options == 'CREATE_SINGLE_JSON':
                if scnProp.up_category in ['Tools']:
                    return {'FINISHED'}

                if self.active_node:
                    module_node = context.space_data.edit_tree.nodes.active
                    module_data = module_node.node_tree
                    # Le proprietà del nodo inputs, vanno settate solo per singolo materiale
                    # Non si può farlo in batch (Per fortuna)
                    group_inputs_properties = mat_info_dict['group_inputs_properties']
                    for idx, input in enumerate(module_node.inputs):
                        sckProp = get_sckprop(module_data.inputs[idx])
                        if sckProp.store_property:
                            value = input.default_value
                            if isinstance(value, int) or isinstance(value, float):
                                value = value
                                group_inputs_properties[input.name] = value
                            else:
                                group_inputs_properties[input.name] = value[:]

                    data_folder_path = os.path.join(lib_path, scnProp.up_category, preview_mat_name, 'data')
                    if not os.path.isdir(data_folder_path):
                        os.mkdir(data_folder_path)

                    json_path = os.path.join(data_folder_path, 'mat_info.json')
                    if not os.path.isfile(json_path):
                        write = True

                    else:
                        existent_json = get_json_data(json_path)
                        exist_storage_info = existent_json.get('storage_info')
                        if exist_storage_info:
                            exist_permission = exist_storage_info.get('permission')
                            if exist_permission:
                                if exist_permission in [storage_info['permission'], ""]:
                                    write = True
                                else:
                                    text = "Attention, the permission to edit this mat_info.json file is: '" + exist_permission + "' You are using: '" + \
                                           storage_info[
                                               'permission'] + "' as permission, If not you, we advise you not to modify these files! You could ruin the entire library!"
                                    draw_info(text, "Info", 'INFO')
                    if write:
                        save_json(json_path, mat_info_dict)
                        module_data['exa_mat_info'] = {}
                        module_data['exa_mat_info'].update(mat_info_dict)

            # 2
            if options in ['CREATE_BATCH_JSON', 'CREATE_BATCH_JSON_CURRENT_CAT']:

                idx = 0
                for library in os.listdir(lib_path):
                    if library.startswith("."):
                        continue
                    if options == 'CREATE_BATCH_JSON_CURRENT_CAT' and library != scnProp.up_category:
                        continue

                    library_path = os.path.join(lib_path, library)
                    if os.path.isdir(library_path):
                        previews = []
                        folders = []

                        for mat_file in os.listdir(library_path):
                            if mat_file.startswith("."):
                                continue
                            mat_file_path = os.path.join(library_path, mat_file)
                            if os.path.isdir(mat_file_path):
                                data_folder_path = os.path.join(library_path, mat_file, "data")
                                # if not os.path.isdir(os.path.join(data_folder_path, "previews", "default")):
                                #     continue
                                if not os.path.isdir(data_folder_path):
                                    continue

                                json_path = os.path.join(data_folder_path, 'mat_info.json')


                                if not os.path.isfile(json_path):
                                    material_info = mat_info_dict.get('material_info')
                                    if material_info:
                                        material_info['material_name'] = mat_file
                                        mat_info_dict['material_info'] = material_info

                                    save_json(json_path, mat_info_dict)
                                else:
                                    existent_json = get_json_data(json_path)
                                    exist_storage_info = existent_json.get('storage_info')
                                    if exist_storage_info:
                                        storage_method = exist_storage_info.get('storage_method')
                                        exist_permission = exist_storage_info.get('permission')
                                        exist_storage_method = exist_storage_info.get('storage_method')
                                        if exist_permission:
                                            if exist_permission in [storage_info['permission'], ""]:
                                                if exist_storage_method in [storage_info['storage_method'], ""]:
                                                    material_info = existent_json.get('material_info')
                                                    if material_info:
                                                        material_info['material_name'] = mat_file
                                                        existent_json['material_info'] = material_info
                                                    save_json(json_path, mat_info_dict)
                                                    idx += 1

        return {'FINISHED'}

    def invoke(self, context, event):
        self.yes_no = 'NO'
        return wima().invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Are you sure to: " + self.descriptions + " ?")
        row = col.row()
        row.scale_y = 1.5
        row.prop(self, 'yes_no', expand=True)


