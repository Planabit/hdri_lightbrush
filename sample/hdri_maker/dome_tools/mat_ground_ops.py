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
import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from ..dome_tools.dome_fc import find_current_dome_version, get_dome_material, asign_vcol_to_node_attribute, \
    get_dome_objects, remove_mat_ground
from ..exaconv import get_objprop
from ..exaproduct import Exa
from ..utility.text_utils import draw_info
from ..utility.utility import set_vertex_color, make_parent, un_parent


class HDRIMAKER_OT_AssignMatGround(Operator):
    """Assign HDRI material"""

    bl_idname = Exa.ops_name + "assign_mat_ground"
    bl_label = "Assign material"
    bl_options = {'INTERNAL', 'UNDO'}

    op_items = [('ADD', "Add", "Add material to the object"), ('REMOVE', "Remove", "Remove material from the object"),
                ('REMOVE_ALL', "Remove All", "Remove material from all objects")]
    options: EnumProperty(items=op_items, name="Options", default='ADD')
    target: StringProperty()

    @classmethod
    def description(cls, context, properties):
        desc = next((item[2] for item in cls.op_items if item[0] == properties.options), "")
        return desc

    def execute(self, context):
        scn = context.scene

        if self.target == 'ACTIVE_OBJECT':
            ob = context.object
        else:
            ob = bpy.data.objects.get(self.target)

        if self.options == 'ADD':
            if not ob:
                text = "Please select an object"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if ob.type != 'MESH':
                text = "Please select a mesh type object"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            dome_parts = find_current_dome_version(context)
            dome_ground = dome_parts.get('dome_ground')
            dome_sky = dome_parts.get('dome_sky')

            if not dome_ground or not dome_sky:
                text = "To assign Ground material to the object, a Dome must be added."
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if ob in [dome_ground, dome_sky]:
                text = "The dome already contains this material"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            dome_material = get_dome_material(dome_ground)  # dome_ground or dome_sky have the same material
            if not dome_material:
                text = "No material on the dome, please delete the dome, and set a new one"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if dome_material:
                if dome_material in ob.data.materials[:]:
                    text = "The ground material is already assigned to the object"
                    draw_info(text, "Info", 'INFO')
                    return {'CANCELLED'}

            # Check if other materials are present in the object
            for mat in ob.data.materials:
                if mat:
                    text = "The object already has a material assigned, for security reasons, the material will" \
                           " not be assigned. This is to avoid problems with the material. " \
                           "This is avoided to avoid problems with your materials applied." \
                           "To continue, remove all materials from the object, or create or copy your object and apply the material"
                    draw_info(text, "Info", 'INFO')
                    return {'CANCELLED'}

            if dome_material not in ob.data.materials[:]:
                ob.data.materials.append(dome_material)

            objProp = get_objprop(ob)
            objProp.object_id_name = 'HDRI_MAKER_GROUND'
            objProp.ground_object_type = 'GROUND'
            set_vertex_color(ob, "HDRI_MAKER_GROUND", color=(1, 1, 1, 1), make_active=True)
            asign_vcol_to_node_attribute(dome_material, v_col_name='HDRI_MAKER_GROUND')

            dome_dict = get_dome_objects()
            dome_handler = dome_dict.get('DOME_HANDLER')
            if dome_handler:
                make_parent(dome_handler, ob)

        elif self.options in ['REMOVE', 'REMOVE_ALL']:
            ob_list = []
            if self.options == 'REMOVE':
                ob_list.extend([ob])

            elif self.options == 'REMOVE_ALL':
                ob_list.extend([o for o in scn.objects if o.type == 'MESH' and get_objprop(o).object_id_name == 'HDRI_MAKER_GROUND'])

            for ob in ob_list:
                objProp = get_objprop(ob)
                remove_mat_ground(ob)

                dome_dict = get_dome_objects()
                dome_handler = dome_dict.get('DOME_HANDLER')
                if dome_handler:
                    if objProp.is_shrinkwrap:
                        # In this case the object is shrinkwrapped to the dome, so it need to be parented to the dome, skip.
                        continue
                    un_parent(ob)

        return {'FINISHED'}

class HDRIMAKER_OT_MaterialSelector(Operator):
    """Change the from ground material to sky material"""

    bl_idname = Exa.ops_name + "material_selector"
    bl_label = "Material Selector"
    bl_options = {'INTERNAL', 'UNDO'}

    # Imposta il materiale a tipo Ground
    # Traduci in Inglese:
    #
    op_items = [('GROUND', "Ground", "Set the material to Ground type, you can move the object to any position, "
                                     "the material will only follow the X and Y coordinates, but not Z."),
                ('SKY', "Sky", "Set the material to Sky type, you can move the object to any position,"
                               "the material will follow all coordinates")]

    options: EnumProperty(items=op_items)
    target: StringProperty()

    @classmethod
    def description(cls, context, properties):
        desc = next((item[2] for item in cls.op_items if item[0] == properties.options), "")
        return desc

    def execute(self, context):
        ob = bpy.data.objects.get(self.target)
        if not ob:
            text = "Please select an object"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        objProp = get_objprop(ob)

        if self.options == 'SKY':
            # If Sky, the vertex color need to be Black
            set_vertex_color(ob, "HDRI_MAKER_GROUND", color=(0, 0, 0, 1), make_active=True)
            objProp.ground_object_type = 'SKY'
        elif self.options == 'GROUND':
            # If Ground, the vertex color need to be White
            set_vertex_color(ob, "HDRI_MAKER_GROUND", color=(1, 1, 1, 1), make_active=True)
            objProp.ground_object_type = 'GROUND'


        return {'FINISHED'}