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
from .batch_save_ops import HDRIMAKER_OT_BatchModal, HDRIMAKER_OT_RemoveFromColProp
from .panorama_save_ops import HDRIMAKER_OT_PanoramaSave
from .redraw_preview import HDRIMAKER_OT_RedrawPreview
from .save_current_world_ops import HDRIMAKER_OT_SaveCurrentBackground
from .save_geometry_nodes import HDRIMAKER_OT_SaveGeoNode
from .save_ops import HDRIMAKER_OT_AddPanoramaCamera, HDRIMAKER_OT_FileToCat, \
    HDRIMAKER_OT_RenameLibTool, HDRIMAKER_OT_ExportHdr, \
    HDRIMAKER_OT_ResnapCamera, HDRIMAKER_OT_CenterView, HDRIMAKER_OT_ConvertToAbsolutePath, \
    HDRIMAKER_OT_AddCategory, HDRIMAKER_OT_RemoveScene

save_tools_classes = [HDRIMAKER_OT_AddPanoramaCamera,
                      HDRIMAKER_OT_FileToCat,
                      HDRIMAKER_OT_RenameLibTool,
                      HDRIMAKER_OT_ExportHdr,
                      HDRIMAKER_OT_ResnapCamera,
                      HDRIMAKER_OT_CenterView,
                      HDRIMAKER_OT_BatchModal,
                      HDRIMAKER_OT_ConvertToAbsolutePath,
                      HDRIMAKER_OT_AddCategory,
                      HDRIMAKER_OT_SaveCurrentBackground,
                      HDRIMAKER_OT_RemoveFromColProp,
                      HDRIMAKER_OT_RemoveScene,
                      HDRIMAKER_OT_RedrawPreview,
                      HDRIMAKER_OT_PanoramaSave,
                      HDRIMAKER_OT_SaveGeoNode
                      ]
