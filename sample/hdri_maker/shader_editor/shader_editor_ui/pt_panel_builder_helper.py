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
import bpy
from bpy.props import StringProperty

from ..functions import check_shader_area_ok
from ...exaconv import get_ngprop, get_scnprop, get_sckprop
from ...exaproduct import Exa
from ...ui_interfaces.draw_functions import draw_all_custom_props
from ...utility.enum_blender_native import get_blender_icons
from ...utility.fc_utils import show_helps_v2
from ...utility.text_utils import wrap_text
from ...utility.utility import get_in_out_group, is_node_group
from ...utility.utility import retrieve_nodes
from ...utility.utility_4 import get_active_socket, is_ng_output, get_socket_color, is_linked_internal, get_socket_type


class HDRIMAKER_UL_node_interface_sockets(bpy.types.UIList):
    filter_string: StringProperty(
        name="filter_string",
        default="",
        description="Filter string for name"
    )

    def draw_item(self, context, layout, _data, item, icon, _active_data, _active_propname, _index):

        self.use_filter_invert = False

        if bpy.app.version < (4, 0, 0):
            is_input = item.is_output == False
            is_output = item.is_output == True
            pass
        else:
            is_input = item.in_out == 'INPUT'
            is_output = item.in_out == 'OUTPUT'

        socket = item
        color = get_socket_color(context, socket)

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            if is_input:
                row.template_node_socket(color=color)
                row.prop(socket, "name", text=str(_index), emboss=False, icon_value=icon)
            if is_output:
                row.prop(socket, "name", text="", emboss=False, icon_value=icon)
                row = row.row(align=True)
                row.alignment = 'RIGHT'
                row.label(text=str(_index))
                row.template_node_socket(color=color)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.template_node_socket(color=color)

    def filter_items(self, context, data, propname):
        """Filter and order items in the list"""

        items = getattr(data, propname)
        if not len(items):
            return [], []

        # Initialize
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            sckProp = get_sckprop(item)
            if sckProp.is_system_socket:
                filtered[i] &= ~self.bitflag_filter_item
            if self.filter_string:
                if not self.filter_string.lower() in item.name.lower():
                    filtered[i] &= ~self.bitflag_filter_item

            if is_ng_output(item):
                filtered[i] &= ~self.bitflag_filter_item

        return filtered, []

    def draw_filter(self, context, layout):

        row = layout.row(align=True)
        row.prop(self, "filter_string", text="Filter", icon="VIEWZOOM")


