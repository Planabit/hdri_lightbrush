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
from .shadow_catcher_ops import HDRIMAKER_OT_DisplaceAdd, HDRIMAKER_OT_DisplaceRemove
from .shadow_catcher_v2 import HDRIMAKER_OT_AddShadowCatcher

shadow_catcher_classes = [HDRIMAKER_OT_AddShadowCatcher,
                          HDRIMAKER_OT_DisplaceAdd,
                          HDRIMAKER_OT_DisplaceRemove]