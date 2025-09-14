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

# Try to make uniques the attributes of the window_manager
# So: window_manager + wm_texture_preview + pcoll_texture_prev

from ..exaproduct import Exa
from ..utility.utility import wima


addon_name_clean = Exa.product.lower()


def pcoll_texture_prev():
    # Convenzioni per i nomi attributi delle collezioni univoche in base al nome dell'addon
    pctp = addon_name_clean + "_texture_preview_icons"
    return pctp


def pcoll_texture_prev_dir():
    # Convenzioni per i nomi attributi delle collezioni univoche in base al nome dell'addon
    pctpd = addon_name_clean + "_texture_preview_icons_dir"
    return pctpd


def wm_texture_preview():
    # Restituisce un attributo per il windowmanager in base al nome dell'addon in uso
    wtp = addon_name_clean + "_texture_preview"
    return wtp


def get_winman_texture_preview():
    return getattr(wima(), wm_texture_preview())


def set_winman_texture_preview(value):
    setattr(wima(), wm_texture_preview(), value)
