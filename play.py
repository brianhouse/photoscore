#!/usr/bin/env python3

import sys, json
from housepy import config, log, util
from score import Note

if len(sys.argv) < 2:
    print("[SCORE FILENAME]")
    exit()
notes = util.load("scores/%s" % sys.argv[1])

for note in notes:
    print(note.on)
