import mido
from mido import Message
from pynput.keyboard import Key, Listener
import threading

class MidiController:
    __instance = None

    @staticmethod 
    def getInstance():
        """ Static access method. """
        if MidiController.__instance == None:
            MidiController()
        return MidiController.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if MidiController.__instance != None:
            raise Exception("This class is a !")
        else:
            MidiController.__instance = self
            self.outport = mido.open_output('TrackerMidiBoard', virtual=True)
            #self.start_keyboard_listener()
            self.last_note = None
            self.playing_note={}
            self.playing_note_from={}
            self.notes = {i: 48 + i for i in range(50)}
            # self.notes = {
            #                 0: 23,  # B0
            #                 1: 24,  # C1
            #                 2: 25,  # C#1 / Db1
            #                 3: 26,  # D1
            #                 4: 27,  # D#1 / Eb1
            #                 5: 28,  # E1
            #                 6: 29,  # F1
            #                 7: 30,  # F#1 / Gb1
            #                 8: 31,  # G1
            #                 9: 32,  # G#1 / Ab1
            #                 10: 33,  # A1
            #                 11: 34,  # A#1 / Bb1
            #                 12: 35,  # B1
            #                 13: 36,  # C2
            #                 # ...and so on
            #             }
            

    def amplitude_to_velocity(self, amplitude):
        """Map an amplitude value between 0.01 and 1 to a MIDI velocity value between 0 and 127."""
        return int(amplitude * 127)

    def send_note_on(self, note, amplitude):
        velocity = self.amplitude_to_velocity(amplitude)
        msg = Message('note_on', note=note, velocity=velocity)
        self.outport.send(msg)
        print(f"send note on {note}")

    def send_note_off(self, note, amplitude):
        velocity = self.amplitude_to_velocity(amplitude)
        msg = Message('note_off', note=note, velocity=velocity)
        self.outport.send(msg)
        print(f"send note OFF {note}")

    def Play(self,area,person_id):
        if( area in self.playing_note_from):
            return
        else:
            self.playing_note[person_id] = area
            self.playing_note_from[area] = person_id
            self.send_note_on(self.notes[area],1)
            

    def Stop(self,person_id):
        if( person_id in self.playing_note):
            area = self.playing_note[person_id]
            if(self.playing_note_from[area] != person_id):
                return
            self.send_note_off(self.notes[area],0)
            del self.playing_note[person_id]
            del self.playing_note_from[area]
            #print(f"send note OFF {self.notes[area]}")

    KEY_TO_NOTE = {
        'a': 0, 's': 1, 'd': 2, 'f': 3, 'g': 4, 'h': 5, 'j': 6, 'k': 7, 'l': 8,
        'q': 9, 'w': 10, 'e': 11, 'r': 12, 't': 13, 'y': 14, 'u': 15, 'i': 16, 'o': 17, 'p': 18,
        'z': 19, 'x': 20, 'c': 21, 'v': 22, 'b': 23, 'n': 24, 'm': 25,
        '1': 26, '2': 27, '3': 28, '4': 29, '5': 30, '6': 31, '7': 32, '8': 33, '9': 34, '0': 35,
        # Add more mappings if needed...
    }

    def on_press(self, key):
        try:
            if key.char in self.KEY_TO_NOTE:
                # Send a note off message for the last note that was played, if any
                if self.last_note is not None:
                    self.send_note_off(self.last_note, 1)
                # Send a note on message for the current note
                self.last_note = self.notes[self.KEY_TO_NOTE[key.char]]
                self.send_note_on(self.last_note, 1)
        except AttributeError:
            pass  # Ignore non-character keys

    def start_keyboard_listener(self):
        listener = Listener(on_press=self.on_press)
        thread = threading.Thread(target=listener.start)
        thread.start()



# # Usage:

# s = MidiController.getInstance()
# s.send_note_on(60, 0.01)  # Quiet note on
# # ...do something...
# s.send_note_off(60, 0.01)  # Quiet note off

# s.send_note_on(60, 1)  # Loud note on
# # ...do something...
# s.send_note_off(60, 1)  # Loud note off
