#
# partner.py <Peter.Bienstman@UGent.be>
#

class Partner(object):

    """Common code between Client and Server."""

    def __init__(self, ui):
        self.ui = ui
        
    def stream_binary_file(self, binary_file, file_size):
        self.ui.set_progress_range(0, file_size)
        self.ui.set_progress_update_interval(file_size/50)
        buffer = binary_file.read(self.BUFFER_SIZE)
        count = self.BUFFER_SIZE
        while buffer:
            self.ui.set_progress_value(count)
            yield buffer
            buffer = binary_file.read(self.BUFFER_SIZE)
            count += self.BUFFER_SIZE
        self.ui.set_progress_value(file_size)

    def download_binary_file(self, filename, stream, file_size):
        downloaded_file = file(filename, "wb")
        self.ui.set_progress_range(0, file_size)
        self.ui.set_progress_update_interval(file_size/50)
        bytes_read = 0
        data = stream.read(self.BUFFER_SIZE)
        while data:
            downloaded_file.write(data)
            bytes_read += len(data)
            self.ui.set_progress_value(bytes_read)
            data = stream.read(self.BUFFER_SIZE)        
        self.ui.set_progress_value(file_size)
        downloaded_file.close()
