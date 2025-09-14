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


# Default Blender scene.render attributes
import time

import bpy


def cycles_render_set_background_360(scene):
    """Set the scene.render attributes for a 360 background render. and the scene.cycles attributes for a 360 background render."""

    render = {'resolution_precentage': 100,
              'pixel_aspect_x': 1,
              'pixel_aspect_y': 1,
              'use_border': False,
              'use_crop_to_border': False,
              'thread_mode': 'AUTO',
              'use_persistent_data': False,
              'preview_pixel_size': 'AUTO',
              'engine': 'CYCLES'}

    # cycles.samples is not included in this cycles attributes because,
    # This is a standard preset for the render, the number of samples is set by the user

    cycles = {'feature_set': 'SUPPORTED',
              'adaptive_threshold': 0.01,
              'adaptive_min_samples': 0,
              'time_limit': 0,
              'max_bounces': 12,
              'diffuse_bounces': 8,
              'glossy_bounces': 4,
              'transmission_bounces': 12,
              'volume_bounces': 0,
              'transparent_max_bounces': 8,
              'sample_clamp_direct': 0,
              'sample_clamp_indirect': 10,
              'blur_glossy': 1,
              'caustic_reflective': True,
              'caustic_refractive': True,
              'use_auto_tile': True,
              'tile_size': 256,
              'use_spatial_splits': False,
              'debug_bvh_time_steps': 0,
              'debug_use_hair_bvh': True,
              'debug_use_compact_bvh': False}

    for key, value in render.items():
        if hasattr(scene.render, key):
            setattr(scene.render, key, value)

    for key, value in cycles.items():
        if hasattr(scene.cycles, key):
            setattr(scene.cycles, key, value)

    scene.update_tag()
    bpy.context.view_layer.update()


def cycles_render_set_preview(scene):
    render = {'resolution_precentage': 100,
              'pixel_aspect_x': 1,
              'pixel_aspect_y': 1,
              'use_border': False,
              'use_crop_to_border': False,
              'thread_mode': 'AUTO',
              'use_persistent_data': False,
              'preview_pixel_size': 'AUTO',
              'engine': 'CYCLES'}

    cycles = {'feature_set': 'SUPPORTED',
              'adaptive_threshold': 0.01,
              'samples': 16,
              'adaptive_min_samples': 0,
              'time_limit': 0,
              'max_bounces': 12,
              'diffuse_bounces': 8,
              'glossy_bounces': 4,
              'transmission_bounces': 12,
              'volume_bounces': 0,
              'transparent_max_bounces': 8,
              'sample_clamp_direct': 0,
              'sample_clamp_indirect': 10,
              'blur_glossy': 1,
              'caustic_reflective': True,
              'caustic_refractive': True,
              'use_auto_tile': True,
              'tile_size': 256,
              'use_spatial_splits': False,
              'debug_bvh_time_steps': 0,
              'debug_use_hair_bvh': True,
              'debug_use_compact_bvh': False,
              'use_denoising': False}

    # Qui sono le vecchie api di Blender inferiori alla versione 3.0
    if bpy.app.version < (3, 0, 0):
        if hasattr(scene.render, 'tile_x'):
            scene.render.tile_x = scene.render.tile_y = cycles.get('tile_size')

    for key, value in render.items():
        if hasattr(scene.render, key):
            setattr(scene.render, key, value)

    for key, value in cycles.items():
        if hasattr(scene.cycles, key):
            setattr(scene.cycles, key, value)

    scene.update_tag()
    bpy.context.view_layer.update()


def output_image_settings(scene, filepath, file_format):
    """Set The output image settings for the render"""

    available = bpy.types.ImageFormatSettings.bl_rna.properties['file_format'].enum_items_static.keys()

    if not file_format in available:
        print("The type" + file_format + " not found in " + available)

    render = {'filepath': filepath,
              'use_file_extension': True,
              'use_render_cache': False,
              'use_overwrite': True,
              'use_placeholder': False}

    if file_format == 'PNG':
        image_settings = {'file_format': file_format,
                          'color_mode': 'RGBA',
                          'color_depth': '16',
                          'color_management': 'FOLLOW_SCENE',
                          'compression': 15}

    elif file_format == 'HDR':
        image_settings = {'file_format': file_format,
                          'color_mode': 'RGB'}

    elif file_format == 'WEBP':
        image_settings = {'file_format': file_format,
                          'color_mode': 'RGBA',
                          'compression': 15}

    for key, value in render.items():
        if hasattr(scene.render, key):
            setattr(scene.render, key, value)

    for key, value in image_settings.items():
        if hasattr(scene.render.image_settings, key):
            setattr(scene.render.image_settings, key, value)

    bpy.context.view_layer.update()


def try_render(scene, filepath, file_format, resolution=(), animation=False, write_still=True, invoke='EXEC_DEFAULT',
               fc_on_finish=None, fc_on_cancel=None, ):
    """Try to render the scene, fc_on_finish and fc_on_cancel are functions that will be called when the render is finished or canceled,
    for example: fc_on_finish can call a function that load the finished render in the viewport,
    render_attributes: accept a dictionary with the render attributes, for example: {'resolution_x': 1920, 'resolution_y': 1080}"""

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]

    output_image_settings(scene, filepath, file_format)

    if fc_on_finish and fc_on_cancel:
        # The handler need to be external to this function
        bpy.app.handlers.render_complete.append(fc_on_finish)
        bpy.app.handlers.render_cancel.append(fc_on_cancel)

    try:
        # In this case try to render with GPU, in some cases it can fail, GPU Ram is not enough
        scene.cycles.device = 'GPU'
        bpy.ops.render.render(invoke, animation=animation, write_still=write_still, scene=scene.name)
    except:
        scene.cycles.device = 'CPU'
        bpy.ops.render.render(invoke, animation=animation, write_still=write_still, scene=scene.name)

