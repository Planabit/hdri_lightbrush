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
from bpy.props import BoolProperty, FloatProperty, StringProperty, CollectionProperty, IntProperty, \
    EnumProperty
from bpy.types import PropertyGroup

from ..socket.socket_callback import update_api_enum, enum_int_socket, \
    update_enum_item_to_socket_idx, HdriMakerEnumSocketInt, update_api_bool_description


class HdriMakerRandomSocketProperties(PropertyGroup):
    """Questa classe aggiunge i bottoni random al nodo gruppo a cui si vuole inserire il random, ogni bottone random
    può essere associato a un socket, questo è disegnato per la randomizzazione dei materiali procedurali in maniera che
    l'utente abbia buoni spunti di partenza su cui modificare tale materiale questo è utile per esempio:
    - Un bottone random per i colori
    - Un bottone random per le proprietà di mixing
    - Un bottone random per le proprietà delle maschere"""

    name: StringProperty(default="Random", description="Name of the random button")
    mark_as_random: BoolProperty(default=False, description="Mark this socket as random")
    float_random_min: FloatProperty(default=0, description="Minimum value for random")
    float_random_max: FloatProperty(default=1, description="Maximum value for random")

class HdriMakerSocketProperties(PropertyGroup):

    api_row_1: BoolProperty(default=False,
                            description="The property will be the first of the Row (The others must be indicated with Row2)")
    api_row_2: BoolProperty(default=False, description="This property will be after Row1")
    api_row_3: BoolProperty(default=False, description="This property will be after Row2")
    api_row_4: BoolProperty(default=False, description="This property will be after Row3")

    api_boolean: BoolProperty(default=False, description="Transform a property of type Value into a Boolean button")
    api_scale_x: FloatProperty(default=1.0, min=0.2, description="Scale x dimension in panel 1 = Default")
    api_scale_y: FloatProperty(default=1.0, min=0.2, description="Scale y dimension in panel 1 = Default")
    api_hide_text: BoolProperty(default=False, description="Hide the property text")
    api_add_color_lab: BoolProperty(default=False,
                                    description="Color lab is an operator used to show a color catalog, it will be placed side by side to the right of the RGB type property")
    api_label_on_top: BoolProperty(default=False, description="The property text is shown at the top")
    api_top_label_text: StringProperty(default="", description="If use api_label_on_top, You can add this extra text, leave blank if you want to use the socket name as the label on top")
    api_keep_socket_label: BoolProperty(default=False,
                                        description="If enabled, the socket label will be kept, otherwise it will be hidden, work in accordance with api_label_on_top")


    api_double_rgb_operator: BoolProperty(default=False,
                                          description="If the next property is of type 'RGB', 2 operators will be added to flip the colors below or above")
    api_col_separator: BoolProperty(default=False, description="Separate the column")
    api_row_separator: BoolProperty(default=False, description="Separate the row (If the row exist")
    # api_show_properties: EnumProperty()
    api_hide_from_panel: BoolProperty(default=False,
                                      description="If enabled, this will not be shown in the HDRi Maker panel")
    api_hide_prop_if_min: StringProperty(name="Hide Min List",
                                         description="Indicates, a list of integers, separated by commas (,)The numbers refer to the Input (Socket) number")
    api_hide_prop_if_max: StringProperty(name="Hide Max List",
                                         description="Indicates, a list of integers, separated by commas (,)The numbers refer to the Input (Socket) number")
    api_icon_true: StringProperty()
    api_icon_false: StringProperty()
    api_transparent_operator: BoolProperty(default=False,
                                           description="Adds an operator used to choose the type of transparency. Useful for managing materials in Eevee")
    api_sss_translucency: BoolProperty(default=False,
                                       description="Adds a button to the right, useful in Eevee to activate Subsurface Translucency")
    api_screen_refraction: BoolProperty(default=False,
                                        description="Adds a button to the right, useful in Eevee to activate Screen Space Refraction")
    api_text_if_true: StringProperty()
    api_text_if_false: StringProperty()
    api_bool_description: StringProperty(default="",
                                         description="Enter a description, it will be shown to Tips button, or when the user move over with the cursor on the Boolean Button",
                                         update=update_api_bool_description)
    api_bool_invert: BoolProperty(default=False, description="Invert the On Off button in the user panel")

    api_bool_mute_nodes_if_true: StringProperty(default="",
                                                description='Enter a list of node names, separated by "//" that you want to mute if the Bool property is True')
    api_bool_mute_nodes_if_false: StringProperty(default="",
                                                 description='Enter a list of node names, separated by "//" that you want to mute if the Bool property is False')

    is_api_enum: BoolProperty(default=False, update=update_api_enum, description="If enabled, it transforms the socket into an Integer type Socket, any number can be an option.")
    api_enum_direction: EnumProperty(default='HORIZONTAL', items=(('HORIZONTAL', "Horizontal", ""), ('VERTICAL', "Vertical","")))
    api_enum_items: EnumProperty(items=enum_int_socket, update=update_enum_item_to_socket_idx)
    api_color_ramp: StringProperty(default="")

    stored_items: StringProperty(default="[]")
    reset_items: BoolProperty(default=True)

    self_id_idx: IntProperty(default=0, description="Questo è interno, per dare un ordine e riconoscere nel callback l'idx del socket inputs")
    api_collection_idx: CollectionProperty(name="Socket Idx", type=HdriMakerEnumSocketInt)

    show_socket_menu: BoolProperty(default=True, description="Used to show properties in the Panel builder Helper menu")
    # is_system_socket è per nascondere il controllo dal pannello di epbr ma si assegna manualmente alla creazione del modulo
    #
    is_system_socket: BoolProperty(default=False,
                                   description="This property is only to exclude the sockets that are needed by modules, mixers, etc to connect to each other. They will not be shown in the panels as they must not be modified by anyone")
    api_displace_alert: BoolProperty(default=False,
                                     description="If displace is active, and this value is not the default value, Show the alert button next to the button displaced in the object's materials panel. If the Displacement is in modifier mode. User alert useful for not breaking the displacement view.")
    # rgb_paint: FloatVectorProperty(name="", subtype='COLOR', default=(1, 1, 1, 1), min=0.0, max=1.0, size=4,
    #                                description="Paint Color", update=update_rgb_paint)
    # black_and_white_paint: FloatProperty(default=1, min=0, max=1, update=update_black_and_white_paint)
    tag_socket: StringProperty()

    store_property: BoolProperty(default=False,
                                 description="If checked, record this property in the json file, so that the material, when used, will be set exactly as you saved it. (Only for textures-type materials)")
    # procedural_tex: EnumProperty(items = enum_procedural_texture)
    is_fake_socket: BoolProperty(default=False,
                                 description="It only shows the texture manager/paint, without showing any sliders in the Addon panel, you can leave, you can leave this socket disconnected, only the button will be shown.")


    docs_key: StringProperty(default="")

    random_socket: CollectionProperty(type=HdriMakerRandomSocketProperties)

    lock_prop: BoolProperty(default=False, name="Lock Property",
                            description="If enabled, the property will be locked, and the Restore To default ignore it")