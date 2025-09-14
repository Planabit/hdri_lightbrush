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
import os

import bpy

from ..utility.text_utils import draw_info

#############Funzione da controllare bene!!!!!!!!!!!!!!!!!!!

def check_if_name_exist_in_category(root, foldername, filename):
    # Check if the name already exists in the category
    # If it exists, it returns True, otherwise it returns False
    for fn in os.listdir(os.path.join(root, foldername)):
        if fn == filename:
            text="The name {} already exists in the category {}.".format(filename, foldername)
            draw_info(text, "Info", 'INFO')

            return True

def write_some_data(filepath, image):
    old_filepath = image.filepath_raw

    # deve mantenere il filepath_raw , altrimenti l'immagine nel progetto verrà
    # linkata a dove viene salvata

    image.filepath_raw = filepath

    if image.file_format:
        image.save()
        image.filepath_raw = old_filepath
        return

    if image.name[-4] == '.':
        if image.name[-3:].isnumeric():
            image.name = image.name[:-4]

            image.file_format = image.name[-3:].upper() if image.name[-3:].upper() != 'EXR' else 'OPEN_EXR'

        else:
            image.file_format = image.name[-3:].upper() if image.name[-3:].upper() != 'EXR' else 'OPEN_EXR'
    else:
        image.file_format = image.name[-4:].upper()

    image.save()
    image.filepath_raw = old_filepath



def stopErrorCharacter(self, context):

    text = "Attention special characters not allowed within the name"
    draw_info(text, "Error", 'ERROR')



def search_hdr_files(path, use_blend=False, only_hdr=True):
    from ..dictionaries.dictionaries import image_format
    hdris = []
    for fn in os.listdir(path):
        if not fn.startswith("."):
            if only_hdr:
                if fn.endswith('.hdr') or fn.endswith('.exr'):
                    hdris.append(os.path.join(path, fn))
            else:

                if [img_f for img_f in image_format() if fn.endswith(img_f)]:
                    hdris.append(os.path.join(path, fn))

            if use_blend:
                if fn.endswith('.blend'):
                    hdris.append(os.path.join(path, fn))

    return hdris



