#
# stopwatch.py <Peter.Bienstman@UGent.be>
#

import time


class Stopwatch(object):
    
    """The main use of the stop watch is to measure the time it takes the user
    to answer a question.
    
    """

    def __init__(self):
        self.start_time = 0
        self.running_time = 0

    def start(self):
        self.start_time = time.time()
        self.running_time = 0

    def pause(self):
        self.running_time += time.time() - self.start_time

    def unpause(self):
        self.start_time = time.time()

    def stop(self):
        # Don't reset start_time here yet, as we rely on it to know when we
        # first showed the card.
        self.running_time += time.time() - self.start_time
        return self.running_time
        
    def time(self):
        return self.running_time


stopwatch = Stopwatch()

