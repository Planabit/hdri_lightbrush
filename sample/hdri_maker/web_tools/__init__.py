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
from .ot_update_menu import HDRIMAKER_OT_CheckForUpdates
from .web_operators.bug_report import HDRIMAKER_OT_Bugreport, HDRIMAKER_OT_copy_info_to_clipboard
from .web_operators.docs_operator import HDRIMAKER_OT_DocsOps
from .web_operators.get_update_library import HDRIMAKER_OT_GetLibraryUpdates
from .web_operators.ot_web_browser import HDRIMAKER_OT_open_web_browser, HDRIMAKER_OT_SendMail
from .web_operators.top_addons_refresh import HDRIMAKER_OT_TopAddonsRefresh

web_tools_classes = [HDRIMAKER_OT_copy_info_to_clipboard,
                     HDRIMAKER_OT_Bugreport,
                     HDRIMAKER_OT_SendMail,
                     HDRIMAKER_OT_TopAddonsRefresh,
                     HDRIMAKER_OT_open_web_browser,
                     HDRIMAKER_OT_CheckForUpdates,
                     HDRIMAKER_OT_GetLibraryUpdates,
                     HDRIMAKER_OT_DocsOps]
