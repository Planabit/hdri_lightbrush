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
from .add_background_ops import HDRIMAKER_OT_AddBackground
from .add_remove_group import HDRIMAKET_OT_AddRemoveGroups
from .background_ops import HDRIMAKER_OT_RemoveMaterial, HDRIMAKET_OT_SearchCurrentWorld, HDRIMAKER_OT_FlipDiffuseLight, \
    HDRIMAKER_OT_SolveNodesProblem, HDRIMAKER_OT_MakeLocal
from .convert_world_ops import HDRIMAKER_OT_ConvertWorld
from .inpaint import HDRIMAKER_OT_InPaint
from .synch_dome_and_background import HDRIMAKER_OT_sync_node_background_rotation

background_tools_classes = [HDRIMAKER_OT_RemoveMaterial,
                            HDRIMAKER_OT_AddBackground,
                            HDRIMAKET_OT_SearchCurrentWorld,
                            HDRIMAKER_OT_FlipDiffuseLight,
                            HDRIMAKER_OT_SolveNodesProblem,
                            HDRIMAKET_OT_AddRemoveGroups,
                            HDRIMAKER_OT_sync_node_background_rotation,
                            HDRIMAKER_OT_MakeLocal,
                            HDRIMAKER_OT_ConvertWorld,
                            HDRIMAKER_OT_InPaint]
