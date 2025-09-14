from . import download
download.downloading()
bl_info = {
    "name": "HDRi Maker",
    "edition": "Studio",
    "author": "Andrea Donati",
    "version": (3, 0, 120),
    "blender": (3, 0, 0),
    "location": "View3D > Tools > HDRi Maker",
    "release": "OFFICIAL",  # "OFFICIAL", "BETA", "ALPHA"
    "description": "Background and Environment Addon",
    "doc_url": "",
    "category": "3D View"}

import bpy

from .addon_preferences import preferences_classes
from .background_tools import background_tools_classes
from .color_lab_tools import color_lab_classes
from .convert_old_library_to_new import convert_old_library_classes
from .custom_property_groups import custom_property_groups_classes
from .dome_tools import dome_classes
from .installer_tools import installation_classes
from .library_manager.lib_ops import lib_ops_classes
from .light_studio import light_studio_classes
from .ops_and_fcs import ops_and_fcs_classes
from .save_tools import save_tools_classes
from .shader_editor import shader_editor_classes
from .shadow_catcher import shadow_catcher_classes
from .ui_interfaces import ui_interfaces_classes
from .ui_interfaces.panel_ops import panel_ops_classes
from .utility import utility_classes
from .volumetric import volumetric_classes
from .web_tools import web_tools_classes
from . import translate
classes = [*preferences_classes,
           *custom_property_groups_classes,
           *background_tools_classes,
           *dome_classes,
           *installation_classes,
           *ops_and_fcs_classes,
           *save_tools_classes,
           *shadow_catcher_classes,
           *shader_editor_classes,
           *ui_interfaces_classes,
           *web_tools_classes,
           *color_lab_classes,
           *convert_old_library_classes,
           *lib_ops_classes,
           *utility_classes,
           *panel_ops_classes,
           *light_studio_classes,
           *volumetric_classes
           ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    from .library_manager import register_library_manager
    register_library_manager()
    from .color_lab_tools import register_colorlab
    register_colorlab()
    from .icons.interfaceicons import register_custom_icons
    register_custom_icons()
    from .handlers.persistent_handlers import register_handlers
    register_handlers()
    from .custom_property_groups import register_custom_property_groups
    register_custom_property_groups()

    from .asset_browser import register_asset_browser_layout
    register_asset_browser_layout()
    translate.register()


def unregister():
    from .handlers.persistent_handlers import on_unregister
    on_unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    from .library_manager import unregister_main_previews_collection
    unregister_main_previews_collection()

    from .icons.interfaceicons import unregister_custom_icons
    unregister_custom_icons()

    from .handlers.persistent_handlers import unregister_handlers
    unregister_handlers()

    from .asset_browser import unregister_asset_browser_layout
    unregister_asset_browser_layout()

    from .library_manager import unregister_library_manager
    unregister_library_manager()
    translate.unregister()


if __name__ == "__main__":
    register()