def draw_socket_list(self, context, in_out):
    layout = self.layout
    snode = context.space_data
    node_tree = snode.edit_tree

    active_socket, active_socket_index = get_active_socket(node_tree, input_output='INPUT')

    if bpy.app.version < (4, 0, 0):
        sockets_propname = 'inputs'
        active_socket_propname = 'active_input'
    else:
        sockets_propname = 'items_tree'
        active_socket_propname = 'active_index'

    split = layout.row()

    if bpy.app.version < (4, 0, 0):
        split.template_list("HDRIMAKER_UL_node_interface_sockets", in_out, node_tree, sockets_propname,
                            node_tree,
                            active_socket_propname)

    else:
        split.template_list("HDRIMAKER_UL_node_interface_sockets", in_out, node_tree.interface, sockets_propname,
                            node_tree.interface,
                            active_socket_propname)

    ops_col = split.column()

    add_remove_col = ops_col.column(align=True)

    if bpy.app.version < (4, 0, 0):
        if in_out == 'INPUT':
            old_in_out = 'IN'
        elif in_out == 'OUTPUT':
            old_in_out = 'OUT'

        props = add_remove_col.operator("node.tree_socket_add", icon='ADD', text="")
        props.in_out = old_in_out
        props = add_remove_col.operator("node.tree_socket_remove", icon='REMOVE', text="")
        props.in_out = old_in_out
    else:
        props = add_remove_col.operator("node.interface_item_new", icon='ADD', text="")
        props.item_type = in_out
        if active_socket and (active_socket.item_type == 'SOCKET' and active_socket.in_out == 'INPUT'):
            add_remove_col.operator("node.interface_item_remove", icon='REMOVE', text="")

    ops_col.separator()

    up_down_col = ops_col.column(align=True)
    if bpy.app.version < (4, 0, 0):
        if in_out == 'INPUT':
            old_in_out = 'IN'
        elif in_out == 'OUTPUT':
            old_in_out = 'OUT'

        props = up_down_col.operator("node.tree_socket_move", icon='TRIA_UP', text="")
        props.in_out = old_in_out
        props.direction = 'UP'
        props = up_down_col.operator("node.tree_socket_move", icon='TRIA_DOWN', text="")
        props.in_out = old_in_out
        props.direction = 'DOWN'
    else:
        props = up_down_col.operator(Exa.ops_name + "move_socket", icon='TRIA_UP', text="")
        props.direction = 'UP'
        props.repr_socket = repr(active_socket)
        props = up_down_col.operator(Exa.ops_name + "move_socket", icon='TRIA_DOWN', text="")
        props.direction = 'DOWN'
        props.repr_socket = repr(active_socket)

    if active_socket:
        row = layout.row(align=True)
        if bpy.app.version < (4, 0, 0):
            # TODO: Controllare se nel rilascio di Blender 4.0 esisteranno ancora GLi Int Socket per i Node Group
            ngProp = get_ngprop(node_tree)
            row.prop(ngProp, 'NodeSocketType', text="")
            row.scale_x = 0.35

            # Per ora ci sono problemi con Blender 4.0 Lasciamo cosi
            socket_manager = row.operator(Exa.ops_name + "socket_manager", text="Change")
            socket_manager.options = 'CHANGE_SOCKET_TYPE'
            socket_manager.repr_node_group = repr(node_tree)
            socket_manager.repr_socket = repr(active_socket)

        else:
            row.label(text="Socket Type:")
            row.prop(active_socket, 'socket_type', text="")
            active_socket.draw(context, layout)


