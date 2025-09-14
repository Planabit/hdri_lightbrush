#   #
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version
#    of the License, or (at your option) any later version.
#   #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#   #
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software Foundation,
#    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#   #
#   Copyright 2024(C) Andrea Donati

from .utility_ops.copy_to_clipboard import HDRIMAKER_OT_copy_to_clipboard
from .utility_ops.ot_open_preferences import HDRIMAKER_OT_open_preferences
from .utility_ops.ot_os_remove import HDRIMAKER_OT_purge_cache
from .utility_ops.ot_reload_preview import HDRIMAKER_OT_restore_all_icons_patch
from .utility_ops.store_node_dimension import HDRIMAKER_OT_NodePropsDimensions

utility_classes = [HDRIMAKER_OT_open_preferences,
                   HDRIMAKER_OT_NodePropsDimensions,
                   HDRIMAKER_OT_restore_all_icons_patch,
                   HDRIMAKER_OT_purge_cache,
                   HDRIMAKER_OT_copy_to_clipboard]
