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
from .asset_browser_ui import HDRIMAKER_PT_AssetBrowser
from .geometry_nodes_UI import HDRIMAKER_PT_GeometryNodeTools
from .menu_pie import HDRIMAKER_MT_PIE_Main
from .ui_v2.main_ui_v2 import HDRIMAKER_PT_BackgroundMenu, HDRIMAKER_PT_DomeMenu, HDRIMAKER_PT_Volumetric, \
    HDRIMAKER_PT_ShadowCatcher, HDRIMAKER_PT_SaveMenu, HDRIMAKER_PT_MainPanel, \
    HDRIMAKER_PT_LightStudio, HDRIMAKER_PT_Welcome, HDRIMAKER_PT_BatchSave, HDRIMAKER_PT_BatchScene, \
    HDRIMAKER_PT_AdminPanel, HDRIMAKER_PT_MakeAssetBrowser

ui_interfaces_classes = [HDRIMAKER_PT_Welcome,
                         HDRIMAKER_PT_BatchSave,
                         HDRIMAKER_PT_BatchScene,
                         HDRIMAKER_PT_MainPanel,
                         HDRIMAKER_PT_BackgroundMenu,
                         HDRIMAKER_PT_DomeMenu,
                         HDRIMAKER_PT_Volumetric,
                         HDRIMAKER_PT_ShadowCatcher,
                         HDRIMAKER_PT_SaveMenu,
                         HDRIMAKER_MT_PIE_Main,
                         HDRIMAKER_PT_GeometryNodeTools,
                         HDRIMAKER_PT_LightStudio,
                         HDRIMAKER_PT_AdminPanel,
                         HDRIMAKER_PT_AssetBrowser,
                         HDRIMAKER_PT_MakeAssetBrowser
                         ]
