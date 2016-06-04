#!/usr/bin/env python3

from housepy import animation, config, log, util
from random import random

characters = "1234567890qwertyuiopasdfghjklzxcvbnm"
colors = [  (0, 0, 1),
            (0, 1, 0),
            (0, 1, 1),
            (1, 0, 0),
            (1, 0, 1),
            (1, 1, 0)
            ]

notes = []

quality = "1"


ctx = animation.Context(600, 800, background=(1., 1., 1., 1.), fullscreen=False, title="score")    
ctx.load_image("IMG_6701.jpg", 600, 800)

def on_key_press(info):
    global quality
    key, modifiers = info
    if key in characters:
        quality = key
        log.info("Quality is %s" % quality)
ctx.add_callback("key_press", on_key_press)

def on_mouse_press(info):
    global notes
    x, y, button, modifiers = info
    if modifiers == 1:
        for note in notes:
            x2, y2, q2 = note
            if util.distance((x * ctx.width, y * ctx.height), (x2 * ctx.width, y2 * ctx.height)) < 3:
                try:
                    notes.remove(note)
                    log.info("Remove %f,%f %s" % note)
                except ValueError:
                    pass
    else:
        notes.append((x, y, quality))
        log.info("Add %f,%f %s" % (x, y, quality))
ctx.add_callback("mouse_press", on_mouse_press)

def draw():
    global notes, quality
    for note in notes:
        x, y, q = note
        intensity = 1.0
        color = list(colors[characters.index(q) % len(colors)])
        color.append(intensity)
        ctx.rect(x - (3 / ctx.width), y - (3 / ctx.height), 7 / ctx.width, 7 / ctx.height, (1., 1., 1., 1.))
        ctx.rect(x - (2 / ctx.width), y - (2 / ctx.height), 5 / ctx.width, 5 / ctx.height, color)            
ctx.start(draw)
