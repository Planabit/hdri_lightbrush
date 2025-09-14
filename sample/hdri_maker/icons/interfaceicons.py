import os

import bpy
import bpy.utils.previews

path = os.path.join(os.path.dirname(__file__), 'addon_icons')

class Ico:
    custom_icons = None


def get_icon(string):
    return Ico.custom_icons[string+".png"].icon_id


def register_custom_icons():
    Ico.custom_icons = bpy.utils.previews.new()
    for idx, ic in enumerate(os.listdir(path)):
        if not ic.startswith("."):
            if ic.endswith(".png") or ic.endswith(".jpg") or ic.endswith(".jpeg") or ic.endswith(".webp"):
                Ico.custom_icons.load(ic, os.path.join(path, ic), 'IMAGE')

def unregister_custom_icons():
    if Ico.custom_icons:
        print("Rimuovo dalla funzione unregister_custom_icons")
        bpy.utils.previews.remove(Ico.custom_icons)
        Ico.custom_icons.clear()

