import mido
from mido import Message

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
            self.playing_note={}
            self.playing_note_from={}
            self.notes = {i: 48 + i for i in range(50)}
            # self.notes = {
                        #     0: 60,  # C4
                        #     1: 62,  # D4
                        #     2: 64,  # E4
                        #     3: 66,  # F#4 / Gb4
                        #     4: 68,  # G#4 / Ab4
                        #     5: 70,  # A#4 / Bb4
                        #     6: 72,  # C5
                        #     7: 74,  # D5
                        #     8: 76,  # E5
                        #     9: 78,  # F#5 / Gb5
                        #     10: 80  # G#5 / Ab5
                        # }

    def amplitude_to_velocity(self, amplitude):
        """Map an amplitude value between 0.01 and 1 to a MIDI velocity value between 0 and 127."""
        return int(amplitude * 127)

    def send_note_on(self, note, amplitude):
        velocity = self.amplitude_to_velocity(amplitude)
        msg = Message('note_on', note=note, velocity=velocity)
        self.outport.send(msg)

    def send_note_off(self, note, amplitude):
        velocity = self.amplitude_to_velocity(amplitude)
        msg = Message('note_off', note=note, velocity=velocity)
        self.outport.send(msg)

    def Play(self,area,person_id):
        if( area in self.playing_note_from):
            return
        else:
            self.playing_note[person_id] = area
            self.playing_note_from[area] = person_id
            self.send_note_on(self.notes[area],1)
            print("send note on {self.notes[area]}")

    def Stop(self,person_id):
        if( person_id in self.playing_note):
            area = self.playing_note[person_id]
            if(self.playing_note_from[area] != person_id):
                return
            self.send_note_off(self.notes[area],1)
            del self.playing_note[person_id]
            del self.playing_note_from[area]
            print("send note OFF {self.notes[area]}")
        



# # Usage:

# s = MidiController.getInstance()
# s.send_note_on(60, 0.01)  # Quiet note on
# # ...do something...
# s.send_note_off(60, 0.01)  # Quiet note off

# s.send_note_on(60, 1)  # Loud note on
# # ...do something...
# s.send_note_off(60, 1)  # Loud note off
