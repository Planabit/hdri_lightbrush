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

# Convenzioni per i nomi attributi delle collezioni univoche in base al nome dell'addon

from ..utility.utility import wima
from ..exaproduct import Exa

addon_name_clean = Exa.product.lower()


def wm_main_preview():
    """Crea un vero e proprio attributo al bpy.data.window_manager["WinMan"].addon_name + '_main_preview'"""
    wmp = addon_name_clean + "_main_preview"
    return wmp


def pcoll_main_prev():
    """Crea un !Sotto attributo! per il wm_main_preview (la La collezione delle icone di preview del materiale)"""
    pcmp = addon_name_clean + "_preview_icons"
    return pcmp


def pcoll_main_prev_dir():
    """Crea un !Sotto attributo! per il wm_main_preview (la directory)"""
    pcmpd = addon_name_clean + "_preview_dir"
    return pcmpd


def get_winman_main_preview():
    """Restituisce il preview corrente del materiale sotto forma di nome senza l'estensione dell'immagine"""
    return getattr(wima(), wm_main_preview())


def set_winman_main_preview(value):
    """Setta il preview del materiale in base all'input value, che è una stringa,
    nota: la value deve esistere ed è in sostanza il nome dell'immagine di preview"""
    setattr(wima(), wm_main_preview(), value)
