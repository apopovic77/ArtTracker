import time
import threading
import curses

class ConsoleRenderer:
    def __init__(self, id=0):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(0)  # Make cursor invisible

        self.xpos = 0
        self.ypos = 0.5  # Set default ypos to be in the middle
        self.stop = False
        self.thread = threading.Thread(target=self.render_loop)

        self.circle = [
            "  ***  ",
            " *   * ",
            f"*  {id}  *",
            "*     *",
            "*     *",
            " *   * ",
            "  ***  "
        ]

    def start(self):
        self.thread.start()

    def set_position(self, xpos, ypos=None):
        self.xpos = max(0, min(1, xpos))  # Ensure xpos is between 0 and 1
        if ypos is not None:  # Only update ypos if a value was provided
            self.ypos = max(0, min(1, ypos))  # Ensure ypos is between 0 and 1

    def render_loop(self):
        while not self.stop:
            self.stdscr.clear()
            position_x = int(self.xpos * (self.stdscr.getmaxyx()[1] - len(self.circle[0])))
            position_y = int(self.ypos * (self.stdscr.getmaxyx()[0] - len(self.circle)))
            for i, line in enumerate(self.circle):
                self.stdscr.addstr(position_y + i, position_x, line)
            self.stdscr.refresh()
            time.sleep(0.01)

    def stop(self):
        self.stop = True
        self.thread.join()
        self.stdscr.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


# # Create a renderer with ID 5
# renderer = ConsoleRenderer(5)
# renderer.start()

# # Animate the character from left to right and back
# try:
#     direction = 1
#     while True:
#         new_xpos = renderer.xpos + 0.01 * direction

#         # If we hit the edge of the screen, reverse direction
#         if new_xpos >= 1.0:
#             new_xpos = 1.0
#             direction = -1
#         elif new_xpos <= 0.0:
#             new_xpos = 0.0
#             direction = 1

#         # Update position
#         renderer.set_position(new_xpos, 0.5)
#         time.sleep(0.01)
# except KeyboardInterrupt:
#     renderer.stop()
