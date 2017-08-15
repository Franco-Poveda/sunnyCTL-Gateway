
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import json
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

do1 = [0, 0, 0, 0]
do2 = [0, 0, 0, 0]
clk = 27
dt = 17
sw = 22

cursor = 0

io.setup(clk, io.IN)
io.setup(dt, io.IN)
io.setup(sw, io.IN, pull_up_down=io.PUD_UP)

def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        './fonts', name))
    return ImageFont.truetype(font_path, size)

# Custom font:
font = make_font("fontawesome-webfont.ttf", device.height / 4)
font2 = make_font('C&C Red Alert [INET].ttf', 13)

def on_message(channel, method_frame, header_frame, body):
    msg = json.loads(body)
    print "new msg"
    global do1, do2
    do1 = msg['do1']
    do2 = msg['do2']
    drawUI(msg['do1'], msg['do2'])
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

def setupAMQP():
    connection = pika.BlockingConnection(
            pika.URLParameters("amqp://sunny:sunny@localhost:5672/%2F"))
    channel = connection.channel()
    global outCh
    outCh = connection.channel()
    outCh.exchange_declare(exchange='tasks',
                         type='topic', durable=True)
    channel.queue_declare(queue='status', durable=False, auto_delete=True)

    channel.queue_bind(exchange='lsc',
                        queue='status',
                        routing_key='curr')
    channel.basic_consume(on_message, 'status')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()

def drawUI(do1, do2):
    with canvas(device) as draw:
        draw.text((15, 0), "Cluster Controller", font=font2, fill="white")
        draw.text((2, 14), text="DO1", font=font2, fill="white")
        draw.text((32, 14), text=dict[do1[0]], font=font, fill="white")
        draw.text((57, 14), text=dict[do1[1]], font=font, fill="white")
        draw.text((82, 14), text=dict[do1[2]], font=font, fill="white")
        draw.text((107, 14), text=dict[do1[3]], font=font, fill="white")

        draw.text((2, 31), text="DO2", font=font2, fill="white")
        draw.text((32,31), text=dict[do2[0]], font=font, fill="white")
        draw.text((57, 31), text=dict[do2[1]], font=font, fill="white")
        draw.text((82, 31), text=dict[do2[2]], font=font, fill="white")
        draw.text((107, 31), text=dict[do2[3]], font=font, fill="white")
        # CURSOR:
        if cursor == 1:
            draw.line((30, 29, 51, 29), fill="white")
            draw.line((30, 29, 30, 23), fill="white")
            draw.line((51, 29, 51, 23), fill="white")
        if cursor == 2:
            draw.line((54, 29, 77, 29), fill="white")
            draw.line((54, 29, 54, 23), fill="white")
            draw.line((77, 29, 77, 23), fill="white")
        if cursor == 3:
            draw.line((78, 29, 101, 29), fill="white")
            draw.line((78, 29, 78, 23), fill="white")
            draw.line((101, 29, 101, 23), fill="white")
        if cursor == 4:
            draw.line((105, 29, 127, 29), fill="white")
            draw.line((105, 29, 105, 23), fill="white")
            draw.line((127, 29, 127, 23), fill="white")

        if cursor == 5:
            draw.line((30, 46, 51, 46), fill="white")
            draw.line((30, 46, 30, 40), fill="white")
            draw.line((51, 46, 51, 40), fill="white")
        if cursor == 6:
            draw.line((54, 46, 77, 46), fill="white")
            draw.line((54, 46, 54, 40), fill="white")
            draw.line((77, 46, 77, 40), fill="white")
        if cursor == 7:
            draw.line((78, 46, 101, 46), fill="white")
            draw.line((78, 46, 78, 40), fill="white")
            draw.line((101, 46, 101, 40), fill="white")
        if cursor == 8:
            draw.line((105, 46, 127, 46), fill="white")
            draw.line((105, 46, 105, 40), fill="white")
            draw.line((127, 46, 127, 40), fill="white")

        if cursor == 9:
            draw.line((0, 63, 20, 63), fill="white")
            draw.line((0, 63, 0, 58), fill="white")
            draw.line((20, 63, 20, 58), fill="white")
        if cursor == 10:
            draw.line((107, 63, 127, 63), fill="white")
            draw.line((107, 63, 107, 58), fill="white")
            draw.line((127, 63, 127, 58), fill="white")

        draw.text((2, 49), text="\uf05d", font=font, fill="white")
        draw.text((110, 49), text="\uf057", font=font, fill="white")

def cb(channel):
    Switch_A = io.input(clk)
    Switch_B = io.input(dt)
    #print Switch_A
    #print Switch_B
    global cursor
    if (Switch_A == Switch_B):                        # Both one active? Yes -> end of sequence
        if channel == dt:                            # Turning direction depends on 
            cursor += 1
            if cursor > 10:
                cursor -=10
        else:                                        # so depending on direction either
            cursor -=1
            if cursor <= 0:
                cursor = 10
        drawUI(do1, do2)
    return  
    
def click(ch):
    print cursor
    if cursor == 1:
        do1[0] = 1 - do1[0]
    if cursor == 2:
        do1[1] = 1 - do1[1]
    if cursor == 3:
        do1[2] = 1 - do1[2]
    if cursor == 4:
        do1[3] = 1 - do1[3]

    if cursor == 5:
        do2[0] = 1 - do2[0]
    if cursor == 6:
        do2[1] = 1 - do2[1]
    if cursor == 7:
        do2[2] = 1 - do2[2]
    if cursor == 8:
        do2[3] = 1 - do2[3]

    if cursor == 9:
        outCh.basic_publish(exchange='tasks',
                          routing_key='write',
                          body=json.dumps({"do1": do1, "do2": do2}))
    drawUI(do1, do2)
    return


io.add_event_detect(dt, io.RISING, callback=cb, bouncetime=200)
io.add_event_detect(clk, io.RISING, callback=cb, bouncetime=200)
io.add_event_detect(sw, io.FALLING, callback=click, bouncetime=300)
#drawUI(do1, do2)
setupAMQP()
