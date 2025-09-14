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
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

from .dome_fc import get_environment_from_world, find_current_dome_version, \
    AssembleDome, Hooks, get_dome_objects, recreate_dome_handler
from ..exaconv import get_objprop, get_scnprop
from ..exaproduct import Exa
from ..utility.text_utils import draw_info
from ..utility.utility import set_object_mode, subdivide_mesh, un_subdivide_mesh, \
    set_object_bounds, get_vertices_from_vg, has_nodetree, set_active_object, hide_object, safety_eval


class HDRIMAKER_OT_move_wrap(Operator):

    bl_idname = Exa.ops_name + "move_wrap"
    bl_label = "Move Wrap"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('UP', "Up", ""), ('DOWN', "Down", "")))

    @classmethod
    def description(cls, context, properties):
        if properties.options == 'UP':
            desc = """Move the wrap up"""
        elif properties.options == 'DOWN':
            desc = """Move the wrap down"""
        return desc

    def execute(self, context):

        dome_parts = find_current_dome_version(context)
        dome_ground = dome_parts.get("dome_ground")
        if not dome_ground:
            return {'CANCELLED'}

        # Get active object if is mesh type
        obj = context.object
        if obj.type != 'MESH':
            return {'CANCELLED'}

        # Check if active object is into the the ground wrap modifier

        # Get the wrap modifier
        mods = dome_ground.modifiers
        wrap = next((m for m in mods if m.type == 'SHRINKWRAP' and m.target == obj), None)
        if not wrap:
            return {'CANCELLED'}

        # Get the wrap modifier index
        wrap_index = mods.find(wrap.name)

        # Se il modificatore precedente è di tipo 'SUBSURF' allora non posso spostare il wrap
        if wrap_index > 0 and mods[wrap_index - 1].type == 'SUBSURF' and self.options == 'UP':
            return {'CANCELLED'}

        # Se il modificatore successivo è di tipo 'CORRECTIVE_SMOOTH' allora non posso spostare il wrap
        if wrap_index < len(mods) - 1 and mods[wrap_index + 1].type == 'CORRECTIVE_SMOOTH' and self.options == 'DOWN':
            return {'CANCELLED'}

        from ..utility.modifiers import move_modifier_index
        # Move the wrap modifier up or down
        if self.options == 'UP':
            move_modifier_index(wrap, to_index=wrap_index - 1)
        elif self.options == 'DOWN':
            move_modifier_index(wrap, to_index=wrap_index + 1)

        return {'FINISHED'}

class HDRIMAKER_OT_domeHooks(Operator):
    bl_idname = Exa.ops_name + "domehooks"
    bl_label = "Dome Hooks"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('ADD', "Add", ""), ('REMOVE', "Remove", "")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'ADD':
            desc = "Add control points"
        elif properties.options == 'REMOVE':
            desc = "Remove control points"
        return desc

    def execute(self, context):
        scn = context.scene
        scnProp = get_scnprop(scn)
        scnProp.hide_hooks = False
        try:
            scnProp.hooks_display_type = 'SPHERE'
        except:
            pass

        set_object_mode(context.view_layer.objects.active)

        dome_parts = find_current_dome_version(context)
        dome_sky = dome_parts.get('dome_sky')
        dome_ground = dome_parts.get('dome_ground')

        if not dome_ground or not dome_sky:
            text = "Dome not found, the hooks can't be added"
            draw_info(text, "INFO", 'INFO')
            return {'CANCELLED'}

        if self.options == 'ADD':
            objProp = get_objprop(dome_sky)
            if objProp.dome_type not in ['CUBE', 'CYLINDER']:
                text = "At the moment only the CUBE and CYLINDER dome, can be have hooks."
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            Hk = Hooks(context, dome_parts)
            Hk.start()

        elif self.options == 'REMOVE':
            Hk = Hooks(context)
            Hk.remove_dome_hooks()

        return {'FINISHED'}

