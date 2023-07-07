from MidiController import MidiController
import time



midi = MidiController()
#midi.start_keyboard_listener()

def main():
    i=0
    while(True):
        midi.send_note_off(i%2,0)
        i+=1
        midi.send_note_on(i%2,1)
        time.sleep(1)
    # Sleep for 2 seconds
    time.sleep(60*60)
    pass


if __name__ == "__main__":
    main()