#
# server.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>

import os
import cgi
import uuid
import time
import select
import tarfile
import tempfile
import cStringIO
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from text_formats.xml_format import XMLFormat


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


# Register binary file formats to send to clients on first sync.

from binary_formats.mnemosyne_format import MnemosyneFormat
binary_formats = [MnemosyneFormat]


BUFFER_SIZE = 8192
        

class Session(object):

    def __init__(self, client_info, database):
        self.token = str(uuid.uuid4())
        self.client_info = client_info
        self.database = database
        self.client_log = []
        self.expires = time.time() + 60*60
        self.backup_file = self.database.backup()
        self.database.set_sync_partner_info(client_info)
        self.database.create_partnership_if_needed_for(client_info["machine_id"])

    def is_expired(self):
        return time.time() > self.expired

    def close(self):
        self.database.update_last_sync_log_entry_for(self.client_info["machine_id"])
        self.database.save()

    def terminate(self):

        """Restore from backup if the session failed to close normally."""

        self.database.restore(self.backup_file)


class Server(WSGIServer):

    program_name = "unknown-SRS-app"
    program_version = "unknown"

    stop_after_sync = False # Setting this True is useful for the testsuite. 

    def __init__(self, machine_id, host, port, ui):
        self.machine_id = machine_id
        WSGIServer.__init__(self, (host, port), WSGIRequestHandler)
        self.set_app(self.wsgi_app)
        self.ui = ui
        self.text_format = XMLFormat()
        self.stopped = False
        self.sessions = {} # {session_token: session}
        self.session_token_for_user = {} # {user_name: session_token}

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
        args = cgi.parse_qs(environ["QUERY_STRING"])
        args = dict([(key, val[0]) for key, val in args.iteritems()])
        # Login method.
        if method == "put_login":
            if len(args) == 0:
                return "200 OK", "xml/text", method, args
            else:
                return "400 Bad Request", "text/plain", None, None                
        # See if the token matches.
        if not "session_token" in args or args["session_token"] \
            not in self.sessions:
            return "403 Forbidden", "text/plain", None, None
        # Call the method.
        if hasattr(self, method) and callable(getattr(self, method)):
            if len(args) == 1:
                return "200 OK", "xml/text", method, args
            else:
                return "400 Bad Request", "text/plain", None, None
        else:
            return "404 Not Found", "text/plain", None, None

    def create_session(self, client_info):
        database = self.open_database(client_info["database_name"])
        session = Session(client_info, database)
        self.sessions[session.token] = session
        self.session_token_for_user[client_info["username"]] = session.token
        return session

    def close_session_with_token(self, session_token):
        session = self.sessions[session_token]
        session.close()        
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]
        
    def terminate_session_with_token(self, session_token):

        """Clean up a session which failed to close normally."""

        session = self.sessions[session_token]
        session.terminate()        
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]
        
    def stop(self):
        self.stopped = True

    def supports_binary_log_download(self, program_name, program_version):
        result = False
        for format in binary_formats:
            if format.supports(program_name, program_version):
                result = True
        return result

    # The following functions are to be overridden by the actual server code,
    # to implement e.g. authorisation and storage.

    def authorise(self, username, password):

        """Returns True if 'password' is correct for 'username'."""
        
        raise NotImplementedError

    def open_database(self, database_name):

        """Returns a database object for the database named 'database_name'.
        Should create the database if it does not exist yet.

        """

        raise NotImplementedError
    
    # The following are methods that are supported by the server through GET
    # and PUT calls. 'get_foo_bar' gets executed after a 'GET /foo/bar'
    # request. Similarly, 'put_foo_bar' gets executed after a 'PUT /foo/bar'
    # request.

    def put_login(self, environ):
        self.ui.status_bar_message("Client logging in...")
        client_info_repr = environ["wsgi.input"].readline()
        client_info = self.text_format.parse_partner_info(client_info_repr)
        if not self.authorise(client_info["username"],
            client_info["password"]):
            return "403 Forbidden"
        # Close old session if it failed to finish properly.
        old_running_session_token = self.session_token_for_user.\
            get(client_info["username"])
        if old_running_session_token:
            self.terminate_session_with_token(old_running_session_token)
        session = self.create_session(client_info)
        # Note that we need to send 'user_id' to the client as well, so that the
        # client can make sure the 'user_id's (used to label the anynymous
        # uploaded logs) are consistent across machines.
        server_info = {"user_id": session.database.user_id(),
            "machine_id": self.machine_id,
            "program_name": self.program_name,
            "program_version": self.program_version,
            "session_token": session.token,
            "supports_binary_log_download": self.supports_binary_log_download\
                (client_info["program_name"], client_info["program_version"])}
        # We check if files were updated outside of the program. This can
        # generate MEDIA_UPDATED log entries, so it should be done first.
        session.database.check_for_updated_media_files()
        return self.text_format.repr_partner_info(server_info)

    def put_client_log_entries(self, environ, session_token):
        self.ui.status_bar_message("Receiving client log entries...")
        session = self.sessions[session_token]
        # Since chunked requests are not supported by the WSGI 1.x standard,
        # the client does not set Content-Length in order to be able to
        # stream the log entries. Therefore, it is our responsability that we
        # consume the entire stream, nothing more and nothing less. For that,
        # we use the file format footer as a sentinel.
        # For simplicity, we also keep the entire stream in memory, as the
        # server is not expected to be resource limited.
        sentinel = self.text_format.log_entries_footer()
        socket = environ["wsgi.input"]      
        lines = []
        line = socket.readline()
        lines.append(line)
        while not line.endswith(sentinel):
            line = socket.readline()
            lines.append(line)
        # In order to do conflict resolution easily, one of the sync partners
        # has to have both logs in memory. We do this at the server side, as
        # the client could be a resource-limited mobile device.
        session.client_log = []
        data_stream = cStringIO.StringIO("".join(lines))
        element_loop = self.text_format.parse_log_entries(data_stream)
        number_of_entries = element_loop.next()
        count = 0
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)  
        for log_entry in element_loop:
            session.client_log.append(log_entry)
            count += 1
            progress_dialog.set_value(count)
        self.ui.status_bar_message("Waiting for client to finish...")
        return "OK"

    def get_server_log_entries(self, environ, session_token):
        self.ui.status_bar_message("Sending log entries to client...")
        session = self.sessions[session_token]
        number_of_entries = session.database.\
            number_of_log_entries_to_sync_for(\
            session.client_info["machine_id"],
            session.client_info["interested_in_old_reps"])
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)
        progress_dialog.set_text("Sending log entries to client...")
        buffer = self.text_format.log_entries_header(number_of_entries)
        count = 0
        for log_entry in session.database.log_entries_to_sync_for(\
            session.client_info["machine_id"],
            session.client_info["interested_in_old_reps"]):
            count += 1
            progress_dialog.set_value(count)
            buffer += self.text_format.repr_log_entry(log_entry)
            if len(buffer) > BUFFER_SIZE:
                yield buffer.encode("utf-8")
                buffer = ""
        buffer += self.text_format.log_entries_footer()
        yield buffer.encode("utf-8")
        # Now that all the data is underway to the client, we can start
        # applying the client log entries.
        for log_entry in session.client_log:
            session.database.apply_log_entry(log_entry)
            
    def get_server_binary_log_entries(self, environ, session_token):
        self.ui.status_bar_message("Sending binary log entries to client...")
        # Construct binary file.
        session = self.sessions[session_token]
        for binary_format in binary_formats:
            if binary_format.supports(session.client_info["program_name"],
                                      session.client_info["program_version"]):
                binary_format = binary_format(session.database)
                binary_file, file_size = binary_format.binary_file_and_size(\
                    session.client_info["interested_in_old_reps"])
                break
        # Send it across.
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_text("Sending binary log entries to client...")
        progress_dialog.set_range(0, file_size)        
        buffer = str(file_size) + "\n" + binary_file.read(BUFFER_SIZE)
        count = BUFFER_SIZE
        while buffer:
            progress_dialog.set_value(count)
            yield buffer
            buffer = binary_file.read(BUFFER_SIZE)
            count += BUFFER_SIZE
        progress_dialog.set_value(file_size)
        # Clean up if needed.
        binary_format.clean_up()
        # This is the initial sync, we don't need to apply client log entries.
            
    def put_client_media_files(self, environ, session_token):
        self.ui.status_bar_message("Receiving client media files...")
        try:
            session = self.sessions[session_token]
            socket = environ["wsgi.input"]
            size = int(socket.readline())
            tar_pipe = tarfile.open(mode="r|", fileobj=socket)
            # Work around http://bugs.python.org/issue7693.
            tar_pipe.extractall(session.database.mediadir().encode("utf-8"))
        except:
            return "CANCEL"
        return "OK"
    
    def get_server_media_files(self, environ, session_token):
        self.ui.status_bar_message("Sending media files to client...")
        try:
            # Determine files to send across.
            session = self.sessions[session_token]
            filenames = list(session.database.media_filenames_to_sync_for(\
                session.client_info["machine_id"]))
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
            os.chdir(session.database.mediadir())
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

    def get_sync_finish(self, environ, session_token):
        self.ui.status_bar_message("Waiting for client to finish...")
        self.close_session_with_token(session_token)
        # Now is a good time to garbage-collect dangling sessions.
        for session in self.sessions:
            if session.is_expired():
                self.terminate_session_with_token(session.token)                
        if self.stop_after_sync:
            self.stop()
        return "OK"
