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
notes = []
ledgers = [0]
columns = [0]
current_note = None
quality = "1"
filename = None
ctx = None

class Note():

    def __init__(self, x, y, quality):
        self.x = x
        self.y = y                
        self.dx = 5 / ctx.width
        self.dy = 5 / ctx.height
        self.quality = quality                
        #
        self.on = None
        self.off = None

    def update(self, x, y):
        if x > self.x + (5 / ctx.width):
            self.dx = x - self.x
        if y > self.y + (5 / ctx.height) and y < self.y + (20 / ctx.height):
            self.dy = y - self.y

    def hit(self, x, y):
        return util.distance((x * ctx.width, y * ctx.height), (self.x * ctx.width, self.y * ctx.height)) < 3

    def calc_play(self):

        # find ledger index
        l = 0        
        while l < len(ledgers) and ledgers[l] < self.y:
            l += 1
        l -= 1
        l = len(ledgers) - l - 1

        # find column index
        c = 0        
        while c < len(columns) and columns[c] < self.x:
            c += 1
        c -= 1

        # cell = (column * len(ledgers)) + ledger   # nope, not so siple
        # print(cell)        

        # start with relative position in cell    
        self.on = self.x
        self.on -= columns[c]

        # add width of all previous columns                
        for ci, x in enumerate(columns[:c]):
            width = columns[ci + 1] - columns[ci] if ci < len(columns) - 1 else 1.0 - columns[ci]
            self.on += width * len(ledgers)
            # print("width %s: %s (* %s ledgers is %s)" % (ci, width, len(ledgers), width * len(ledgers)))

        # add width of previous cells in this columns
        width = columns[c + 1] - columns[c] if c < len(columns) - 1 else 1.0 - columns[c]
        # print("width current (%s): %s (* %s ledgers is %s)" % (c, width, l, width * l))
        self.on += width * l
        self.off = self.on + self.dx

        # print()


def on_key_press(info):
    global quality
    key, modifiers = info
    if key in characters:
        quality = key
        log.info("Quality is %s" % quality)
    elif key == '－':
        export()

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
    elif modifiers == 64:
        ledgers.append(y)
        ledgers.sort()
        log.info("Add ledger %f" % y)
    elif modifiers == 132:
        columns.append(x)
        columns.sort()
        log.info("Add column %f" % x)
    else:
        note = Note(x, y, quality)
        notes.append(note)
        current_note = note
        log.info("Add note %f,%f" % (x, y))

def on_mouse_drag(info):
    global current_note
    x, y, dx, dy, button, modifiers = info
    if current_note is not None and x < ctx.width:
        current_note.update(x, y)

def calc_play():
    global notes
    for note in notes:
        note.calc_play()
        # print(note.x, note.on)
    # duration = len(ledgers) * len(columns)
    # print()
    duration = 0.0
    for ci, x in enumerate(columns):
        width = columns[ci + 1] - columns[ci] if ci < len(columns) - 1 else 1.0 - columns[ci]
        duration += width * len(ledgers)
    for note in notes:
        note.on /= duration
        note.off /= duration
        print(note.x, note.y, note.on, note.off)

def export():
    global notes, filename
    if not len(notes):
        return
    calc_play()        
    notes.sort(key=lambda x: x.on)
    fn = "scores/%s_%s.score" % (filename.split('.')[0], util.timestamp())    
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    util.save(fn, (notes, ledgers, columns))
    log.info("Saved %s" % fn)

def draw():
    global notes, ledgers, columns
    for column in columns:
        ctx.line(column, 0, column, 1, color=(0., 0., 0., 0.25), thickness=3.0)
    for ledger in ledgers:
        ctx.line(0, ledger, 1, ledger, color=(0., 0., 0., 0.25), thickness=1.0)
    for note in notes:
        intensity = 1.0
        color = list(colors[characters.index(note.quality) % len(colors)])
        color.append(intensity)
        ctx.rect(note.x - (3 / ctx.width), note.y - (3 / ctx.height), note.dx + (2 / ctx.width), note.dy + (2 / ctx.height), (1., 1., 1., 1.))
        ctx.rect(note.x - (2 / ctx.width), note.y - (2 / ctx.height), note.dx, note.dy, color)            

def main():
    global filename, ctx, notes, ledgers, columns

    if len(sys.argv) < 2:
        print("[IMAGE FILENAME]")
        exit()
    filename = sys.argv[1]
    if len(sys.argv) > 2:
        notes, ledgers, columns = util.load("scores/%s" % sys.argv[2])

    image = Image.open(filename)
    aspect = image.size[1] / image.size[0]
    width = int(HEIGHT / aspect)

    ctx = animation.Context(width, HEIGHT, background=(1., 1., 1., 1.), fullscreen=False, title="score")    
    ctx.add_callback("key_press", on_key_press)
    ctx.add_callback("mouse_press", on_mouse_press)
    ctx.add_callback("mouse_drag", on_mouse_drag)
    ctx.load_image(filename, 0, 0, ctx.width, ctx.height)
    ctx.start(draw)

if __name__ == "__main__":
    main()    

