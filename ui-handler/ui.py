
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import time
import datetime
import RPi.GPIO as io


from PIL import ImageFont
from luma.core.virtual import viewport

from luma.core.render import canvas
from luma.core.interface.serial import spi
from luma.oled.device import sh1106

serial = spi(device=0, port=0)
device = sh1106(serial)

device.clear()

io.setmode(io.BCM)

io.setup(12, io.OUT)
io.setup(16, io.OUT)
io.setup(26, io.OUT)
io.setup(21, io.OUT)

io.setup(18, io.OUT)
io.setup(15, io.OUT)
io.setup(23, io.OUT)
io.setup(22, io.OUT)


do1 = [0, 0, 0, 0]
do2 = [0, 0, 0, 0]
dict = {0: "\uf205", 1: "\uf204"}


def syncState():
    do1[0] = io.input(12)
    do1[1] = io.input(16)
    do1[2] = io.input(26)
    do1[3] = io.input(21)

    do2[0] = io.input(18)
    do2[1] = io.input(15)
    do2[2] = io.input(23)
    do2[3] = io.input(22)    


def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)


def main():

    font = make_font("fontawesome-webfont.ttf", device.height / 4)
    mfont = make_font("fontawesome-webfont.ttf", device.height / 4)

    # use custom font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             'fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 13)

    font3 = ImageFont.truetype(font_path, 11)

    i = -100
    while True:
        syncState()
        with canvas(device) as draw:
            if i >= device.width:
                i = -150
            i = i + 1
            now = datetime.datetime.now()
            stime = now.strftime("%H:%M:%S")

            draw.text((15, 0), "Cluster Controller", font=font2, fill="white")

            draw.text((2, 14), text="DO1", font=font2, fill="white")
            draw.text((32, 14), text=dict[do1[0]], font=font, fill="white")
            draw.text((57, 14), text=dict[do1[1]], font=font, fill="white")
            draw.text((82, 14), text=dict[do1[2]], font=font, fill="white")
            draw.text((107, 14), text=dict[do1[3]], font=font, fill="white")

            draw.text((2, 30), text="DO2", font=font2, fill="white")
            draw.text((32, 30), text=dict[do2[0]], font=font, fill="white")
            draw.text((57, 30), text=dict[do2[1]], font=font, fill="white")
            draw.text((82, 30), text=dict[do2[2]], font=font, fill="white")
            draw.text((107, 30), text=dict[do2[3]], font=font, fill="white")
            # MENU:
            #draw.line((1, 50, 120, 50), fill="white")
            draw.text((2, 49), text="\uf05d", font=mfont, fill="white")
            draw.text((110, 49), text="\uf057", font=mfont, fill="white")

    time.sleep(0.8)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
