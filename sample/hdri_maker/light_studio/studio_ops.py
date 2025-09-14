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
import os.path

import bpy
from bpy.types import Operator

from ..background_tools.background_fc import import_hdri_maker_world, assign_image_to_background_node, get_nodes_dict
from ..dome_tools.dome_fc import AssembleDome, get_dome_objects
from ..exaconv import get_scnprop
from ..exaproduct import Exa
from ..library_manager.get_library_utils import risorse_lib
from ..light_studio.light_studio_fc import update_lights_studio_count
from ..utility.utility import purge_all_group_names
from ..utility.utility_4 import get_ng_inputs


class HDRIMAKER_OT_AssembleStudio(Operator):
    """Configure the light Studio Scene"""

    bl_idname = Exa.ops_name + "assemble_studio"
    bl_label = "Assemble Light Studio"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return "Create the Entire Light Studio Scene, with Background, Dome Backdrop and Lights"

    def execute(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        # Questo operatore, deve configurare la scena con Luci/Sfondo/Dome

        # Aggiungere sfondo se non c'è, lo sfondo deve avere l'immagine Grigia

        # Load Background
        filepath = os.path.join(risorse_lib(), "blendfiles", "hdr", "grey_background.hdr")
        image = bpy.data.images.load(filepath)
        world = import_hdri_maker_world(context, rename="Light Studio")
        assign_image_to_background_node(image, environment='COMPLETE')
        purge_all_group_names(world.node_tree)

        # Load Dome
        scnProp.dome_types = os.path.join(risorse_lib(), "blendfiles", "domes", "dome.blend")
        ADome = AssembleDome(context, image=image, dome_name="DOME_" + world.name)
        ADome.start()

        # Get the dome material Color Mixer, and set it to "Solid Color"
        dome_dict = get_dome_objects()
        dome_material = dome_dict.get('DOME_MATERIAL')
        if dome_material:
            node_dict =  get_nodes_dict(dome_material.node_tree)
            mixer = node_dict.get('MIXER')
            if mixer:
                is_solid_color = next((i for i in mixer.inputs if i.name.lower().replace(" ", "_") == "is_solid_color"), None)
                if is_solid_color:
                    ng_inputs = get_ng_inputs(mixer.node_tree)
                    node_tree_input = next((i for i in ng_inputs if i.name.lower().replace(" ", "_") == "is_solid_color"), None)
                    if node_tree_input:
                        is_solid_color.default_value = node_tree_input.max_value


        # Load Lights
        update_lights_studio_count(scnProp, context)



        return {'FINISHED'}

