
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import threading
import os
import json
import time
import pika

import RPi.GPIO as io
from PIL import ImageFont
from luma.core.virtual import viewport
from luma.core.render import canvas
from luma.core.interface.serial import spi
from luma.oled.device import sh1106


serial = spi(device=0, port=0)
device = sh1106(serial)
device.clear()

dict = {0: "\uf205", 1: "\uf204"}


def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        './fonts', name))
    print font_path
    return ImageFont.truetype(font_path, size)


def worker(do1, do2):
    connection = pika.BlockingConnection(
        pika.URLParameters("amqp://sunny:sunny@localhost:5672/%2F"))
    channel = connection.channel()

    channel.queue_declare(queue='status', durable=False, auto_delete=True)

    channel.queue_bind(exchange='lsc',
                       queue='status',
                       routing_key='curr')

    for method, properties, body in channel.consume('status'):
        print body
        msg = json.loads(body)
        do1 = msg['do1']
        do2 = msg['do2']

    channel.start_consuming()


def ui(do1, do2):
    # Custom font:
    font = make_font("fontawesome-webfont.ttf", device.height / 4)
    font2 = make_font('C&C Red Alert [INET].ttf', 13)
    while True:
        with canvas(device) as draw:
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
            # draw.line((1, 50, 120, 50), fill="white")
            draw.text((2, 49), text="\uf05d", font=font, fill="white")
            draw.text((110, 49), text="\uf057", font=font, fill="white")

    time.sleep(0.8)

    do1 = [0, 0, 0, 0]
    do2 = [0, 0, 0, 0]
    t_msg = threading.Thread(target=worker, args=(do1, do2))
    t_ui = threading.Thread(target=ui, args=(do1, do2))
    t_msg.start()
    t_ui.start()
