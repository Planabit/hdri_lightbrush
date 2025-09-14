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

def complete_format():
    """This is the Blender complete format supported"""
    cf = (
        ".png", ".jpg", ".bmp", ".sgi", ".rgb", ".bw", ".jpeg", ".jp2", ".j2c", ".tga", ".cin", ".dpx", ".exr", ".hdr",
        ".tif", ".tiff", ".mov", ".mpg", ".mpeg", ".dvd", ".vob", ".mp4", ".avi", ".dv", ".ogg", ".ogv", ".mkv", ".flv")
    return cf


def socket_forbidden():
    sf = ['NodeSocketBool', 'NodeSocketVectorDirection', 'NodeSocketString']
    return sf

def socket_types():
    # Colore dei sockets
    st = {'NodeSocketBool': (0.6, 0.6, 0, 1),
          'NodeSocketColor': (0.7, 0.7, 0, 0),
          'NodeSocketFloat': (0.6, 0.6, 0.6, 1),
          'NodeSocketFloatAngle': (0.6, 0.6, 0.6, 1),
          'NodeSocketFloatFactor': (0.6, 0.6, 0.6, 1),
          'NodeSocketFloatPercentage': (0.6, 0.6, 0.6, 1),
          'NodeSocketFloatTime': (0.6, 0.6, 0.6, 1),
          'NodeSocketFloatUnsigned': (0.6, 0.6, 0.6, 1),
          'NodeSocketInt': (0, 0.6, 0.4, 1),
          'NodeSocketIntFactor': (0, 0.6, 0.4, 1),
          'NodeSocketIntPercentage': (0, 0.6, 0.4, 1),
          'NodeSocketIntUnsigned': (0, 0.6, 0.4, 1),
          'NodeSocketShader': (0, 0.9, 0.8, 1),
          'NodeSocketString': (0.4, 0.4, 0.4, 1),
          'NodeSocketVector': (0.350, 0.350, 1, 1),
          'NodeSocketVectorAcceleration': (0.350, 0.350, 1, 1),
          'NodeSocketVectorDirection': (0.350, 0.350, 1, 1),
          'NodeSocketVectorEuler': (0.350, 0.350, 1, 1),
          'NodeSocketVectorTranslation': (0.350, 0.350, 1, 1),
          'NodeSocketVectorVelocity': (0.350, 0.350, 1, 1),
          'NodeSocketVectorXYZ': (0.350, 0.350, 1, 1)}

    return st

def mat_info_example():
    from ..exaproduct import Exa
    product_name = Exa.product.lower()

    mi = {"date": "",
          "storage_info": {
              "permission": None,
              "json_version": 1.0,
              "storage_method": None,
              "blender_version": bpy.app.version,
              product_name + "version": Exa.blender_manifest['version']
          },
          "material_info": {
              "material_name": None,
              "author": None,
              "website_name": None,
              "website_url": None,
              "license": None,
              "license_description": None,
              "license_link": None
          },
          "group_inputs_properties": {

          },
          "material_properties": {
              "use_screen_refraction": False,
              "use_sss_translucency": False,
              "blend_method": "OPAQUE",
              "shadow_method": "OPAQUE",
              "use_backface_culling": False,
              "alpha_threshold": 0.5,
              "refraction_depth": 0.0
          }
          }
    return mi

def module_outputs():
    module_outputs = {0: {'name': 'Transparent', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      1: {'name': 'Base Color', 'bl_socket_idname': 'NodeSocketColor', 'default_value': (1.0, 1.0, 1.0, 1.0)},
                      2: {'name': 'Subsurface', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      3: {'name': 'Subsurface Radius', 'bl_socket_idname': 'NodeSocketVector', 'default_value': (1.0, 0.2, 0.1), 'min_value': 0, 'max_value': 1},
                      4: {'name': 'Subsurface Color', 'bl_socket_idname': 'NodeSocketColor', 'default_value': (1,1,1,1)},
                      5: {'name': 'Metallic', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      6: {'name': 'Specular', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      7: {'name': 'Specular Tint', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      8: {'name': 'Roughness', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      9: {'name': 'Anisotropic', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      10: {'name': 'Anisotropic Rotation', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      11: {'name': 'Sheen', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      12: {'name': 'Sheen Tint', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      13: {'name': 'Clearcoat', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      14: {'name': 'Clearcoat Roughness', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      15: {'name': 'IOR', 'bl_socket_idname': 'NodeSocketFloat', 'default_value': 1.45, 'min_value': 0, 'max_value': 1000},
                      16: {'name': 'Transmission', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      17: {'name': 'Transmission Roughness', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      18: {'name': 'Emission', 'bl_socket_idname': 'NodeSocketColor', 'default_value': (0, 0, 0, 1)},
                      19: {'name': 'Emission Strength', 'bl_socket_idname': 'NodeSocketFloat', 'default_value': 0, 'min_value': 0, 'max_value': 6.80564e+38},
                      20: {'name': 'Alpha', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 1, 'min_value': 0, 'max_value': 1},
                      21: {'name': 'Bump Strength', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      22: {'name': 'Bump Distance', 'bl_socket_idname': 'NodeSocketFloat', 'default_value': 0, 'min_value': 0, 'max_value': 1000},
                      23: {'name': 'Bump Height', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      24: {'name': 'Normal Strength', 'bl_socket_idname': 'NodeSocketFloat', 'default_value': 0, 'min_value': 0, 'max_value': 10},
                      25: {'name': 'Normal Color', 'bl_socket_idname': 'NodeSocketColor', 'default_value': (0.503, 0.503, 1 ,1)},
                      26: {'name': 'Clearcoat Bump Strength', 'bl_socket_idname': 'NodeSocketFloatFactor', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      27: {'name': 'Clearcoat Bump Distance', 'bl_socket_idname': 'NodeSocketFloat', 'default_value': 0, 'min_value': 0, 'max_value': 1000},
                      28: {'name': 'Clearcoat Bump Height', 'bl_socket_idname': 'NodeSocketFloat', 'default_value': 0, 'min_value': 0, 'max_value': 1},
                      29: {'name': 'Clearcoat Normal Strength', 'bl_socket_idname': 'NodeSocketFloat', 'default_value': 0, 'min_value': 0, 'max_value': 10},
                      30: {'name': 'Clearcoat Normal Color', 'bl_socket_idname': 'NodeSocketColor', 'default_value': (0.503, 0.503, 1,1)},
                      31: {'name': 'Tangent', 'bl_socket_idname': 'NodeSocketVector', 'default_value': (0, 0, 0), 'min_value': 0, 'max_value': 6.80564e+38},
                      32: {'name': 'Volume', 'bl_socket_idname': 'NodeSocketShader'}}
    return module_outputs




