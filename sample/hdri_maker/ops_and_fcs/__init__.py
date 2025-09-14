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
from .flip_normals import HDRIMAKER_OT_FlipNormals
from .ops import HDRIMAKER_OT_restore_node_value, HDRIMAKER_OT_SelectObject
from .ot_boolean_socket import HDRIMAKER_OT_boolean_socket
from .ot_python_ops import HDRIMAKER_OT_PythonOps
from .ot_show_tips import HDRIMAKER_OT_show_tips

ops_and_fcs_classes = [HDRIMAKER_OT_PythonOps,
                       HDRIMAKER_OT_boolean_socket,
                       HDRIMAKER_OT_restore_node_value,
                       HDRIMAKER_OT_show_tips,
                       HDRIMAKER_OT_SelectObject,
                       HDRIMAKER_OT_FlipNormals]