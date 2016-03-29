#
# partner.py <Peter.Bienstman@UGent.be>
#

import os
from utils import file_, path_getsize

class Partner(object):

    """Common code between Client and Server."""

    def __init__(self, ui):
        self.ui = ui

    def stream_binary_file(self, filename, progress_bar=True):
        binary_file = file_(filename, "rb")
        file_size = path_getsize(filename)
        buffer = binary_file.read(self.BUFFER_SIZE)
        if progress_bar:
            self.ui.set_progress_range(file_size)
            self.ui.set_progress_update_interval(file_size/50)
            self.ui.increase_progress(len(buffer))
        while buffer:
            yield buffer
            buffer = binary_file.read(self.BUFFER_SIZE)
            if progress_bar:
                self.ui.increase_progress(len(buffer))
        if progress_bar:
            self.ui.set_progress_value(file_size)

    def download_binary_file(self, stream, filename, file_size,
                             progress_bar=True):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        downloaded_file = file_(filename, "wb")
        if progress_bar:
            self.ui.set_progress_range(file_size)
            self.ui.set_progress_update_interval(file_size/50)
        buffer = stream.read(self.BUFFER_SIZE)
        while buffer:
            downloaded_file.write(buffer)
            if progress_bar:
                self.ui.increase_progress(len(buffer))
            buffer = stream.read(self.BUFFER_SIZE)
        if progress_bar:
            self.ui.set_progress_value(file_size)
        downloaded_file.close()

