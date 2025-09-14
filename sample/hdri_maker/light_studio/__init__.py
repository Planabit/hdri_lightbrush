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
from .light_studio_ops import HDRIMAKER_OT_CreateLightStudio, HDRIMAKER_OT_RandomLightColor, HDRIMAKER_OT_ParentTarget
from .studio_ops import HDRIMAKER_OT_AssembleStudio
from .sun_ops import HDRIMAKER_OT_SunMaker, HDRIMAKER_OT_SyncSun

light_studio_classes = [HDRIMAKER_OT_CreateLightStudio,
                        HDRIMAKER_OT_AssembleStudio,
                        HDRIMAKER_OT_RandomLightColor,
                        HDRIMAKER_OT_ParentTarget,
                        HDRIMAKER_OT_SunMaker,
                        HDRIMAKER_OT_SyncSun]
