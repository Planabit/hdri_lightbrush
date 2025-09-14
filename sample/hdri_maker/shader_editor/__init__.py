from .shader_editor_ops.assign_color_ramp import HDRIMAKER_OT_assign_color_ramp
from .shader_editor_ops.ot_get_shadernodes_info import HDRIMAKER_OT_CreateShaderNodesProperties
from .shader_editor_ops.ot_icon_button import HDRIMAKER_OT_icon_button
from .shader_editor_ops.ot_import_texture import HDRIMAKER_OT_ImportTexture
from .shader_editor_ops.ot_library_manipulator import HDRIMAKER_OT_LibraryManipulator
from .shader_editor_ops.ot_move_socket import HDRIMAKER_OT_move_socket
from .shader_editor_ops.ot_nodes_utility import HDRIMAKER_OT_NodesUtility, HDRIMAKER_OT_StoreNodesAttributes, \
    HDRIMAKER_OT_CopyNodeDescriptionToClipboard
from .shader_editor_ops.ot_pt_icon_manager_panel import HDRIMAKER_OT_icon_manager_panel
from .shader_editor_ops.ot_pt_tag_panel_ops import HDRIMAKER_OT_tag_panel_utils
from .shader_editor_ops.ot_redraw_previews import HDRIMAKER_OT_RedrawAllPreviews
from .shader_editor_ops.ot_save_node_group import HDRIMAKER_OT_SaveNodeGroup
from .shader_editor_ops.ot_socket_manager import HDRIMAKER_OT_socket_manager
from .shader_editor_ops.ot_tag_node_socket import HDRIMAKER_OT_tag_node_socket

from .shader_editor_ui.pt_color_lab import HDRIMAKER_PT_ColorLabUtility
from .shader_editor_ui.pt_library_creator_utility import HDRIMAKER_PT_LibraryCreatorUtility
from .shader_editor_ui.pt_node_utility import HDRIMAKER_PT_NodeUtility
from .shader_editor_ui.pt_panel_builder_helper import HDRIMAKER_PT_PanelBuilderHelper, \
    HDRIMAKER_UL_node_interface_sockets
from .shader_editor_ui.pt_shader_editor import HDRIMAKER_PT_ShaderEditor
from .shader_editor_ui.pt_texture_editor import HDRIMAKER_PT_TextureBrowser

shader_editor_classes = [HDRIMAKER_OT_NodesUtility,
                         HDRIMAKER_OT_CreateShaderNodesProperties,
                         HDRIMAKER_OT_tag_node_socket,
                         HDRIMAKER_OT_tag_panel_utils,
                         HDRIMAKER_OT_socket_manager,
                         HDRIMAKER_OT_move_socket,
                         HDRIMAKER_OT_SaveNodeGroup,
                         HDRIMAKER_OT_LibraryManipulator,
                         HDRIMAKER_PT_ShaderEditor,
                         HDRIMAKER_OT_icon_button,
                         HDRIMAKER_OT_icon_manager_panel,
                         HDRIMAKER_PT_TextureBrowser,
                         HDRIMAKER_OT_ImportTexture,
                         HDRIMAKER_PT_NodeUtility,
                         HDRIMAKER_PT_LibraryCreatorUtility,
                         HDRIMAKER_PT_PanelBuilderHelper,
                         HDRIMAKER_UL_node_interface_sockets,
                         HDRIMAKER_PT_ColorLabUtility,
                         HDRIMAKER_OT_StoreNodesAttributes,
                         HDRIMAKER_OT_CopyNodeDescriptionToClipboard,
                         HDRIMAKER_OT_RedrawAllPreviews,
                         HDRIMAKER_OT_assign_color_ramp
                         ]
