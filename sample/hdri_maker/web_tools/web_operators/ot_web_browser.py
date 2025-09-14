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
import os
import webbrowser

from bpy.props import StringProperty
from bpy.types import Operator

from ..webservice import get_json_online
from ...exaproduct import Exa
from ...library_manager.get_library_utils import risorse_lib
from ...utility.json_functions import get_json_data
from ...utility.text_utils import draw_info


class HDRIMAKER_OT_open_web_browser(Operator):
    bl_idname = Exa.ops_name+"open_web_browser"
    bl_label = "Browser"
    bl_options = {'INTERNAL'}

    url: StringProperty()
    options: StringProperty()
    description: StringProperty()
    docs_key: StringProperty()
    json_dictionary: StringProperty()

    @classmethod
    def description(cls, context, properties):
        if properties.description:
            desc = properties.description
        elif properties.options == 'OPEN_URL':
            desc = "Visit website: " + properties.url
        elif properties.options == 'GET_URL_KEY':
            desc = "Online Manual: " + properties.docs_key
        else:
            desc = ""
        return desc

    def execute(self, context):

        if self.options == 'GET_URL_KEY': # Per qualsiasi motivo storto, va a questo indirizzo che è quello della homepage
            url = Exa.url_docs
        else:
            url = Exa.ulr_website

        def error_mex():
            text = "It seems that your computer has not set a default Browser. " \
                   "Please add a default browser to correctly view the online page that must be opened via this button"
            draw_info(text, "Info", 'INFO')

        if self.options == 'GET_URL_KEY':
            # Opzione dedicata all'apertura del manuale online, le chiavi devono essere inserite nelle interfacce
            # ogni chiave ha un value che sarà l'indirizzo. Il dizionario json è dichiarato nel prodotto su extreme-addons
            # si può anche utilizzare un dizionario json su gibhub in caso di emergenza nel caso si cambi dominio

            if self.json_dictionary == 'exa_manual.json':
                exa_url = Exa.urls_manual
            elif self.json_dictionary == 'exa_social.json':
                exa_url = Exa.urls_social
            elif self.json_dictionary == 'exa_urls.json':
                exa_url = Exa.urls_exa_urls

            get_json_online(urls=exa_url, save_name=self.json_dictionary)
            json_file = os.path.join(risorse_lib(), "online_utility", self.json_dictionary)
            if not json_file:
                return{'FINISHED'}
            json_data = get_json_data(json_file)
            if not json_file:
                return{'FINISHED'}

            if json_data:
                if self.json_dictionary == 'exa_manual.json':
                    manual = json_data.get("manual")
                    if manual:
                        manual_urls = manual.get("manual_urls")
                        if manual_urls:
                            current_url = manual_urls.get(self.docs_key)
                            if current_url:
                                url = current_url

                elif self.json_dictionary == 'exa_social.json':
                    social = json_data.get("social")
                    if social:
                        current_url = social.get(self.docs_key)
                        if current_url:
                            url = current_url

                elif self.json_dictionary == 'exa_urls.json':
                    urls = json_data.get("urls")
                    if urls:
                        current_url = urls.get(self.docs_key)
                        if current_url:
                            url = current_url

            try:
                webbrowser.open(url)
            except:
                error_mex()

        elif self.options == 'OPEN_URL':
            try:
                webbrowser.open(self.url)
            except:
                error_mex()

        return {'FINISHED'}


class HDRIMAKER_OT_SendMail(Operator):
    bl_idname = Exa.ops_name + "sendmail"
    bl_label = "Send Mail"
    bl_options = {'INTERNAL'}

    email: StringProperty()
    subject: StringProperty()
    message: StringProperty()

    @classmethod
    def description(cls, context, properties):
        return "Send a mail to: " + properties.email

    def execute(self, context):
        webbrowser.open("mailto:" + self.email + "?subject=" + self.subject + "&body=" + self.message)
        return {'FINISHED'}
