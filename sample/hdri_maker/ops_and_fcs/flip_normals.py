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
from bpy.props import StringProperty
from bpy.types import Operator

from ..exaproduct import Exa


class HDRIMAKER_OT_FlipNormals(Operator):

    bl_idname = Exa.ops_name + "flip_normals"
    bl_label = "Flip Normals"
    bl_description = "Flip normals of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    target: StringProperty()

    def execute(self, context):

        ob = bpy.data.objects.get(self.target)
        if not ob:
            text = "No object found with name: " + self.target
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        if ob.type != 'MESH':
            text = "Object is not a mesh: " + self.target
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        if ob.mode == 'EDIT':
            text = "Object is in edit mode: " + self.target + ". Please exit edit mode and try again."
            self.report({'ERROR'}, text)
            return {'CANCELLED'}

        # Flip normal face using bmesh module
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.to_mesh(ob.data)
        bm.free()

        return {'FINISHED'}
