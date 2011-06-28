#
# partner.py <Peter.Bienstman@UGent.be>
#

from utils import SyncError

BUFFER_SIZE = 8192


class Partner(object):

    """Common code between Client and Server."""

    def __init__(self, ui):
        self.ui = ui

    def stream_log_entries(self, log_entries, number_of_entries):

        """As the first line in the stream, we send across the number of log
        entries, so that the other side can track progress. We also buffer the
        stream until we have sufficient data to send, in order to improve
        throughput.
        We also tried compression here, but for typical scenarios that seems
        to be slightly slower on a WLAN and mobile phone.

        """
        
        self.ui.set_progress_range(0, number_of_entries)
        self.ui.set_progress_update_interval(number_of_entries/50)
        buffer = self.text_format.log_entries_header(number_of_entries)
        count = 0
        for log_entry in log_entries:
            count += 1
            self.ui.set_progress_value(count)
            buffer += self.text_format.repr_log_entry(log_entry)
            if len(buffer) > BUFFER_SIZE:
                yield buffer.encode("utf-8")
                buffer = ""
        buffer += self.text_format.log_entries_footer()
        yield buffer.encode("utf-8")

    def download_log_entries(self, stream, callback, context):
        element_loop = self.text_format.parse_log_entries(stream)        
        try:
            number_of_entries = int(element_loop.next())
        except:
            raise SyncError("Downloading log entries: error on remote side.")
        if number_of_entries == 0:
            return
        self.ui.set_progress_range(0, number_of_entries)
        self.ui.set_progress_update_interval(number_of_entries/50)
        count = 0
        for log_entry in element_loop:
            callback(context, log_entry)
            count += 1
            self.ui.set_progress_value(count)
        self.ui.set_progress_value(number_of_entries)
        
    def stream_binary_file(self, binary_file, file_size):
        self.ui.set_progress_range(0, file_size)
        self.ui.set_progress_update_interval(file_size/50)
        #buffer = str(file_size) + "\n" + binary_file.read(BUFFER_SIZE)
        buffer = binary_file.read(BUFFER_SIZE)
        count = BUFFER_SIZE
        while buffer:
            self.ui.set_progress_value(count)
            yield buffer
            buffer = binary_file.read(BUFFER_SIZE)
            count += BUFFER_SIZE
        self.ui.set_progress_value(file_size)

    def download_binary_file(self, filename, stream, file_size):
        downloaded_file = file(filename, "wb")
        #try:
        #    file_size = int(stream.readline())
        #except:
        #    raise SyncError("Downloading binary file: error on remote side.")
        self.ui.set_progress_range(0, file_size)
        self.ui.set_progress_update_interval(file_size/50)
        remaining = file_size
        while remaining:
            if remaining < BUFFER_SIZE:
                downloaded_file.write(stream.read(remaining))
                remaining = 0
            else:
                data = stream.read(BUFFER_SIZE)
                #import sys; sys.stderr.write("---"+data+"---")
                downloaded_file.write(data)                
                #downloaded_file.write(stream.read(BUFFER_SIZE))
                remaining -= BUFFER_SIZE
            self.ui.set_progress_value(file_size - remaining)


        # TODO: tmp hack, times out but saves the day.
        data = stream.read(0)
        #data = stream.read(BUFFER_SIZE)
        #import sys; sys.stderr.write("---"+data+"---")
        #downloaded_file.write(data)          


        
        self.ui.set_progress_value(file_size)
        downloaded_file.close()
