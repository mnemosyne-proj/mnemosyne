#
# partner.py <Peter.Bienstman@UGent.be>
#

import os

class Partner(object):

    """Common code between Client and Server."""

    def __init__(self, ui):
        self.ui = ui
        
    def stream_binary_file(self, binary_file, file_size,
                           progress_bar=True):
        buffer = binary_file.read(self.BUFFER_SIZE)
        if progress_bar:
            self.ui.set_progress_range(0, file_size)
            self.ui.set_progress_update_interval(file_size/50)
            bytes_read = len(buffer)
        while buffer:
            yield buffer
            buffer = binary_file.read(self.BUFFER_SIZE)
            if progress_bar:
                self.ui.set_progress_value(bytes_read)
                bytes_read += len(buffer)
        if progress_bar:
            self.ui.set_progress_value(file_size)
        
    def download_binary_file(self, filename, stream, file_size,
                             progress_bar=True):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        downloaded_file = file(filename, "wb")
        if progress_bar:
            self.ui.set_progress_range(0, file_size)
            self.ui.set_progress_update_interval(file_size/50)
            bytes_read = 0
        buffer = stream.read(self.BUFFER_SIZE)
        while buffer:
            downloaded_file.write(buffer)
            if progress_bar:
                bytes_read += len(buffer)
                self.ui.set_progress_value(bytes_read)
            buffer = stream.read(self.BUFFER_SIZE)
        if progress_bar:
            self.ui.set_progress_value(file_size)
        downloaded_file.close()
        
