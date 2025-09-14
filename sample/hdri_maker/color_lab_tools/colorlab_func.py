import os

from .hex_to_rgb import rgb_to_hex
from ..utility.json_functions import get_json_data


# Viene popolato all'avvio dai files json con rispettive data


class CL:
    color_lab_dict = {}
    color_lab_items = {'current_system': "", 'current_category': "", 'current_name': "", 'system_list': [],
                       'category_list': [], 'color_list': []}



def update_hex_viewer(self, context):

    r, g, b = self.color_lab_example
    self.color_lab_hex = rgb_to_hex(r, g, b)

def get_color_lab_items(item):

    return CL.color_lab_items[item]


def searchCallback(self, context):
    enum_colors = []
    for system, sis_dict in CL.color_lab_dict.items():
        for category, colors in sis_dict.items():
            for name, code in colors.items():
                enum_colors.append((system + '###' + category + '###' + name, name, ""))

    return enum_colors


def update_color_lab_system(self, context):

    CL.color_lab_items['current_system'] = ""
    CL.color_lab_items['current_category'] = ""
    enum_color_lab_system(self, context)
    enum_color_lab_category(self, context)
    cat_list = CL.color_lab_items['category_list']
    self.color_lab_category = cat_list[0][0]


def update_color_lab_category(self, context):
    CL.color_lab_items['current_system'] = ""
    CL.color_lab_items['current_category'] = ""
    enum_color_lab_system(self, context)
    enum_color_lab_category(self, context)
    enum_color_lab_name(self, context)
    self.color_lab_name = CL.color_lab_items['color_list'][0][0]


# Questa funzione serve per togliere il nome dal preview nel caso l'utente modifichi il colore, in quel caso non sarebbe piu lo stesso cercato nelle cartelle
def update_color_lab_example(self, context):
    self.color_lab_show_name = '?'


def update_color_lab_name(self, context):
    colore = CL.color_lab_dict[self.color_lab_system][self.color_lab_category][self.color_lab_name]['rgb']
    self.color_lab_example = colore
    self.color_lab_show_name = self.color_lab_name


def enum_color_lab_system(self, context):
    if CL.color_lab_items['system_list']:
        return CL.color_lab_items['system_list']

    for idx, (system, value) in enumerate(CL.color_lab_dict.items()):
        CL.color_lab_items['system_list'].append((system, system, "", idx))

    return CL.color_lab_items['system_list']


def enum_color_lab_category(self, context):
    if self.color_lab_system == 'current_system':
        return CL.color_lab_items['category_list']

    CL.color_lab_items['category_list'].clear()
    CL.color_lab_items['current_system'] = self.color_lab_system

    for idx, (key, value) in enumerate(CL.color_lab_dict[self.color_lab_system].items()):
        CL.color_lab_items['category_list'].append((key, key, "", idx))

    return CL.color_lab_items['category_list']


def enum_color_lab_name(self, context):
    current_color_system = CL.color_lab_dict[self.color_lab_system][self.color_lab_category]
    if CL.color_lab_items['current_category'] == self.color_lab_category and CL.color_lab_items['current_system'] == self.color_lab_system:
        return CL.color_lab_items['color_list']

    CL.color_lab_items['color_list'].clear()
    CL.color_lab_items['current_system'] = self.color_lab_system
    CL.color_lab_items['current_category'] = self.color_lab_category

    for idx, (key, value) in enumerate(current_color_system.items()):
        CL.color_lab_items['color_list'].append((key, key, "", idx))

    return CL.color_lab_items['color_list']


# Necessita della libreria di colori in formato json
dir = os.path.join(os.path.dirname(__file__), 'color_list')

for fn in os.listdir(dir):
    if fn.startswith("."):
        continue
    if fn.lower().endswith(".json"):
        color_cat = fn.replace(".json", "")
        json_data = get_json_data(os.path.join(dir, fn))
        CL.color_lab_dict[color_cat] = json_data
