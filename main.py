#!/usr/bin/env python3

import sys, os
from PIL import Image
from housepy import animation, config, log, util
from random import random

HEIGHT = 700

characters = "1234567890qwertyuiopasdfghjklzxcvbnm"
colors = [  (0, 0, 1),
            (0, 1, 0),
            (0, 1, 1),
            (1, 0, 0),
            (1, 0, 1),
            (1, 1, 0)
            ]

class Note():

    def __init__(self, on, y, quality):
        self.on = on
        self.off = on + (5 / ctx.width)
        self.y = y
        self.velocity = (5 / ctx.height)
        self.quality = quality                

    def update(self, x, y):
        if x > self.on + (5 / ctx.width):
            self.off = x
        y -= self.y
        if y > (5 / ctx.height) and y < (20 / ctx.height):
            self.velocity = y

    def hit(self, x, y):
        return util.distance((x * ctx.width, y * ctx.height), (self.on * ctx.width, self.y * ctx.height)) < 3

notes = []
current_note = None

quality = "1"

if len(sys.argv) < 2:
    print("[IMAGE FILENAME]")
    exit()
filename = sys.argv[1]
if len(sys.argv) > 2:
    notes = util.load("scores/%s" % sys.argv[2])

image = Image.open(filename)
aspect = image.size[1] / image.size[0]
width = int(HEIGHT / aspect)

ctx = animation.Context(width, HEIGHT, background=(1., 1., 1., 1.), fullscreen=False, title="score")    
ctx.load_image(filename, 0, 0, ctx.width, ctx.height)

def on_key_press(info):
    global quality
    key, modifiers = info
    if key in characters:
        quality = key
        log.info("Quality is %s" % quality)
    elif key == '－':
        export()
ctx.add_callback("key_press", on_key_press)

def on_mouse_press(info):
    global notes, current_note
    x, y, button, modifiers = info
    if modifiers == 1:
        for note in notes:
            if note.hit(x, y):
                try:
                    notes.remove(note)
                    log.info("Removed note")
                except ValueError:
                    pass
    else:
        note = Note(x, y, quality)
        notes.append(note)
        current_note = note
        log.info("Add note %f,%f" % (x, y))
ctx.add_callback("mouse_press", on_mouse_press)

def on_mouse_drag(info):
    global current_note
    x, y, dx, dy, button, modifiers = info
    current_note.update(x, y)
ctx.add_callback("mouse_drag", on_mouse_drag)

def export():
    global notes
    if not len(notes):
        return
    notes.sort(key=lambda x: x.on)
    fn = "scores/%s_%s.pkl" % (filename.split('.')[0], util.timestamp())    
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    util.save(fn, notes)
    log.info("Saved %s" % fn)

def draw():
    global notes, quality
    for note in notes:
        x1, x2, y, q = note.on, note.off, note.y, note.quality
        width = x2 - x1
        height = note.velocity
        intensity = 1.0
        color = list(colors[characters.index(q) % len(colors)])
        color.append(intensity)
        ctx.rect(x1 - (3 / ctx.width), y - (3 / ctx.height), width + (2 / ctx.width), height + (2 / ctx.height), (1., 1., 1., 1.))
        ctx.rect(x1 - (2 / ctx.width), y - (2 / ctx.height), width, height, color)            
ctx.start(draw)
