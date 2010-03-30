#
# server.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>

import os
import cgi
import select
import tarfile
import tempfile
import cStringIO
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from data_format import DataFormat


# Avoid delays caused by Nagle's algorithm.
# http://www.cmlenz.net/archives/2008/03/python-httplib-performance-problems

import socket
realsocket = socket.socket
def socketwrap(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    sockobj = realsocket(family, type, proto)
    sockobj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sockobj
socket.socket = socketwrap

# Work around http://bugs.python.org/issue6085.

def not_insane_address_string(self):
    host, port = self.client_address[:2]
    return "%s (no getfqdn)" % host

WSGIRequestHandler.address_string = not_insane_address_string

# Don't pollute our testsuite output.

def dont_log(*kwargs):
    pass

WSGIRequestHandler.log_message = dont_log


class Server(WSGIServer):

    program_name = "unknown-SRS-app"
    program_version = "unknown"

    stop_after_sync = False # Setting this True is useful for the testsuite. 

    def __init__(self, machine_id, host, port, ui):
        WSGIServer.__init__(self, (host, port), WSGIRequestHandler)
        self.set_app(self.wsgi_app)
        self.ui = ui
        self.data_format = DataFormat()
        self.stopped = False
        self.logged_in = False
        self.machine_id = machine_id
        self.client_info = {}

    def wsgi_app(self, environ, start_response):
        status, mime, method, args = self.get_method(environ)
        response_headers = [("Content-type", mime)]
        start_response(status, response_headers)
        if method:
            return getattr(self, method)(environ, **args)
        else:
            return status

    def serve_forever(self):
        self.ui.status_bar_message("Waiting for client connection...")
        while not self.stopped:
            if select.select([self.socket], [], [])[0]:
                self.handle_request()
        self.socket.close()

    def get_method(self, environ):
        # Convert e.g. GET /foo/bar into get_foo_bar.
        method = (environ["REQUEST_METHOD"] + \
                "_".join(environ["PATH_INFO"].split("/"))).lower()
        if method != "put_login" and not self.logged_in:
            return "403 Forbidden", "text/plain", None, None
        if hasattr(self, method) and callable(getattr(self, method)):
            args = cgi.parse_qs(environ["QUERY_STRING"])
            args = dict([(key, val[0]) for key, val in args.iteritems()])
            if len(args) == 0:
                return "200 OK", "xml/text", method, args
            else:
                return "400 Bad Request", "text/plain", None, None
        else:
            return "404 Not Found", "text/plain", None, None

    def stop(self):
        self.stopped = True

    # The following functions are to be overridden by the actual server code,
    # to implement e.g. authorisation and storage.

    def authorise(self, username, password):

        """Returs True if 'password' is correct for 'username'."""
        
        raise NotImplementedError

    def open_database(self, database_name):

        """Sets self.database to a database object for the database named
        'database_name'. Should create the database if it does not exist yet.

        """

        raise NotImplementedError

    # The following are methods that are supported by the server through GET
    # and PUT calls. 'get_foo_bar' gets executed after a 'GET /foo/bar'
    # request. Similarly, 'put_foo_bar' gets executed after a 'PUT /foo/bar'
    # request.

    def put_login(self, environ):
        self.ui.status_bar_message("Client logging in...")
        client_info_repr = environ["wsgi.input"].readline()
        self.client_info = \
            self.data_format.parse_partner_info(client_info_repr)
        if not self.authorise(self.client_info["username"],
            self.client_info["password"]):
            self.logged_in = False
            return "403 Forbidden"
        self.logged_in = True
        self.open_database(self.client_info["database_name"])
        self.database.set_sync_partner_info(self.client_info)
        self.database.backup()
        self.database.create_partnership_if_needed_for(\
            self.client_info["machine_id"])
        # Note that we need to send 'user_id' to the client as well, so that the
        # client can make sure the 'user_id's (used to label the anynymous
        # uploaded logs) are consistent across machines.
        server_info = {"user_id": self.database.user_id(),
            "machine_id": self.machine_id,
            "program_name": self.program_name,
            "program_version": self.program_version}
        return self.data_format.repr_partner_info(server_info)

    def put_client_log_entries(self, environ):
        self.ui.status_bar_message("Receiving client log entries...")
        # Since chunked requests are not supported by the WSGI 1.x standard,
        # the client does not set Content-Length in order to be able to
        # stream the log entries. Therefore, it is our responsability that we
        # consume the entire stream, nothing more and nothing less. For that,
        # we use the file format footer as a sentinel.
        # For simplicity, we also keep the entire stream in memory, as the
        # server is not expected to be resource limited.
        sentinel = self.data_format.log_entries_footer
        socket = environ["wsgi.input"]
        number_of_entries = int(socket.readline())
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)        
        lines = []
        line = socket.readline()
        lines.append(line)
        while not line.endswith(sentinel):
            line = socket.readline()
            lines.append(line)
        # In order to do conflict resolution easily, one of the sync partners
        # has to have both logs in memory. We do this at the server side, as
        # the client could be a resource-limited mobile device.
        self.client_log = []
        count = 0
        data_stream = cStringIO.StringIO("".join(lines))
        for log_entry in self.data_format.parse_log_entries(data_stream):
            self.client_log.append(log_entry)
            count += 1
            progress_dialog.set_value(count)
        self.ui.status_bar_message("Waiting for client to finish...")
        return "OK"

    def get_server_log_entries(self, environ):
        self.ui.status_bar_message("Sending log entries to client...")
        number_of_entries = self.database.number_of_log_entries_to_sync_for(\
            self.client_info["machine_id"])
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)
        progress_dialog.set_text("Sending log entries to client...")
        buffer = str(number_of_entries) + "\n"
        buffer += self.data_format.log_entries_header
        BUFFER_SIZE = 8192
        count = 0
        for log_entry in self.database.log_entries_to_sync_for(\
            self.client_info["machine_id"]):
            count += 1
            progress_dialog.set_value(count)
            buffer += self.data_format.repr_log_entry(log_entry)
            if len(buffer) > BUFFER_SIZE:
                yield buffer.encode("utf-8")
                buffer = ""
        buffer += self.data_format.log_entries_footer
        yield buffer.encode("utf-8")
        # Now that all the data is underway to the client, we can start
        # applying the client log entries.
        for log_entry in self.client_log:
            self.database.apply_log_entry(log_entry)
        self.database.update_last_sync_log_entry_for(\
            self.client_info["machine_id"])
        
    def put_client_media_files(self, environ):
        self.ui.status_bar_message("Receiving client media files...")
        try:
            socket = environ["wsgi.input"]
            size = int(socket.readline())
            tar_pipe = tarfile.open(mode="r|", fileobj=socket)
            # Work around http://bugs.python.org/issue7693.
            tar_pipe.extractall(self.database.mediadir().encode("utf-8"))
        except:
            return "CANCEL"
        return "OK"
    
    def get_server_media_files(self, environ):
        self.ui.status_bar_message("Sending media files to client...")
        try:
            # Determine files to send across.
            self.database.check_for_updated_media_files()
            filenames = list(self.database.media_filenames_to_sync_for(\
                self.client_info["machine_id"]))
            # TODO: implement creating pictures from cards, based on the
            # following client_info fields: "cards_as_pictures",
            # "cards_pictures_res", "reset_cards_as_pictures".
            if len(filenames) == 0:
                yield "0\n"
                return
            # Create a temporary tar file with the files.
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file_name = tmp_file.name
            saved_path = os.getcwdu()
            os.chdir(self.database.mediadir())
            BUFFER_SIZE = 8192
            tar_pipe = tarfile.open(mode="w|", fileobj=tmp_file,
                bufsize=BUFFER_SIZE, format=tarfile.PAX_FORMAT)
            for filename in filenames:
                tar_pipe.add(filename)
            tar_pipe.close()
            # Determine tar file size.
            tmp_file = file(tmp_file_name, "rb")
            file_size = os.path.getsize(tmp_file_name)
            progress_dialog = self.ui.get_progress_dialog()
            progress_dialog.set_range(0, file_size)
            # Send tar file across.
            progress_dialog.set_text("Sending media files to client...")
            buffer = str(file_size) + "\n" + tmp_file.read(BUFFER_SIZE)
            count = BUFFER_SIZE
            while buffer:
                progress_dialog.set_value(count)
                yield buffer
                buffer = tmp_file.read(BUFFER_SIZE)
                count += BUFFER_SIZE
            progress_dialog.set_value(file_size)
            os.remove(tmp_file_name)
            os.chdir(saved_path)
        except:
            yield "CANCEL"

    def get_sync_finish(self, environ):
        self.ui.status_bar_message("Waiting for client to finish...")
        self.logged_in = False
        if self.stop_after_sync:
            self.stop()
        return "OK"
