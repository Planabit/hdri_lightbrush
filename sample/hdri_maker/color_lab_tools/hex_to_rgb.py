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



