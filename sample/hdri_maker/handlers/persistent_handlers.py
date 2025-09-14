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
import bpy
from bpy.app.handlers import persistent

from ..dome_tools.dome_fc import set_reflection_plane_size
from ..library_manager.pcoll_utils import get_libraries_location, set_libraries_location
from ..shadow_catcher.shadow_catcher_fc import update_shadow_catcher
from ..utility.classes_utils import GlobalVar
from ..utility.utility import get_shading_engine, get_addon_preferences


def on_unregister():
    """This function is called when the addon is unregistered"""
    set_libraries_location()


def update_all():
    from ..web_tools.ot_update_menu import compile_addon_updates
    # Here the json file is downloaded and the updates_props properties are compiled
    # which are stored in HDRiMakerUpdates, to create an interactive interface that shows the updates
    # available about the addon
    compile_addon_updates()
    from ..exaproduct import Exa
    from ..web_tools.webservice import get_json_online
    get_json_online(urls=Exa.urls_exa_libraries_volumes, save_name="exa_library_volumes.json",
                    show_popup=False)
    get_json_online(urls=Exa.top_addons, save_name="exa_top_addons.json", show_popup=False)
    # get_json_online(urls=Exa.urls_social, save_name="urls_social.json", show_popup=False)

@persistent
def on_blender_start(self):
    """This function is called when blender is started or a file is loaded"""

    preferences = get_addon_preferences()
    preferences.exapacks_install.clear()

    from ..web_tools.check_update_time import is_time_to_check_update
    if is_time_to_check_update():
        update_all()

    try:
        from ..ui_interfaces.ui_v2.main_ui_v2 import refresh_interface
        refresh_interface()
    except:
        pass


def engine_change():
    """This function is called when the engine is changed, it is called by desgraph_update_pre function"""
    update_shadow_catcher()

@persistent
def depsgraph_update_pre(scena):
    try:
        # In extreme cases, if some Addon or Render-farm creates strange unknown problems, this condition, makes it exit
        # From the function
        scn = bpy.context.scene
    except:
        return

    if GlobalVar.contextEngine is None:
        GlobalVar.contextEngine = get_shading_engine()
        return

    if get_shading_engine() != GlobalVar.contextEngine:
        GlobalVar.contextEngine = get_shading_engine()
        # Run the engine change function:
        engine_change()

    set_reflection_plane_size()

def background_timer():

    timer_loop = 0.25

    try:
        # In extreme cases, if some Addon or Render-farm creates strange unknown problems, this condition, makes it exit
        # From the function
        scn = bpy.context.scene
    except:
        return timer_loop

    if GlobalVar.contextEngine is None:
        GlobalVar.contextEngine = get_shading_engine()
        return timer_loop

    if get_shading_engine() != GlobalVar.contextEngine:
        GlobalVar.contextEngine = get_shading_engine()
        # Run the engine change function:
        engine_change()

    set_reflection_plane_size()

    return timer_loop

def on_register():
    """This function is called when the addon is registered"""
    get_libraries_location(adjust=True) # Questo quando si attiva l'addon trova i percorsi delle librerie senza dover riavviare blender
    return None


def register_handlers():
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre)
    bpy.app.handlers.load_post.append(on_blender_start)
    # on_register()
    # Questo trucchetto fa si che prima sia caricato l'addon e subito dopo 1 secondo esso possa usare le funzioni e gli
    # operatori contenuti in on_register
    bpy.app.timers.register(on_register, first_interval=1, persistent=True)

def unregister_handlers():
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre)
    bpy.app.handlers.load_post.remove(on_blender_start)
    # bpy.app.timers.unregister(background_timer)
