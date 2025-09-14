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
from bpy.props import StringProperty
from bpy.types import Operator

from ..exaproduct import Exa


# Nota: Questo operatore se presente una versione nuova, mostrerà una eventuale lista di versioni nuove,
# Il messaggio in testa all'interfaccia verrà mostrato al prossimo riavvio di Blender, per non creare fastidio quando si preme il bottone
# Questo operatore è per visualizzare quali aggiornamenti ci sono online e basta.


class HDRIMAKER_OT_CheckForUpdates(Operator):
    """Check for updates"""
    bl_idname = Exa.ops_name+"check_for_updates"
    bl_label = "Get updates"
    bl_options = {'INTERNAL'}

    options: StringProperty()

    def execute(self, context):
        from ..utility.text_utils import draw_info
        compile_addon_updates()
        text = "Check for updates done !"
        draw_info(text, "Info", 'INFO')
        self.report({'INFO'}, text)
        return {'FINISHED'}

def compile_addon_updates():
    from ..web_tools.webservice import get_json_online
    from ..installer_tools.fc_update_utility import compare_version
    from ..utility.utility import redraw_all_areas

    json_data = get_json_online(urls=Exa.urls_update, save_name="exa_update.json")
    update_list = json_data.get('updates')
    get_json_online(urls=Exa.urls_orderpages, save_name="exa_orderpages.json")

    compare_version()
    redraw_all_areas()

    from ..utility.utility import get_addon_preferences
    preferences = get_addon_preferences()
    preferences.updates_props.clear()
    for idx, (update_key, update_data) in enumerate(update_list.items()):
        update_item = preferences.updates_props.add()
        update_item.idx = idx
        update_item.name = "Version: " + update_key
        update_item.version_button = False

    # We need to save the preferences to make sure the update list is saved into the properties
    bpy.ops.wm.save_userpref()
