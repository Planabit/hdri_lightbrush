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
from bpy.types import Operator

from ...exaproduct import Exa

def get_sys_info_dict():
    def get_string(ob):
        if type(ob) == str:
            return ob
        if type(ob) in [int, float, bool, list, tuple, dict]:
            return str(ob)
        if type(ob) == bytes:
            return ob.decode('utf-8')
        return "Unknown"



    sys_info = {}

    # Prepariamo un dizionario con le informazioni di sistema, deve contenere:
    # - versione di Blender
    # - versione di HDRIMaker
    # - versione di CPU
    # - versione di GPU
    # - versione di sistema operativo
    # - Branch di Blender

    # Os Version:
    import platform

    gpu_spec = "Unknown (fill in)"
    if not bpy.app.background:
        try:
            import gpu
            gpu_spec = gpu.platform.renderer_get()
        except:
            pass

    blender_version = bpy.app.version_string
    build_branch = get_string(bpy.app.build_branch)
    build_commit_date = get_string(bpy.app.build_commit_date)
    build_commit_time = get_string(bpy.app.build_commit_time)
    build_hash = get_string(bpy.app.build_hash)

    sys_info["blender_info"] = ("%s, %s, %s, %s, %s" % (
    blender_version, build_branch, build_commit_date, build_commit_time, build_hash))

    sys_info["os"] = get_string(platform.system())
    sys_info['gpu_spec'] = gpu_spec
    sys_info["hdrimaker_version"] = get_string(Exa.blender_manifest["version"])
    # Get installed addons (Without default ones or HDRIMaker)

    # Avoid to get the default addons
    default_addons = ["BioVision Motion Capture (BVH) format",
                      "FBX format",
                      "STL format",
                      "Scalable Vector Graphics (SVG) 1.1 format",
                      "Stanford PLY format",
                      "UV Layout",
                      "Wavefront OBJ format (legacy)",
                      "glTF 2.0 format",
                      "Cycles Render Engine",
                      "Pose Library",
                      "Web3D X3D/VRML2 format"]

    addons = []
    try:
        for pack_name in bpy.context.preferences.addons.keys():
            import sys
            mod = sys.modules[pack_name]
            addon_name = mod.bl_info.get("name")
            if addon_name not in default_addons:
                addons.append(addon_name)
    except Exception as e:
        print("From HDRIMaker: Error getting addons list into function get_sys_info_dict error: %s" % e)
        pass

    # Transform the list in a string
    addons = ", ".join(addons)
    sys_info["active_addons"] = addons

    return sys_info


class HDRIMAKER_OT_Bugreport(Operator):
    bl_idname = Exa.ops_name + "bug_report"
    bl_label = "Report a Bug on Github"
    bl_description = "Prepare a bug report for github, get system information and open the browser, prefilling the report"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        info_dict = get_sys_info_dict()

        # Compile the report
        body = "## System Information\n"
        body += "**Blender version:** %s\n" % info_dict["blender_info"]
        body += "**HDRIMaker version:** %s\n" % info_dict["hdrimaker_version"]
        body += "**OS:** %s\n" % info_dict["os"]
        body += "**GPU:** %s\n" % info_dict["gpu_spec"]
        body += "**Active Addons:** %s\n" % info_dict["active_addons"]


        body += "\n## Description\n"
        body += "**Describe the bug here:**\n\n"
        # Leave black line for the user to write the bug description
        body += "\n\n"
        # Spiagate gli step per riprodurre il bug
        body += "**Steps to reproduce:**\n\n"
        body += "1. \n"
        body += "2. \n"
        body += "3. \n"
        body += "4. \n"
        body += "5. \n"
        body += "\n\n"

        body = body.replace(" ", "%20")
        body = body.replace("\n", "%0A")
        body = body.replace("#", "%23")

        import webbrowser
        bug_report_url = "https://github.com/ExtremeAddons/hdri_maker/issues/new?body="
        webbrowser.open(bug_report_url + body)

        return {'FINISHED'}

class HDRIMAKER_OT_copy_info_to_clipboard(Operator):
    bl_idname = Exa.ops_name + "copy_info_to_clipboard"
    bl_label = "Copy System Information to Clipboard"
    bl_description = "Copy system information to clipboard"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        from ...utility.text_utils import draw_info

        info_dict = get_sys_info_dict()

        # Compile the report
        body = "System Information: "
        body += "Blender version: %s, " % info_dict["blender_info"]
        body += "HDRIMaker version: %s, " % info_dict["hdrimaker_version"]
        body += "OS: %s, " % info_dict["os"]
        body += "GPU: %s" % info_dict["gpu_spec"]
        body += "Active Addons: %s" % info_dict["active_addons"]

        bpy.context.window_manager.clipboard = body

        print("System information copied to clipboard")
        print(body)
        text = "System information copied to clipboard, you can now paste it where you need"
        self.report({'INFO'}, text)

        draw_info(text, "Info", 'INFO')
        return {'FINISHED'}