class HDRIMAKER_OT_dome(Operator):
    bl_idname = Exa.ops_name + "dome"
    bl_label = "Dome"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('ADD', "Add", ""), ('RELOAD', "Reload", ""), ('REMOVE', "Remove", ""),
                                 ('RESET_LEVEL', "Reset Level", ""), ('RESET_LOCATION', "Reset Location", ""),
                                 ('RESET_ROTATION', "Reset Rotation", ""), ('RESET_SCALE', "Reset Scale", ""),
                                 ('SHOW_HANDLER', "Show Handler", ""), ('RELOAD_DOME_HANDLER', "Reload Dome Handler", "")))

    @classmethod
    def description(cls, context, properties):

        desc = ""
        if properties.options == 'ADD':
            desc = "Add Dome"
        elif properties.options == 'RELOAD':
            desc = "Reload image into the dome"
        elif properties.options == 'REMOVE':
            desc = "Remove Dome"
        elif properties.options == 'RESET_LEVEL':
            desc = "Restore X and Y rotation to 0 keeping the Z rotation unchanged."
        elif properties.options == 'RESET_LOCATION':
            desc = "Restore the location of the dome to the origin (0, 0, 0)"
        elif properties.options == 'RESET_ROTATION':
            desc = "Restore the rotation of the dome on the Z axis to 0 (keeping the X and Y rotation unchanged)"
        elif properties.options == 'SHOW_HANDLER':
            desc = "Show the dome handler"
        elif properties.options == 'RELOAD_DOME_HANDLER':
            desc = "Reload the dome handler"

        return desc

    def execute(self, context):

        if self.options in ['RESET_LEVEL', 'RESET_LOCATION', 'RESET_ROTATION', 'RESET_SCALE', 'SHOW_HANDLER', 'RELOAD_DOME_HANDLER']:
            dome_objects = get_dome_objects()
            dome_handler = dome_objects.get('DOME_HANDLER')

            if self.options == 'RELOAD_DOME_HANDLER':
                recreate_dome_handler()
                return {'FINISHED'}

            if not dome_handler:
                text = "Dome Handler not found"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if self.options == 'RESET_LEVEL':
                dome_handler.rotation_euler = (0, 0, dome_handler.rotation_euler[2])
                set_active_object(dome_handler)

            if self.options == 'RESET_LOCATION':
                dome_handler.location = (0, 0, 0)
                set_active_object(dome_handler)

            if self.options == 'RESET_ROTATION':
                dome_handler.rotation_euler = (dome_handler.rotation_euler[0], dome_handler.rotation_euler[1], 0)
                set_active_object(dome_handler)

            if self.options == 'RESET_SCALE':
                dome_handler.scale = (1, 1, 1)
                set_active_object(dome_handler)

            if self.options == 'SHOW_HANDLER':
                hide_object(dome_handler, hide=False)

            return {'FINISHED'}


        scn = context.scene
        scnProp = get_scnprop(scn)
        scnProp.hide_dome = False
        scnProp.show_dome_wireframe = False

        set_object_mode(context.view_layer.objects.active)

        if self.options in ['ADD', 'RELOAD']:
            if bpy.app.version >= (4, 2, 0):
                scn.eevee.use_raytracing = True

            world = scn.world
            if not world or not has_nodetree(world):
                text = "Before adding a dome, you must add a world background"
                draw_info(text, "INFO", 'INFO')
                return {'CANCELLED'}
            # bpy.ops.hdrimaker.addbackground(environment='COMPLETE', invoke_browser=False)
            # world = scn.world

            environment = get_environment_from_world(world)
            # node_group = environment.get('node_group') <-- this is not used for now.

            image = environment.get('image')
            if not image:
                text = "No image is present in the world, so it is not possible to create the DOME, since the DOME is based on an image," \
                       " so before creating the DOME, you must create a world using an image. You can also import an image from a file. To do this, hold down " \
                       "SHIFT or CTRL and click on 'Add' in the HDRi Maker panel and select the image to import."
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            if self.options == 'RELOAD':
                if image:
                    A_Dome = AssembleDome(context, image=image, dome_name="DOME_" + world.name)
                    A_Dome.asign_image_to_dome()
                    return {'FINISHED'}

            from ..light_studio.sun_ops import get_sun_sinc_driver
            sun_drivers = get_sun_sinc_driver(world.node_tree)

            Hooks(context).remove_dome_hooks()
            # In this case we have an image in the world, and the image is used as environment, so we can use it as dome
            ADome = AssembleDome(context, image=image, dome_name="DOME_" + world.name)
            ADome.start()

            if sun_drivers:
                from ..light_studio.sun_ops import sync_sun
                sync_sun(context, options='SYNC')

        elif self.options == 'REMOVE':
            ADome = AssembleDome(context)
            ADome.remove_all()


        return {'FINISHED'}

