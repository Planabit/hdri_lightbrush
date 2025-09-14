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
from mathutils import Vector
from numpy import mean

from ...collections_scene.collection_fc import get_dome_collection
from ...dome_tools.dome_fc import get_dome_objects
from ...utility.constraints import limit_location_constraints, limit_rotation_constraints
from ...utility.utility import Mtrx, get_view_3d_area, hide_object, lock_object, set_active_object, deselect_all


class ObjectCallback:
    skip_update = False


def update_un_lock_dome_handler(self, context):
    """Switch between lock and unlock the dome handler for manual manipulation"""
    dome_objects = get_dome_objects()
    dome_handler = dome_objects.get('DOME_HANDLER')
    dome_reflection_plane = dome_objects.get('DOME_REFLECTION_PLANE')
    if not dome_handler:
        return

    status = False if self.un_lock_dome_handler else True

    if dome_handler:
        if self.un_lock_dome_handler is False:
            ObjectCallback.skip_update = True
            self.scale_dome_handler = 1
            # Riporta il dome al centro della scena se disattivata la proprietà
            dome_handler.location = (0, 0, 0)
            dome_handler.rotation_euler = (0, 0, 0)
            dome_handler.scale = (1, 1, 1)

        hide_object(dome_handler, hide=status)
        lock_object(dome_handler, hide_select=status, location=(status, status, status), rotation=(status, status, status), scale=(status, status, status))

        limit_location_constraints(dome_handler, hide=status)
        limit_rotation_constraints(dome_handler, hide=status)

        if self.un_lock_dome_handler:
            # Set active object as the dome handler
            set_active_object(dome_handler)
        else:
            if context.view_layer.objects.active == dome_handler:
                # Potrebbe essere che il dome handler rimanga attivo e selezionato anche se è stato disattivato,
                # quindi va deselezionato e rimosso come attivo
                deselect_all()


    if dome_reflection_plane:
        lock_object(dome_reflection_plane, hide_select=True,
                    location=(status, status, status), rotation=(status, status, status), scale=(False, False, False))

        limit_location_constraints(dome_reflection_plane, hide=status)
        limit_rotation_constraints(dome_reflection_plane, hide=status)



def update_expand_hooks(self, context):

    tools_col = get_dome_collection(create=False)
    if not tools_col:
        return

    for ob in tools_col.objects:
        if ob.hdri_prop_obj.object_id_name == 'DOME_HOOK':
            ob.location = Mtrx(ob, ob.location[:], self.expand_hooks).scale_vertex()


def update_scale_dome_handler(self, context):
    """Update scale dome handler"""
    if ObjectCallback.skip_update:
        ObjectCallback.skip_update = False
        return
    
    ob = self.id_data
    scale = self.scale_dome_handler
    ob.scale = (scale, scale, scale)


def update_alpha(self, context):
    objProp = context.object.hdri_prop_obj
    for s in context.object.material_slots:
        if s.material:
            if s.material.hdri_prop_mat.mat_id_name == 'EEVEE_SHADOW_CATCHER':
                if bpy.app.version < (4, 2, 0):
                    s.material.blend_method = objProp.alpha_mode
                else:
                    s.material.surface_render_method = objProp.alpha_mode



def update_hide_full(self, context):
    ob = self.id_data
    hide_object(ob, self.hide_full)


def update_show_wireframe(self, context):
    area = get_view_3d_area()
    if not area:
        return

    obj = self.id_data
    objProp = obj.hdri_prop_obj
    if objProp.show_wireframe:
        obj.show_wire = True
        area.overlay.show_overlays = True

    else:
        obj.show_wire = False




def update_subdivision(self, context):
    ob = self.id_data
    subdivision_modifier = next((mod for mod in ob.modifiers if mod.type == 'SUBSURF'), None)

    if subdivision_modifier:
        subdivision_modifier.levels = self.subdivision
        subdivision_modifier.render_levels = self.subdivision




def get_locationX(self):
    return self.get('locationX', 0)

def set_locationX(self, value):
    obj = self.id_data

    x_axis = Vector((1, 0, 0))
    delta = value - self.get('locationX', 0)
    v = (obj.matrix_world.to_3x3() @ x_axis).normalized()
    obj.matrix_world.translation += delta * v
    self.locationX = value


def get_locationY(self):
    return self.get('locationY', 0)


def set_locationY(self, value):
    y_axis = Vector((0, 1, 0))
    delta = value - self.get('locationY', 0)
    v = (self.matrix_world.to_3x3() @ y_axis).normalized()
    self.matrix_world.translation += delta * v
    self['locationY'] = value


def get_locationZ(self):
    return self.get('locationZ', 0)

def set_locationZ(self, value):
    z_axis = Vector((0, 0, 1))
    delta = value - self.get('locationZ', 0)
    v = (self.matrix_world.to_3x3() @ z_axis).normalized()
    self.matrix_world.translation += delta * v
    self['locationZ'] = value


