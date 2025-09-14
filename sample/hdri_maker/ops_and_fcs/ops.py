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

from bpy.props import StringProperty
from bpy.types import Operator

from .material_utility import restore_node_inputs_default_value
from ..exaproduct import Exa
from ..utility.utility import safety_eval


class HDRIMAKER_OT_restore_node_value(Operator):
    """Restore node to default values"""
    bl_idname = Exa.ops_name + "restore_node_value"
    bl_label = "Restore to default values"
    bl_options = {'INTERNAL', 'UNDO'}

    repr_node: StringProperty()

    @classmethod
    def description(cls, context, properties):
        return "Restore node to default values"

    def invoke(self, context, event):
        # Invoke confirm dialog
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        node = safety_eval(self.repr_node)
        restore_node_inputs_default_value(node)

        return {'FINISHED'}


class HDRIMAKER_OT_SelectObject(Operator):
    """Select object"""
    bl_idname = Exa.ops_name + "select_object"
    bl_label = "Select Object"
    bl_options = {'INTERNAL', 'UNDO'}

    target: StringProperty()

    def execute(self, context):
        # Check if object exists and is into the scene
        obj = context.scene.objects.get(self.target)
        if not obj:
            return {'CANCELLED'}
        # Deselect all objects
        for o in context.selected_objects:
            o.select_set(False)
        # Select the object
        obj.select_set(True)
        # Set the object as active
        context.view_layer.objects.active = obj

        return {'FINISHED'}
