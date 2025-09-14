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


def copy_scale_constraints(ob, name="Copy Scale", target=None, subtarget="",
                           use_x=True, use_y=True, use_z=True, power=1, use_make_uniform=False,
                           use_offset=False, use_add=False, target_space='WORLD', owner_space='WORLD',
                           space_object=None, space_subtarget=""):

    """Add a blender copy scale constraint to an object"""

    cons = ob.constraints.get(name)
    if not cons:
        cons = ob.constraints.new(type='COPY_SCALE')

    for key, value in locals().items():
        if key == 'ob':
            continue
        if hasattr(cons, key):
            setattr(cons, key, value)

    cons = ob.constraints.get(name)
    if not cons:
        cons = ob.constraints.new(type='COPY_SCALE')
        cons.name = name

    for key, value in locals().items():
        if key == 'ob':
            continue
        if hasattr(cons, key):
            setattr(cons, key, value)

    return cons


def limit_location_constraints(objs, hide=None, name="Limit Location",
                               use_min_x=False, use_min_y=False, use_min_z=False,
                               use_max_x=False, use_max_y=False, use_max_z=False,
                               min_x=0, min_y=0, min_z=0,
                               max_x=0, max_y=0, max_z=0,
                               owner_space='WORLD', influence=1, use_transform_limit=False):

    """Add a blender limit location constraint to an object"""

    # Check if objs is a list or a single object
    if not isinstance(objs, list):
        objs = [objs]

    for ob in objs:
        cons = ob.constraints.get(name)

        if hide is not None and cons:
            cons.enabled = hide
            break

        if not cons:
            cons = ob.constraints.new(type='LIMIT_LOCATION')
            cons.name = name

        for key, value in locals().items():
            if key == 'ob':
                continue
            if hasattr(cons, key):
                setattr(cons, key, value)



def limit_rotation_constraints(objs, hide=None, name="Limit Rotation",
                               use_limit_x=False, use_limit_y=False, use_limit_z=False,
                               min_x=0, min_y=0, min_z=0,
                               max_x=0, max_y=0, max_z=0,
                               owner_space='WORLD', influence=1, use_transform_limit=False):


    """Add a blender limit rotation constraint to an object"""

    # Check if objs is a list or a single object
    if not isinstance(objs, list):
        objs = [objs]

    for ob in objs:
        cons = ob.constraints.get(name)

        if hide is not None and cons:
            cons.enabled = hide
            break

        if not cons:
            cons = ob.constraints.new(type='LIMIT_ROTATION')
            cons.name = name

        for key, value in locals().items():
            if key == 'ob':
                continue
            if hasattr(cons, key):
                setattr(cons, key, value)

def limit_scale_constraints(objs, hide=None, name="Limit Scale",
                            use_min_x=True, use_min_y=True, use_min_z=True,
                            use_max_x=True, use_max_y=True, use_max_z=True,
                            min_x=1, min_y=1, min_z=1,
                            max_x=1, max_y=1, max_z=1,
                            owner_space='WORLD', influence=1, use_transform_limit=False):

    """Add a blender limit scale constraint to an object"""

    # Check if objs is a list or a single object
    if not isinstance(objs, list):
        objs = [objs]
    for ob in objs:
        cons = ob.constraints.get(name)
        if hide is not None and cons:
            cons.enabled = hide
            break

        if not cons:
            cons = ob.constraints.new(type='LIMIT_SCALE')
            cons.name = name

        for key, value in locals().items():
            if key == 'ob':
                continue
            if hasattr(cons, key):
                setattr(cons, key, value)


def damper_track_constraints(objs, name="Damped Track", target=None, track_axis='TRACK_NEGATIVE_Z', influence=1):

    """Add a blender damper track constraint to an object"""

    # Check if objs is a list or a single object
    if not isinstance(objs, list):
        objs = [objs]

    for ob in objs:
        cons = ob.constraints.get(name)
        if not cons:
            cons = ob.constraints.new(type='DAMPED_TRACK')
            cons.name = name

        for key, value in locals().items():
            if key == 'ob':
                continue
            if hasattr(cons, key):
                setattr(cons, key, value)
