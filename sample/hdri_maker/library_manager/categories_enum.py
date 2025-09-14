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

from ..exaconv import get_scnprop
from ..library_manager.get_library_utils import current_lib
from ..library_manager.tag_filter import tag_search_active, find_tags



class MatDict:
    mats_categories = {"library": "", "categories": [], "index": [], "tagged": []}


def get_mats_categories():
    return MatDict.mats_categories

def enum_up_category(self, context):
    scnProp = get_scnprop(context.scene)

    if not current_lib():
        name = 'Empty Collection...'
        MatDict.mats_categories["categories"] = [(name, name, "", 'KEYTYPE_JITTER_VEC', 0)]
        return MatDict.mats_categories['categories']

    # directory
    if MatDict.mats_categories["library"] == scnProp.libraries_selector:
        return MatDict.mats_categories["categories"]

    # Questo lo si usa per il discorso della ricerca dei materiali, se siamo sotto ricerca tag
    MatDict.mats_categories["tagged"] = []

    updirectory = current_lib()  # if scnProp.libraries_selector == 'DEFAULT' else user_lib
    ###########

    cat_list = []
    if os.path.isdir(updirectory):
        dirListing = os.listdir(updirectory)
        for item in dirListing:
            if item.startswith("."):
                continue
            if '._data' in item:
                continue
            if not os.path.isdir(os.path.join(updirectory, item)):
                continue
            append_cat = True
            # Sezione per eventuale ricerca tag
            if tag_search_active(scnProp):
                mat_list = []
                for mat in os.listdir(os.path.join(updirectory, item)):
                    data_json = os.path.join(updirectory, item, mat, "data", "tags.json")
                    if os.path.isfile(data_json):
                        if find_tags(data_json, scnProp.tag_search, scnProp.tag_exclusion):
                            MatDict.mats_categories["tagged"].append(mat)
                            mat_list.append(mat)
                if not mat_list:
                    append_cat = False
            #############################################

            if append_cat:
                cat_list.append(item)

    if len(cat_list) == 0:
        cat_list.append('Empty Collection...')

    cat_list.sort()

    if scnProp.libraries_selector == 'DEFAULT':
        if not tag_search_active(scnProp):
            cat_list.insert(0, "Tools")

    MatDict.mats_categories["index"] = cat_list

    categories = []
    for idx, name in enumerate(cat_list):
        if name == "Tools" and scnProp.libraries_selector == 'DEFAULT':
            icon = 'KEYTYPE_MOVING_HOLD_VEC'
        else:
            icon = 'KEYTYPE_BREAKDOWN_VEC'
        categories.append((name, name, "", icon, idx))

    MatDict.mats_categories["categories"] = categories
    MatDict.mats_categories["library"] = scnProp.libraries_selector

    return MatDict.mats_categories["categories"]


def update_first_cat(self, context):
    MatDict.mats_categories['library'] = ''
    enum_up_category(self, context)
    self.up_category = MatDict.mats_categories["categories"][0][0]
