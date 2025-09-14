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

from ..utility.json_functions import get_json_data


def tag_search_active(scnProp):
    # Funzione che da come esito se si sta cercando un tag
    is_active = False
    if scnProp.menu_tag_search:
        if not scnProp.tag_search.isspace() and scnProp.tag_search != "":
            is_active = True
        if not scnProp.tag_exclusion.isspace() and scnProp.tag_exclusion != "":
            is_active = True
        return is_active


def find_tags(file_path, string, exclusion):
    # Restituisce vero o falso se trova o no dei tag, la funzione deve essere chiamata a ogni singolo percorso materiale
    tags_found = None
    if not os.path.isfile(file_path):
        return tags_found
    json_data = get_json_data(file_path)
    if not json_data:
        return tags_found

    js_tag = json_data.get("tags")
    if not js_tag:
        return tags_found

    search_tags = string.split(" ")
    for st in search_tags:
        if st == "":
            search_tags.remove(st)

    exclusion_tags = exclusion.split(" ")
    for et in exclusion_tags:
        if et == "":
            exclusion_tags.remove(et)

    for jt in js_tag:
        for et in exclusion_tags:
            if jt.startswith(et):
                return False

    how_many_tag = []
    for jt in js_tag:
        jt = jt.lower()
        for st in search_tags:
            st = st.lower()
            if jt.startswith(st):
                how_many_tag.append(jt)

    if len(how_many_tag) >= len(search_tags):
        tags_found = True

    return tags_found
