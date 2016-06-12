#!/usr/bin/env python3

import sys, json, time, threading
from housepy import config, log, util, midi
from score import Note

midi.log_midi = True

DURATION = 1 * 60.0 # minutes
MIN_VELOCITY = 0.5

midi_out = midi.MidiOut(1)

class Player(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = False if __name__ == "__main__" else True
        self.playing = False
        self.notes = None

    def play(self, notes):
        if self.playing:
            log.warning("Already playing")
            return  
        self.notes = notes      
        self.start()

    def run(self):
        log.info("Playing...")
        self.playing = True
        note_ons = [(note.on * DURATION, int(note.channel), int(note.pitch), int(127 * ((note.velocity * MIN_VELOCITY) + MIN_VELOCITY))) for note in self.notes]
        note_offs = [(note.off * DURATION, int(note.channel), int(note.pitch), 0) for note in self.notes]
        notes = (note_ons + note_offs)
        notes.sort(key=lambda n: n[0])
        start_t = time.time()
        n = 0
        while True:
            t = time.time() - start_t
            if t > notes[n][0]:
                midi_out.send_note(notes[n][1], notes[n][2], notes[n][3])
                n += 1
                if n == len(notes):
                    break
            time.sleep(0.01)
        self.playing = False
        log.info("--> done")


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("[SCORE FILENAME]")
    #     exit()
    filename = "IMG_6714_1465680609.score"
    notes, ledgers, columns = util.load("scores/%s" % filename)
    player = Player()
    player.play(notes)