def draw_sockets(self, context, group, col, sockets_propname):
    """Funzione per la visualizzazione e costruzione dei nodi"""
    if not group:
        return

    active_socket, active_socket_index = get_active_socket(group.node_tree, input_output=sockets_propname)

    if not active_socket:
        return

    ngProp = get_ngprop(group.node_tree)

    # col.prop(scnProp, 'search_inputs', text="Search Inputs", icon='VIEWZOOM')
    # col.separator()
    input = active_socket
    sckProp = get_sckprop(input)

    input_nodes, output_nodes = get_in_out_group(group.node_tree)

    is_unused = True
    if sckProp.is_fake_socket:
        is_unused = False

    if is_linked_internal(active_socket):
        is_unused = False

    # if not scnProp.search_inputs.lower() in input.name.lower():
    #     return

    if sckProp.is_system_socket:
        return

    box_row = col.row()
    if is_unused: box_row.alert = True

    box = box_row.box()

    col1 = box.column(align=True)

    row = col1.row(align=True)
    row.alignment = 'RIGHT'
    show_helps_v2(layout=row, docs_key="SOCKET_OPTIONS")

    # row = col1.row(align=True)
    # # row.prop(sckProp, 'show_socket_menu', text="",
    # #          icon='DOWNARROW_HLT' if sckProp.show_socket_menu else 'RIGHTARROW', emboss=False)
    # row.template_node_socket(color=socket_types().get(group.inputs[idx].bl_idname))
    # row.scale_x = 0.5
    # row.label(text=str(idx))
    # row = row.row(align=True)
    # row.scale_x = 1.5
    # row.prop(input, 'name', text="")
    #
    # socket_manager = row.operator(Exa.ops_name+"socket_manager", text="", icon='X')
    # socket_manager.options = 'REMOVE_SOCKET'
    # socket_manager.node_groups = group.node_tree.name
    # socket_manager.group_inputs_idx = idx

    col1.separator()
    if is_unused:
        col1.label(text="This input is unused")

    col1.separator()

    row = col1.row(align=True)
    row.prop(sckProp, 'api_row_1', text="Row 1")
    row.prop(sckProp, 'api_row_2', text="Row 2")
    row.prop(sckProp, 'api_row_3', text="Row 3")
    row.prop(sckProp, 'api_row_4', text="Row 4")

    row = col1.row(align=True)
    row.prop(sckProp, 'api_col_separator', text="Separate Col")
    row.prop(sckProp, 'api_row_separator', text="Separate Row")
    row.prop(sckProp, 'api_double_rgb_operator', text="Switch Double RGB")

    row = col1.row(align=True)
    row.prop(sckProp, 'api_transparent_operator', text="Transparent OPS")
    row.prop(sckProp, 'api_sss_translucency', text="SSS Translucency OPS")
    row.prop(sckProp, 'api_screen_refraction', text="Raytracer OPS")

    row = col1.row(align=True)
    row.prop(sckProp, 'api_hide_text', text="Hide Text")
    row.prop(sckProp, 'api_add_color_lab', text="Color lab OPS")
    row.prop(sckProp, 'api_label_on_top', text="Label on top")

    row = col1.row(align=True)
    row.prop(sckProp, 'api_displace_alert', text="Displace Alert (for mapping)")
    row.prop(sckProp, 'api_hide_from_panel', text="Hide From Panel")

    if get_socket_type(input) in ['VALUE', 'INT']:
        row = col1.row(align=True)
        row.prop(sckProp, 'api_boolean', text="Bool OPS")
    else:
        row.label(text="")

    row = col1.row(align=True)

    row.prop(sckProp, 'is_api_enum', text="Enum Int Options")
    row.prop(sckProp, 'lock_prop', text="Lock Prop")

    row = col1.row(align=True)
    row.operator(Exa.ops_name + 'assign_color_ramp', text="Set Color Ramp", icon='ADD').options = 'SET'
    if sckProp.api_color_ramp:
        row.operator(Exa.ops_name + 'assign_color_ramp', text="Remove Color Ramp", icon='REMOVE').options = 'REMOVE'

    col1.separator()

    row = col1.row(align=True)
    row.prop(sckProp, 'api_scale_x', text="Row Scale x")
    row.prop(sckProp, 'api_scale_y', text="Row Scale y")

    if sckProp.api_boolean:
        col1.separator()
        col1.label(
            text="""If Bool is False Hide the Input(s) To separate use: "," (use the index number of the socket)""")
        row = col1.row(align=True)
        row.prop(sckProp, 'api_hide_prop_if_min', text="")
        row.scale_x = 0.5
        socket_manager = row.operator(Exa.ops_name + "socket_manager", text="Rectify")
        socket_manager.options = "HIDE_LIST_MIN"
        socket_manager.repr_node_group = repr(group.node_tree)
        socket_manager.repr_socket = repr(active_socket)

        col1.label(
            text="""If Bool is True Hide the Input(s) To separate use: "," (use the index number of the socket)""")
        row = col1.row(align=True)
        row.prop(sckProp, 'api_hide_prop_if_max', text="")
        row.scale_x = 0.5
        socket_manager = row.operator(Exa.ops_name + "socket_manager", text="Rectify")
        socket_manager.options = "HIDE_LIST_MAX"
        socket_manager.repr_node_group = repr(group.node_tree)
        socket_manager.repr_socket = repr(active_socket)

        col1.separator()

        col1.label(text="""If Bool is False (Min Value) Mute the Node(s) To separate use: "//" (Use the node name) """)
        row = col1.row(align=True)
        row.prop(sckProp, 'api_bool_mute_nodes_if_false', text="")
        # row.scale_x = 0.5
        # socket_manager = row.operator(Exa.ops_name+"socket_manager", text="Rectify")
        # socket_manager.options = "RECTIFY_MUTE_NODE_LIST_FALSE"
        # socket_manager.node_groups = group.node_tree.name
        # socket_manager.group_inputs_idx = idx

        col1.separator()

        col1.label(text="""If Bool is True (Min Value) Mute the Node(s) To separate use: "//" (Use the node name) """)
        row = col1.row(align=True)
        row.prop(sckProp, 'api_bool_mute_nodes_if_true', text="")
        # row.scale_x = 0.5
        # socket_manager = row.operator(Exa.ops_name+"socket_manager", text="Rectify")
        # socket_manager.options = "RECTIFY_MUTE_NODE_LIST_TRUE"
        # socket_manager.node_groups = group.node_tree.name
        # socket_manager.group_inputs_idx = idx

        col1.separator()

        row = col1.row(align=True)
        false = sckProp.api_icon_false if sckProp.api_icon_false in get_blender_icons() else 'NONE'
        true = sckProp.api_icon_true if sckProp.api_icon_true in get_blender_icons() else 'NONE'
        iconmanager = row.operator(Exa.ops_name + "icon_manager_panel", text="Icon If True: " + true,
                                   icon=true)
        iconmanager.options = "ICON_TRUE"
        iconmanager.repr_socket = repr(active_socket)

        iconmanager = row.operator(Exa.ops_name + "icon_manager_panel", text="Icon If False: " + false,
                                   icon=false)
        iconmanager.options = "ICON_FALSE"
        iconmanager.repr_socket = repr(active_socket)

        row = col1.row(align=True)
        icon_button = row.operator(Exa.ops_name + "icon_button", text="Remove True icon")
        icon_button.options = "REMOVE_ICON_TRUE"
        icon_button.repr_socket = repr(active_socket)

        icon_button = row.operator(Exa.ops_name + "icon_button", text="Remove False icon")
        icon_button.options = "REMOVE_ICON_FALSE"
        icon_button.repr_socket = repr(active_socket)

        col1.prop(sckProp, 'api_bool_invert', text="Invert checkbox")

        col1.separator()
        col1.prop(sckProp, 'api_text_if_true', text="Text if True")
        col1.prop(sckProp, 'api_text_if_false', text="Text if False")

    col1.separator()
    col1.prop(sckProp, 'api_bool_description', text="Description")

    if sckProp.api_label_on_top:
        col1.separator()
        row = col1.row(align=True)
        row.prop(sckProp, 'api_top_label_text', text="Additional label")
        row.prop(sckProp, 'api_keep_socket_label', text="Keep Socket Label")

    try:

        if hasattr(input, 'default_value'):
            col1.separator()
            row = col1.row()
            row.prop(input, 'default_value', text="Default Value")
    except:
        pass

    if "NodeSocketVector" in input.bl_socket_idname:
        col1.separator()
        row = col1.row(align=True)
        row.prop(input, 'min_value', text="Min Value")
        row.prop(input, 'max_value', text="Max Value")

    if sckProp.is_api_enum:
        col1.separator()
        add_enum = col1.operator(Exa.ops_name + "socket_manager", text="Set/Update this range as Enum Props",
                                 icon="EVENT_RETURN")
        add_enum.options = 'SET_API_ENUM'
        add_enum.repr_node_group = repr(group.node_tree)
        add_enum.repr_socket = repr(active_socket)

        col1.separator()
        row = col1.row()
        row.scale_x = 0.5
        row.label(text="Index:")
        row.scale_x = 1.5
        row.label(text="Name:")
        row.scale_x = 2
        row.label(text="Description:")
        for colidx, props in enumerate(sckProp.api_collection_idx):
            row = col1.row()
            row.scale_x = 0.5
            row.label(text=props.idx)
            row.scale_x = 1.5
            row.prop(props, 'name', text="")
            row.scale_x = 2
            row.prop(props, 'description', text="")
            row.scale_x = 1 if props.icon != 'NONE' else 0.25
            icon_ops = row.operator(Exa.ops_name + "icon_manager_panel", text="", icon=props.icon)
            icon_ops.options = 'ADD_ICON_TO_ENUM_SOCKET'
            icon_ops.socket_enum_idx = colidx
            icon_ops.repr_socket = repr(active_socket)

            if props.icon != 'NONE':
                remove_ops = row.operator(Exa.ops_name + "icon_button", text="", icon='CANCEL')
                remove_ops.options = 'REMOVE_ICON_FROM_ENUM_SOCKET'
                remove_ops.socket_enum_idx = colidx
                remove_ops.repr_socket = repr(active_socket)

        col1.prop(sckProp, 'api_enum_direction', text="Tab Direction")

    col1.separator()
    tag = sckProp.tag_socket if sckProp.tag_socket else 'None'
    tag_panel_utils = col1.operator(Exa.ops_name + "tag_panel_utils", text="Texture Manager Tag: '" + tag + "'")
    tag_panel_utils.options = 'TAG_SOCKET'
    tag_panel_utils.repr_socket = repr(input)
    if sckProp.tag_socket != '':
        col1.prop(sckProp, 'is_fake_socket', text="Show only texture manager")

    col1.separator()
    minibox = col1.box()
    row = minibox.row(align=True)
    row.label(text="Docs Key: {}".format(sckProp.docs_key))
    row.operator(Exa.ops_name + "copy_to_clipboard", text="To Clipboard").text = sckProp.docs_key

    # Otteniamo tutti gli items contenuti nella proprietà ngProp.random_socket se ne esistono ed esponiamole in una lista
    # di massimo 2 per riga
    if len(sckProp.random_socket[:]) > 0:
        random_box = col1.box()
        random_col = random_box.column(align=True)
        random_col.label(text="Active randoms:")
        for idx, item in enumerate(sckProp.random_socket):
            row = random_box.row(align=True)
            row.prop(item, 'mark_as_random', text=item.name)


