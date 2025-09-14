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

import math

def hex_to_rgb(hexColor):
    # Thankyou for this functions @ K. A. Buhr on stackexchange
    # https://blender.stackexchange.com/questions/158896/how-set-hex-in-rgb-node-python
    def srgb_to_rgbLineare(c):
        if c < 0:
            return 0
        elif c < 0.04045:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    def hex_to_rgb(hex):
        r = (hex & 0xff0000) >> 16
        g = (hex & 0x00ff00) >> 8
        b = (hex & 0x0000ff)
        return tuple([srgb_to_rgbLineare(c/0xff) for c in (r,g,b)] + [1])

    return hex_to_rgb(hexColor)


def rgb_to_hex(red, green, blue):
    # Thankyou for This functions @ batFINGER on stackexchange
    #
    # https://blender.stackexchange.com/questions/234388/how-to-convert-rgb-to-hex-almost-there-1-error-colors


    def linear_to_srgb8(c):
        if c < 0.0031308:
            srgb = 0.0 if c < 0.0 else c * 12.92
        else:
            srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055

        if srgb > 1: srgb = 1

        return round(255 * srgb)

    def toHex(r, g, b):
        return "%02x%02x%02x" % (
            linear_to_srgb8(r),
            linear_to_srgb8(g),
            linear_to_srgb8(b),
        )

    return toHex(red, green, blue)


kelvin_dict = {"Kelvin":
    {
        "1900 Candle": {"rgb": (255, 147, 41)},
        "2600 40w Tungsten": {"rgb": (255, 197, 143)},
        "2850 100W Tungsten": {"rgb": (255, 214, 170)},
        "3200 Halogen": {"rgb": (255, 241, 224)},
        "5200 Carbon Arc": {"rgb": (255, 250, 244)},
        "5400 High Noon Sun": {"rgb": (255, 255, 251)},
        "6000 Direct Sunlight": {"rgb": (255, 255, 255)},
        "7000 Overcast Sky": {"rgb": (201, 226, 255)},
        "20000 Clear Blue Sky": {"rgb": (64, 156, 255)}
    },
    "Fluorescent":
    {
        "Warm Fluorescent": {"rgb": (255, 244, 229)},
        "Standard Fluorescent": {"rgb": (244, 255, 250)},
        "Cool White Fluorescent": {"rgb": (212, 235, 255)},
        "Full Spectrum Fluorescent": {"rgb": (255, 244, 242)},
        "Grow Light Fluorescent": {"rgb": (255, 239, 247)},
        "Black Light Fluorescent": {"rgb": (167, 0, 255)}
    }


}


def srgb_to_rgbLineare(c):
    if c < 0:
        return 0
    elif c < 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** 2.4

# Create a dict with rgb 255 == 1.0, need to be convert the rgb values to 0.0 - 1.0 range and put hex value into the dict
# def calc():
#     new_dict = {}
#     for key, value in kelvin_dict.items():
#         rgb = value.get('rgb')
#         hex = rgb_to_hex(rgb[0], rgb[1], rgb[2])
#         blender_rgb = hex_to_rgb(hex)
#         new_dict[key] = {'rgb': blender_rgb, 'hex': hex}
#
#     return new_dict

def calc_v2():
    new_dict = {}
    for key, value in kelvin_dict.items():
        diction = new_dict[key] = {}
        for k, v in value.items():
            rgb = v.get('rgb')
            r = srgb_to_rgbLineare(rgb[0] / 255)
            g = srgb_to_rgbLineare(rgb[1] / 255)
            b = srgb_to_rgbLineare(rgb[2] / 255)
            blender_rgb = (r, g, b, 1)

            hex_color = rgb_to_hex(rgb[0]/255, rgb[1]/255, rgb[2]/255)

            diction[k] = {'rgb': blender_rgb, 'hex': hex_color}

    return new_dict


print(calc_v2())
