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

from ..utility.utility import use_temp_override


def add_corrective_smooth(ob, name="", vertex_group=None, show_expanded=False, smooth_type='LENGTH_WEIGHTED'):
    """Add Corrective Smooth modifier to object"""

    smooth = ob.modifiers.new(name=name, type='CORRECTIVE_SMOOTH')
    smooth.iterations = 5
    smooth.use_only_smooth = True
    smooth.show_expanded = show_expanded
    smooth.smooth_type = smooth_type
    if vertex_group:
        smooth.vertex_group = vertex_group

    return smooth

def add_shrinkwrap(ob, target,name="", vertex_group=None, show_expanded=False):
    """Add Shrinkwrap to object, with target"""

    shrinkwrap = ob.modifiers.new(name=name, type='SHRINKWRAP')
    shrinkwrap.target = target
    shrinkwrap.wrap_method = 'PROJECT'
    shrinkwrap.use_negative_direction = True
    shrinkwrap.use_positive_direction = True
    shrinkwrap.use_project_z = True
    shrinkwrap.show_expanded = show_expanded
    if vertex_group:
        shrinkwrap.vertex_group = vertex_group

    return shrinkwrap

def add_hook_modifier(obj, hook_obj, name="",  vertices=[], center=None, show_expanded=False):
    mod = obj.modifiers.new(
        name=name,
        type='HOOK',
    )
    mod.object = hook_obj
    vertex_indices = [v.index for v in vertices]
    mod.vertex_indices_set(vertex_indices)
    # mod.center = self.dome.matrix_world @ lower_vertex.co
    mod.show_expanded = show_expanded
    if center:
        mod.center = center

    return mod

def add_subdivision_surface(ob, name="", subdivision_type='SIMPLE', levels=1, render_levels=1,
                            show_only_control_edges=False, use_limit_surface=True, quality=3,
                            uv_smooth='PRESERVE_BOUNDARIES', boundary_smooth='ALL', use_creases=True,
                            use_custom_normals=False, show_expanded=False):
    """Add Subdivision Surface modifier to object"""

    subd = ob.modifiers.new(name=name, type='SUBSURF')
    subd.subdivision_type = subdivision_type
    subd.levels = levels
    subd.render_levels = render_levels
    subd.show_only_control_edges = show_only_control_edges
    subd.use_limit_surface = use_limit_surface
    subd.quality = quality
    subd.uv_smooth = uv_smooth
    subd.boundary_smooth = boundary_smooth
    subd.use_creases = use_creases
    subd.use_custom_normals = use_custom_normals
    subd.show_expanded = show_expanded

    return subd


def move_modifier_index(mod, to_index=-1):
    """Move modifier to index"""
    ob = mod.id_data
    modifiers = ob.modifiers
    c = {"object": ob, "active_object": ob}

    if to_index == -1:
        to_index = len(modifiers) - 1

    if use_temp_override():
        # Use bpy.context.temp_override if the version is 3.2 or higher
        with bpy.context.temp_override(object=ob):
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=to_index)

    else:
        bpy.ops.object.modifier_move_to_index(c, modifier=mod.name, index=to_index)

    modifiers.update()

def remove_all_modifiers(ob):
    """Remove all modifiers from object"""
    # Using reverse and pop
    for mod in reversed(ob.modifiers):
        ob.modifiers.remove(mod)

def remove_empty_shrinkwrap_modifiers(ob):
    """Remove all empty shrinkwrap modifiers from object"""
    # Using reverse and pop
    for mod in reversed(ob.modifiers):
        if mod.type == 'SHRINKWRAP' and mod.target is None:
            ob.modifiers.remove(mod)

