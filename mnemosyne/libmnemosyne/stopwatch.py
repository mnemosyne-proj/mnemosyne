#
# stopwatch.py <Peter.Bienstman@gmail.com>
#

import time

from mnemosyne.libmnemosyne.component import Component


class Stopwatch(Component):

    """The main use of the stop watch is to measure the time it takes the user
    to answer a question. 'start_time' is used to keep track of when the card
    was first shown.

    """

    component_type = "stopwatch"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self.start_time = 0
        self.start_time_of_leg = 0
        self.running_time = 0

    def start(self):
        self.start_time = time.time()
        self.start_time_of_leg = self.start_time
        self.running_time = 0

    def pause(self):
        self.running_time += time.time() - self.start_time_of_leg

    def unpause(self):
        self.start_time_of_leg = time.time()

    def stop(self):
        # Don't reset start_time here yet, as we rely on it to know when we
        # first showed the card.
        self.running_time += time.time() - self.start_time_of_leg
        return self.running_time

    def time(self):
        return self.running_time

