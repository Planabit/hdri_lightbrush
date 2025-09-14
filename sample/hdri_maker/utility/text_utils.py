import re
import textwrap
from html import parser
from urllib.parse import urlparse

import bpy

from ..icons.interfaceicons import get_icon
from ..exaproduct import Exa


def url_to_domain_name(url):
    domain = urlparse(url).netloc
    return domain

def decode_escape(string):
    return parser.unescape(string)

def wrap_text(layout, string, enum=None, text_length=80, center=False, icon=None, open_link=False):
    layout = layout.column(align=True)
    # Decodifichiamo nel caso sia stato utilizzato un Escape
    string = decode_escape(string)

    wrapper = textwrap.TextWrapper(width=text_length, break_long_words=False, break_on_hyphens=False)
    word_list = wrapper.wrap(text=string)
    if enum:
        enum = str(enum) + "-"
    else:
        enum = ""
    icon_is_drawed = False
    draw_button = ""
    for idx, wrap in enumerate(word_list):
        row = layout.row(align=True)
        if center:
            row.alignment = 'CENTER'

        if open_link:

            pre = ""
            post = ""
            for word in wrap.split(" "):
                if is_url(word):
                    draw_button = word
                if not draw_button:
                    pre += " " + word
                else:
                    if not draw_button == word:
                        post += " " + word
            if pre:
                if icon and icon != "" and not icon_is_drawed:
                    row.label(text=enum + pre if enum else pre, icon=icon)
                    icon_is_drawed = True
                else:
                    row.label(text=enum + pre if enum else pre)

            if draw_button:
                row = layout.row(align=True)
                open_url = row.operator(Exa.ops_name+"open_web_browser", text=url_to_domain_name(draw_button), icon='URL', depress=True)
                open_url.url = draw_button
                open_url.options = 'OPEN_URL'

            if post:
                row = layout.row(align=True)
                if icon and icon != "" and not icon_is_drawed:
                    row.label(text=enum + post if enum else post, icon=icon)
                    icon_is_drawed = True
                else:
                    row.label(text=enum + post if enum else post)
            continue


        if icon and icon != "" and not icon_is_drawed:
            row.label(text=enum + wrap if enum else wrap, icon=icon)
            icon_is_drawed = True
        else:
            row.label(text=enum + wrap if enum else wrap)

def draw_info(string, title, icon, popup_size_y = 130, context=bpy.context, text_wrap=True):
    def draw(self, context):
        if text_wrap:
            wrap_text(self.layout, string, None, popup_size_y, None, "")
        else:
            layout = self.layout
            layout.label(text=string)

    try: context.window_manager.popup_menu(draw, title=title, icon=icon)
    except: context.window_manager.popup_menu(draw, title=title)

def write_with_icons(layout, horizontal_vertical, text, use_template_icon, scale):
    # Funzione che restituisce una scrittura in icone, bisogna avere un dizionario con tali icone in icons_dict
    text = text.lower()

    if "HORIZONTAL":
        layout = layout.row(align=True)
    else:
        layout = layout.column(align=True)

    for letter in text:
        if letter == "?":
            letter = "question_mark"

        if horizontal_vertical == "VERTICAL":
            layout = layout.column(align=True)
        if letter != " ":
            icon = "write_letter_" + letter
        else:
            icon = "letter_space"
        layout.alignment = 'CENTER'

        if use_template_icon:
            layout.template_icon(icon_value=get_icon(icon), scale=scale)
        else:
            layout.label(icon_value=get_icon(icon))
        # else: row.label(icon = 'NONE',text="")

    return layout

def is_url(text):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, text) is not None
