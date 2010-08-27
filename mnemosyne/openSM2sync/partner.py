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

        """Send log entries across in a streaming manner.
        Normally, one would use "Transfer-Encoding: chunked" for that, but
        chunked requests are not supported by the WSGI 1.x standard.
        However, it seems we can get around sending a Content-Length header if
        the server knows when the datastream ends. We use the data format
        footer as a terminator for that. The server then uses the class
        UnsizedLogEntryStreamReader to read that stream.
        As the first line in the stream, we send across the number of log
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
        if 1:
            number_of_entries = int(element_loop.next())
        else:
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
        buffer = str(file_size) + "\n" + binary_file.read(BUFFER_SIZE)
        count = BUFFER_SIZE
        while buffer:
            self.ui.set_progress_value(count)
            yield buffer
            buffer = binary_file.read(BUFFER_SIZE)
            count += BUFFER_SIZE
        self.ui.set_progress_value(file_size)

    def download_binary_file(self, filename, stream):
        downloaded_file = file(filename, "wb")
        try:
            file_size = int(stream.readline())
        except:
            raise SyncError("Downloading binary file: error on remote side.")
        self.ui.set_progress_range(0, file_size)
        self.ui.set_progress_update_interval(file_size/50)
        remaining = file_size
        while remaining:
            if remaining < BUFFER_SIZE:
                downloaded_file.write(stream.read(remaining))
                remaining = 0
            else:
                downloaded_file.write(stream.read(BUFFER_SIZE))
                remaining -= BUFFER_SIZE
            self.ui.set_progress_value(file_size - remaining)
        self.ui.set_progress_value(file_size)
        downloaded_file.close()


class UnsizedLogEntryStreamReader(object):

    """Since chunked requests are not supported by the WSGI 1.x standard, the
    client does not set Content-Length in order to be able to stream the log
    entries. Therefore, it is our responsability that we consume the entire
    stream, nothing more and nothing less. In practice, that means replacing
    reads with readlines and watching for a terminator string.
    
    """

    def __init__(self, stream, terminator):
        self.stream = stream
        self.terminator = terminator.rstrip()
        self.finished = False

    def read(self, size):
        if self.finished:
            return ""
        buffer = []
        buffer_length = 0
        while True:
            line = self.stream.readline()
            buffer_length += len(line)
            buffer.append(line)
            if line.rstrip().endswith(self.terminator):
                self.finished = True
            if self.finished or buffer_length > size:
                return "".join(buffer)
