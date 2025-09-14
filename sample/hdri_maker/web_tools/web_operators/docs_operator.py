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
from bpy.props import StringProperty
from bpy.types import Operator

from ...exaproduct import Exa


def draw(self, context):
    cls = HDRIMAKER_OT_DocsOps
    urls = cls._urls
    layout = self.layout
    col = layout.column(align=True)

    for idx, (key, url) in enumerate(urls.items()):
        row = col.row(align=True)
        open_url = row.operator(Exa.ops_name + "open_web_browser", text=key, icon='URL')
        open_url.options = 'OPEN_URL'
        if not url:
            url = Exa.url_docs
        open_url.url = url


class HDRIMAKER_OT_DocsOps(Operator):
    bl_idname = Exa.ops_name + "docs"
    bl_label = "Online Documentation"
    bl_options = {'INTERNAL'}

    _urls = {}
    docs_key: StringProperty()

    @classmethod
    def description(cls, context, properties):
        return "Open the online documentation"

    def invoke(self, context, event):
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Open the online documentation")
        layout.label(text="Test")

    def execute(self, context):
        import os
        from ...web_tools.webservice import get_json_online
        from ...library_manager.get_library_utils import risorse_lib
        from ...utility.text_utils import draw_info
        from ...utility.json_functions import get_json_data
        from ...web_tools.json_writer import json_timer_check

        exa_manual = "exa_manual.json"

        json_file = os.path.join(risorse_lib(), "online_utility", exa_manual)

        json_data = json_timer_check(json_file)
        if not json_data:
            get_json_online(urls=Exa.urls_manual, save_name=exa_manual, show_popup=False)

        if not os.path.isfile(json_file):
            text = "Can't find the online documentation, retry later"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'FINISHED'}


        json_data = get_json_data(json_file)
        if not json_data:
            text = "Can't find the online documentation, retry later"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'FINISHED'}

        manual_urls = json_data.get("manual_urls")
        if not manual_urls:
            text = "Can't find the online documentation, retry later"
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'FINISHED'}

        documentation = manual_urls.get(self.docs_key)
        if not documentation:
            # Nel caso in cui la chiave non esiste, scarica di nuovo il exa_manual.json, e l'utente deve riprovare a cliccare
            get_json_online(urls=Exa.urls_manual, save_name=exa_manual, show_popup=False)

            text = "Can't find this key ( {} ) of the documentation, please retry, or contact me".format(self.docs_key)
            draw_info(text, "Info", 'INFO')
            self.report({'ERROR'}, text)
            return {'FINISHED'}

        cls = self.__class__
        cls._urls.clear()
        cls._urls = documentation

        wm = context.window_manager
        wm.popup_menu(draw, title="Online Documentation", icon='INFO')

        return {'FINISHED'}
