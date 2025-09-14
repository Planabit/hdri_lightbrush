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

# ###########################################################################################################
# ##############================LibrariesSwitch==============#####################################################
import os

from ..utility.utility import get_addon_preferences


class StoreLibraries(object):
    # Librarie nel libraries_selector
    libraries = []

def enum_libraries_selector(self, context):

    preferences = get_addon_preferences()
    expansions = preferences.expansion_filepaths

    default = ('DEFAULT', "HDRi Maker Library", "Default Library")
    user = ('USER', "User Library", "User Personal Library")

    if default not in StoreLibraries.libraries:
        StoreLibraries.libraries.append(default)
    if user not in StoreLibraries.libraries:
        StoreLibraries.libraries.append(user)

    for idx, item in enumerate(expansions):
        # if item.path not in libraries:
        if not os.path.isdir(item.path):
            continue
        lib = (item.path, item.name, "")
        if lib not in StoreLibraries.libraries:
            StoreLibraries.libraries.append(lib)


    return StoreLibraries.libraries
