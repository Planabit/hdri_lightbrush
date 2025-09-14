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
from bpy.props import EnumProperty, FloatProperty, FloatVectorProperty, BoolProperty, StringProperty, IntProperty
from bpy.types import PropertyGroup

from .scene_callback import updatebackground, update_shadow_preferences, update_fog_details, \
    enum_node_utility, update_hooks_display_size, update_empty_type, hide_unide_dome, \
    update_hide_hooks, update_dome_wireframe, update_materials_colorspace, update_volumetric_preferences
from ...dome_tools.dome_fc import DomeUtil
from ...library_manager.categories_enum import enum_up_category, update_first_cat
from ...library_manager.k_size_enum import update_k_size, enum_k_size
from ...library_manager.libraries_enum import enum_libraries_selector
from ...library_manager.main_pcoll import update_tag_search, update_first_icon
from ...light_studio.light_studio_fc import update_lights_studio_count
from ...utility.enum_blender_native import enum_empty_types, enum_light_type, enum_blender_colorspace
from ...volumetric.volumetric_fc import enum_volumetric_groups


class HdriMakerSceneProperty(PropertyGroup):
    menu_environment: BoolProperty(default=False, description='Background options')
    # menu_icon_theme: EnumProperty(default='BLUE', update=iconsSwitch,
    #                               items=(('BLUE', "Blue", ""), ('PINK', "Pink", "")))

    auto_add: BoolProperty(default=False,
                           description='If this button is on, the backgrounds of the scene will change automatically as the preview changes only by the arrows use')
    last_preview: StringProperty()

    save_menu: BoolProperty(default=False, description='This menu is dedicated to saving backgrounds')
    save_type: EnumProperty(default='CURRENT', items=(('CURRENT', "Current Background", 'Save the current background'),
                                                      ('PANORAMA', "Panorama 360",
                                                       "Create a 360 degree panoramic photo from current scene"),
                                                      ('BATCH', "Batch from folder",
                                                       "Multiple batch, save all the backgrounds contained in a directory")))

    scene_id_name: StringProperty()

    render_sample: IntProperty(default=512, min=32, max=2048,
                               description='Render resolution, attention, a large number means better quality, but more time')

    safety_delete: BoolProperty(default=False, description='Safety delete category')

    compute_processor: EnumProperty(default='GPU', items=(('GPU', "Gpu", ""), ('CPU', "Cpu", "")))
    collection_management: BoolProperty(default=False)
    
    shadow_detail: EnumProperty(update=update_shadow_preferences,
                                default='DEFAULT',
                                description="This preset facilitates the Blender settings, to make the shadows more or "
                                            "less realistic according to the power of the hardware in use.",
                                items=(('VERY_LOW', "Very Low", ""),
                                       ('LOW', "Low", ""),
                                       ('DEFAULT', "Default", ""),
                                       ('HIGH', "High", ""),
                                       ('VERY_HIGH', "Very High", ""),
                                       ('ULTRA', "Ultra", ""),
                                       ))

    volumetric_detail: EnumProperty(update=update_volumetric_preferences,
                                    default='DEFAULT',
                                    description="This preset facilitates the Blender settings, to make the volumetric "
                                                "more or less realistic according to the power of the hardware in use.",
                                    items=(('VERY_LOW', "Very Low", ""),
                                           ('LOW', "Low", ""),
                                           ('DEFAULT', "Default", ""),
                                           ('HIGH', "High", ""),
                                           ('VERY_HIGH', "Very High", ""),
                                           ('ULTRA', "Ultra", ""),
                                           ))

    blurry_value: FloatProperty(default=0, min=0, max=0.5, update=updatebackground,
                                description='Adjust the blurry intensity')
    colorize_mix: FloatProperty(default=0, min=0, max=1, update=updatebackground,
                                description='Adjust the colorize intensity')
    colorize: FloatVectorProperty(name="", subtype='COLOR', default=(0, 0, 0, 1), min=0.0, max=1.0, size=4,
                                  description='Colorize background', update=updatebackground)

    hdri_projected_menu: BoolProperty(default=False)

    fog_detail: EnumProperty(update=update_fog_details, default='4_32_8', items=(('16_8_2', "Very low", ""),
                                                                                 ('8_16_4', "Low", ""),
                                                                                 ('4_32_8', "Default", ""),
                                                                                 ('2_32_32', "High", ""),
                                                                                 ('2_64_64', "Very high", ""),
                                                                                 ('2_128_128', "Best", "")))

    # V3:

    self_tag: BoolProperty(default=False)

    dome_types: EnumProperty(items=DomeUtil.enum_domes)

    up_category: EnumProperty(items=enum_up_category,
                              update=update_first_icon,
                              description="This is the category of the library you are currently using")

    libraries_selector: EnumProperty(update=update_first_cat,
                                     items=enum_libraries_selector,
                                     description="This is the list of all the libraries")

    temp_tag: StringProperty()
    tag_search: StringProperty(update=update_tag_search,
                               description="Enter the tags you want to search for, keep the tags separated by a space")
    tag_exclusion: StringProperty(update=update_tag_search,
                                  description="Enter the tags you want to exclude, keep the tags separated by a space")
    menu_tag_search: BoolProperty(default=False, update=update_tag_search,
                                  description="Show tag search box, keep search box open if you are using a search. Close the search box and you will return to view all materials.")

    edit_tag: BoolProperty(default=False, description="Shows the tools for editing the tags of this material")

    k_size: EnumProperty(items=enum_k_size,
                         update=update_k_size)

    node_margin: IntProperty(default=50, min=0, description="Space between one node and another")

    # /‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾
    # Mat_info
    permission: StringProperty(
        description="This is a kind of Password, it allows you to put any string, to make it difficult for a user to modify these json files. For example, the Extreme PBR library has Permission: Andrew_D, if you use Andrew_D, you will be able to edit the data_info.json files (Practice that should not be done). So use your name, or something similar. So users won't modify your mat_info.json")  # Andrew_D for full privilege
    author: StringProperty()
    license: StringProperty()
    license_link: StringProperty()
    license_description: StringProperty()
    website_url: StringProperty()
    website_name: StringProperty()
    #
    # /‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾

    saveNgpath: StringProperty(subtype='DIR_PATH')
    node_utils_list: EnumProperty(items=enum_node_utility)
    storage_method: EnumProperty(default='TEXTURE_IMAGES',
                                 items=([(i, i, "") for i in ['TEXTURE_IMAGES', 'ENVIRONMENT_IMAGE', 'SAVE_MODULE', 'SAVE_MATERIAL']]))

    hooks_display_size: FloatProperty(default=1.0, min=0.1, description="Adjust the size of the Hooks",
                                      update=update_hooks_display_size)

    hooks_display_type: EnumProperty(items=enum_empty_types, update=update_empty_type)
    hide_dome: BoolProperty(description="Hide the Dome", update=hide_unide_dome)
    hide_hooks: BoolProperty(description="Hide Hooks", update=update_hide_hooks)

    show_dome_wireframe: BoolProperty(default=False, description="Show Dome Wireframe", update=update_dome_wireframe)

    show_hooks_menu: BoolProperty(default=False, description="Show Hooks Menu")
    show_wrap_menu: BoolProperty(default=False, description="Show Wrap Menu")
    show_dome_menu: BoolProperty(default=False, description="Show Dome Menu")
    show_ground_menu: BoolProperty(default=False, description="Show Ground Menu")

    # ------------------------------------------------------------------------------------------------------------------
    # Zip Maker (exapack)
    exapack_prefix_name: StringProperty(default="HDRMkr", description="Prefix name for the zip file")
    exapack_preindex: EnumProperty(default='000',
                                   items=(('00', "01", ""), ('000', "001", ""), ('000', "0001", "")),
                                   description="Suffix number for the zip file")

    exapack_pause: BoolProperty(default=False, description="Pause the process zipping process")
    exapack_terminate: BoolProperty(default=False,
                                    description="Terminate the process zipping process (Waiting for finish the current files)")

    exapack_ignore_material_version: BoolProperty(default=False, description="Ignore the material version, (Make the library without 1k, 2k, 4k, etc)")

    import multiprocessing
    exapack_cores: IntProperty(default=1, min=1, max=multiprocessing.cpu_count(),
                               description="Number of cores to use in the process zipping process")

    exapack_library_type: EnumProperty(default='default_library',
                                       items=(('default_library', "default_library", ""), ('expansion_library', "expansion_library", "")),
                                       description="Type of library to create, depending on the type of library, the process of the installation will be different")

    exapack_library_name: StringProperty(default="", description="Name of the library")

    # ------------------------------------------------------------------------------------------------------------------
    # Light Studio
    light_studio_count: IntProperty(default=4, min=1, max=32, description="Number of lights",
                                    update=update_lights_studio_count)

    light_type: EnumProperty(items=enum_light_type, update=update_lights_studio_count)

    light_shape: EnumProperty(update=update_lights_studio_count,
                              items=((i, i.title(), "") for i in ['SQUARE', 'DISK', 'RECTANGLE', 'ELLIPSE']))

    materials_colorspace: EnumProperty(items=enum_blender_colorspace,
                                       description="Colorspace of the materials (Linear is the default option for the Background Image)",
                                       update=update_materials_colorspace)

    volumetric_groups: EnumProperty(items=enum_volumetric_groups, description="Choose the Volumetric type")

    convert_to_new_default_lib_path: StringProperty(name="Convert Default Lib",
                                                    subtype='DIR_PATH',
                                                    description="Convert the old library to the new library into this path")

    convert_to_new_user_lib_path: StringProperty(name="Convert User Lib",
                                                 subtype='DIR_PATH',
                                                 description="Convert the old library to the new library into this path")
    show_light_studio: BoolProperty(default=False, description="Show Light Studio")
    show_sun_studio: BoolProperty(default=False, description="Show Sun Submenu")
