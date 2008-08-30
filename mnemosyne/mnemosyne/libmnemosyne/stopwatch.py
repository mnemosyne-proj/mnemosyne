#
# stopwatch.py <Peter.Bienstman@UGent.be>
#

import time


class Stopwatch(object):

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
        self.running_time += time.time() - self.start_time
        self.start_time = 0
        return self.running_time
        
    def time(self):
        return self.running_time

