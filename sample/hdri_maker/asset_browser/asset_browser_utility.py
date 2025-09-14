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
import os

import bpy

from ..utility.utility import use_temp_override


def asset_browser_create_cat_file(path, cat):
    txt_file = os.path.join(path, "blender_assets.cats.txt")
    # The text to insert is:

    # This is an Asset Catalog Definition file for Blender.
    #
    # Empty lines and lines starting with `#` will be ignored.
    # The first non-ignored line should be the version indicator.
    # Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"


    if not os.path.isfile(txt_file):
        # Create text file
        with open(txt_file, "w") as f:
            # Insert the comment text:
            f.write("# This is an Asset Catalog Definition file for Blender.\n") # need to go ahead and write the first line
            # Wrap the text to 80 character
            f.write("#\n")
            f.write("# Empty lines and lines starting with `#` will be ignored.\n")
            f.write("# The first non-ignored line should be the version indicator.\n")
            f.write("# Other lines are of the format \"UUID:catalog/path/for/assets:simple catalog name\"\n")
            # Make blank line
            f.write("\n\n")
            # Insert the version indicator
            f.write("VERSION 1\n")
            # Make blank line
            f.write("\n\n")


    with open(txt_file) as f:
        lines = f.readlines()

        # Check if the catalog is already in the file
        for line in lines:
            if cat in line:
                # Return the UUID of the catalog
                return line.split(":")[0] # As the UUID is the first element of the line

    with open(txt_file, "a") as f:
        # If the catalog is not in the file, add it
        # Get the UUID of the catalog
        import uuid
        cat_uuid = str(uuid.uuid4())
        # Add the catalog to the file
        # Write the catalog to the file, into the last line

        f.write("\n"+cat_uuid + ":" + cat)

    # Copy the "blender_assets.cats.txt" file to the same directory and rename it to "blender_assets.cats.txt~"
    import shutil
    shutil.copy(txt_file, txt_file+"~")


    return cat_uuid


def asset_browser_assign_custom_preview(item, image_filepath):
    override = bpy.context.copy()
    override['id'] = item

    if use_temp_override():
        with bpy.context.temp_override(**override):
            bpy.ops.ed.lib_id_load_custom_preview(filepath=image_filepath)
    else:
        bpy.ops.ed.lib_id_load_custom_preview(override, filepath=image_filepath)