class HDRIMAKER_PT_PanelBuilderHelper(bpy.types.Panel):
    bl_label = "Panel Builder Helper"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HDRi Maker"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return check_shader_area_ok(context)

    def draw(self, context):

        scn = context.scene
        scnProp = get_scnprop(scn)

        layout = self.layout

        def disable():
            text = "Attention, to use this menu, you must be inside a group node"
            wrap_text(layout=self.layout, string=text, text_length=60)

        if context.space_data.shader_type == 'WORLD':
            id_data = scn.world
            id_data_string = "bpy.data.worlds"
        elif context.space_data.shader_type == 'OBJECT':
            ob = context.object
            id_data = ob.active_material if ob and ob.active_material else None
            id_data_string = "bpy.data.worlds"

        if not id_data:
            disable()
            return

        node_tree = context.space_data.edit_tree
        if node_tree and node_tree.nodes:
            active_node = node_tree.nodes.active

        node_tree = context.space_data.edit_tree
        retrieve = retrieve_nodes(id_data.node_tree)
        group = next((n for n in retrieve if n.type == 'GROUP' if n.node_tree if n.node_tree == node_tree),
                     None)

        if not group:
            disable()
            return
        if not group.type == 'GROUP':
            disable()
            return
        if not group.node_tree:
            disable()
            return

        ngProp = get_ngprop(group.node_tree)
        id_name = ngProp.group_id_name

        layout.prop(group.node_tree, 'name', text="Group Name")
        layout.prop(ngProp, 'ng_description', text="Group Description")

        easypanel = layout.operator(Exa.ops_name + "easypanelops", text="HDRi Maker Panel Preview",
                                    icon='PROPERTIES')
        easypanel.options = 'SHOW_PANEL_PREVIEW'
        easypanel.id_data_string = id_data_string
        easypanel.id_data_name = id_data.name
        easypanel.node_groups = group.name

        draw_socket_list(self, context, "INPUT")

        col = self.layout.column(align=True)

        # draw_sockets(self, context, world, group, bcol, scnProp)

        draw_sockets(self, context, group, col, "INPUT")

        if is_node_group(node_tree):
            draw_all_custom_props(ngProp, layout)
