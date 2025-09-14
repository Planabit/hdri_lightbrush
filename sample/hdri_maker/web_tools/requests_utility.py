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
import json
import os
import ssl
import time

import requests

from .get_user_data import get_token_from_json, get_user_data, write_tokens_to_json
from ..exaproduct import Exa
from ..utility.text_utils import draw_info
from ..utility.utility import url_to_domain_name, get_addon_dir, save_text_file


# if bpy.app.version >= (3, 0, 0):
#     from requests.packages.urllib3.exceptions import InsecureRequestWarning
#     requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_ssl_certificate(url):
    domain = url_to_domain_name(url)
    ssl_folder = os.path.join(get_addon_dir(), "addon_resources", "ssl")
    ert = ssl.get_server_certificate((domain, 443), ssl_version=3)
    file_path = os.path.join(ssl_folder, domain + ".crt")
    save_text_file(ert, file_path)
    return file_path


def grab_json_respose_values(r, url):
    """If ok return from json respose (As input)
       In this order: success, message, total_chunks, current_chunk, filename, file"""
    status_code = json_ok = success = message = None

    try:
        status_code = r.status_code
    except:
        pass

    try:
        json_respose = get_json_from_respose(r, url)
        json_ok = True
    except:
        return status_code, json_ok, success, message

    if json_respose:
        success = json_respose.get("success")
        message = json_respose.get("message")

    return status_code, json_ok, success, message


def grab_tokens_from_respose(r, url):
    try:
        json_respose = get_json_from_respose(r, url)
        token = json_respose.get('token')
        refresh_token = json_respose.get('refresh')
    except:
        return None, None
    return token, refresh_token


# ------------------------------------------------------------
# Post

class RequestsPost:
    _respose_time = None

    def __init__(self, url="", data=None, stream=False, timeout=25, session=None, retry=1, show_popup=True):
        self.url = url
        self.data = data
        self.stream = stream
        self.timeout = timeout
        self.session = session
        self.retry = retry
        self.show_popup = show_popup

    def requests_post(self):
        """Fa una chiamata post Le risposte, saranno in Json,
        url=internet url
        data=data da inserire nel data post """
        if not self.session:
            self.session = requests.Session()

        for n in range(0, self.retry):
            try:
                time_start = time.time()
                r = self.session.post(self.url, json=self.data, timeout=self.timeout, stream=self.stream, verify=True)
                self._respose_time = time.time() - time_start
                print("# -- From requests_post() Fc, with:")
                print("# -  Url:", self.url)
                print("# -- R Status Code:", r.status_code)
                return r
            except requests.exceptions.RequestException as e:
                print("# -- From requests_post() with url:", self.url)
                print("# -- Except:", e)
                if self.show_popup:
                    text = "Please Check your internet connection. "
                    text += "Except: " + str(e)
                    draw_info(text, "Info", 'INFO')
                if n == self.retry:
                    return


def session_get(url, session, timeout=15, headers=None, stream=False):
    try:
        r = session.get(url, timeout=timeout, headers=headers, stream=stream)
        if r.status_code == 200:
            return r
        else:
            text = "Connection Problem:" + str(r.status_code)
            return text
    except requests.exceptions.RequestException as e:
        text = "Requests Get Except: " + str(e) + "   " \
                                                  "Try to check your Internet Connection        " \
                                                  "If the problem persists, contact me on the Extreme-addons.com" \
                                                  " chat, we will reply within 24 hours"
        return text


def requests_get(url, params={}, timeout=15, headers=None, get_status=False, show_popup=True, context_exist=True,
                 stream=False):
    #
    status_code = ""
    r = None
    try:
        r = requests.get(url, json=params, timeout=timeout, headers=headers, verify=True, stream=stream)
        if r.status_code == 200:
            return r
        if get_status:
            text = "Connection Problem: " + str(r.status_code)
            if not context_exist:
                # Questa uscita è per l'operatore multythread, poichè senò Blender va in crash
                return text

            draw_info(text, "Info", 'INFO')
    except requests.exceptions.RequestException as e:
        if get_status:
            try:
                status_code = r.status_code
            except:
                pass

            if show_popup:
                text = "Requests Get Except: " + str(e) + "   " \
                                                          "Try to check your Internet Connection        " \
                                                          "If the problem persists, contact me on the Extreme-addons.com" \
                                                          " chat, we will reply within 24 hours"

                # if status_code:
                #     text += "Status Code: " + status_code
                if not context_exist:
                    return text
                draw_info(text, "Info", 'INFO')
        # print("#--------------------------------------------------------")
        # print("Connection error in the fc requests_get() with this url:")
        # print(url)
        # print("Except:", e)
        # print("#--------------------------------------------------------")


def grab_headers(r, url):
    headers_ok = headers = filename = content_length = None
    total_chunks = 0
    current_chunk = 0
    try:
        headers = r.headers
        headers_ok = True
    except:
        pass

    if headers:
        filename = headers.get("ea_fileName")
        current_chunk = headers.get("ea_currentChunk")
        total_chunks = headers.get("ea_totalChunks")
        content_length = headers.get("Content-Length")
        if current_chunk:
            current_chunk = int(current_chunk)
        if total_chunks:
            total_chunks = int(total_chunks)
        if content_length:
            content_length = int(content_length)

    return headers_ok, total_chunks, current_chunk, filename, content_length


# ------------------------------------------------------------

def get_json_from_respose(r, url, context_exist=True, show_popup=True):
    try:
        json_data = r.json()
        return json_data
    except:
        text = "Bad Json Respose from: " + url + " (See the consolle)"
        if not context_exist:
            return text
        if show_popup:
            draw_info(text, "Info", 'INFO')
        print("#------------------ Bad Json Respose---------------------")
        print("From Fc: get_json_from_respose() try to convert requests in to r.json()")
        print("From this url:", url)
        print("Obtain this respose: ", r)
        print("#--------------------------------------------------------")


def get_new_token():
    """Questa funzione, serve per ottenere un nuovo token, tramite get token, se non si riesce ad ottenere, bisogna rifare il login"""

    token, refresh_token = get_token_from_json()

    if not refresh_token:
        print("From get_new_token Fc", "no refresh_token")
        return

    data = get_user_data()
    mac = data.get("mac")

    if not mac:
        print("From get_new_token Fc", "No Mac")
        return

    par_data = {"Authorization": "Bearer " + refresh_token,
                "mac": mac}
    params = json.dumps(par_data, indent=4)

    r = requests_get(Exa.url_refresh_token, params=params, timeout=25, headers=None, get_status=True, show_popup=False,
                     context_exist=False)

    if not r:
        print("From get_new_token Fc", "No Respose")
        return

    if r.status_code == 401:
        print("From get_new_token Fc", "Status code 401")
        return

    new_token, new_refresh_token = grab_tokens_from_respose(r, Exa.url_refresh_token)

    if not new_token:
        print("From get_new_token Fc", "no token")
        return

    write_tokens_to_json(token=new_token, refresh_token=None)

    return True
