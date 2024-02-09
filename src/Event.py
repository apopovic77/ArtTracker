class Event:
    def __init__(self):
        self._handlers = []

    def subscribe(self, handler):
        self._handlers.append(handler)

    def unsubscribe(self, handler):
        self._handlers.remove(handler)

    def trigger(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)