class HDRIMAKER_OT_SubdivideDomeGround(Operator):
    """Subdivide The Dome Ground"""

    bl_idname = Exa.ops_name + "subdividedomeground"
    bl_label = "Subdivide Dome Ground"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('SUBDIVIDE', "Subdivide", ""), ('UNSUBDIVIDE', "Un-subdivide", "")))
    max_vertices_count = 50000  # The maximum number of vertices allowed in the dome Ground

    def execute(self, context):
        dome_parts = find_current_dome_version(context)
        dome_ground = dome_parts.get('dome_ground')
        dome_sky = dome_parts.get('dome_sky')

        objProp = get_objprop(dome_ground)

        if not dome_ground:
            text = "Dome is not present in the current scene, so it is not possible to subdivide the ground."
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if dome_ground.mode != 'OBJECT':
            set_object_mode(dome_ground)

        if self.options == 'SUBDIVIDE':
            vertices_count = len(get_vertices_from_vg(dome_ground, "Ground"))
            if vertices_count > self.max_vertices_count:
                text = "To avoid slowdown problems, the maximum allowed number of subdivisions for the ground of the Dome " \
                       "has already been reached. It is not possible to increase. At the moment the number of vertices is: " \
                       + str(vertices_count) + " The next step would bring the vertices to about: " \
                       + str(vertices_count * 4) + " which is too much."
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            # By using bmesh, we can subdivide the ground, only the vertices into the vertex group "Ground" will be subdivided
            subdivide_mesh(dome_ground, vertex_group="Ground", cuts=1, len_vertices=False, use_grid_fill=False)
            objProp.subdivision_step += 1

            return {'FINISHED'}

        elif self.options == 'UNSUBDIVIDE':

            if objProp.subdivision_step < 1:
                text = "The minimum subdivision step is 0"
                draw_info(text, "Info", 'INFO')
                return {'CANCELLED'}

            un_subdivide_mesh(dome_ground, vertex_group="Ground", iterations=2)
            objProp.subdivision_step -= 1

        return {'FINISHED'}

class HDRIMAKER_OT_SetObjectView(Operator):
    """Toggles the visibility of the object in the viewport"""

    bl_idname = Exa.ops_name + "setobjectview"
    bl_label = "Toggle Object View"
    bl_options = {'INTERNAL', 'UNDO'}

    display_type: EnumProperty(items=(('TEXTURED', "Textured", ""), ('BOUNDS', "Bounds", "")))
    object_name: StringProperty()

    def execute(self, context):

        ob = bpy.data.objects.get(self.object_name)

        if ob.type != 'MESH':
            text = "Please select a mesh type object"
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if not ob:
            text = "Dome is not present in the current scene, so it is not possible to set the object view."
            draw_info(text, "Info", 'INFO')
            return {'CANCELLED'}

        if self.display_type == 'BOUNDS':
            # In this case, the object need to be showed only in the viewport with the display_type = 'BOUNDS'
            set_object_bounds(ob, display_type='BOUNDS')

        elif self.display_type == 'TEXTURED':
            # In this case, the object need to be showed in the viewport and in the render
            set_object_bounds(ob, display_type='TEXTURED')

        return {'FINISHED'}

class HDRIMAKER_OT_toggle_hide_object(Operator):

    bl_idname = Exa.ops_name + "toggle_hide_object"
    bl_label = "Toggle Hide Object"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('HIDE', "Hide", ""), ('UNHIDE', "Unhide", "")))
    repr_object: StringProperty()

    def execute(self, context):
        obj = safety_eval(self.repr_object)

        if self.options == 'HIDE':
            hide_object(obj, hide=True, use_hide_viewport=True, use_hide_set=True)
        elif self.options == 'UNHIDE':
            hide_object(obj, hide=False, use_hide_viewport=True, use_hide_set=True)

        return {'FINISHED'}



class HDRIMAKER_OT_store_hook_location(Operator):
    bl_idname = Exa.ops_name + "store_hook_location"
    bl_label = "Store Hook Location"
    bl_options = {'INTERNAL', 'UNDO'}

    options: EnumProperty(items=(('STORE', "Store", ""), ('REMOVE', "Remove", "")))

    @classmethod
    def description(cls, context, properties):
        desc = ""
        if properties.options == 'STORE':
            desc = "Store Hook Location"
        elif properties.options == 'REMOVE':
            desc = "Remove Hook Location"
        return desc

    def execute(self, context):
        dome_parts = find_current_dome_version(context)
        dome_ground = dome_parts.get('dome_ground')
        if not dome_ground:
            return {'CANCELLED'}

        if self.options == 'STORE':
            pass

        elif self.options == 'REMOVE':
            pass

        return {'FINISHED'}


