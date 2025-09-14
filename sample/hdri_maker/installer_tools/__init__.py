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
from .installer_tools_ops.compare_with_exapack import HDRIMAKER_OT_try_compile_exapack
from .installer_tools_ops.create_zip_library import HDRIMAKER_OT_CreateZipLibrary, HDRIMAKER_OT_MakeJsonExaCollection, \
    HDRIMAKER_OT_GenerateZipsJson, HDRIMAKER_OT_CreateTagAndMatInfo
from .installer_tools_ops.exapack_volumes_ops import HDRIMAKER_OT_remove_volume
from .installer_tools_ops.install_zip_library import HDRIMAKER_OT_install_exapacks, HDRIMAKER_OT_AbortZipInstall, \
    HDRIMAKER_OT_ChooseExaPacks, HDRIMAKER_OT_FinishConfirm
from .installer_tools_ops.make_user_lib import HDRIMAKER_OT_make_user_library
from .installer_tools_ops.ot_choose_path import HDRIMAKER_OT_ChoosePath
from .installer_tools_ops.ot_reset_lib_path import HDRIMAKER_OT_ResetLibPath
from .installer_tools_ops.remind_me_later import HDRIMAKER_OT_remind_me_later

installation_classes = [HDRIMAKER_OT_ChoosePath,
                        HDRIMAKER_OT_ResetLibPath,
                        HDRIMAKER_OT_CreateZipLibrary,
                        HDRIMAKER_OT_install_exapacks,
                        HDRIMAKER_OT_AbortZipInstall,
                        HDRIMAKER_OT_ChooseExaPacks,
                        HDRIMAKER_OT_FinishConfirm,
                        HDRIMAKER_OT_remove_volume,
                        HDRIMAKER_OT_MakeJsonExaCollection,
                        HDRIMAKER_OT_GenerateZipsJson,
                        HDRIMAKER_OT_CreateTagAndMatInfo,
                        HDRIMAKER_OT_make_user_library,
                        HDRIMAKER_OT_try_compile_exapack,
                        HDRIMAKER_OT_remind_me_later
                        ]
