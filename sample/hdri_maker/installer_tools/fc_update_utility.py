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

from ..exaproduct import Exa
from ..library_manager.get_library_utils import risorse_lib
from ..utility.json_functions import get_json_data
from ..utility.utility import get_version_to_int, get_addon_preferences


def compare_version():

    preferences = get_addon_preferences()
    preferences.need_update = False
    preferences.update_urgency = False
    exa_update = os.path.join(risorse_lib(), "online_utility", "exa_update.json")

    if not os.path.isfile(exa_update):
        return

    update_data = get_json_data(exa_update)
    if not update_data:
        return
    updates = update_data.get('updates')
    if not updates:
        return

    find_urgency = False
    current_version = get_version_to_int(Exa.blender_manifest['version'])
    for version, values in updates.items():
        available_version = get_version_to_int(version)
        if available_version > current_version:
            preferences.need_update = True
            urgency = values.get("urgency")
            if urgency:
                find_urgency = True

        # Proprietà preferenze che serve per assegnare un messaggio di update importante e urgente, verrà mostrato nella main UI
        preferences.update_urgency = find_urgency
