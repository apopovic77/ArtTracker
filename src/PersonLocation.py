from datetime import datetime, timedelta
import random
from Midi.MidiController import MidiController


class Event:
    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)

class Area:
    @staticmethod
    def IsInArea(x_pos):
        if(x_pos < 0):
            return 0
        
        bandwidth = 1/Area.NAreas
        for n in range(1, Area.NAreas+1):
            if x_pos < bandwidth * n :
                return n

        return Area.NAreas + 1


    @staticmethod
    def SetArea(n_areas):
        Area.NAreas = n_areas
        Area.StateNames = ['Outside Entrance',] + [f'Area {i}' for i in range(1, n_areas + 1)] + ['Outside Exit']

    NAreas = 1
    StateNames = []

class PersonLocation:
    def __init__(self,id):
        self.id = id
        self.observations = []
        self.last_location = 0
        self.LocationChanged = Event()
        self.last_update_time = datetime.now()
        self.color = self.generate_random_color()
        

    def update(self,person):
        self.observations.append(person)
        old_last_location = self.last_location
        self.last_location = self.IsInArea()
        self.last_update_time = datetime.now()

        if(self.last_location != old_last_location):
            self.location_changed()
            return True
        return False
    
    

    def IsInArea(self):
        if(len(self.observations) == 0):
            return 0
        
        bb = self.observations[-1].boundingbox
        return Area.IsInArea(bb.x + bb.width/2)

    def last_update_is_older_than(self,msec):
        current_datetime = datetime.now()
        time_difference = current_datetime - self.last_update_time
        threshold = timedelta(milliseconds=msec)
        return time_difference > threshold

    def HasLeft(self):
        if(self.last_update_is_older_than(1000) ==True or self.last_location == Area.NAreas+1):
            old_last_location = self.last_location
            self.last_location = Area.NAreas+1
            self.last_update_time = datetime.now()

            if(self.last_location != old_last_location):
                self.location_changed()
            return True
        else:
            return False
    
    def location_changed(self):
        self.LocationChanged(self, self.last_location)

        s = MidiController.getInstance()
        s.Stop(id)
        s.Play(self.last_location,id)


        
    def generate_random_color(self):
        r = random.randint(0, 255)  # Random value for red (0-255)
        g = random.randint(0, 255)  # Random value for green (0-255)
        b = random.randint(0, 255)  # Random value for blue (0-255)
        return (r,g,b)

    
