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
import time

from ..library_manager.get_library_utils import risorse_lib
from ..utility.utility import get_addon_preferences
from ..utility.json_functions import get_json_data, save_json


def write_last_check(check_file):
    now = datetime.datetime.now()
    human_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    data = {"last_check": int(time.time()),
            "datetime": human_datetime}
    save_json(check_file, data)


def is_time_to_check_update():
    """Check if enough time has passed, returns only true false"""
    # A json file is written, only if it is the first time, and only if the time elapsed is
    # equal to or greater than the time set by the user, the save json happens only if time_passed instruction here below
    # and if the file does not exist. So be careful, to make sure that file is always deleted, or rewritten in these
    # two cases.
    # Get addon directory:
    folder = os.path.join(risorse_lib(), "online_utility")
    if not os.path.isdir(folder):
        os.mkdir(folder)

    check_file = os.path.join(folder, "last_update_check.json")
    if not os.path.isfile(check_file):
        write_last_check(check_file)
        return True

    addon_preferences = get_addon_preferences()

    if addon_preferences.check_update_frequency_control == 'NEVER':
        return False

    seconds_per_day = 86400  # Questi sono i secondi in un giorno
    frequency_control = float(
        addon_preferences.check_update_frequency_control)  # Questa è la proprietà impostata dall'utente

    if frequency_control == 0:
        # In questo caso l'utente ha impostato "Mai" quindi zero
        return

    days = seconds_per_day * frequency_control

    data = get_json_data(check_file)
    last_check = data.get("last_check")

    time_passed = time.time() - last_check
    if time_passed >= days:
        write_last_check(check_file)
        return True
