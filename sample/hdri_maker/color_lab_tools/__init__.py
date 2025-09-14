from bpy.props import PointerProperty

from .color_lab_ops.ot_color_lab_scroll import HDRIMAKER_OT_ColorLabScroll
from .color_lab_ops.ot_color_lab_search_hex import HDRIMAKER_OT_SearchHex
from .color_lab_ops.ot_color_utility import HDRIMAKER_OT_ColorUtility
from .color_lab_ops.ot_pt_color_lab_panel_ops import HDRIMAKER_OT_color_lab
from .color_lab_scene_props import HdriMakerColorLabSceneProperties

color_lab_classes = [HdriMakerColorLabSceneProperties,
                     HDRIMAKER_OT_color_lab,
                     HDRIMAKER_OT_ColorLabScroll,
                     HDRIMAKER_OT_SearchHex,
                     HDRIMAKER_OT_ColorUtility]

def register_colorlab():
    from bpy.types import Scene
    Scene.hdri_maker_colorlab_scene_prop = PointerProperty(type=HdriMakerColorLabSceneProperties)


